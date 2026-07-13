import pandas as pd

def process_downtime_data(downtime, vm_art_master, fleet_overview, abbreviated_region, uniquefm_not_null):
    vm_art_master_with_region = join_art_master_region(vm_art_master, abbreviated_region)
    vm_art_master_final = join_art_master_region_fleet_overview(vm_art_master_with_region, fleet_overview)
    downtime_cleaned = join_downtime_art_master_final(downtime, vm_art_master_final)
    downtime_with_issues = join_downtime_available_sol(downtime_cleaned, uniquefm_not_null)
    return vm_art_master_final, downtime_cleaned, downtime_with_issues


# --- Art master, region, fleet overview, downtime joins ---
def join_art_master_region(art_master, abb_region):
    merged = pd.merge(
            art_master,
            abb_region,
            how='left',
            left_on='region',
            right_on='region',
            suffixes=['_art', '_']
        )
    return merged

# --- Downtime join with fleet overview ---
def join_art_master_region_fleet_overview(art_master_region, fleet_overview):
    merged = pd.merge(
            art_master_region,
            fleet_overview,
            how='left',
            left_on='idwtg',
            right_on='wtgnumber',
            suffixes=['_art', '_fleet']
        )
    return merged

# --- Downtime join ---
def join_downtime_art_master_final(downtime, art_master_final):
    merged = pd.merge(
            downtime,
            art_master_final,
            how='left',
            left_on='turbine_fqsn',
            right_on='turbinefqsn',
            suffixes=['_downtime', '_art_master_final']
        )
    return merged

# --- Join downtime and available solutions ---
def join_downtime_available_sol(downtime, sol_final):
    merged = pd.merge(
            downtime,
            sol_final,
            how='left',
            left_on='unique_code',
            right_on='unique_kks',
            suffixes=['_downtime', '_']
        )
    return merged
