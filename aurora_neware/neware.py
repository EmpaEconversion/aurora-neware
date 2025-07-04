"""Python API for Neware Battery Testing System.

Contains a single class NewareAPI that provides methods to interact with the
Neware Battery Testing System.
"""

import re
import socket
from pathlib import Path
from types import TracebackType

from defusedxml import ElementTree

# Possible commands from Neware's API
# DONE
# connect, getdevinfo, getchlstatus, start, stop, download, downloadlog, inquire, inquiredf,
# clearflag, light, downloadStepLayer
# REMAINING
# broadcaststop, continue, chl_ctrl, goto, parallel, getparallel, resetalarm, reset


def _auto_convert_type(value: str) -> int | float | str | None:
    """Try to automatically convert a string to float or int."""
    if value == "--":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _xml_to_records(
    xml_string: str,
    list_name: str = "list",
) -> list[dict]:
    """Extract elements inside <list> tags, convert to a list of dictionaries.

    Args:
        xml_string: raw xml string
        list_name: the tag that contains the list of elements to parse

    Returns:
        list of dictionaries like 'orient = records' in JSON

    """
    # Parse response XML string
    root = ElementTree.fromstring(xml_string)
    # Find <list> element
    list_element = root.find(list_name)
    # Extract <name> elements to a list of dictionaries
    result = []
    for el in list_element:
        el_dict = el.attrib
        if el.text:
            el_dict[el.tag] = el.text
        result.append(el_dict)
    return [{k: _auto_convert_type(v) for k, v in el.items()} for el in result]


def _xml_to_lists(
    xml_string: str,
    list_name: str = "list",
) -> dict[str, list]:
    """Extract elements inside <list> tags, convert to a dictionary of lists.

    Args:
        xml_string: raw xml string
        list_name: the tag that contains the list of elements to parse

    Returns:
        dict where keys are the names of records, each has a list of values
            like 'orient = list' in JSON

    """
    result = _xml_to_records(xml_string, list_name)
    return _lod_to_dol(result)


def _lod_to_dol(ld: list[dict]) -> dict[str, list]:
    """Convert list of dictionaries to dictionary of lists."""
    try:
        return {k: [d[k] for d in ld] for k in ld[0]}
    except IndexError:
        return {}


class NewareAPI:
    """Python API for Neware Battery Testing System.

    Provides a method to send and receive commands to the Neware Battery Testing
    System with xml strings, and convenience methods to start, stop, and get the
    status and data from the channels.
    """

    def __init__(self, ip: str = "127.0.0.1", port: int = 502) -> None:
        """Initialize the NewareAPI object with the IP, port, and channel map."""
        self.ip = ip
        self.port = port
        self.neware_socket = socket.socket()
        self.channel_map: dict[str, dict] = {}
        self.start_message = '<?xml version="1.0" encoding="UTF-8" ?><bts version="1.0">'
        self.end_message = "</bts>"
        self.termination = "\n\n#\r\n"

    def connect(self) -> None:
        """Establish the TCP connection."""
        self.neware_socket.connect((self.ip, self.port))
        connect = "<cmd>connect</cmd><username>admin</username><password>neware</password><type>bfgs</type>"
        self.command(connect)
        self.channel_map = self.getdevinfo()

    def disconnect(self) -> None:
        """Close the port."""
        if self.neware_socket:
            self.neware_socket.close()

    def __enter__(self) -> "NewareAPI":
        """Establish the TCP connection when entering the context."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the port when exiting the context."""
        self.disconnect()

    def __del__(self) -> None:
        """Close the port when the object is deleted."""
        self.disconnect()

    def get_pipeline(self, pipeline_id: str) -> dict:
        """Get the channel information for a single pipeline."""
        try:
            return self.channel_map[pipeline_id]
        except KeyError as e:
            msg = (
                f"Pipeline ID {pipeline_id} not in channel map. "
                "Pipeline IDs are in the format {device ID}-{sub-device ID}-{channel ID}. "
                "On Neware cyclers these are usually integers e.g. 120-10-8 is device 120, sub-device 10, channel 8. "
                "You can check available pipelines with getdevinfo() or the 'neware status' CLI command."
            )
            raise KeyError(msg) from e

    def command(self, cmd: str) -> str:
        """Send a command to the device, and return the response."""
        self.neware_socket.sendall(
            str.encode(self.start_message + cmd + self.end_message + self.termination, "utf-8"),
        )
        received = ""
        while not received.endswith(self.termination):
            received += self.neware_socket.recv(2048).decode()
        return received[: -len(self.termination)]

    def start(
        self,
        pipeline_ids: str | list[str],
        sample_ids: str | list[str],
        xml_files: str | Path | list[str] | list[Path],
        save_location: str = "C:\\Neware data\\",
    ) -> list[dict]:
        """Start designated payload file on a pipeline.

        Args:
            pipeline_ids: pipeline to start the job on
            sample_ids: barcode used in Newares BTS software
            xml_files: path to payload file
            save_location: location to save the data

        Returns:
            one dictionary per channel, key 'start' is 'ok' if job started, otherwise 'false'

        """
        # Check inputs
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}
        if isinstance(sample_ids, str):
            sample_ids = [sample_ids]
        if isinstance(xml_files, list):
            xml_filepaths = [Path(f) for f in xml_files]
        if isinstance(xml_files, str | Path):
            xml_filepaths = [Path(xml_files)]
        if not all(f.exists() for f in xml_filepaths):
            raise FileNotFoundError

        allowed_states = ["finish", "stop", "protect"]
        status = self.inquire(pipeline_ids)
        blocked_pipelines = {
            k: v.get("workstatus") for k, v in status.items() if v.get("workstatus") not in allowed_states
        }
        if blocked_pipelines:
            msg = (
                "Can only start jobs if pipeline state is "
                f"{', '.join(repr(state) for state in allowed_states)}. "
                "The following pipelines are in blocked states: "
                f"{blocked_pipelines}"
            )
            raise ValueError(msg)

        # Create and submit command XML string
        header = f'<cmd>start</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip, payload, sampleid in zip(pipelines.values(), xml_filepaths, sample_ids, strict=True):
            middle += (
                f'<start ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" barcode="{sampleid}">'
                f"{payload}</start>"
            )
        footer = (
            f'<backup backupdir="{save_location}" remotedir="" filenametype="0" '
            'customfilename="" addtimewhenrepeat="0" createdirbydate="0" '
            'filetype="0" backupontime="1" backupontimeinterval="720" '
            'backupfree="1" /></list>"'
        )
        cmd = header + middle + footer
        result = self.command(cmd)
        return _xml_to_records(result)

    def stop(self, pipeline_ids: str | list[str] | tuple[str]) -> list[dict]:
        """Stop job running on pipeline(s)."""
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}

        header = f'<cmd>stop</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<stop ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}">true</stop>'
            )
        footer = "</list>"
        result = self.command(header + middle + footer)
        return _xml_to_records(result)

    def getchlstatus(self, pipeline_ids: str | list[str] | None = None) -> dict[str, dict]:
        """Get status of pipeline(s).

        Args:
            pipeline_ids (optional): pipeline ID or list of pipeline IDs
                if not given, all pipelines from channel map are used

        Returns:
            a dictionary per channel with status

        Raises:
            KeyError: if pipeline ID not in the channel map

        """
        # Get the (subset) of the channel map
        if not pipeline_ids:  # If no argument passed use all pipelines
            pipelines = self.channel_map
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}

        # Create and submit command XML string
        header = f'<cmd>getchlstatus</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<status ip="{pip["ip"]}" devtype="{pip["devtype"]}" '
                f'devid="{pip["devid"]}" subdevid="{pip["subdevid"]}" '
                f'chlid="{pip["Channelid"]}">true</status>'
            )
        footer = "</list>"
        xml_string = self.command(header + middle + footer)
        records = _xml_to_records(xml_string)

        # Sometimes the response subdevid is incorrectly 1
        # E.g. if you request the status of 13-5-5 it correctly gets the status of 13-5-5, but tells
        # you it is returning the status of 13-1-5.
        # Workaround: instead of returning the result directly, we merge it with the input
        # pipelines, prioritising the (correct) channel information from the channel map.
        return {
            pipeline_id: {**record, **pipeline_dict}
            for (pipeline_id, pipeline_dict), record in zip(pipelines.items(), records, strict=True)
        }

    def inquire(self, pipeline_ids: str | list[str] | None = None) -> dict[str, dict]:
        """Inquire the status of the channel.

        Returns useful information like device id, cycle number, step, workstatus, current, voltage,
        time, and whether the channel is currently open.

        Args:
            pipeline_ids (optional): pipeline IDs or list of pipeline Ids
                default: None, will get all pipeline IDs in the channel map

        Returns:
            a dictionary per channel with the latest info and data point
                key is the pipeline ID e.g. "13-1-5"

        """
        # Get the (subset) of the channel map
        if not pipeline_ids:  # If no argument passed use all pipelines
            pipelines = self.channel_map
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}

        # Create and submit command XML string
        header = f'<cmd>inquire</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<inquire ip="{pip["ip"]}" devtype="{pip["devtype"]}" '
                f'devid="{pip["devid"]}" subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}"\n'
                'aux="0" barcode="1">true</inquire>'
            )
        footer = "</list>"
        xml_string = self.command(header + middle + footer)

        records = _xml_to_records(xml_string)

        return {
            pipeline_id: {**record, **pipeline_dict}
            for (pipeline_id, pipeline_dict), record in zip(pipelines.items(), records, strict=True)
        }

    def inquiredf(self, pipeline_ids: str | list[str] | None = None) -> dict[str, dict]:
        """Use the inquiredf command on the channel.

        Returns information about the latest test e.g. test ID and number of datapoints.

        Args:
            pipeline_ids (optional): pipeline IDs or list of pipeline IDs
                default: None, will get all pipeline IDs in the channel map

        Returns:
            a dictionary per channel with the latest info and data point
                key is the pipeline ID e.g. "13-1-5"

        """
        # Get the (subset) of the channel map
        if not pipeline_ids:  # If no argument passed use all pipelines
            pipelines = self.channel_map
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}

        # Create and submit command XML string
        header = f'<cmd>inquiredf</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<chl devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" testid="0" />'
            )
        footer = "</list>"
        xml_string = self.command(header + middle + footer)
        records = _xml_to_records(xml_string)

        return {
            pipeline_id: {**record, **pipeline_dict}
            for (pipeline_id, pipeline_dict), record in zip(pipelines.items(), records, strict=True)
        }

    def downloadlog(self, pipeline_id: str) -> list[dict]:
        """Download the log information for latest test. Only queries one channel at a time.

        Args:
            pipeline_id: ID of the pipeline in format {devid}-{subdevid}-{chlid} e.g. 220-10-2

        Returns:
            List of dictionaries containing log information.

        """
        pip = self.get_pipeline(pipeline_id)
        command = (
            "<cmd>downloadlog</cmd>"
            f'<download devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
            f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" testid="0"/>'
        )
        result = self.command(command)
        return _xml_to_records(result)

    def download(self, pipeline_id: str, last_n_points: int = 10000) -> dict[str, list]:
        """Download the data points for a channel. By default grabs the last 10000 points.

        WARNING: for large amounts of data (>100k) this can take seconds.
        Download and parse the .nda/.ndax file if speed matters.

        Args:
            pipeline_id: ID of the pipeline in format {devid}-{subdevid}-{chlid} e.g. 220-10-2
            last_n_points: how many datapoints to download, set to 0 to get all data

        Returns:
            Dictionary of lists of data from latest test

        """
        res = self.inquiredf(pipeline_id)

        n_total = res[pipeline_id]["count"]
        start = min(n_total, n_total - last_n_points if last_n_points else 0)
        n_remaining = n_total - start
        chunk_size = 1000
        data: list[dict] = []
        pip = self.get_pipeline(pipeline_id)
        while n_remaining > 0:
            cmd_string = (
                "<cmd>download</cmd>"
                f'<download devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" '
                f'auxid="0" testid="0" startpos="{start + len(data) + 1}" count="{chunk_size}"/>'
            )
            xml_string = self.command(cmd_string)
            data += _xml_to_records(xml_string)
            n_remaining -= chunk_size
        # Orient as dict of lists
        return _lod_to_dol(data)

    def getdevinfo(self) -> dict[str, dict]:
        """Get device information.

        Returns:
            IP, device type, device id, sub-device id and channel id of all channels

        """
        command = "<cmd>getdevinfo</cmd>"
        xml_string = self.command(command)
        devices = _xml_to_records(xml_string, "middle")
        if not devices:
            msg = "No devices found. Check that devices are working in BTS Client."
            raise ValueError(msg)
        return {f"{d['devid']}-{d['subdevid']}-{d['Channelid']}": d for d in devices}

    def light(self, pipeline_ids: str | list[str], light_on: bool = True) -> list[dict]:
        """Set light on channel.

        Args:
            pipeline_ids: pipeline IDs to light
            light_on (default: True): whether to turn light on or off

        Returns:
            a dictionary per channel, key 'light' has value 'ok' if function worked

        """
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}
        light_str = "true" if light_on else "false"
        header = f'<cmd>light</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<light ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}">{light_str}</light>'
            )
        footer = "</list>"
        xml_string = self.command(header + middle + footer)
        return _xml_to_records(xml_string)

    def clearflag(self, pipeline_ids: str | list[str]) -> list[dict]:
        """Clear flag on channel e.g. after buzzer alarm.

        Args:
            pipeline_ids: pipeline IDs to light e.g. "120-3-8"

        Returns:
            a dictionary per channel, key 'clearflag' has value 'ok' if function worked

        """
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}
        header = f'<cmd>clearflag</cmd><list count = "{len(pipelines)}">'
        middle = ""
        for pip in pipelines.values():
            middle += (
                f'<clearflag ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}">true</clearflag>'
            )
        footer = "</list>"
        xml_string = self.command(header + middle + footer)
        return _xml_to_records(xml_string)

    def get_steps(self, pipeline_id: str) -> list[dict]:
        """Get the step layer of data, such as step index and type, start and end time etc."""
        pip = self.get_pipeline(pipeline_id)
        command = (
            f"<cmd>downloadStepLayer</cmd>"
            f'<downloadStepLayer devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
            f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" />'
        )
        xml_string = self.command(command)
        return _xml_to_records(xml_string)

    def get_testid(self, pipeline_ids: str | list[str] | None) -> dict[str, dict]:
        """Get the test ID of pipelines."""
        if pipeline_ids is None:
            pipelines = self.channel_map
        if isinstance(pipeline_ids, str):
            pipelines = {pipeline_ids: self.get_pipeline(pipeline_ids)}
        elif isinstance(pipeline_ids, list):
            pipelines = {p: self.get_pipeline(p) for p in pipeline_ids}
        # Download 0 data points to find test ID
        for pip in pipelines.values():
            command = (
                "<cmd>download</cmd>"
                f'<download devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" '
                f'auxid="0" testid="0" startpos="0" count="0"/>'
            )
            resp = self.command(command)
            match = re.search(r'(?<=testid=")\d+(?=")', resp)
            if match:
                # Add test number to the channel map info
                pip["test_id"] = int(match.group())
                pip["full_test_id"] = f"{pip['devid']}-{pip['subdevid']}-{pip['Channelid']}-{int(match.group())}"
            else:
                raise ValueError
        return pipelines
