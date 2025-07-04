<p align="center">
  <img src="https://github.com/user-attachments/assets/49e6cb62-4cf9-49e0-b2dd-8bc6aa943b89#gh-light-mode-only" width="500" align="center" alt="aurora-neware logo">
  <img src="https://github.com/user-attachments/assets/29fb6253-aa98-4b03-bf36-89104f03d3c5#gh-dark-mode-only" width="500" align="center" alt="aurora-neware logo">
</p>

</br>

## Overview
`aurora-neware` provides a standalone Python API and command line interface (CLI) to control Neware cylers.

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
pip install aurora-neware
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
from aurora_neware import NewareAPI

with NewareAPI() as nw:  # connect to the instrument
    nw.start(
        "pipeline_id",
        "my_sample",
        "my_protocol.xml",
    )
```

## For maintainers

To create a new release, clone the repository, install development dependencies with `pip install '.[dev]'`, and then execute `bumpver update --major/--minor/--patch`.
This will:

  1. Create a tagged release with bumped version and push it to the repository.
  2. Trigger a GitHub actions workflow that creates a GitHub release.

Additional notes:

  - Use the `--dry` option to preview the release change.
  - The release tag (e.g. a/b/rc) is determined from the last release.
    Use the `--tag` option to override the release tag.


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact
For any questions or issues, please open an issue on GitHub or contact econversion@empa.ch.

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
