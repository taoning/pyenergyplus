import json
import unittest
from pathlib import Path

from pyenergyplus.model import EnergyPlusModel
from pyenergyplus.model.model import WindowMaterialGas, GasType

DATA_DIR = Path(__file__).parent / "data"


class TestEnergyPlusModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DATA_DIR / "RefBldgPrimarySchoolNew2004_Chicago.epJSON") as f:
            cls.model1 = EnergyPlusModel.model_validate(json.load(f))
        with open(DATA_DIR / "RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON") as f:
            cls.model2 = EnergyPlusModel.model_validate(json.load(f))

    def test_validate(self):
        self.assertIsNotNone(self.model1.version)

    def test_validate2(self):
        self.assertIsNotNone(self.model2.version)

    def test_validate_component(self):
        gas = WindowMaterialGas(
            gas_type=GasType.air,
            thickness=0.2,
            molecular_weight=28.97,
        )
        gas.thickness = -0.3
        with self.assertRaises(Exception):
            WindowMaterialGas.model_validate(gas.__dict__)


if __name__ == "__main__":
    unittest.main()
