"""Test CLI."""

import json
from pathlib import Path

from typer.testing import CliRunner

from aurora_neware.cli.main import app

runner = CliRunner()


def test_help(mock_bts) -> None:
    """Test --help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.stdout


def test_status(mock_bts) -> None:
    """Test pipelines CLI function."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert isinstance(output, dict)
    expect = {
        "dev": "27-21-1-1-0",
        "cycle_id": 1,
        "step_type": None,
        "workstatus": "finish",
        "barcode": "251203_kigr_gen17_01",
        "current": 0,
        "voltage": 3.8834,
        "capacity": 0,
        "energy": 0,
        "totaltime": 0,
        "relativetime": 0,
        "open_or_close": 0,
        "log_code": 0,
        "ip": "127.0.0.1",
        "devtype": 27,
        "devid": 21,
        "subdevid": 1,
        "Channelid": 1,
        "channel": "true",
    }
    assert output["21-1-1"] == expect
    assert len(output) == 16

    result = runner.invoke(app, ["status", "21-1-1"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["21-1-1"] == expect
    assert len(output) == 1

    result = runner.invoke(app, ["status", "21-1-1", "--state=finish"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["21-1-1"] == expect
    assert len(output) == 1

    result = runner.invoke(app, ["status", "21-1-1", "--state=working"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert len(output) == 0

    result = runner.invoke(app, ["status", "21-1-1", "--state=cheese"])
    assert result.exit_code == 2


def test_get_num_datapoints(mock_bts) -> None:
    """Test get-num-datapoints CLI command."""
    result = runner.invoke(app, ["get-num-datapoints", "21-1-1"])
    output = json.loads(result.stdout)
    assert output == {"21-1-1": 219585}


def test_get_data(mock_bts) -> None:
    """Test get-data CLI command."""
    result = runner.invoke(app, ["get-data", "21-1-1", "10"])
    output = json.loads(result.stdout)
    assert all(len(v) == 10 for v in output.values())
    assert all(
        k in output
        for k in [
            "seqid",
            "stepid",
            "cycleid",
            "steptype",
            "testtime",
            "atime",
            "volt",
            "curr",
            "cap",
            "eng",
        ]
    )


def test_start(mock_bts, tmp_path: Path) -> None:
    """Test start CLI command."""
    xml_file = tmp_path / "payload.xml"

    result = runner.invoke(app, ["start", "21-1-1", "my_sample", str(xml_file)])
    assert result.exit_code == 1
    with xml_file.open("w") as f:
        f.write("hello there")

    result = runner.invoke(app, ["start", "21-1-1", "my_sample", str(xml_file)])
    assert result.exit_code == 0
    assert result.stdout == ""

    result = runner.invoke(app, ["start", "21-1-1", "my_sample", str(xml_file), "-vv"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "21-1-1"


def test_stop(mock_bts) -> None:
    """Test stop CLI command."""
    result = runner.invoke(app, ["stop", "21-1-1"])
    assert result.exit_code == 0
    assert result.stdout == ""


def test_clearflag(mock_bts) -> None:
    """Test clearflag CLI command."""
    result = runner.invoke(app, ["clearflag", "21-1-1"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "clearflag": "false"}]


def test_get_job_id(mock_bts) -> None:
    """Test get-job-id CLI command."""
    result = runner.invoke(app, ["get-job-id", "21-1-1"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output == {"21-1-1": 143}

    result = runner.invoke(app, ["get-job-id", "21-1-1", "--full-id"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output == {"21-1-1": "21-1-1-143"}
