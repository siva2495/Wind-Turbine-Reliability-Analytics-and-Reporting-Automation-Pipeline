import pandas as pd
import numpy as np

def add_features(vm_art_master, fleet_overview, downtime):
    # Example: Add N155 generation
    vm_art_master['generation'] = np.where(
        vm_art_master['type'].astype(str).str.upper() == 'N155',
        'N155',
        vm_art_master['generation']
    )
    fleet_overview['generation'] = np.where(
        fleet_overview['type'].astype(str).str.upper() == 'N155',
        'N155',
        fleet_overview['generation']
    )
    # Datetime conversion
    downtime['start_time'] = pd.to_datetime(downtime['start_time'])
    downtime['end_time'] = pd.to_datetime(downtime['end_time'])
    downtime['event_id'] = downtime['turbine_fqsn'].astype(str) + '_' + downtime['code'].astype(str) + '_' + downtime['start_time'].dt.strftime('%Y%m%d%H%M%S')
    return vm_art_master, fleet_overview, downtime