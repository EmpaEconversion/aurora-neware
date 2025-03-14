"""CLI for the Neware battery cycling API."""

import json
from typing import Annotated, Optional

import typer

from neware_api import NewareAPI

app = typer.Typer()


@app.command()
def start() -> None:
    """Start the cycling process."""
    typer.echo("Starting the cycling process for battery is NOT IMPLEMENTED YET.")


@app.command()
def status(pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None) -> None:  # noqa: UP007
    """Get the status of the cycling process for all or selected pipelines.

    Example usage:
    >>> neware status
    {"13-1-1": {"ip":127.0.0.1, "devtype": 27 ... }, "13-1-2": { ... }, ...
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
        typer.echo(json.dumps(nw.inquire_channel(pipeline_ids)))

@app.command()
def inquiredf(pipeline_ids: Annotated[Optional[list[str]], typer.Argument()] = None) -> None:  # noqa: UP007
    """Get test information from channels."""
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.inquiredf(pipeline_ids)))

@app.command()
def downloadlog(pipeline_id: str) -> None:
    """Download log data from specified channel."""
    with NewareAPI() as nw:
        typer.echo(json.dumps(nw.downloadlog(pipeline_id)))

if __name__ == "__main__":
    app()
