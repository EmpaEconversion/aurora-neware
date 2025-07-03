"""CLI for the Neware battery cycling API."""

import json
from pathlib import Path
from typing import Annotated

import typer

from aurora_neware import NewareAPI

app = typer.Typer()

IndentOption = Annotated[int | None, typer.Option(help="Indent the output.")]
PipelinesArgument = Annotated[list[str] | None, typer.Argument()]
NumberOfPoints = Annotated[int, typer.Argument()]
PathArgument = Annotated[Path, typer.Argument(help="Path to a file")]


VALID_STATES = ["working", "stop", "finish", "protect", "pause"]


def validate_state(state: list[str] | None) -> list[str]:
    """Validate the list of provided statuses."""
    if not state:
        return []
    invalid = [s for s in state if s not in VALID_STATES]
    if invalid:
        error_message = f"Invalid state: {', '.join(invalid)}. Valid options are: {', '.join(VALID_STATES)}"
        raise typer.BadParameter(error_message)
    return state


@app.command()
def status(
    pipeline_ids: PipelinesArgument = None,
    state: Annotated[
        list[str] | None,
        typer.Option(..., "--state", "-s", help="Allowed channel state(s)", callback=validate_state),
    ] = None,
    indent: IndentOption = None,
) -> None:
    """Get the status of the cycling process for all or selected pipelines.

    Example usage:
    >>> neware status
    {"13-1-1": {"ip":127.0.0.1, "devtype": 27 ... }, "13-1-2": { ... }, ... }
    >>> neware status 13-1-5
    {"13-1-5":{...}}
    >>> neware status 13-1-5 14-3-5
    {"13-1-5":{...}, "14-3-5":{...}}

    Args:
        pipeline_ids (optional): list of pipeline IDs to get status from
            will use the full channel map if not provided
        state (optional): list of allowed channel statuses
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        channels = nw.inquire(pipeline_ids)
        if state:
            channels = {key: value for key, value in channels.items() if value["workstatus"] in state}
        typer.echo(json.dumps(channels, indent=indent))


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
            will use the full channel map if not provided
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        output = {key: value["count"] for key, value in nw.inquiredf(pipeline_ids).items()}
    typer.echo(json.dumps(output, indent=indent))


@app.command()
def get_data(pipeline_id: str, n_points: NumberOfPoints = 0, indent: IndentOption = None) -> None:
    """Get data points (voltage, current, time, etc.) from specified channel.

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
def log(pipeline_id: str, indent: IndentOption = None) -> None:
    """Download log information from specified channel.

    Example usage:
    >>> neware log 220-10-1
    [{"seqid": 1, "log_code": 100000, "atime": "2024-12-12 15:31:01"}, ... ]

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1
        indent (optional): an integer number that controls the identation of the printed output

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.downloadlog(pipeline_id), indent=indent))


@app.command()
def start(
    pipeline_id: str, sample_id: str, xml_file: PathArgument, save_location: PathArgument = "C:\\Neware data\\"
) -> None:
    """Start job on selected channel.

    Example usage:
    >>> neware start 220-10-1 "my_sample_id" "C:/path/to/job.xml"
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 0, "start": "ok"}]
    >>> neware start 220-5-3 "my_sample_id" "C:/path/to/invalid.xml"
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
            xml_file.resolve(),
            save_location=save_location.resolve(),
        )
        if result[0]["start"] != "ok":
            typer.echo(json.dumps(result), err=True)


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
        if result[0]["stop"] != "ok":
            typer.echo(json.dumps(result), err=True)


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
def get_job_id(pipeline_ids: PipelinesArgument = None, full_id: bool = False, indent: IndentOption = None) -> None:
    """Get the latest test ID from selected pipeline.

    Example usage:
    >>> neware get-job-id 101-1-1 101-1-2
    {"101-1-1": 21, "101-1-2": 22}

    >>> neware get-job-id --full-id 101-1-1 101-1-2
    {"101-1-1": "101-1-1-21", "101-1-2": "101-1-2-22"}

    Args:
        pipeline_ids (optional): list of pipeline IDs in format {devid}-{subdevid}-{chlid} e.g. 220-10-1 220-10-2
            will use the full channel map if not provided (warning: this function is slow compared to status)
        full_id (optional): controls whether to print short or full id
        indent (optional): an integer number that controls the identation of the printed output

    """
    id_key = "full_test_id" if full_id else "test_id"

    with NewareAPI() as nw:
        result = nw.get_testid(pipeline_ids)
    out = {key: value[id_key] for key, value in result.items()}
    typer.echo(json.dumps(out, indent=indent))
