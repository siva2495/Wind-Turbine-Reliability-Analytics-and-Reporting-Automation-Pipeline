import pandas as pd
import numpy as np

def priority(farm_level_kpi_with_comment,top_5_issues_per_site_before,  solution_with_ir_improvement):
    df_combined = process_req_data_for_priority_score(farm_level_kpi_with_comment, top_5_issues_per_site_before, solution_with_ir_improvement)
    df_with_priority = assign_priority(df_combined, ['region', 'id'], 'priority_score', 'priority_number_within_region')
    df_with_priority = assign_priority(df_with_priority, ['service_point', 'id'], 'priority_score', 'priority_number_within_service_point')
    df_with_priority = priority_update(df_with_priority, 'priority_score', 'priority_number_within_region', 'priority_update_region')
    df_with_priority = priority_update(df_with_priority, 'priority_score', 'priority_number_within_service_point', 'priority_update_service_point')
    return df_with_priority


def process_req_data_for_priority_score(farm_level_kpi_with_comment, top_5_issues_per_site_before, solution_with_ir_improvement):
    # Select and rename relevant columns from the input dataframes
    issue_col = ['region', 'country', 'generation', 'name', 'id', 'issue', '#wtg aff.', '#wtg tot.', 'intervention_rate']
    farm_col = ['name', '#wtg aff.', '#wtg tot.', 'event_count', 'region_x', 'country', 'service_point', 'generation_x', 
                'key', 'distinct_event_count', 'intervention_rate', 'MTBI(d)', 'MTTR(h)', '% to target', '% IR Impact', 
                 'First_Time_Fix', 'First_Time_Fail', 'FTFR (%)', 'target26', 'status'] #'farm',
    sol_col = ['name', 'id', 'key', 'solution_id', 'solution_name', 'solution_code', 'effectiveness', 'ir_improvement']

    df_farm_level_kpi = farm_level_kpi_with_comment[farm_col]
    df_top_5_issues = top_5_issues_per_site_before[issue_col]
    df_solution_with_ir_improvement = solution_with_ir_improvement[sol_col]

    # Create key columns
    df_top_5_issues['key'] = df_top_5_issues['name'].astype(str) + '_' + df_top_5_issues['id'].astype(str)
    df_solution_with_ir_improvement['key'] = df_solution_with_ir_improvement['name'].astype(str) + '_' + df_solution_with_ir_improvement['id'].astype(str)

    # Merge top 5 issues with solutions
    merged_1 = pd.merge(df_top_5_issues, df_solution_with_ir_improvement, how='left', on='key')

    # Merge with farm level kpi
    merged_2 = pd.merge(merged_1, df_farm_level_kpi, how='left', left_on='name_x', right_on='name')

    # Select and rename columns
    col_req = ['region', 'country_x', 'generation', 'name_x', 'id_x', 'issue', 'intervention_rate_x', 'solution_id', 
               'solution_name', 'solution_code', 'effectiveness', 'ir_improvement', '#wtg aff._y', '#wtg tot._y', 
               'service_point', 'intervention_rate_y', 'MTBI(d)', 'MTTR(h)', '% to target', '% IR Impact', #'farm',  
               'FTFR (%)', 'target26', 'status']
    merged_2 = merged_2[col_req]
    merged_2 = merged_2.rename(columns={
        'region' : 'region', 
        'country_x' : 'country', 
        'generation' : 'generation', 
        'name_x' : 'name', 
        'id_x' : 'id', 
        'issue' : 'issue',
        'intervention_rate_x': 'isssue_ir', 
        'solution_id': 'solution_id', 
        'solution_name': 'solution_name', 
        'solution_code': 'solution_code',
        'effectiveness': 'effectiveness', 
        'ir_improvement':'ir_improvement', 
        '#wtg aff._y' : '#wtg aff.', 
        '#wtg tot._y': '#wtg tot.',
        'service_point' : 'service_point', 
        'intervention_rate_y': 'farm_intervention_rate', 
        'MTBI(d)': 'MTBI(d)',
        'MTTR(h)': 'MTTR(h)', 
        '% to target': '% to target', 
        '% IR Impact': '% IR Impact', 
        #'farm': 'farm',  
        'FTFR (%)': 'FTFR (%)', 
        'target26': 'target26', 
        'status': 'status'
    })

    # Calculate priority score
    merged_2['priority_score'] = merged_2['% IR Impact'] * merged_2['isssue_ir'] * merged_2['effectiveness'] * 100
    return merged_2

# Assign priority within region and service point
def assign_priority(df, group_cols, score_col, new_col):
    for col in group_cols + [score_col]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
    df[score_col] = pd.to_numeric(df[score_col], errors='coerce').fillna(0)
    ranks = df.groupby(group_cols)[score_col].rank(method='dense', ascending=False)
    df[new_col] = ranks.fillna(0).astype(int)
    return df

def priority_update(df, score_col, priority, priority_update):
    df[priority_update] = df.apply(
        lambda row: 0 if row[score_col] == 0.00 else row[priority],
        axis=1
    )
    return df