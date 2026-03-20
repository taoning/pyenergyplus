import tempfile
from pyenergyplus.api import EnergyPlusAPI
from pyenergyplus.dataset import ref_models, weather_files

api = EnergyPlusAPI()
state = api.state_manager.new_state()

idf = ref_models["small_office"]
epw = weather_files["usa_il_chicago"]

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
    try:
        api.runtime.run_energyplus(state, ['-w', epw, '-d', tmpdir, '-r', idf])
    finally:
        api.state_manager.delete_state(state)
