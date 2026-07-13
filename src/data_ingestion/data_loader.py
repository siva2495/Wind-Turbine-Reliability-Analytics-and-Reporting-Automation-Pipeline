import pandas as pd
import numpy as np
import re
import os
import glob
import yaml


# def load_data():
#     #read all the input data
#     windpulse_solution = pd.read_csv('data/input/windpulse_solutions.csv', encoding="cp1252")
#     rp_issue_library = pd.read_csv('data/input/rp_issue_library.csv', encoding="cp1252")
#     db_issue_fm = pd.read_csv('data/input/DB_issuesFM.csv', encoding="cp1252")
#     nc_mapping_combo = pd.read_csv('data/input/NC_mapping_combo.csv', encoding="cp1252")
#     abbreviated_region = pd.read_csv('data/input/AbbreviatedRegion.csv')
#     vm_art_master = pd.read_csv('data/input/vm_art_master_data.csv', encoding="cp1252")
#     fleet_overview = pd.read_csv('data/input/GlobalFleetOverview.csv', encoding="cp1252", low_memory=False)
#     downtime = pd.read_excel('data/input/Downtimes2025-SeveralRegions-generations.xlsx', sheet_name='Export')
#     fr_target2026 = pd.read_csv('data/input/fr_target_2026.csv')

#     return (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
#             abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026)

def load_data_from_config(config, key, encoding=None, sheet_name=None, low_memory=None):
    """
    Loads a CSV file specified by key in the config's data_paths section.
    """
    file_path = config['data_paths'][key]
    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path, sheet_name=sheet_name)
    return pd.read_csv(file_path, encoding=encoding)