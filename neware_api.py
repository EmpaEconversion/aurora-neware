"""Python API for Neware Battery Testing System.

Contains a single class NewareAPI that provides methods to interact with the
Neware Battery Testing System.
"""

import re
import socket
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Literal

def _auto_convert_type(value: str) -> int|float|str:
    """Try to automatically convert a string to float or int."""
    if value=='--':
        return None
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value
    
def _extract_from_xml(
        xml_string: str,
        list_name: str = 'list',
        orient: Literal['records', 'list'] = 'records'
    ) -> list[dict] | dict[list]:
    """Extract elements inside <list> tags, convert to a list of dictionaries.

    Args:
        xml_string (str): raw xml string
        list_name (str): the tag that contains the list of elements to parse
        orient ('records' or 'list', default 'records'): whether to return a list of 
            dictionaries (records) or convert to a dictionary of lists (list)

    """
    # Parse response XML string
    root = ET.fromstring(xml_string)
    # Find <list> element
    list_element = root.find(list_name)
    # Extract <name> elements to a list of dictionaries
    result = []
    for el in list_element:
        el_dict = el.attrib
        if el.text:
            el_dict[el.tag] = el.text
        result.append(el_dict)
    result = [{k : _auto_convert_type(v) for k,v in el.items()} for el in result]
    if orient == 'list':
        result = _lod_to_dol(result)
    return result

def _lod_to_dol(ld: list[dict]) -> dict[list]:
    """Convert list of dictionaries to dictionary of lists."""
    return {k: [d[k] for d in ld] for k in ld[0]}

class NewareAPI:
    """Python API for Neware Battery Testing System.
    
    Provides a method to send and receive commands to the Neware Battery Testing
    System with xml strings, and convenience methods to start, stop, and get the
    status and data from the channels.
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 502):
        """Initialize the NewareAPI object with the IP, port, and channel map."""
        self.ip = ip
        self.port = port
        self.neware_socket = socket.socket()
        self.channel_map = None
        self.start_message = '<?xml version="1.0" encoding="UTF-8" ?><bts version="1.0">'
        self.end_message = "</bts>"
        self.termination = "\n\n#\r\n"

    def connect(self) -> None:
        """ Establish the TCP connection """
        self.neware_socket.connect((self.ip, self.port))
        connect = (
            '<cmd>connect</cmd>'
            '<username>admin</username><password>neware</password><type>bfgs</type>'
        )
        self.command(connect)
        self.channel_map = self.update_channel_map()

    def disconnect(self) -> None:
        """ Close the port """
        if self.neware_socket:
            self.neware_socket.close()

    def __enter__(self):
        """Establish the TCP connection when entering the context."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def command(self, cmd: str) -> str:
        """Send a command to the device, and return the response."""
        self.neware_socket.sendall(
            str.encode(self.start_message+cmd+self.end_message+self.termination, 'utf-8')
        )
        received = ""
        while not received.endswith(self.termination):
            received += self.neware_socket.recv(2048).decode()
        return received[:-len(self.termination)]

    def start_job(self, pipeline: str, sampleid: str, payload_xml_path: str, save_location: str = "C:\\Neware data\\") -> str:
        """Start designated payload file on a pipeline.

        Args:
            pipeline (str): pipeline to start the job on
            sampleid (str): barcode used in Newares BTS software
            payload_xml_path (str): path to payload file

        Returns:
            str: XML string response

        """
        pip = self.channel_map[pipeline]
        cmd = (
            '<cmd>start</cmd>'
            '<list count="1" DBC_CAN="1">'
            f'<start ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}"'
            f'subdevid="{pip["subdevid"]}" '
            f'chlid="{pip["Channelid"]}" '
            f'barcode="{sampleid}">'
            f'{payload_xml_path}</start>'
            f'<backup backupdir="{save_location}" remotedir="" filenametype="0" '
            'customfilename="" addtimewhenrepeat="0" createdirbydate="0" '
            'filetype="0" backupontime="0" backupontimeinterval="720" '
            'backupfree="1" />'
            '</list>'
        )
        return self.command(cmd)

    def stop_job(self, pipelines: str|list[str]|tuple[str]) -> str:
        """Stop job running on pipeline(s)."""
        if isinstance(pipelines, str):
            pipelines = [pipelines]

        header = f'<cmd>stop</cmd><list count = "{len(pipelines)}">'
        cmd_string = ""
        for pipeline in pipelines:
            pip = self.channel_map[pipeline]
            cmd_string += (
                f'\t\t<stop ip="{pip["ip"]}" devtype="{pip["devtype"]}" devid="{pip["devid"]}" '
                f'subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}">true</stop>\n'
            )
        footer = '</list>'
        return self.command(header+cmd_string+footer)

    def get_status(self, pipelines: str | list[str] = None) -> str:
        """Get status of pipeline(s).

        Args:
            pipelines (str|list[str], optional): list of pipeline IDs
                if not given, all pipelines from channel map are used

        Returns:
            list[dict]: a dictionary per channel with status

        """
        # Make list of pipelines
        if not pipelines:  # If no argument passed use all pipelines
            pipelines = self.channel_map.keys()
        if isinstance(pipelines,str):
            pipelines = [pipelines]
        
        # Create and submit command XML string
        header = f'<cmd>getchlstatus</cmd><list count = "{len(self.channel_map)}">'
        middle = ""
        for pipeline in pipelines:
            pip = self.channel_map[pipeline]
            middle += (
                f'<status ip="{pip["ip"]}" devtype="{pip["devtype"]}" '
                f'devid="{pip["devid"]}" subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}">true</status>'
            )
        footer = '</list>'
        xml_string = self.command(header+middle+footer)
        
        return _extract_from_xml(xml_string)

    def inquire_channel(self, pipelines: str | list[str] = None) -> list[dict]:
        """Inquire the status of the channel.

        Returns useful information like device id, cycle number, step, workstatus, current, voltage,
        time, and whether the channel is currently open.

        Args:
            pipelines (str|list[str], optional): pipeline IDs or list of pipeline Ids
                default: None, will get all pipeline IDs in the channel map

        Returns:
            list[dict]: a dictionary per channel with the latest info and data point

        """
        # Make list of pipelines
        if not pipelines:
            pipelines = self.channel_map.keys()
        if isinstance(pipelines, str):
            pipelines = [pipelines]
        
        # Create and submit command XML string
        header = (
            '<cmd>inquire</cmd>'
            f'<list count = "{len(self.channel_map)}">'
        )
        middle = ""
        for pipeline in pipelines:
            pip = self.channel_map[pipeline]
            middle += (
                f'<inquire ip="{pip["ip"]}" devtype="{pip["devtype"]}" '
                f'devid="{pip["devid"]}" subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}"\n'
                'aux="0" barcode="1">true</inquire>'
            )
        footer = '</list>'
        xml_string = self.command(header+middle+footer)

        return _extract_from_xml(xml_string)

    def download_data(self, pipeline: str) -> None:
        """Download the data points for chlid.

        Uses the channel map to get the device id, subdevice id, and channel id.

        """
        chunk_size = 1000
        data = []
        pip = self.channel_map[pipeline]
        devid = pip["devid"]
        subdevid = pip["subdevid"]
        chlid = pip["Channelid"]
        while len(data)%chunk_size == 0:
            cmd_string = (
                '<cmd>download</cmd>'
                f'<download devtype="{pip["devtype"]}" devid="{pip["devid"]}" subdevid="{pip["subdevid"]}" chlid="{pip["Channelid"]}" '
                f'auxid="0" testid="0" startpos="{len(data)+1}" count="{chunk_size}"/>'
            )
            xml_string = self.command(cmd_string)
            data+=_extract_from_xml(xml_string)
        # Orient as dict of lists
        return _lod_to_dol(data)

    def xml_to_csv(self, filepath: str) -> None:
        """Convert the xml file to csv file."""
        pattern = r'<(.*?)\/>'
        key_vals_pattern = r'(\w+)="([^"]*)"'
        buffer = ''
        data = []
        save_file = filepath.rsplit('.', 1)[0]
        with open(filepath, 'r', encoding='utf-8') as file:
            while True:
                chunk = buffer + file.read(2048)
                if not chunk:
                    break

                # Process the chunk up to the last complete piece of data
                last_newline = chunk.rfind('\n')
                if last_newline != -1:
                    data_to_process = chunk[:last_newline]
                    buffer = chunk[last_newline+1:]
                else:
                    data_to_process = chunk
                    buffer = ''
                # Regular expression pattern to match each row
                matches = re.findall(pattern, data_to_process)
                for match in matches:
                    # Fine Key-Value pairs
                    key_val_matches = re.findall(key_vals_pattern, match)
                    # Convert the matches into a dictionary
                    row = {key: value for key, value in key_val_matches}
                    data.append(row)
        df = pd.DataFrame(data)
        df.to_csv(save_file+'.csv', index=False)

    def device_info(self) -> list[dict]:
        """Get device information.

        Returns:
            list[dict]: IP, device type, device id, sub-device id and channel id of all channels

        """
        command = '<cmd>getdevinfo</cmd>'
        xml_string = self.command(command)
        return _extract_from_xml(xml_string, 'middle')
    
    def update_channel_map(self) -> None:
        devices = self.device_info()
        self.channel_map = {
            f"{d["devid"]}-{d["subdevid"]}-{d["Channelid"]}": d
            for d in devices
        }
