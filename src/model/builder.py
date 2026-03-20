"""
Functions: helper function usually to create base level components
Classes: Factory class to create systems
"""

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from . import model as epm


class Spectrum(Enum):
    """Spectrum for optical properties."""

    solar = "solar"
    visible = "visible"


class Direction(Enum):
    """Direction for optical properties."""

    front = "front"
    back = "back"


class RadiativeType(Enum):
    """Radiative type for optical properties."""

    transmittance = "transmittance"
    reflectance = "reflectance"
    absorptance = "absorptance"


class LayerType(Enum):
    """Product type for layer."""

    glazing = "glazing"
    blinds = "blinds"
    fabric = "fabric"


class ConstructionComplexFenestrationStateLayerInput(BaseModel):
    """Input for ConstructionComplexFenestrationStateLayer."""

    name: str
    product_type: LayerType
    thickness: float
    conductivity: None | float
    emissivity_front: float
    emissivity_back: float
    infrared_transmittance: float
    directional_absorptance_front: List[float]
    directional_absorptance_back: List[float]
    top_opening_multiplier: float
    bottom_opening_multiplier: float
    left_side_opening_multiplier: float
    right_side_opening_multiplier: float
    front_opening_multiplier: float
    slat_width: float
    slat_spacing: float
    slat_thickness: float
    slat_angle: float
    slat_conductivity: float
    slat_curve: float


class ConstructionComplexFenestrationStateInput(BaseModel):
    """Input for ConstructionComplexFenestrationState."""

    layers: List[ConstructionComplexFenestrationStateLayerInput]
    gaps: List[Union[epm.WindowMaterialGasMixture, epm.WindowMaterialGas]]
    solar_reflectance_back: List[List[float]]
    solar_transmittance_front: List[List[float]]
    visible_reflectance_back: List[List[float]]
    visible_transmittance_front: List[List[float]]
    matrix_basis: str = "Full Klems"


def build_matrix_two_dimension_single_row(
    matrix: List[float],
) -> epm.MatrixTwoDimension:
    """Build MatrixTwoDimension object from single row matrix.

    Args:
        matrix: single row matrix

    Returns:
        MatrixTwoDimension object
    """
    return epm.MatrixTwoDimension(
        number_of_columns=len(matrix),
        number_of_rows=1,
        values=[epm.Value2(value=val) for val in matrix],
    )


def build_matrix_two_dimension(matrix: List[List[float]]) -> epm.MatrixTwoDimension:
    """Get MatrixTwoDimension object from matrix.

    Args:
        matrix: List of list of float matrix data

    Returns:
        MatrixTwoDimension object
    """
    return epm.MatrixTwoDimension(
        number_of_columns=len(matrix[0]),
        number_of_rows=len(matrix),
        values=[epm.Value2(value=val) for row in matrix for val in row],
    )


class EnergyPlusModel(epm.EnergyPlusModel):
    """EnergyPlusModel with builder methods to add systems."""

    def add(self, objkey, objname, obj):
        """Add object to EnergyPlusModel.
        This method assume the object is a dictionary in
        EnergyPlusModel.

        Args:
            objkey: key of object in EnergyPlusModel
            objname: name of the object
            obj: object to add
        """
        if getattr(self, objkey) is None:
            setattr(self, objkey, {objname: obj})
        else:
            getattr(self, objkey)[objname] = obj

    def add_construction_complex_fenestration_state(
        self,
        name: str,
        input: ConstructionComplexFenestrationStateInput,
    ) -> None:
        """Add a construction_complex_fenestration_state to the model.
        We also set all fenestration_surface_detailed in the model to
        the first construction_complex_fenestration_state.

        Args:
            name: name of glazing system
            input: input parameters construction_complex_fenestration_state
        """
        if self.fenestration_surface_detailed is None:
            raise ValueError("No fenestration_surface_detailed found in this model")

        builder = ConstructionComplexFenestrationStateBuilder(name, self, input)
        builder.add_to_enenrgyplus_model()

        if self.construction_complex_fenestration_state is None:
            raise ValueError("No construction_complex_fenestration_state")

        # Set the all fenestration surface constructions to the 1st cfs
        first_cfs = next(iter(self.construction_complex_fenestration_state.keys()))
        for window in self.fenestration_surface_detailed.values():
            if window.surface_type.value == "Window":
                window.construction_name = first_cfs


class ConstructionComplexFenestrationStateBuilder:
    """Builder class for ConstructionComplexFenestrationState."""

    def __init__(
        self,
        name: str,
        energyplus_model: "EnergyPlusModel",
        input: Optional[ConstructionComplexFenestrationStateInput],
    ):
        self.energyplus_model = energyplus_model
        self.name = name
        self.attributes = {}
        self.input = input

    def add_to_enenrgyplus_model(self):
        if self.input is not None:
            self.set_all_input(self.input)
        if self.attributes == {}:
            raise ValueError(
                "Attributes not set for ConstructionComplexFenestrationState"
            )
        self.energyplus_model.add(
            "construction_complex_fenestration_state",
            self.name,
            epm.ConstructionComplexFenestrationState.model_validate(self.attributes),
        )

    def set_all_input(self, input: ConstructionComplexFenestrationStateInput):
        if input.matrix_basis == "Full Klems":
            basis_matrix_name = "FullKlemsBasis"
            self.set_basis_matrix_name(basis_matrix_name)
        else:
            raise NotImplementedError("Only Full Klems is supported")

        # Fixed basis type, basis symmetry type, and window thermal model
        self.set_basis_type(epm.BasisType.lbnlwindow)
        self.set_basis_symmetry_type(epm.BasisSymmetryType.none)
        self.set_window_thermal_model("ThermParam_1")

        self.set_optical_complex_matrix_name(
            Spectrum.solar,
            Direction.back,
            RadiativeType.reflectance,
            f"{self.name}_RbSol",
            input.solar_reflectance_back,
        )
        self.set_optical_complex_matrix_name(
            Spectrum.solar,
            Direction.front,
            RadiativeType.transmittance,
            f"{self.name}_TfSol",
            input.solar_transmittance_front,
        )
        # typo in schema
        self.set_optical_complex_matrix_name(
            Spectrum.visible,
            Direction.back,
            RadiativeType.transmittance,
            f"{self.name}_Tbvis",
            input.visible_reflectance_back,
        )
        self.set_optical_complex_matrix_name(
            Spectrum.visible,
            Direction.front,
            RadiativeType.transmittance,
            f"{self.name}_Tfvis",
            input.visible_transmittance_front,
        )

        for idx, layer in enumerate(input.layers):
            self.set_layer_directional_absorptance_matrix_name(
                idx + 1,
                Direction.front,
                f"{self.name}_layer_{idx+1}_fAbs",
                layer.directional_absorptance_front,
            )
            self.set_layer_directional_absorptance_matrix_name(
                idx + 1,
                Direction.back,
                f"{self.name}_layer_{idx+1}_bAbs",
                layer.directional_absorptance_back,
            )
            self.set_layer(idx + 1, layer)

        for idx, gap in enumerate(input.gaps):
            self.set_gap(
                idx + 1,
                f"{self.name}_gap_{idx + 1}",
                gap,
            )

    def set_gap(
        self,
        layer_index: int,
        name: str,
        gap: Union[epm.WindowMaterialGas, epm.WindowMaterialGasMixture],
    ) -> "ConstructionComplexFenestrationStateBuilder":
        """Set gap layer.

        Args:
            layer_index: index of layer
            name: name of gap
            gas_type: gas type
            thickness: thickness of gap

        Returns:
            ConstructionComplexFenestrationStateBuilder

        Raises:
            ValueError: If layer index is not between 1 and 4.
        """
        if layer_index < 1 or layer_index > 4:
            raise ValueError("Layer index must be between 1 and 4.")
        gas_name = f"{name}_gas"
        if isinstance(gap, epm.WindowMaterialGas):
            self.energyplus_model.add(
                "window_material_gas",
                gas_name,
                gap,
            )
        elif isinstance(gap, epm.WindowMaterialGasMixture):
            self.energyplus_model.add("window_material_gas_mixture", gas_name, gap)
        else:
            raise NotImplementedError(f"Gas type {gap} not supported")

        self.energyplus_model.add(
            "window_material_gap",
            name,
            epm.WindowMaterialGap(
                gas_or_gas_mixture_=gas_name,
                thickness=gap.thickness,
                pressure=101325.0,
            ),
        )
        self.attributes[f"gap_{layer_index}_name"] = name
        return self

    def set_basis_type(self, basis_type: epm.BasisType):
        self.attributes["basis_type"] = basis_type
        return self

    def set_basis_symmetry_type(self, basis_symmetry_type: epm.BasisSymmetryType):
        self.attributes["basis_symmetry_type"] = basis_symmetry_type
        return self

    def set_window_thermal_model(self, name: str):
        """Fixed thermal model settings for CFS."""
        self.energyplus_model.add(
            "window_thermal_model_params",
            name,
            epm.WindowThermalModelParams(
                standard=epm.Standard.iso15099,
                thermal_model=epm.ThermalModel.iso15099,
                sdscalar=1.0,
                deflection_model=epm.DeflectionModel.no_deflection,
            ),
        )
        self.attributes["window_thermal_model"] = name
        return self

    def set_basis_matrix_name(self, name: str):
        self.energyplus_model.add(
            "matrix_two_dimension",
            name,
            build_matrix_two_dimension(
                [
                    [0.0, 1.0],
                    [10.0, 8.0],
                    [20.0, 16.0],
                    [30.0, 20.0],
                    [40.0, 24.0],
                    [50.0, 24.0],
                    [60.0, 24.0],
                    [70.0, 16.0],
                    [82.5, 12.0],
                ]
            ),
        )
        self.attributes["basis_matrix_name"] = name
        return self

    def set_optical_complex_matrix_name(
        self,
        spectrum: Spectrum,
        direction: Direction,
        radiative_type: RadiativeType,
        name: str,
        matrix_data: List[List[float]],
    ) -> "ConstructionComplexFenestrationStateBuilder":
        self.energyplus_model.add(
            "matrix_two_dimension",
            name,
            build_matrix_two_dimension(matrix_data),
        )
        attribute_key = f"{spectrum.value}_optical_complex_{direction.value}_{radiative_type.value}_matrix_name"
        self.attributes[attribute_key] = name
        return self

    def set_layer(
        self,
        layer_index: int,
        layer: ConstructionComplexFenestrationStateLayerInput,
    ) -> "ConstructionComplexFenestrationStateBuilder":
        """Set layer.

        Args:
            layer_index: index of layer
            name: name of layer
            product_type: product type
            emissivity_front: front side emissivity
            emissivity_back: back side emissivity
            ir_transmittance: infrared transmittance
            conductivity: conductivity
            thickness: thickness

        Returns:
            ConstructionComplexFenestrationStateBuilder

        Raises:
            ValueError: If layer index is not between 1 and 5.
        """
        if layer_index < 1 or layer_index > 5:
            raise ValueError("Layer index must be between 1 and 5.")

        if layer.product_type == LayerType.glazing:
            self.energyplus_model.add(
                "window_material_glazing",
                layer.name,
                epm.WindowMaterialGlazing(
                    back_side_infrared_hemispherical_emissivity=layer.emissivity_back,
                    conductivity=layer.conductivity,
                    front_side_infrared_hemispherical_emissivity=layer.emissivity_front,
                    infrared_transmittance_at_normal_incidence=layer.infrared_transmittance,
                    optical_data_type=epm.OpticalDataType.bsdf,
                    poisson_s_ratio=0.22,
                    thickness=layer.thickness,
                    window_glass_spectral_data_set_name="",
                ),
            )
        # Assuming shading if not glazing
        else:

            self.energyplus_model.add(
                "window_material_complex_shade",
                layer.name,
                epm.WindowMaterialComplexShade(
                    back_emissivity=layer.emissivity_back,
                    top_opening_multiplier=layer.top_opening_multiplier,
                    bottom_opening_multiplier=layer.bottom_opening_multiplier,
                    left_side_opening_multiplier=layer.left_side_opening_multiplier,
                    right_side_opening_multiplier=layer.right_side_opening_multiplier,
                    front_opening_multiplier=layer.front_opening_multiplier,
                    conductivity=layer.conductivity,
                    front_emissivity=layer.emissivity_front,
                    ir_transmittance=layer.infrared_transmittance,
                    layer_type=(
                        epm.LayerType.bsdf
                        if layer.product_type == LayerType.fabric
                        else epm.LayerType.venetian_horizontal
                    ),
                    thickness=layer.thickness,
                    slat_width=layer.slat_width,
                    slat_spacing=layer.slat_spacing,
                    slat_thickness=layer.slat_thickness,
                    slat_angle=layer.slat_angle,
                    slat_conductivity=layer.slat_conductivity,
                    slat_curve=layer.slat_curve,
                ),
            )
        layer_key = (
            f"layer_{layer_index}_name" if layer_index > 1 else "outside_layer_name"
        )
        self.attributes[layer_key] = layer.name
        return self

    def set_layer_directional_absorptance_matrix_name(
        self,
        layer_index: int,
        direction: Direction,
        name: str,
        layer_absorptance: List[float],
    ) -> "ConstructionComplexFenestrationStateBuilder":
        """Set layer directional absorptance matrix name.

        Args:
            layer_index: index of layer
            direction: direction of optical properties
            name: name of matrix
            layer_absorptance: layer absorptance matrix

        Returns:
            ConstructionComplexFenestrationStateBuilder

        Raises:
            ValueError: If layer index is not between 1 and 5.

        """
        if layer_index < 1 or layer_index > 5:
            raise ValueError("Layer index must be between 1 and 5.")

        self.energyplus_model.add(
            "matrix_two_dimension",
            name,
            build_matrix_two_dimension_single_row(layer_absorptance),
        )
        if layer_index == 1:
            attribute_key = (
                f"outside_layer_directional_{direction.value}_absorptance_matrix_name"
            )
        else:
            attribute_key = f"layer_{layer_index}_directional_{direction.value}_absorptance_matrix_name"
        self.attributes[attribute_key] = name
        return self
