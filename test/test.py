from pyenergyplus.api import EnergyPlusAPI

api = EnergyPlusAPI()
state = api.state_manager.new_state()

# api.runtime.run_energyplus(state, ['-w', 'in.epw', '-r', 'in.idf'])
api.runtime.run_energyplus(state, ['--convert-only', 'in.idf'])
