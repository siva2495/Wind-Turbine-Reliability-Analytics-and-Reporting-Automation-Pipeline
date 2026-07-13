import pandas as pd
import numpy as np
from src.data_processing.issue_snd_solution_processing import *
from src.data_processing.downtime_data_processing import *

def get_wtgs_per_issue(db_issue_fm, rp_issue_library, ncmapping_combo, downtime, top_5_issues_per_site_before):
    issue_final = join_db_issues_solution(db_issue_fm, rp_issue_library, 'id', 'id')
    reg_issue_col = ['id', 'title', 'fmcodes', 'issue', 'uniquefm', 'title_rp', 'fmdescriptions']
    issue_final = issue_final[reg_issue_col]
    ncmapping_issue = join_ncmapping_sol_final(ncmapping_combo, issue_final)
    ncmapping_issue = ncmapping_issue[~ncmapping_issue['id'].isnull()].reset_index(drop=True)
    downtime_with_issues = join_downtime_available_sol(downtime, ncmapping_issue)
    downtime_with_issues = downtime_with_issues[~downtime_with_issues['id'].isnull()]
    downtime_with_issues['id'] = downtime_with_issues['id'].astype(int)
    downtime_with_issues['key'] = downtime_with_issues['name'].astype(str) + '_' + downtime_with_issues['id'].astype(str)
    top_5_issues_per_site = top_5_issues_per_site_before.copy()
    top_5_issues_per_site['key'] = top_5_issues_per_site['name'].astype(str) + '_' + top_5_issues_per_site['id'].astype(str)
    issues_wtg = join_downtime_top5_issue(downtime_with_issues, top_5_issues_per_site)
    final_farm_issue_wtg = agrregate_data_to_name_id(issues_wtg)
    return final_farm_issue_wtg

# Join DB issues and solution library
def join_db_issues_solution(db_issue_fm, solution_df, col1, col2):
    merged = pd.merge(
        db_issue_fm,
        solution_df,
        how='inner',
        left_on=col1,
        right_on=col2,
        suffixes=['', '_rp']
    )
    return merged

# Join nc mapping with issues
def join_ncmapping_sol_final(ncmapping, sol_final):
    merged = pd.merge(
        ncmapping,
        sol_final,
        how='left',
        left_on='unique_gc',
        right_on='uniquefm',
    )
    return merged

# Join downtime with issues
def join_downtime_available_sol(downtime, sol_final):
    merged = pd.merge(
        downtime,
        sol_final,
        how='left',
        left_on='unique_code',
        right_on='unique_kks',
        suffixes=['', '_issue']
    )
    return merged

def join_downtime_top5_issue(downtime_with_issues, top_5_issue):
    merged = pd.merge(
        downtime_with_issues,
        top_5_issue,
        how='left',
        on='key',
        suffixes=['', '_issue']
    )
    return merged

# Aggregate to name/id level
def agrregate_data_to_name_id(solution_with_comments):
    required_cols = ['region', 'country', 'generation', 'name', 'service_point', 'code', 'code_description', 'grouped_code', 'gcode_description', 'id', 'issue', '#wtg aff.', '#wtg tot.', 'solution_comments']
    for col in required_cols:
        if col not in solution_with_comments.columns:
            raise ValueError(f"solution_with_comments must contain column '{col}'")
    def _agg(g: pd.DataFrame) -> pd.Series:
        return pd.Series({
            'turbine_fqsn': '\n'.join(g['turbine_fqsn'].astype(str).unique()),
            'code': '\n'.join(g['code'].astype(str).unique()),
            'code_description': '\n'.join(g['code_description'].astype(str).unique().tolist()),
            'grouped_code': '\n'.join(g['grouped_code'].astype(str).unique()),
            'gcode_description': '\n'.join(g['gcode_description'].astype(str).unique())
        })
    out = (
        solution_with_comments.groupby(['region', 'country', 'generation', 'name', 'service_point', 'id', 'issue'])
                            .apply(_agg)
                            .reset_index()
    )
    return out