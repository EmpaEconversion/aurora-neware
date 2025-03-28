"""CLI for the Neware battery cycling API."""

import json
from typing import Annotated

import typer

from neware_api import NewareAPI

app = typer.Typer()

IndentOption = Annotated[int | None, typer.Option(help="Indent the output.")]
PipelinesArgument = Annotated[list[str] | None, typer.Argument()]


@app.command()
def status(
    pipeline_ids: PipelinesArgument = None,
    indent: IndentOption = None,
) -> None:
    """Get the status of the cycling process for all or selected pipelines.

    Example usage:
    >>> neware statuss
    {"13-1-1": {"ip":127.0.0.1, "devtype": 27 ... }, "13-1-2": { ... }, ... }
    >>> neware status 13-1-5
    {"13-1-5":{...}}
    >>> neware status 13-1-5 14-3-5
    {"13-1-5":{...}, "14-3-5":{...}}

    Args:
        pipeline_ids (optional): list of pipeline IDs to get status from
            will use the full channel map if not provided
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquire(pipeline_ids), indent=indent))


@app.command()
def get_num_datapoints(
    pipeline_ids: PipelinesArgument = None,
    indent: IndentOption = None,
) -> None:
    """Get test information for all or selected pipelines.

    Example usage:
    >>> neware get-num-datapoints
    {"120-1-1": 20, "120-1-2": 45, ... }
    >>> neware get-num-datapoints 220-2-2
    {"220-2-2": 55}

    Args:
        pipeline_ids (optional): list of pipeline IDs in format {devid}-{subdevid}-{chlid} e.g. 220-10-1 220-10-2
            will use the full channel map if not provided`
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        output = {key: value["count"] for key, value in nw.inquiredf(pipeline_ids).items()}
    typer.echo(json.dumps(output, indent=indent))


@app.command()
def download(pipeline_id: str, n_points: int, indent: IndentOption = None) -> None:
    """Download data (voltage, current, time, etc.) from specified channel.

    Example usage:
    >>> neware download 220-10-1 10
    {"cycleid": [488, ...], "volt": [4.11252689361572, ... ], "curr": [0.00271010375581682, ...], ...}

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1
        n_points: last n points to download, set to 0 to download all data (can be slow)
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.download(pipeline_id, n_points), indent=indent))


@app.command()
def downloadlog(pipeline_id: str, indent: IndentOption = None) -> None:
    """Download log information from specified channel.

    Example usage:
    >>> neware downloadlog 220-10-1
    [{"seqid": 1, "log_code": 100000, "atime": "2024-12-12 15:31:01"}, ... ]

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.downloadlog(pipeline_id), indent=indent))


@app.command()
def start(pipeline_id: str, sample_id: str, xml_file: str, save_location: str | None = "C:\\Neware data\\") -> None:
    """Start job on selected channel.

    Example usage:
    >>> neware start 220-10-1 "my_sample_name" "C:/path/to/job.xml"
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 0, "start": "ok"}]
    >>> neware start 220-5-3 "my_sample_name" "C:/path/to/invalid.xml"
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 0, "start": "false"}]

    In the second case, download and check the Neware logs for more information.

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1
        sample_id: to use as a barcode in the experiment
        xml_file: path to a valid XML file with job information
        save_location: where to save the backup files

    """
    with NewareAPI() as nw:
        result = nw.start(
            pipeline_id,
            sample_id,
            xml_file,
            save_location=save_location,
        )
        typer.echo(json.dumps(result))


@app.command()
def stop(pipeline_id: str) -> None:
    """Stop job on selected channel.

    Example usage:
    >>> neware stop 220-10-1
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 1, "stop": "ok"}]

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1

    """
    with NewareAPI() as nw:
        result = nw.stop(pipeline_id)
        typer.echo(json.dumps(result))


@app.command()
def clearflag(pipeline_ids: Annotated[list[str], typer.Argument()], indent: IndentOption = None) -> None:
    """Clear flag on selected channel(s).

    Example usage:
    >>> neware clearflag 220-10-1
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 1, "clearflag": "ok"}]

    Args:
        pipeline_ids: list of pipeline IDs in format {devid}-{subdevid}-{chlii} e.g. 220-10-1 220-10-2
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.clearflag(pipeline_ids), indent=indent))


@app.command()
def testid(pipeline_ids: PipelinesArgument = None, indent: IndentOption = None) -> None:
    """Get the latest test ID from selected pipeline.

    Example usage:
    >>> neware testid 220-1-1
    {"220-1-1": {"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 1, "Channelid": 1,
    "channel": "true", "test_id": 66, "full_test_id": "220-1-1-66"}}

    Args:
        pipeline_ids (optional): list of pipeline IDs in format {devid}-{subdevid}-{chlid} e.g. 220-10-1 220-10-2
            will use the full channel map if not provided (warning: this function is slow compared to status)
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.get_testid(pipeline_ids), indent=indent))
