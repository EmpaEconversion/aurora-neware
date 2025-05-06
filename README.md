# neware-api

## Overview
`neware-api` provides a Python API and command line interface (CLI) to control Neware cylers.

It is designed for BTS 8.0 and WHW-200L-160CH-B systems, and should work on other cyclers using BTS 8.0.

## Features
- CLI and Python API
- Connect to Neware cyclers
- Retrieve status, data, logs
- Start and stop experiments

## Installation
Install on a Windows PC with BTS server and client 8.0, connected to one or more Neware cyclers with the API activated.

In a Python >3.12 environment, run:
```
pip install git+https://github.com/EmpaEconversion/neware-api.git
```

## CLI usage

See commands and arguments with
```
neware --help
neware <COMMAND> --help
```

E.g. to check the status of all channels use
```
neware status
```

To start a job use
```
neware start "pipeline_id" "my_sample" "my_protocol.xml"
```

A `pipeline` is defined by `{Device ID}-{Sub-device ID}-{Channel ID}`, e.g. `"100-2-3"` for machine 100, sub-device 2, channel 3.

## API usage

Commands are also available through Python, e.g.
```python
python from neware_api import NewareAPI

with NewareAPI() as nw:  # connect to the instrument
    nw.start(
        "pipeline_id",
        "my_sample",
        "my_protocol.xml",
    )
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact
For any questions or issues, please open an issue on GitHub or contact econversion@empa.ch.

## Contributors

- [Graham Kimbell](https://github.com/g-kimbell)
- [Aliaksandr Yakutovich](https://github.com/yakutovicha)

## Acknowledgements

This software was developed at the Materials for Energy Conversion Lab at the Swiss Federal Laboratories for Materials Science and Technology (Empa), and supported through the EU's Horizon programme under the IntelLiGent project (101069765) and the Swiss State Secretariat for Education, Research and Innovation (SERI) (22.00142). 🇪🇺🇨🇭
