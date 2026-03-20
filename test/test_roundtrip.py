import json
import tempfile
import unittest
from pathlib import Path

from pyenergyplus.api import EnergyPlusAPI
from pyenergyplus.dataset import ashrae_models, weather_files
from pyenergyplus.model import EnergyPlusModel

DATA_DIR = Path(__file__).parent / "data"


class TestRoundTrip(unittest.TestCase):
    def _api_run(self, args):
        api = EnergyPlusAPI()
        state = api.state_manager.new_state()
        try:
            return api.runtime.run_energyplus(state, args)
        finally:
            api.state_manager.delete_state(state)

    def _roundtrip(self, raw, weather, tmpdir):
        model = EnergyPlusModel.model_validate(raw)
        out = model.model_dump(mode="json", exclude_unset=True, by_alias=True)
        epjson_path = Path(tmpdir) / "model.epJSON"
        epjson_path.write_text(json.dumps(out))
        ret = self._api_run(["-w", str(weather), "-d", str(tmpdir), str(epjson_path)])
        self.assertEqual(ret, 0)

    def test_roundtrip_medium_office(self):
        with open(DATA_DIR / "RefBldgMediumOfficeNew2004_Chicago_epJSON.epJSON") as f:
            raw = json.load(f)
        with tempfile.TemporaryDirectory() as tmpdir:
            self._roundtrip(raw, weather_files["usa_il_chicago"], tmpdir)

    def test_roundtrip_primary_school(self):
        with open(DATA_DIR / "RefBldgPrimarySchoolNew2004_Chicago.epJSON") as f:
            raw = json.load(f)
        with tempfile.TemporaryDirectory() as tmpdir:
            self._roundtrip(raw, weather_files["usa_il_chicago"], tmpdir)

    def test_roundtrip_ashrae_office_small(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            # Convert bundled IDF to epJSON first
            ret = self._api_run(
                ["--convert-only", "-d", str(tmpdir), ashrae_models["office_small"]]
            )
            self.assertEqual(ret, 0, "IDF to epJSON conversion failed")

            epjson_path = tmpdir / "ASHRAE901_OfficeSmall_STD2019_Denver.epJSON"
            raw = json.loads(epjson_path.read_text())
            self._roundtrip(raw, weather_files["usa_co_denver"], tmpdir)


if __name__ == "__main__":
    unittest.main()
