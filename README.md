# pyenergyplus (LBNL)

`pyenergyplus` is a pip-installable wheel that packages the EnergyPlus
simulation engine and its Python API. It also ships `pyenergyplus.model`,
a Pydantic v2 sub-package providing data models for the EnergyPlus epJSON
format. Both components are versioned together and always track the same
EnergyPlus release.

## Installation

```bash
pip install pyenergyplus-lbnl
```

## Usage

### Simulation API

```python
from pyenergyplus.api import EnergyPlusAPI

api = EnergyPlusAPI()
state = api.state_manager.new_state()
api.runtime.run_energyplus(state, ["-w", "weather.epw", "-r", "model.idf"])
```

### epJSON data models (`pyenergyplus.model`)

Load an epJSON file into a typed `EnergyPlusModel`:

```python
import json
from pyenergyplus.model import EnergyPlusModel

with open("model.epJSON") as f:
    model = EnergyPlusModel.model_validate(json.load(f))

print(model.version)
```

Modify fields through the Pydantic model, then serialize back to a dict and
write to a file for simulation. Use `by_alias=True` so object-type keys match
the EnergyPlus epJSON format (e.g. `"Building"` not `"building"`), and
`exclude_none=True` to omit optional fields that were not set:

```python
import json, tempfile, os
from pyenergyplus.api import EnergyPlusAPI
from pyenergyplus.model import EnergyPlusModel

with open("model.epJSON") as f:
    model = EnergyPlusModel.model_validate(json.load(f))

# --- make changes to the model here ---

epjson_dict = model.model_dump(by_alias=True, exclude_none=True)

with tempfile.NamedTemporaryFile(
    mode="w", suffix=".epJSON", delete=False
) as tmp:
    json.dump(epjson_dict, tmp)
    tmp_path = tmp.name

api = EnergyPlusAPI()
state = api.state_manager.new_state()
api.runtime.run_energyplus(state, ["-w", "weather.epw", "-r", tmp_path])
os.unlink(tmp_path)
```

Individual model classes are importable from `pyenergyplus.model.model`:

```python
from pyenergyplus.model.model import WindowMaterialGas, GasType

gas = WindowMaterialGas(gas_type=GasType.air, thickness=0.012)
```

### Builder helpers

```python
from pyenergyplus.model.builder import (
    ConstructionComplexFenestrationStateBuilder,
    ConstructionComplexFenestrationStateInput,
)
```

## Bundled reference models and weather files

```python
from pyenergyplus.dataset import ref_models, ashrae_models, weather_files

idf_path = ref_models["large_office"]
epw_path = weather_files["chicago"]
```
