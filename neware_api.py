""" Python API for Neware Battery Testing System 

Contains a single class NewareAPI that provides methods to interact with the
Neware Battery Testing System.
"""

import os
import re
import socket
from datetime import datetime
import pandas as pd
import shortuuid
import xmltodict

class NewareAPI:
    """ Python API for Neware Battery Testing System
    
    Provides a method to send and receive commands to the Neware Battery Testing
    System with xml strings, and convenience methods to start, stop, and get the
    status and data from the channels.
    """
    def __init__(self, ip: str, port: int, channel_map: dict):
        """ Initialize the NewareAPI object with the IP, port, and channel map."""
        self.ip = ip
        self.port = port
        self.channel_map = channel_map
        self.neware_socket = None
        self.end_message = "\n\n#\r\n"

    def connect(self) -> None:
        """ Establish the TCP connection """
        self.neware_socket = socket.socket()
        self.neware_socket.connect((self.ip, self.port))
        connect = (
            '<?xml version="1.0" encoding="UTF-8" ?><bts version="1.0"><cmd>connect</cmd>'
            '<username>admin</username><password>neware</password><type>bfgs</type></bts>'
        )
        self.command(connect)

    def disconnect(self) -> None:
        """ Close the port """
        if self.neware_socket:
            self.neware_socket.close()

    def __enter__(self):
        """
        Establish the TCP connection when entering the context.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def command(self, cmd: str) -> str:
        """ Send a command to the device, and return the response. """
        self.neware_socket.sendall(str.encode(cmd+self.end_message, 'utf-8'))
        received = ""
        while not received.endswith(self.end_message):
            received += self.neware_socket.recv(2048).decode()
        return received[:-len(self.end_message)]


    def start_job(self, pipeline: str, sampleid: str, payload_xml_path: str) -> str:
        """ Start designated payload file on a pipeline.

        sampleid is used as the barcode in the Neware system.
        """
        devid, subdevid, chlid = self.channel_map[pipeline]
        cmd = (
            '<?xml version="1.0" encoding="UTF-8" ?>'
            '<bts version="1.0">'
            '<cmd>start</cmd>'
            '<list count="1" DBC_CAN="1">'
            f'<start ip="127.0.0.1" devtype="24" devid="{devid}"'
            f'subdevid="{subdevid}" '
            f'chlid="{chlid}" '
            f'barcode="{sampleid}">'
            f'{payload_xml_path}</start>'
            '<backup backupdir="C:\\BACKUP" remotedir="" filenametype="1" '
            'customfilename="" addtimewhenrepeat="0" createdirbydate="0" '
            'filetype="1" backupontime="0" backupontimeinterval="720" '
            'backupfree="0" />'
            '</list></bts>'
        )
        return self.command(cmd)

    def stop_job(self, pipelines: str|list[str]|tuple[str]) -> str:
        """ Stop job running on pipeline(s) """
        if isinstance(pipelines, str):
            n_channels = 1
            pipeline = [pipelines]
        elif isinstance(pipelines, tuple) or isinstance(pipelines, list):
            n_channels = len(pipelines)
        else:
            print("Cannot read Channel ID, make sure the type is correct.")

        header = (
            '<?xml version="1.0" encoding="UTF-8" ?>\n'
            '<bts version="1.0">\n\t<cmd>stop</cmd>\n'
            f'\t<list count = "{n_channels}">\n'
        )
        footer = '\t</list>\n</bts>'
        cmd_string = ""
        for pipeline in pipelines:
            devid, subdevid, chlid = self.channel_map[pipeline]
            cmd_string += (
                f'\t\t<stop ip="127.0.0.1" devtype="24" devid="{devid}" '
                f'subdevid="{subdevid}" chlid="{chlid}">true</stop>\n'
            )
        return self.command(header+cmd_string+footer)

    def get_status(self, pipeline: str = '') -> str:
        """ Get status of pipeline(s)
        
        Without pipeline argument, it will return status of all pipelines.
        """
        devid, subdevid, chlid = self.channel_map[pipeline]
        header = (
            f'<?xml version="1.0" encoding="UTF-8" ?>\n<bts version="1.0">\n\t'
            f'<cmd>getchlstatus</cmd>\n\t<list count = "{len(self.channel_map)}">\n'
        )
        footer = '\t</list>\n</bts>'
        cmd_string = ""
        for devid, subdevid, chlid in self.channel_map.values():
            cmd_string += (
                '\t\t<status ip="127.0.0.1" devtype="24" '
                f'devid="{devid}" subdevid="{subdevid}" chlid="{chlid}">true</status>\n'
            )
        rspns = self.command(header+cmd_string+footer)
        if pipeline:
            match = re.search(f'devid="{devid}" subdevid="{subdevid}" chlid="{chlid}"' + r'\>(.*?)\<', rspns)
            if match:
                return match.group(1)
            else:
                return rspns
        else:
            return rspns

    def inquire_channel(self, pipeline: str) -> dict:
        """ Inquire the status of the channel """
        # TODO how is this different from get_status?
        devid, subdevid, chlid = self.channel_map[pipeline]
        cmd_string = (
            '<?xml version="1.0" encoding="UTF-8" ?>'
            '<bts version="1.0"><cmd>inquire</cmd>'
            '<list count = "1">'
            '<inquire ip="127.0.0.1" devtype="24" '
            f'devid="{devid}" subdevid="{subdevid}" chlid="{chlid}" '
            'aux="0" barcode="1">true</inquire>'
            '</list></bts>'
        )
        recv_str = self.command(cmd_string)
        pattern = r'<inquire(.*?)\/>'
        match = re.search(pattern, recv_str)
        key_vals_pattern = r'(\w+)="([^"]*)"'
        key_val_matches = re.findall(key_vals_pattern, match[0])
        channel_status = {key: value for key, value in key_val_matches}
        return channel_status

    def download_data(self, pipeline: str, save_path: str = '') -> None:
        """ Downloads the data points for chlid.
        
        Uses the channel map to get the device id, subdevice id, and channel id.
        save_path must contain file name, if not given it defaults to C:/DATA
        """
        start_pos = 1
        count = '100'
        name = self.inquire_channel(pipeline)['barcode']
        if not save_path:
            data_folder = 'C:'+os.sep+"DATA"+os.sep
            date = datetime.today().strftime('%Y-%m-%d')
            if not os.path.exists(data_folder+date):
                os.makedirs(data_folder+date)
            uniqeid = str(shortuuid.uuid())
            new_file = data_folder+date+os.sep+date+"_"+name+"_"+uniqeid+".txt"
        else:
            new_file = save_path

        devid, subdevid, chlid = self.channel_map[pipeline]
        while count == '100':
            cmd_string = (
                '<?xml version="1.0" encoding="UTF-8" ?><bts version="1.0">'
                '<cmd>download</cmd>'
                f'<download devtype="24" devid="{devid}" '
                f'subdevid="{subdevid}" '
                f'chlid="{chlid}" '
                f'auxid="0" testid="0" startpos="{start_pos}" count="100"/>'
                '</bts>'
            )
            return_data = self.command(cmd_string)
            match = re.search(r'<list count="(\d+)">(.*?)</list>', return_data, re.DOTALL)
            if match:
                # Extract the count and the matched text
                count = match.group(1)
                start_pos += int(count)
                extracted_data = match.group(2)
                if save_path:
                    pass
                with open(new_file, 'a', encoding='utf-8') as f:
                    f.write(extracted_data)
            else:
                print('error')
                break
        self.xml_to_csv(new_file)
        # deletes the txt file
        if os.path.isfile(new_file):
            os.remove(new_file)

    def xml_to_csv(self, filepath: str) -> None:
        """ Converts the xml file to csv file """
        pattern = r'<(.*?)\/>'
        key_vals_pattern = r'(\w+)="([^"]*)"'
        buffer = ''
        data = []
        save_file = filepath.rsplit('.', 1)[0]
        with open(filepath, 'r', encoding='utf-8') as file:
            while True:
                chunk = buffer + file.read(2048)
                if not chunk:
                    break

                # Process the chunk up to the last complete piece of data
                last_newline = chunk.rfind('\n')
                if last_newline != -1:
                    data_to_process = chunk[:last_newline]
                    buffer = chunk[last_newline+1:]
                else:
                    data_to_process = chunk
                    buffer = ''
                # Regular expression pattern to match each row
                matches = re.findall(pattern, data_to_process)
                for match in matches:
                    # Fine Key-Value pairs
                    key_val_matches = re.findall(key_vals_pattern, match)
                    # Convert the matches into a dictionary
                    row = {key: value for key, value in key_val_matches}
                    data.append(row)
        df = pd.DataFrame(data)
        df.to_csv(save_file+'.csv', index=False)

    def device_info(self) -> dict:
        """ Get device information """
        device_info = (
            '<?xml version="1.0" encoding="UTF-8" ?>'
            '<bts version="1.0"><cmd>getdevinfo</cmd></bts>'
        )
        return xmltodict.parse(self.command(device_info))
