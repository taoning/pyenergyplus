import json
import unittest
from pathlib import Path

from pyenergyplus.model import EnergyPlusModel
from pyenergyplus.model.builder import (
    ConstructionComplexFenestrationStateBuilder,
    ConstructionComplexFenestrationStateInput,
    ConstructionComplexFenestrationStateLayerInput,
    LayerType,
)
from pyenergyplus.model.model import GasType, WindowMaterialGas

DATA_DIR = Path(__file__).parent / "data"


def _make_layer(name):
    return ConstructionComplexFenestrationStateLayerInput(
        name=name,
        product_type=LayerType.glazing,
        thickness=0.003,
        conductivity=1.0,
        emissivity_back=0.3,
        emissivity_front=0.3,
        infrared_transmittance=0,
        directional_absorptance_back=[0 for _ in range(145)],
        directional_absorptance_front=[0 for _ in range(145)],
        top_opening_multiplier=1.0,
        bottom_opening_multiplier=1.0,
        left_side_opening_multiplier=1.0,
        right_side_opening_multiplier=1.0,
        front_opening_multiplier=1.0,
        slat_width=0.01,
        slat_spacing=0.01,
        slat_thickness=0.01,
        slat_angle=0.0,
        slat_conductivity=1.0,
        slat_curve=0.0,
    )


class TestCCFSBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DATA_DIR / "RefBldgPrimarySchoolNew2004_Chicago.epJSON") as f:
            cls.model1 = EnergyPlusModel.model_validate(json.load(f))

        cls.cfs_input = ConstructionComplexFenestrationStateInput(
            layers=[_make_layer("layer1"), _make_layer("layer2")],
            gaps=[WindowMaterialGas(gas_type=GasType.air, thickness=0.01)],
            solar_reflectance_back=[[0 for _ in range(145)] for _ in range(145)],
            solar_transmittance_front=[[0 for _ in range(145)] for _ in range(145)],
            visible_reflectance_back=[[0 for _ in range(145)] for _ in range(145)],
            visible_transmittance_front=[[0 for _ in range(145)] for _ in range(145)],
        )

    def test_ccfs_builder(self):
        builder = ConstructionComplexFenestrationStateBuilder(
            "test", self.model1, self.cfs_input
        )
        builder.add_to_enenrgyplus_model()
        self.assertIsNotNone(self.model1.construction_complex_fenestration_state)
        self.assertIsNotNone(
            self.model1.construction_complex_fenestration_state["test"]
        )


if __name__ == "__main__":
    unittest.main()
