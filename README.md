<h1 align="center">
  <img src="https://github.com/user-attachments/assets/de390844-f425-4fe0-8b97-a32d94ee7414" width="500" align="center" alt="aurora-biologic logo">
</h1>

</br>

[![PyPI version](https://img.shields.io/pypi/v/aurora-neware.svg)](https://pypi.org/project/aurora-neware/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/empaeconversion/aurora-neware/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/aurora-neware.svg)](https://pypi.org/project/aurora-neware/)
[![Checks](https://img.shields.io/github/actions/workflow/status/empaeconversion/aurora-neware/CI.yml)](https://github.com/EmpaEconversion/aurora-neware/actions/workflows/CI.yml)
[![Coverage](https://img.shields.io/codecov/c/github/empaeconversion/aurora-neware)](https://app.codecov.io/gh/EmpaEconversion/aurora-neware)


A standalone Python package, command line interface (CLI), and REST API to control Neware battery cyclers.

It is designed for BTS 8.0 and WHW-200L-160CH-B systems, and should work on other cyclers using BTS 8.0.

## Features
- Python package, CLI, REST API
- Connect to Neware cyclers
- Retrieve status, data, logs
- Start and stop experiments

## Installation
Install on a Windows PC with BTS server and client 8.0, connected to one or more Neware cyclers with the API activated.

With Python >3.10, run:
```shell
pip install aurora-neware
```

> [!IMPORTANT]
> Your BTS software must have the API activated, accessed with Help -> Mode settings.
>
> You may need to contact Neware for an activation key.

## CLI usage

See commands and arguments with:
```shell
neware --help
neware <COMMAND> --help
```

E.g. to check the status of all channels use:
```shell
neware status
```

To start a job use:
```shell
neware start "pipeline_id" "my_sample" "my_protocol.xml"
```

A `pipeline` is defined by `{Device ID}-{Sub-device ID}-{Channel ID}`, e.g. `"100-2-3"` for machine 100, sub-device 2, channel 3.

## Python usage

Commands are also available through Python, e.g.:
```python
from aurora_neware import NewareAPI

with NewareAPI() as nw:  # connect to the instrument
    nw.start(
        "pipeline_id",
        "my_sample",
        "my_protocol.xml",
    )
```

## REST API usage

Install additional dependencies with
```shell
pip install aurora-neware[api]
```
Then start the server by running
```shell
uvicorn aurora_neware.api.main:app --host localhost --port 8000
```
You can then see the available endpoints at `http://localhost:8000/docs`.

To make the server reachable from other machines on the network, you can use `--host 0.0.0.0`. We strongly recommend only doing this in a secure network and using an API key, otherwise anyone with access can stop every measurement and set the voltage to max on every channel connected.

Set an API key with the `AURORA_NEWARE_API_KEY` environment variable, and ensure that you see the message "API key authentication enabled" when starting the server.

In PowerShell (only lasts for that session):
```shell
$env:AURORA_NEWARE_API_KEY = "myverysecretkey"
```
Or set the key permanently in Windows environment variables.

Then users should pass this key in their requests, e.g.
```shell
curl.exe -H "X-API-Key: myverysecretkey" http://<server-ip>:8000/status
```
Or use the 'authorize' button on `http://localhost:8000/docs`.

## Contributors

- [Graham Kimbell](https://github.com/g-kimbell)
- [Aliaksandr Yakutovich](https://github.com/yakutovicha)

## Acknowledgements

This software was developed at the Laboratory of Materials for Energy Conversion at Empa, the Swiss Federal Laboratories for Materials Science and Technology, and supported by funding from the [IntelLiGent](https://heuintelligent.eu/) project and [Battery 2030+](https://battery2030.eu/) initiative from the European Union’s research and innovation program under grant agreement No. 101069765 and No. 101104022 and from the Swiss State Secretariat for Education, Research, and Innovation (SERI) under contract No. 22.001422 and 300313.

<img src="https://github.com/user-attachments/assets/373d30b2-a7a4-4158-a3d8-f76e3a45a508#gh-light-mode-only" height="100" alt="IntelLiGent logo">
<img src="https://github.com/user-attachments/assets/9d003d4f-af2f-497a-8560-d228cc93177c#gh-dark-mode-only" height="100" alt="IntelLiGent logo">&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://github.com/user-attachments/assets/21ebfe94-5524-487c-a24b-592f68193efc#gh-light-mode-only" height="100" alt="Battery 2030+ logo">
<img src="https://github.com/user-attachments/assets/5bcd9d36-1851-4439-9c71-4dbe09c21df0#gh-dark-mode-only" height="100" alt="Battery 2030+ logo">&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://github.com/user-attachments/assets/1d32a635-703b-432c-9d42-02e07d94e9a9" height="100" alt="EU flag">&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://github.com/user-attachments/assets/cd410b39-5989-47e5-b502-594d9a8f5ae1" height="100" alt="Swiss secretariat">
