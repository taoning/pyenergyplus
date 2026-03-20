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

```python
import json
from pyenergyplus.model import EnergyPlusModel

with open("model.epJSON") as f:
    model = EnergyPlusModel.model_validate(json.load(f))

print(model.version)
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

## Codegen (regenerating `pyenergyplus.model.model`)

When upgrading EnergyPlus, regenerate the Pydantic models from the new schema:

```bash
# 1. Copy the new schema into codegen/
cp /path/to/EnergyPlus/Energy+.schema.epJSON codegen/

# 2. Regenerate
python codegen/codegen.py
```

The output is written to `src/model/model.py`. Commit both the updated schema
and the regenerated file together with the submodule bump.
