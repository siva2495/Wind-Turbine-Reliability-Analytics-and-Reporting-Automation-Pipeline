import pandas as pd

def materialized_view_for_farm_kpi_issue_sol(farm_kpi_data, farm_issue_solution_data):
    """
    Creates a materialized view combining farm-level KPI data with issue and solution details.

    This function merges farm KPI summary data with issue-level solution data for each wind farm,
    producing a comprehensive DataFrame suitable for reporting and dashboarding. The resulting
    DataFrame includes farm KPIs, intervention rates, issue IDs, issue names, and solution comments.

    Parameters:
        farm_kpi_data (pd.DataFrame): DataFrame containing farm-level KPI summary.
            Required columns: 'name', 'service_point', '#wtg aff.', '#wtg tot.', 'region_x', 'country_x',
                              'generation_x', 'key', 'intervention_rate_x', 'MTBI(d)', 'MTTR(h)', '% to target',
                              '% IR Impact', 'FTFR (%)', 'target26', 'status'
        farm_issue_solution_data (pd.DataFrame): DataFrame containing issue and solution details per farm.
            Required columns: 'name', 'issue_id', 'intervention_rate', 'solution_comments', 'issue'

    Returns:
        pd.DataFrame: Materialized view DataFrame with merged farm KPI and issue/solution columns.
            Columns include farm KPIs, intervention rates, issue IDs, issue names, and solution comments.

    Raises:
        ValueError: If any required column is missing from the input DataFrames.
    """
    def merge_farm_kpi_with_solutions(farm_kpi, farm_solutions):
        required_farm_kpi_cols = ['name']
        required_farm_solutions_cols = ['name', 'issue_id', 'intervention_rate', 'solution_comments']
        for col in required_farm_kpi_cols:
            if col not in farm_kpi.columns:
                raise ValueError(f"farm_kpi must contain column '{col}'")
        for col in required_farm_solutions_cols:
            if col not in farm_solutions.columns:
                raise ValueError(f"farm_solutions must contain column '{col}'")
        merged = pd.merge(
            farm_kpi,
            farm_solutions,
            how='left',
            on='name'
        )
        return merged
    merged = merge_farm_kpi_with_solutions(farm_kpi_data, farm_issue_solution_data)

    columns_needed = ['name',  'service_point', '#wtg aff.', '#wtg tot.', 'region_x', 'country_x', 
                      'generation_x', 'key', 'intervention_rate_x', 'MTBI(d)', 'MTTR(h)', '% to target',
                      '% IR Impact', 'FTFR (%)','target26', 'status', 'issue_id', 'issue', 'intervention_rate_y',
                      'solution_comments']
    materialized_view_data = merged[columns_needed]
    materialized_view_data.rename(columns={
     'name' : 'name',
     'service_point' : 'service_point',
     '#wtg aff.' : '#wtg aff.', 
     '#wtg tot.' : '#wtg tot.', 
     'region_x' : 'region',
     'country_x' : 'country', 
     'generation_x' : 'generation', 
     'key' : 'key', 
     'intervention_rate_x' : 'farm_intervention_rate', 
     'MTBI(d)' : 'MTBI(d)', 
     'MTTR(h)' : 'MTTR(h)', 
     '% to target' : '% to target',
     '% IR Impact' : '% IR Impact',  
     'FTFR (%)' : 'FTFR (%)',
     'target26' : 'target_intervention_rate', 
     'status' : 'Intervention_rate_status', 
     'issue_id' : 'issue_id', 
     'issue' : 'issue_name', 
     'intervention_rate_y' : 'intervention_rate_by_issue',
    'solution_comments': 'solution_availability_and_ir_improvement'}, inplace=True)
    return materialized_view_data