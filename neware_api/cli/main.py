"""CLI for the Neware battery cycling API."""

import json
from typing import Annotated, Optional

import typer

from neware_api import NewareAPI

app = typer.Typer()


@app.command()
def status(
    pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None,  # noqa: UP007
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

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquire(pipeline_ids)))


@app.command()
def inquiredf(
    pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None,  # noqa: UP007
) -> None:
    """Get test information for all or selected pipelines.

    Example usage:
    >>> neware inquiredf
    {"120-1-1": {"testid": 20, "count": 754268, ... }, "120-1-2": {"testid": 21, "count": 721343, ... }, ... }
    >>> neware status 220-2-2
    {"220-2-2": {"devtype": 27, "devid": 220, "subdevid": 2, "chlid": 2, "testid": 123, "count": 416605, ... }}
    >>> neware status 120-1-5 120-1-6
    {"120-1-5": {...}, "120-1-6": {...}}

    Args:
        pipeline_ids (optional): list of pipeline IDs in format {devid}-{subdevid}-{chlid} e.g. 220-10-1 220-10-2
            will use the full channel map if not provided

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquiredf(pipeline_ids)))


@app.command()
def download(pipeline_id: str, n_points: int) -> None:
    """Download data (voltage, current, time, etc.) from specified channel.

    Example usage:
    >>> neware download 220-10-1 10
    {"cycleid": [488, ...], "volt": [4.11252689361572, ... ], "curr": [0.00271010375581682, ...], ...}

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1
        n_points: last n points to download, set to 0 to download all data (can be slow)

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.download(pipeline_id, n_points)))


@app.command()
def downloadlog(pipeline_id: str) -> None:
    """Download log information from specified channel.

    Example usage:
    >>> neware downloadlog 220-10-1
    [{"seqid": 1, "log_code": 100000, "atime": "2024-12-12 15:31:01"}, ... ]

    Args:
        pipeline_id: pipeline ID in format {devid}-{subdevid}-{chlid} e.g. 220-10-1

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.downloadlog(pipeline_id)))


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
def clearflag(pipeline_ids: Annotated[list[str], typer.Argument()]) -> None:
    """Clear flag on selected channel(s).

    Example usage:
    >>> neware clearflag 220-10-1
    [{"ip": "127.0.0.1", "devtype": 27, "devid": 220, "subdevid": 10, "chlid": 1, "clearflag": "ok"}]

    Args:
        pipeline_ids: list of pipeline IDs in format {devid}-{subdevid}-{chlii} e.g. 220-10-1 220-10-2

    """
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.clearflag(pipeline_ids)))


if __name__ == "__main__":
    app()
