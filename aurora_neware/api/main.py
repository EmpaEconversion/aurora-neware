"""FastAPI REST API for aurora_neware."""

import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from aurora_neware import NewareAPI

logger = logging.getLogger(__name__)

API_KEY = os.environ.get("AURORA_NEWARE_API_KEY")

if API_KEY:
    logger.warning("🔑 API key authentication enabled")
else:
    logger.warning(
        "⚠️⚠️⚠️ No API key authentication enabled! ⚠️⚠️⚠️\n"
        "Anyone with access to this endpoint can stop all your measurements and set every channel to max voltage.\n"
        "Only use in this mode within a trusted network!\n"
        "Set an API key with the 'AURORA_NEWARE_API_KEY' environment variable.\n"
        "E.g.\n"
        '$env:AURORA_NEWARE_API_KEY = "myverysecretkey"\n'
        "uvicorn aurora_neware.api.main:app --host=0.0.0.0 --port=8000"
    )

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_key(key: str | None = Security(api_key_header)) -> None:
    """If API key is set, compare against requests."""
    if API_KEY is None:
        return  # no key configured = open access
    if key is None or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, ARG001
    """Check that the status of channels can be read on startup."""
    with NewareAPI() as nw:
        nw.inquire()
    yield


app = FastAPI(
    title="Neware REST API",
    lifespan=lifespan,
    dependencies=[Security(verify_key)],
)


@app.exception_handler(KeyError)
def _key_error_handler(_request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValueError)
def _value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(FileNotFoundError)
def _file_not_found_handler(_request: Request, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


VALID_STATES = ["working", "stop", "finish", "protect", "pause"]


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
    with NewareAPI() as nw:
        channels = nw.inquire(pipeline_ids or None)
    if state:
        channels = {k: v for k, v in channels.items() if v["workstatus"] in state}
    return channels


@app.get("/datapoints")
def datapoints(
    pipeline_ids: Annotated[list[str] | None, Query()] = None,
) -> dict:
    """Get the number of datapoints on all or selected pipelines."""
    with NewareAPI() as nw:
        result = nw.inquiredf(pipeline_ids or None)
    return {k: v["count"] for k, v in result.items()}


@app.get("/data/{pipeline_id}")
def get_data(pipeline_id: str, n_points: int = 0) -> dict:
    """Get data points from a pipeline."""
    with NewareAPI() as nw:
        return nw.download(pipeline_id, n_points)


@app.get("/log/{pipeline_id}")
def log(pipeline_id: str) -> list:
    """Get log entries from a pipeline."""
    with NewareAPI() as nw:
        return nw.downloadlog(pipeline_id)


@app.post("/start/{pipeline_id}")
def start(
    pipeline_id: str,
    sample_id: str,
    xml_file: str,
    save_location: str = "C:\\Neware data\\",
) -> list:
    """Start a job on a pipeline."""
    with NewareAPI() as nw:
        return nw.start(
            pipeline_id,
            sample_id,
            Path(xml_file).resolve(),
            save_location=Path(save_location).resolve(),
        )


@app.post("/stop/{pipeline_id}")
def stop(pipeline_id: str) -> list:
    """Stop a job on a pipeline."""
    with NewareAPI() as nw:
        return nw.stop(pipeline_id)


@app.post("/clear-flag")
def clear_flag(
    pipeline_ids: Annotated[list[str], Query()],
) -> list:
    """Clear flag on one or more pipelines."""
    with NewareAPI() as nw:
        return nw.clearflag(pipeline_ids)


@app.get("/job-id")
def job_id(
    pipeline_ids: Annotated[list[str] | None, Query()] = None,
    full_id: bool = False,
) -> dict:
    """Get the latest test ID from all or selected pipelines."""
    id_key = "full_test_id" if full_id else "test_id"
    with NewareAPI() as nw:
        result = nw.get_testid(pipeline_ids or None)
    return {k: v[id_key] for k, v in result.items()}
