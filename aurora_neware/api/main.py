"""FastAPI REST API for aurora_neware."""

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from aurora_neware import NewareAPI

VALID_STATES = ["working", "stop", "finish", "protect", "pause"]

app = FastAPI(title="Neware REST API")


@app.get("/status")
def status(
    pipeline_ids: Annotated[list[str] | None, Query()] = None,
    state: Annotated[list[str] | None, Query()] = None,
) -> dict:
    """Get the status of all or selected pipelines."""
    if state:
        invalid = [s for s in state if s not in VALID_STATES]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid state: {', '.join(invalid)}. Valid options are: {', '.join(VALID_STATES)}",
            )
    try:
        with NewareAPI() as nw:
            channels = nw.inquire(pipeline_ids or None)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if state:
        channels = {k: v for k, v in channels.items() if v["workstatus"] in state}
    return channels


@app.get("/datapoints")
def datapoints(
    pipeline_ids: Annotated[list[str] | None, Query()] = None,
) -> dict:
    """Get the number of datapoints on all or selected pipelines."""
    try:
        with NewareAPI() as nw:
            result = nw.inquiredf(pipeline_ids or None)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {k: v["count"] for k, v in result.items()}


@app.get("/data/{pipeline_id}")
def get_data(pipeline_id: str, n_points: int = 0) -> dict:
    """Get data points from a pipeline."""
    try:
        with NewareAPI() as nw:
            return nw.download(pipeline_id, n_points)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/log/{pipeline_id}")
def log(pipeline_id: str) -> list:
    """Get log entries from a pipeline."""
    try:
        with NewareAPI() as nw:
            return nw.downloadlog(pipeline_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/start/{pipeline_id}")
def start(
    pipeline_id: str,
    sample_id: str,
    xml_file: str,
    save_location: str = "C:\\Neware data\\",
) -> list:
    """Start a job on a pipeline."""
    try:
        with NewareAPI() as nw:
            return nw.start(
                pipeline_id,
                sample_id,
                Path(xml_file).resolve(),
                save_location=Path(save_location).resolve(),
            )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/stop/{pipeline_id}")
def stop(pipeline_id: str) -> list:
    """Stop a job on a pipeline."""
    try:
        with NewareAPI() as nw:
            return nw.stop(pipeline_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/clear-flag")
def clear_flag(
    pipeline_ids: Annotated[list[str], Query()],
) -> list:
    """Clear flag on one or more pipelines."""
    try:
        with NewareAPI() as nw:
            return nw.clearflag(pipeline_ids)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/job-id")
def job_id(
    pipeline_ids: Annotated[list[str] | None, Query()] = None,
    full_id: bool = False,
) -> dict:
    """Get the latest test ID from all or selected pipelines."""
    id_key = "full_test_id" if full_id else "test_id"
    try:
        with NewareAPI() as nw:
            result = nw.get_testid(pipeline_ids or None)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {k: v[id_key] for k, v in result.items()}
