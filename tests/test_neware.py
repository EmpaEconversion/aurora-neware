"""Tests for neware.py."""

from pathlib import Path

import pytest

from aurora_neware import NewareAPI
from aurora_neware.neware import _lod_to_dol


def test_init(mock_bts) -> None:
    """Test API object initialisation."""
    with NewareAPI() as nw:
        assert nw.termination == "\n\n#\r\n"
        assert isinstance(nw.channel_map, dict)
        assert len(nw.channel_map) == 16


def test_init_no_devices(mock_bts, no_devices) -> None:
    """Test API object initialisation."""
    with pytest.raises(ValueError) as excinfo:
        NewareAPI().connect()
    assert "No devices found." in str(excinfo.value)


def test_get_status(mock_bts) -> None:
    """Test getchlstatus function."""
    with NewareAPI() as nw:
        res = nw.getchlstatus()
        assert len(res) == 16
        expect = {
            "ip": "127.0.0.1",
            "devtype": 27,
            "devid": 21,
            "subdevid": 1,
            "chlid": 1,
            "reservepause": 1,
            "status": "finish",
            "Channelid": 1,
            "channel": "true",
        }
        assert res["21-1-1"] == expect

        res = nw.getchlstatus("21-1-1")
        assert len(res) == 1
        assert res["21-1-1"] == expect

        res = nw.getchlstatus(["21-1-1"])
        assert len(res) == 1
        assert res["21-1-1"] == expect


def test_get_pipeline(mock_bts) -> None:
    """Test get_pipeline function."""
    with NewareAPI() as nw:
        res = nw.get_pipeline("21-1-1")
        expect = {
            "ip": "127.0.0.1",
            "devtype": 27,
            "devid": 21,
            "subdevid": 1,
            "Channelid": 1,
            "channel": "true",
        }
        assert res == expect
        with pytest.raises(KeyError) as excinfo:
            nw.get_pipeline("21-1-1asgadgh")
        assert "not in channel map" in str(excinfo.value)


def test_inquire(mock_bts) -> None:
    """Test inquire function."""
    with NewareAPI() as nw:
        res = nw.inquire()
        assert len(res) == 16
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
        assert res["21-1-1"] == expect

        res = nw.inquire("21-1-1")
        assert len(res) == 1
        assert res["21-1-1"] == expect

        res = nw.inquire(["21-1-1"])
        assert len(res) == 1
        assert res["21-1-1"] == expect


def test_inquiredf(mock_bts) -> None:
    """Test inquiredf function."""
    with NewareAPI() as nw:
        res = nw.inquiredf()
        assert len(res) == 16
        expect = {
            "devtype": 27,
            "devid": 21,
            "subdevid": 1,
            "chlid": 1,
            "testid": 143,
            "count": 219585,
            "chl": "true",
            "ip": "127.0.0.1",
            "Channelid": 1,
            "channel": "true",
        }
        assert res["21-1-1"] == expect

        res = nw.inquiredf("21-1-1")
        assert len(res) == 1
        assert res["21-1-1"] == expect

        res = nw.inquiredf(["21-1-1"])
        assert len(res) == 1
        assert res["21-1-1"] == expect


def test_start(mock_bts, tmp_path: Path) -> None:
    """Test start function."""
    with NewareAPI() as nw:
        xml_file = tmp_path / "payload.xml"
        save_location = tmp_path / "save_here.ndax"
        with pytest.raises(FileNotFoundError):
            nw.start("21-1-1", "mysample", str(xml_file), str(save_location))
        with xml_file.open("w") as f:
            f.write("hello there")
        assert xml_file.exists()

        res = nw.start("21-1-1", "mysample", str(xml_file), str(save_location))
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "start": "ok"}]

        res = nw.start(["21-1-1"], ["mysample"], [str(xml_file)], str(save_location))
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "start": "ok"}]

        with pytest.raises(ValueError) as excinfo:
            nw.start("21-1-2", "mysample", str(xml_file), str(save_location))
        assert "Can only start jobs if pipeline state is" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            res = nw.start(
                ["21-1-1", "21-1-2"], ["mysample1", "mysample2"], [str(xml_file), str(xml_file)], str(save_location)
            )
        assert "Can only start jobs if pipeline state is" in str(excinfo.value)


def test_stop(mock_bts) -> None:
    """Test stop function."""
    with NewareAPI() as nw:
        res = nw.stop("21-1-1")
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "stop": "ok"}]
        nw.stop(["21-1-1", "21-1-2"])
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "stop": "ok"}]


def test_downloadlog(mock_bts) -> None:
    """Test downloadlog function."""
    with NewareAPI() as nw:
        res = nw.downloadlog("21-1-1")
        assert res == [
            {"seqid": 1, "log_code": 100000, "atime": "2025-12-03 16:44:02"},
            {"seqid": 139025, "log_code": 100215, "atime": "2025-12-19 16:36:19"},
            {"seqid": 139026, "log_code": 100213, "atime": "2025-12-19 16:36:20"},
            {"seqid": 139026, "log_code": 100007, "atime": "2025-12-19 16:36:20"},
            {"seqid": 219585, "log_code": 100001, "atime": "2025-12-28 22:30:11"},
        ]


def test_download(mock_bts) -> None:
    """Test download function."""
    with NewareAPI() as nw:
        res = nw.download("21-1-1", last_n_points=10)
        assert res == {
            "seqid": [219576, 219577, 219578, 219579, 219580, 219581, 219582, 219583, 219584, 219585],
            "stepid": [24, 24, 24, 24, 24, 24, 24, 24, 24, 24],
            "cycleid": [29, 29, 29, 29, 29, 29, 29, 29, 29, 29],
            "steptype": ["dc", "dc", "dc", "dc", "dc", "dc", "dc", "dc", "dc", "dc"],
            "testtime": [
                36070000,
                36080000,
                36080300,
                36090000,
                36100000,
                36110000,
                36118500,
                36120000,
                36130000,
                36136400,
            ],
            "atime": [
                "2025-12-28 22:29:05",
                "2025-12-28 22:29:15",
                "2025-12-28 22:29:15",
                "2025-12-28 22:29:25",
                "2025-12-28 22:29:35",
                "2025-12-28 22:29:45",
                "2025-12-28 22:29:53",
                "2025-12-28 22:29:55",
                "2025-12-28 22:30:05",
                "2025-12-28 22:30:11",
            ],
            "volt": [
                3.6780698299408,
                3.65799260139465,
                3.65737199783325,
                3.63519644737244,
                3.60988855361938,
                3.58231687545776,
                3.55714106559753,
                3.55259799957275,
                3.52100968360901,
                3.49995565414429,
            ],
            "curr": [
                -0.000295051460852847,
                -0.000295052188448608,
                -0.000295052188448608,
                -0.000295052799629048,
                -0.000295051460852847,
                -0.000295053294394165,
                -0.000295051577268168,
                -0.000295052566798404,
                -0.000295051228022203,
                -0.000295051460852847,
            ],
            "cap": [
                0.00295628436449786,
                0.00295710395391022,
                0.00295712845399976,
                0.00295792357064784,
                0.0029587431345135,
                0.00295956272699793,
                0.00296025932766497,
                0.00296038226224482,
                0.00296120182611048,
                0.00296172639355063,
            ],
            "eng": [
                0.0135611368830335,
                0.0135641349350401,
                0.0135642616078258,
                0.0135671608150005,
                0.0135701298713684,
                0.0135730659113564,
                0.0135755632072687,
                0.0135760009288788,
                0.013578899204731,
                0.013580740429461,
            ],
        }


def test_get_test_id(mock_bts) -> None:
    """Test get_test_id function."""
    with NewareAPI() as nw:
        expect = {
            "21-1-1": {
                "ip": "127.0.0.1",
                "devtype": 27,
                "devid": 21,
                "subdevid": 1,
                "Channelid": 1,
                "channel": "true",
                "test_id": 143,
                "full_test_id": "21-1-1-143",
            }
        }
        res = nw.get_testid("21-1-1")
        assert res == expect
        res = nw.get_testid(["21-1-1"])
        assert res == expect


def test_get_steps(mock_bts) -> None:
    """Test get_steps function."""
    with NewareAPI() as nw:
        res = nw.get_steps("21-1-1")
        assert res[0] == {
            "startseqid": 1,
            "endseqid": 4321,
            "stepindex": 1,
            "stepid": 1,
            "cycleid": 1,
            "steptype": "rest",
            "steptime": 43200000,
            "endatime": "2025-12-04 04:44:02",
            "startvolt": 3.1829857421875,
            "endvolt": 3.13540078125,
            "startcurr": 0,
            "endcurr": 0,
            "cap": 0,
            "eng": 0,
            "dcir": 0,
        }
        assert len(res) == 3


def test_light(mock_bts) -> None:
    """Test light function."""
    with NewareAPI() as nw:
        res = nw.light("21-1-1")
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "light": "ok"}]
        res = nw.light(["21-1-1"])
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "light": "ok"}]


def test_clearflag(mock_bts) -> None:
    """Test clearflag function."""
    with NewareAPI() as nw:
        res = nw.clearflag("21-1-1")
        assert res == [{"ip": "127.0.0.1", "devtype": 27, "devid": 21, "subdevid": 1, "chlid": 1, "clearflag": "false"}]


def test_lod_to_dol() -> None:
    """Test list of dictionaries to dictionary of lists."""
    lod = [
        {"seqid": 1, "log_code": 100000, "atime": "2025-12-03 16:44:02"},
        {"seqid": 139025, "log_code": 100215, "atime": "2025-12-19 16:36:19"},
        {"seqid": 139026, "log_code": 100213, "atime": "2025-12-19 16:36:20"},
        {"seqid": 139026, "log_code": 100007, "atime": "2025-12-19 16:36:20"},
        {"seqid": 219585, "log_code": 100001, "atime": "2025-12-28 22:30:11"},
    ]
    dol = {
        "seqid": [1, 139025, 139026, 139026, 219585],
        "log_code": [100000, 100215, 100213, 100007, 100001],
        "atime": [
            "2025-12-03 16:44:02",
            "2025-12-19 16:36:19",
            "2025-12-19 16:36:20",
            "2025-12-19 16:36:20",
            "2025-12-28 22:30:11",
        ],
    }
    assert _lod_to_dol(lod) == dol

    assert _lod_to_dol([]) == {}

    with pytest.raises(KeyError):
        _lod_to_dol([{"a": 1, "b": 2}, {"b": 2}])
