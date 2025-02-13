"""CLI for the Neware battery cycling API."""

import json
import re
from typing import Annotated, Optional

import typer

from neware_api import NewareAPI

app = typer.Typer()


@app.command()
def start(
    pipeline: str,
    sampleid: str,
    payload_xml_path: str,
    save_location: Annotated[str, typer.Argument()] = "C://Neware data/",
) -> None:
    """Start the cycling process.

    Example usage:
    >>> neware start '13-1-2' 'mysamplename' 'my/file/location/ocv.xml' 'my/data/location/'

    Args:
        pipeline: the identifier given by device-subdevice-channel e.g. 13-1-2
        sampleid: name of the sample, used as the barcode in the measurement
        payload_xml_path: path to the xml job file on the cycler server machine
        save_location (default C:/Neware data): location to save the data on server

    Raises:
        KeyError if pipeline ID not in channel map

    """
    typer.echo(
        f"Sample {sampleid} starting job {payload_xml_path} on channel {pipeline}, saving data to {save_location}."
    )
    with NewareAPI() as nw:
        response = nw.start_job(
            pipeline=pipeline,
            sampleid=sampleid,
            payload_xml_path=payload_xml_path,
            save_location=save_location,
        )
    match = re.search("(?<=>)(.*)(?=</start>)", response)
    result = match.group(1) if match else ""
    if result == "ok":
        typer.echo("Successfully started job.")
    elif result == "false":
        typer.echo("Starting job failed. Downlaod and check BTS log for more detail.")
    else:
        typer.echo(f"Device response not understood:\n{response}")


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


if __name__ == "__main__":
    app()
