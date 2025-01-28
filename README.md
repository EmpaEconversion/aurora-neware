# neware-api

## Overview
`neware-api` is a Python package being developed to interact with the Neware battery testing system.

The package provides a command line interface to query and control cylers.

It is designed for BTS 8.0 and WHW-200L-160CH-B systems, and should work on other cyclers using BTS 8.0.

## Features
- Command line interface
- Connect to Neware cyclers
- Retrieve status of channels
- Start and stop experiments

## Installation
Install on a Windows PC with BTS server and client 8.0, connected to a Neware cycler with the API activated.
Then in a Python >3.12 environment, run:
```
pip install git+https://github.com/EmpaEconversion/neware-api.git
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contact
For any questions or issues, please open an issue on GitHub or contact econversion@empa.ch.

## Contributors

- [Graham Kimbell](https://github.com/g-kimbell)
- [Aliaksandr Yakutovich](https://github.com/yakutovicha)

## Acknowledgements

This software is developed at the Materials for Energy Conversion Lab at the Swiss Federal Laboratories for Materials Science and Technology (Empa).
