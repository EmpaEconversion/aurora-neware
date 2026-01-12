"""Mocks and fakes for testing."""

from types import MappingProxyType


class FakeSocket:
    """Class to give expected responses from socket.

    Responses were captured from a real BTS8.0 machine.
    """

    def __init__(self) -> None:
        """Initialise the 'socket'."""
        self.sent_data: list[str] = []
        self._recv_buffer = b""

    def connect(self, address: tuple[str, int]) -> None:
        """Fake connect to an IP and port."""
        self.address = address

    def sendall(self, data: bytes) -> None:
        """Fake send a command and prepare a response."""
        text = data.decode("utf-8")
        self.sent_data.append(text)
        self._get_response(text)

    def recv(self, bufsize: int) -> bytes:
        """Receive the response."""
        if not self._recv_buffer:
            return b""
        chunk = self._recv_buffer[:bufsize]
        self._recv_buffer = self._recv_buffer[bufsize:]
        return chunk

    def close(self) -> None:
        """Close the fake connection."""
        return

    def _get_response(self, text: str) -> None:
        for pattern, response in self._response_map.items():
            if pattern in text:
                self._recv_buffer += response + b"\n\n#\r\n"
                return
        msg = f"Unknown command:\n{text}"
        raise AssertionError(msg)

    _connect_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>connect_resp</cmd>\r\n"
        b"  <result>ok</result>\r\n"
        b"</bts>"
    )

    _get_devinfo_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n<bts version="1.0">\r\n'
        b'  <cmd>getdevinfo_resp</cmd>\r\n  <serverip count="1">\r\n'
        b'    <server ip="127.0.0.1" port="3306" />\r\n  </serverip>\r\n'
        b'  <middle count="16">\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="1">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="2">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="3">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="4">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="5">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="6">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="7">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="1" Channelid="8">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="1">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="2">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="3">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="4">true</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="5">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="6">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="7">false</channel>\r\n'
        b'    <channel ip="127.0.0.1" devtype="27" devid="21" subdevid="2" Channelid="8">false</channel>\r\n'
        b"</middle>\r\n</bts>"
    )

    _get_devinfo_bad_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n<bts version="1.0">\r\n'
        b'  <cmd>getdevinfo_resp</cmd>\r\n  <serverip count="1">\r\n'
        b'    <server ip="127.0.0.1" port="3306" />\r\n  </serverip>\r\n'
        b'  <middle count="0">\r\n'
        b"</middle>\r\n</bts>"
    )

    _get_status_all_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>getchlstatus_resp</cmd>\r\n"
        b'  <list count="16">\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="2" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="3" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="4" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="5" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="6" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="7" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="8" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="1" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="2" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="3" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="4" reservepause="1">finish</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="5" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="6" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="7" reservepause="1">working</status>\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="2" chlid="8" reservepause="1">working</status>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _get_status_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>getchlstatus_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <status ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1" reservepause="1">finish</status>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquire_all_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquire_resp</cmd>\r\n"
        b'  <list count="16">\r\n'
        b'    <inquire dev="27-21-1-1-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251203_kigr_gen17_01" current="0" voltage="3.8834" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-1-2-0" cycle_id="44" step_id="4" step_type="dc" workstatus="working" barcode="251203_kigr_gen17_02" current="-0.0003" voltage="4.6947" capacity="0.001" energy="0.0047" totaltime="3189199.3" relativetime="12319" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-1-3-0" cycle_id="41" step_id="2" step_type="cc" workstatus="working" barcode="251203_kigr_gen17_03" current="0.0003" voltage="4.8076" capacity="0.0034" energy="0.0158" totaltime="3189197" relativetime="40704.7" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-1-4-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251203_kigr_gen17_04" current="0" voltage="0.5741" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-1-5-0" cycle_id="43" step_id="2" step_type="dc" workstatus="working" barcode="251203_kigr_gen17_05" current="-0.0004" voltage="0.0152" capacity="0.0018" energy="0.0002" totaltime="3189174.7" relativetime="15958.2" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-1-6-0" cycle_id="38" step_id="2" step_type="dc" workstatus="working" barcode="251203_kigr_gen17_06" current="-0.0004" voltage="0.3529" capacity="0.0003" energy="0.0002" totaltime="3189172.5" relativetime="2421.8" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-1-7-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_01" current="0" voltage="3.7393" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-1-8-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_02" current="0" voltage="3.7105" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-2-1-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_03" current="0" voltage="3.3164" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-2-2-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_04" current="0" voltage="3.456" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-2-3-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_05" current="0" voltage="3.4164" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-2-4-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251114_kigr_gen14_06" current="0" voltage="3.6526" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-2-5-0" cycle_id="597" step_id="11" step_type="dc" workstatus="working" barcode="251121_kigr_gen15_01" current="-0.0015" voltage="3.5832" capacity="0.0006" energy="0.0022" totaltime="4232943" relativetime="1388.2" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-2-6-0" cycle_id="601" step_id="10" step_type="cv" workstatus="working" barcode="251121_kigr_gen15_02" current="0.0002" voltage="4.1995" capacity="0.0002" energy="0.0007" totaltime="4232834.8" relativetime="1209.3" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-2-7-0" cycle_id="530" step_id="9" step_type="cc" workstatus="working" barcode="251121_kigr_gen15_03" current="0.0015" voltage="3.6485" capacity="0.0002" energy="0.0007" totaltime="4232832.3" relativetime="476.8" open_or_close="0" log_code="102000" />\r\n'
        b'    <inquire dev="27-21-2-8-0" cycle_id="594" step_id="9" step_type="cc" workstatus="working" barcode="251121_kigr_gen15_04" current="0.0015" voltage="3.6153" capacity="0.0001" energy="0.0004" totaltime="4232829.9" relativetime="250.2" open_or_close="0" log_code="102000" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquire_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquire_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <inquire dev="27-21-1-1-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251203_kigr_gen17_01" current="0" voltage="3.8834" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquire_21_1_1_and_2_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquire_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <inquire dev="27-21-1-1-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251203_kigr_gen17_01" current="0" voltage="3.8834" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b'    <inquire dev="27-21-1-2-0" cycle_id="44" step_id="4" step_type="dc" workstatus="working" barcode="251203_kigr_gen17_02" current="-0.0003" voltage="4.6947" capacity="0.001" energy="0.0047" totaltime="3189199.3" relativetime="12319" open_or_close="0" log_code="102000" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquire_21_1_2_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquire_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <inquire dev="27-21-1-2-0" cycle_id="44" step_id="4" step_type="dc" workstatus="working" barcode="251203_kigr_gen17_02" current="-0.0003" voltage="4.6947" capacity="0.001" energy="0.0047" totaltime="3189199.3" relativetime="12319" open_or_close="0" log_code="102000" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquire_21_1_4_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquire_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <inquire dev="27-21-1-4-0" cycle_id="1" step_type="--" workstatus="finish" barcode="251203_kigr_gen17_04" current="0" voltage="0.5741" capacity="0" energy="0" totaltime="0" relativetime="0" open_or_close="0" log_code="0" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquiredf_all_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquiredf_resp</cmd>\r\n"
        b'  <list count="16">\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="1" testid="143" count="219585">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="2" testid="144" count="320850">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="3" testid="145" count="320668">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="4" testid="146" count="230808">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="5" testid="147" count="321113">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="6" testid="148" count="320821">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="7" testid="100" count="283034">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="8" testid="101" count="281689">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="1" testid="102" count="295221">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="2" testid="103" count="250005">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="3" testid="104" count="239986">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="4" testid="105" count="248384">true</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="5" testid="106" count="469912">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="6" testid="107" count="470033">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="7" testid="108" count="464669">false</chl>\r\n'
        b'    <chl devtype="27" devid="21" subdevid="2" chlid="8" testid="109" count="469828">false</chl>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _inquiredf_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>inquiredf_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <chl devtype="27" devid="21" subdevid="1" chlid="1" testid="143" count="219585">true</chl>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _start_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>start_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <start ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">ok</start>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _start_21_1_4_bad_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>start_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <start ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="2">false</start>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _stop_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>stop_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">ok</stop>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _stop_21_1_1_and_21_1_2_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>stop_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">ok</stop>\r\n'
        b'    <stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="2">ok</stop>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _stop_21_1_4_bad_reponse = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>stop_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="4">false</stop>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _download_21_1_1_repsonse = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>donwload_resp</cmd>\r\n"
        b'  <download devtype="27" devid="21" subdevid="1" chlid="1" testid="143" startpos="219576" count="1000" auxid="0" />\r\n'
        b'  <list count="10">\r\n'
        b'    <data seqid="219576" stepid="24" cycleid="29" steptype="dc" testtime="36070000" atime="2025-12-28 22:29:05" volt="3.6780698299408" curr="-0.000295051460852847" cap="0.00295628436449786" eng="0.0135611368830335" />\r\n'
        b'    <data seqid="219577" stepid="24" cycleid="29" steptype="dc" testtime="36080000" atime="2025-12-28 22:29:15" volt="3.65799260139465" curr="-0.000295052188448608" cap="0.00295710395391022" eng="0.0135641349350401" />\r\n'
        b'    <data seqid="219578" stepid="24" cycleid="29" steptype="dc" testtime="36080300" atime="2025-12-28 22:29:15" volt="3.65737199783325" curr="-0.000295052188448608" cap="0.00295712845399976" eng="0.0135642616078258" />\r\n'
        b'    <data seqid="219579" stepid="24" cycleid="29" steptype="dc" testtime="36090000" atime="2025-12-28 22:29:25" volt="3.63519644737244" curr="-0.000295052799629048" cap="0.00295792357064784" eng="0.0135671608150005" />\r\n'
        b'    <data seqid="219580" stepid="24" cycleid="29" steptype="dc" testtime="36100000" atime="2025-12-28 22:29:35" volt="3.60988855361938" curr="-0.000295051460852847" cap="0.0029587431345135" eng="0.0135701298713684" />\r\n'
        b'    <data seqid="219581" stepid="24" cycleid="29" steptype="dc" testtime="36110000" atime="2025-12-28 22:29:45" volt="3.58231687545776" curr="-0.000295053294394165" cap="0.00295956272699793" eng="0.0135730659113564" />\r\n'
        b'    <data seqid="219582" stepid="24" cycleid="29" steptype="dc" testtime="36118500" atime="2025-12-28 22:29:53" volt="3.55714106559753" curr="-0.000295051577268168" cap="0.00296025932766497" eng="0.0135755632072687" />\r\n'
        b'    <data seqid="219583" stepid="24" cycleid="29" steptype="dc" testtime="36120000" atime="2025-12-28 22:29:55" volt="3.55259799957275" curr="-0.000295052566798404" cap="0.00296038226224482" eng="0.0135760009288788" />\r\n'
        b'    <data seqid="219584" stepid="24" cycleid="29" steptype="dc" testtime="36130000" atime="2025-12-28 22:30:05" volt="3.52100968360901" curr="-0.000295051228022203" cap="0.00296120182611048" eng="0.013578899204731" />\r\n'
        b'    <data seqid="219585" stepid="24" cycleid="29" steptype="dc" testtime="36136400" atime="2025-12-28 22:30:11" volt="3.49995565414429" curr="-0.000295051460852847" cap="0.00296172639355063" eng="0.013580740429461" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _download0_21_1_1_repsonse = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>donwload_resp</cmd>\r\n"
        b'  <download devtype="27" devid="21" subdevid="1" chlid="1" testid="143" startpos="0" count="0" auxid="0" />\r\n'
        b'  <list count="0" />\r\n'
        b"</bts>"
    )

    _downloadlog_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>donwloadlog_resp</cmd>\r\n"
        b'  <download devtype="27" devid="21" subdevid="1" chlid="1" testid="143" log_lever="0" />\r\n'
        b'  <list count="5">\r\n'
        b'    <data seqid="1" log_code="100000" atime="2025-12-03 16:44:02" />\r\n'
        b'    <data seqid="139025" log_code="100215" atime="2025-12-19 16:36:19" />\r\n'
        b'    <data seqid="139026" log_code="100213" atime="2025-12-19 16:36:20" />\r\n'
        b'    <data seqid="139026" log_code="100007" atime="2025-12-19 16:36:20" />\r\n'
        b'    <data seqid="219585" log_code="100001" atime="2025-12-28 22:30:11" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _download_step_layer_21_1_1_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>downloadStepLayer_resp</cmd>\r\n"
        b'  <downloadStepLayer devtype="27" devid="21" subdevid="1" chlid="1" testid="143" />\r\n'
        b'  <list count="3">\r\n'
        b'    <data startseqid="1" endseqid="4321" stepindex="1" stepid="1" cycleid="1" steptype="rest" steptime="43200000" endatime="2025-12-04 04:44:02" startvolt="3.1829857421875" endvolt="3.13540078125" startcurr="0" endcurr="0" cap="0" eng="0" dcir="0" />\r\n'
        b'    <data startseqid="4322" endseqid="7518" stepindex="2" stepid="2" cycleid="1" steptype="cc" steptime="31799100" endatime="2025-12-04 13:34:01" startvolt="3.19527578125" endvolt="4.9000171875" startcurr="0.000294779107207432" endcurr="0.000295047357212752" cap="0.00260622496716678" eng="0.0123314764350653" dcir="0" />\r\n'
        b'    <data startseqid="7519" endseqid="7927" stepindex="3" stepid="3" cycleid="1" steptype="cv" steptime="3932700" endatime="2025-12-04 14:39:33" startvolt="4.8999890625" endvolt="4.899825390625" startcurr="0.000295047706458718" endcurr="0.000147477534483187" cap="0.00023461104137823" eng="0.00114955275785178" dcir="0" />\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _clear_flag_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>clearflag_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <clearflag ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">false</clearflag>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _light_response = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<bts version="1.0">\r\n'
        b"  <cmd>light_resp</cmd>\r\n"
        b'  <list count="1">\r\n'
        b'    <light ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">ok</light>\r\n'
        b"  </list>\r\n"
        b"</bts>"
    )

    _response_map = MappingProxyType(
        {
            "<cmd>connect</cmd>": _connect_response,
            "<cmd>getdevinfo</cmd>": _get_devinfo_response,
            '<cmd>getchlstatus</cmd><list count = "16">': _get_status_all_response,
            '<cmd>getchlstatus</cmd><list count = "1">': _get_status_21_1_1_response,
            '<cmd>inquire</cmd><list count = "16">': _inquire_all_response,
            '<cmd>inquire</cmd><list count = "1"><inquire ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1"': _inquire_21_1_1_response,
            '<cmd>inquire</cmd><list count = "2"><inquire ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1"': _inquire_21_1_1_and_2_response,
            '<cmd>inquire</cmd><list count = "1"><inquire ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="2"': _inquire_21_1_2_response,
            '<cmd>inquire</cmd><list count = "1"><inquire ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="4"': _inquire_21_1_4_response,
            '<cmd>inquiredf</cmd><list count = "16">': _inquiredf_all_response,
            '<cmd>inquiredf</cmd><list count = "1">': _inquiredf_21_1_1_response,
            '<cmd>start</cmd><list count = "1"><start ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1"': _start_21_1_1_response,
            '<cmd>start</cmd><list count = "1"><start ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="4"': _start_21_1_4_bad_response,
            '<cmd>stop</cmd><list count = "1"><stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">true</stop></list>': _stop_21_1_1_response,
            '<cmd>stop</cmd><list count = "2">': _stop_21_1_1_and_21_1_2_response,
            '<cmd>stop</cmd><list count = "1"><stop ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="4">true</stop></list>': _stop_21_1_4_bad_reponse,
            '<cmd>download</cmd><download devtype="27" devid="21" subdevid="1" chlid="1" auxid="0" testid="0" startpos="219576" count="1000"/>': _download_21_1_1_repsonse,
            '<cmd>download</cmd><download devtype="27" devid="21" subdevid="1" chlid="1" auxid="0" testid="0" startpos="0" count="0"/>': _download0_21_1_1_repsonse,
            '<cmd>downloadlog</cmd><download devtype="27" devid="21" subdevid="1" chlid="1" testid="0"/>': _downloadlog_21_1_1_response,
            '<cmd>downloadStepLayer</cmd><downloadStepLayer devtype="27" devid="21" subdevid="1" chlid="1" />': _download_step_layer_21_1_1_response,
            '<cmd>clearflag</cmd><list count = "1"><clearflag ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">true</clearflag></list>': _clear_flag_response,
            '<cmd>light</cmd><list count = "1"><light ip="127.0.0.1" devtype="27" devid="21" subdevid="1" chlid="1">true</light></list>': _light_response,
        }
    )
