import pandas as pd
import numpy as np
import re

def clean_data(df):
    df = standardize_column_names(df)
    return df

def standardize_column_names(df: pd.DataFrame, lowercase=True, replace_spaces=True, remove_special=True, collapse_underscores=True, strip_underscores=True, make_unique=True) -> pd.DataFrame:
    import re
    df_out = df.copy()
    cols = [str(c).strip() for c in df_out.columns]
    if lowercase:
        cols = [c.lower() for c in cols]
    if replace_spaces:
        cols = [re.sub(r"[\s\-\/]+", "_", c) for c in cols]
    if remove_special:
        cols = [re.sub(r"[^0-9a-zA-Z_]", "", c) for c in cols]
    if collapse_underscores:
        cols = [re.sub(r"_+", "_", c) for c in cols]
    if strip_underscores:
        cols = [c.strip("_") for c in cols]
    if make_unique:
        cols = _make_unique(cols)
    df_out.columns = cols
    return df_out

def _make_unique(cols):
    counts = {}
    unique_cols = []
    for c in cols:
        if c not in counts:
            counts[c] = 1
            unique_cols.append(c)
        else:
            counts[c] += 1
            unique_cols.append(f"{c}_{counts[c]}")
    return unique_cols

 # Filter required columns from the dataframes
def filter_required_columns(windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo):
    col_sol = ['solution_id', 'solution_name', 'solution_code', 'software_change', 'available', 'when_available', 
                'alarm_codes', 'alarm_description', 'turbine', 'avail', 'issue_id', 'effectiveness']

    col_issue_lib = ['id', 'title', 'generation', 'fmcodes', 'fmdescriptions']

    col_issue_db = ['id', 'generation', 'title', 'fmcodes', 'issue', 'uniquefm']

    col_ncmap = ['field', 'kks', 'code_group', 'code_description', 'grouped_code', 'gcode_description', 
                    'unique_kks', 'unique_gc']

    windpulse_solution = windpulse_solution[col_sol]
    rp_issue_library = rp_issue_library[col_issue_lib]
    db_issue_fm = db_issue_fm[col_issue_db]
    nc_mapping_combo = nc_mapping_combo[col_ncmap]

    return (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo)