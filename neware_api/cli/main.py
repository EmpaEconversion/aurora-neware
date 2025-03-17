"""CLI for the Neware battery cycling API."""

import json
from typing import Annotated, Optional

import typer

from neware_api import NewareAPI

app = typer.Typer()

@app.command()
def status(
    pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None  # noqa: UP007
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

    Raises:
        KeyError if pipeline ID not in channel map

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquire(pipeline_ids)))

@app.command()
def inquiredf(
    pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None  # noqa: UP007
) -> None:
    """Get test information from channels."""
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquiredf(pipeline_ids)))

@app.command()
def downloadlog(pipeline_id: str) -> None:
    """Download log data from specified channel."""
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.downloadlog(pipeline_id)))

@app.command()
def start(
    pipeline_id: str,
    sample_id: str,
    xml_file: str,
    save_location: str | None = "C:\\Neware data\\"
) -> None:
    """Start job on selected channel.

    Example usage:
    >>> neware start 220-10-1 "my_sample_name" "C:/path/to/job.xml"
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 0, "start": "ok"}]
    >>> neware start 220-5-3 "my_sample_name" "C:/path/to/invalid.xml"
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 0, "start": "false"}]

    In the second case, download and check the Neware logs for more information.

    Args:
        pipeline_id: pipeline ID in formation {devid}-{subdevid}-{chlii} e.g. 220-10-1
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

    """
    with NewareAPI() as nw:
        result = nw.stop(pipeline_id)
        typer.echo(json.dumps(result))

@app.command()
def clearflag(pipeline_ids: Annotated[list[str], typer.Argument()]) -> None:
    """Clear flag on selected channel(s).

    Example usage:
    >>> neware clearflag 220-10-1
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 1, "clearflag": "ok"}]

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.clearflag(pipeline_ids)))

if __name__ == "__main__":
    app()
