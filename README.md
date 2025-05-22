# pyenergyplus (LBNL)

## Overview

pyenergyplus is a direct port of the pyenergyplus API inside the regular EnergyPlus
distribution into a standalone Python package. Nothing is changed and no
additional code is written. The purpose of this port is to have a standalone
Python package so that regular Python users can access EnergyPlus through the
pyenergyplus API without having to separately install EnergyPlus and manage the
environment manually.

## Installation

You can install pyenergyplus using pip:

```bash
pip install pyenergyplus
```

## Usage Example

Here's a simple example of how to use pyenergyplus:

```python
from pyenergyplus.api import EnergyPlusAPI

# Create an API instance
api = EnergyPlusAPI()

# Create a new state
state = api.state_manager.new_state()

# Run EnergyPlus with your input files
api.runtime.run_energyplus(state, ['-w', 'path/to/weather.epw', '-r', 'path/to/model.idf'])
```

## Features

- Access to EnergyPlus functionality through Python
- Includes reference building models and weather files
- Cross-platform support (Windows, macOS, Linux)
- No need for separate EnergyPlus installation

## License

See [LICENSE.txt](LICENSE.txt) for details.
