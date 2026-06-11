"""Tests for the FastAPI REST API."""

from pathlib import Path

from fastapi.testclient import TestClient

from aurora_neware.api.main import app

client = TestClient(app)


def test_status_all(mock_bts) -> None:
    """GET /status returns all 16 pipelines."""
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 16
    assert data["21-1-1"]["workstatus"] == "finish"
    assert data["21-1-1"]["voltage"] == 3.8834


def test_status_single(mock_bts) -> None:
    """GET /status?pipeline_ids=21-1-1 returns one pipeline."""
    r = client.get("/status", params={"pipeline_ids": "21-1-1"})
    assert r.status_code == 200
    data = r.json()
    assert list(data.keys()) == ["21-1-1"]


def test_status_state_filter(mock_bts) -> None:
    """State filter keeps matching pipelines and discards others."""
    r = client.get("/status", params={"pipeline_ids": "21-1-1", "state": "finish"})
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/status", params={"pipeline_ids": "21-1-1", "state": "working"})
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_status_invalid_state(mock_bts) -> None:
    """Invalid state value returns 400."""
    r = client.get("/status", params={"state": "cheese"})
    assert r.status_code == 400
    assert "Invalid state" in r.json()["detail"]


def test_status_unknown_pipeline(mock_bts) -> None:
    """Unknown pipeline_id returns 404."""
    r = client.get("/status", params={"pipeline_ids": "99-9-9"})
    assert r.status_code == 404


def test_datapoints(mock_bts) -> None:
    """GET /datapoints returns count per pipeline."""
    r = client.get("/datapoints", params={"pipeline_ids": "21-1-1"})
    assert r.status_code == 200
    assert r.json() == {"21-1-1": 219585}


def test_datapoints_all(mock_bts) -> None:
    """GET /datapoints with no filter returns all 16 pipelines."""
    r = client.get("/datapoints")
    assert r.status_code == 200
    assert len(r.json()) == 16


def test_get_data(mock_bts) -> None:
    """GET /data/{pipeline_id} returns column-oriented measurement data."""
    r = client.get("/data/21-1-1", params={"n_points": 10})
    assert r.status_code == 200
    data = r.json()
    expected_keys = {"seqid", "stepid", "cycleid", "steptype", "testtime", "atime", "volt", "curr", "cap", "eng"}
    assert expected_keys.issubset(data.keys())
    assert all(len(v) == 10 for v in data.values())


def test_get_data_unknown_pipeline(mock_bts) -> None:
    """Unknown pipeline_id on /data returns 404."""
    r = client.get("/data/99-9-9")
    assert r.status_code == 404


def test_log(mock_bts) -> None:
    """GET /log/{pipeline_id} returns list of log entries."""
    r = client.get("/log/21-1-1")
    assert r.status_code == 200
    data = r.json()
    assert data == [
        {"seqid": 1, "log_code": 100000, "atime": "2025-12-03 16:44:02"},
        {"seqid": 139025, "log_code": 100215, "atime": "2025-12-19 16:36:19"},
        {"seqid": 139026, "log_code": 100213, "atime": "2025-12-19 16:36:20"},
        {"seqid": 139026, "log_code": 100007, "atime": "2025-12-19 16:36:20"},
        {"seqid": 219585, "log_code": 100001, "atime": "2025-12-28 22:30:11"},
    ]


def test_log_unknown_pipeline(mock_bts) -> None:
    """Unknown pipeline_id on /log returns 404."""
    r = client.get("/log/99-9-9")
    assert r.status_code == 404


def test_start_missing_file(mock_bts, tmp_path: Path) -> None:
    """POST /start returns 400 when xml_file does not exist."""
    r = client.post("/start/21-1-1", params={"sample_id": "s1", "xml_file": str(tmp_path / "missing.xml")})
    assert r.status_code == 400


def test_start_ok(mock_bts, tmp_path: Path) -> None:
    """POST /start returns the start result when the job succeeds."""
    xml_file = tmp_path / "payload.xml"
    xml_file.write_text("hello there")
    r = client.post("/start/21-1-1", params={"sample_id": "s1", "xml_file": str(xml_file)})
    assert r.status_code == 200
    data = r.json()
    assert data[0]["start"] == "ok"


def test_start_invalid_state(mock_bts, tmp_path: Path) -> None:
    """POST /start returns 400 when pipeline is not in a startable state."""
    xml_file = tmp_path / "payload.xml"
    xml_file.write_text("hello there")
    # 21-1-2 is "working" in mock data — cannot start
    r = client.post("/start/21-1-2", params={"sample_id": "s1", "xml_file": str(xml_file)})
    assert r.status_code == 400
    assert "Can only start jobs" in r.json()["detail"]


def test_start_false(mock_bts, tmp_path: Path) -> None:
    """POST /start returns 200 with start=false when Neware rejects the job."""
    xml_file = tmp_path / "payload.xml"
    xml_file.write_text("hello there")
    # 21-1-4 produces start=false in mock data
    r = client.post("/start/21-1-4", params={"sample_id": "s1", "xml_file": str(xml_file)})
    assert r.status_code == 200
    assert r.json()[0]["start"] == "false"


def test_stop_ok(mock_bts) -> None:
    """POST /stop returns result with stop=ok."""
    r = client.post("/stop/21-1-1")
    assert r.status_code == 200
    assert r.json()[0]["stop"] == "ok"


def test_stop_false(mock_bts) -> None:
    """POST /stop returns 200 with stop=false when Neware rejects."""
    r = client.post("/stop/21-1-4")
    assert r.status_code == 200
    assert r.json()[0]["stop"] == "false"


def test_clear_flag(mock_bts) -> None:
    """POST /clear-flag returns clear-flag result list."""
    r = client.post("/clear-flag", params={"pipeline_ids": "21-1-1"})
    assert r.status_code == 200
    expected = [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "clearflag": "false"}]
    assert r.json() == expected


def test_job_id(mock_bts) -> None:
    """GET /job-id returns short test ID."""
    r = client.get("/job-id", params={"pipeline_ids": "21-1-1"})
    assert r.status_code == 200
    assert r.json() == {"21-1-1": 143}


def test_job_id_full(mock_bts) -> None:
    """GET /job-id?full_id=true returns full test ID string."""
    r = client.get("/job-id", params={"pipeline_ids": "21-1-1", "full_id": "true"})
    assert r.status_code == 200
    assert r.json() == {"21-1-1": "21-1-1-143"}
