import pandas as pd
import yaml
from src.data_processing.cleaners import clean_data, filter_required_columns
from src.data_ingestion.data_loader import load_data_from_config #, load_data
from src.data_processing.downtime_data_processing import join_downtime_available_sol, process_downtime_data
from src.data_processing.issue_snd_solution_processing import *
from src.data_processing.downtime_data_processing import process_downtime_data
from src.data_processing.mapping import get_generation_mapping, get_region_mapping, map_and_create_key
from src.reporting.farm_level_aggregation import farm_level_summary
from src.reporting.issue_level_aggregation import create_summary_by_issue, prepare_available_issue_to_unquefm_level
from src.reporting.materialized_view_for_farm_kpi_issue_sol import materialized_view_for_farm_kpi_issue_sol
from src.utils.features import add_features
from src.utils.get_top_n_issue_per_windfarm import *
from src.utils.master_date_builder import master_date
from src.utils.create_kpis import *
from src.utils.commentry import add_interventionrate_status_comment, solution_comment
from src.utils.wtgs_per_issues import get_wtgs_per_issue
from src.utils.priority_score import priority

def main():    
    # Load your data
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    windpulse_solution = load_data_from_config(config, "windpulse_solution", encoding="cp1252")
    rp_issue_library = load_data_from_config(config, "rp_issue_library", encoding="cp1252")
    db_issue_fm = load_data_from_config(config, "db_issue_fm", encoding="cp1252")
    nc_mapping_combo = load_data_from_config(config, "nc_mapping_combo", encoding="cp1252")
    abbreviated_region = load_data_from_config(config, "abbreviated_region")
    vm_art_master = load_data_from_config(config, "vm_art_master", encoding="cp1252")
    fleet_overview = load_data_from_config(config, "fleet_overview", encoding="cp1252", low_memory=False)
    downtime = load_data_from_config(config, "downtime", sheet_name='Export')
    fr_target2026 = load_data_from_config(config, "fr_target2026", encoding="cp1252")

    # (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
    #  abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026) = load_data()
    
    # standardize column names
    def cleaning(windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
               abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026):
        windpulse_solution = clean_data(windpulse_solution)
        rp_issue_library = clean_data(rp_issue_library)
        db_issue_fm = clean_data(db_issue_fm)
        nc_mapping_combo = clean_data(nc_mapping_combo)
        abbreviated_region = clean_data(abbreviated_region)
        vm_art_master = clean_data(vm_art_master)
        fleet_overview = clean_data(fleet_overview)
        downtime = clean_data(downtime)
        fr_target2026 = clean_data(fr_target2026)
        return (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
                abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026)
    # Clean
    (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
     abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026) = cleaning(
        windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo,
        abbreviated_region, vm_art_master, fleet_overview, downtime, fr_target2026)
    
    # Filter required columns from the dataframes
    (windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo) = filter_required_columns(
        windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo)
    # add features
    vm_art_master, fleet_overview, downtime = add_features(vm_art_master, fleet_overview, downtime)
    print("="*100)
    print("\nData loaded and cleaned. Starting processing...\n")
    print("="*100)

    print(windpulse_solution['solution_id'].isnull().sum())
    # Process issue and solution data
    issue_with_available_sol, uniquefm_not_null = process_solutions(
        windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo)
    
    print("Issue with available solutions:")
    print(issue_with_available_sol.shape)
    print("Unique FM not null:")
    print(uniquefm_not_null.shape)

    # Process downtime data
    vm_art_master_final, downtime_cleaned, downtime_with_issues = process_downtime_data(
        downtime, vm_art_master, fleet_overview, abbreviated_region, uniquefm_not_null)
    
    print("shape of downtime before joining issues and solutions:")
    print(downtime.shape)
    print("Downtime with issues and solutions:")
    print(downtime_with_issues.shape)

    # master date table
    master_date_table = master_date(downtime)

    print("\nMaster date table:")
    print("date min:", min(master_date_table['date']))
    print("date max:", max(master_date_table['date']))
    print("sum of data available:", master_date_table['data_available'].sum())

    print("\n Downtime with issues columns:", downtime_with_issues['event_id'].head())
    # ceate farm level summary for KPI calculation
    farm_level = farm_level_summary(vm_art_master_final, downtime_with_issues)
    # kpi_data['key'] = kpi_data['region'] + '-' + kpi_data['generation']

    farm_level_filtered = farm_level[(farm_level['key'].isin(['LATAM-AW-3000', 'Nordics-DELTA4000', 'SAAPAC-N155', 'Central-DELTA', 'Mediterranean-GAMMA']) ) & (farm_level['#wtg aff.'] != 0)]
    farm_level_filtered = farm_level_filtered.sort_values(by='#wtg aff.', ascending=False).reset_index(drop=True)

    print("\nFarm level summary for KPI calculation:")
    print("="*100)
    print('shape of farm level summary:', farm_level.shape)
    print('shape of filtered farm level summary:', farm_level_filtered.shape)
    print(farm_level_filtered.head())

    # Add KPIs
    farm_level_kpi = add_fault_rate(farm_level_filtered, downtime_with_issues, master_date_table)
    farm_level_kpi = add_mtbi(farm_level_kpi)
    farm_level_kpi = add_mttr(farm_level_kpi, 
                              downtime_with_issues, 
                              group_col='name', 
                              duration_col='duration_h', 
                              code_col='code', 
                              mttr_col='MTTR(h)')
    
    farm_level_kpi['% to target'] = farm_level_kpi.apply(lambda row: percent_to_target(row), axis=1)
    farm_level_kpi['% IR Impact'] = farm_level_kpi.apply(lambda row: percent_ir_impact(downtime_with_issues, row['name']), axis=1)
    
    turbine_results, farm_results = calculate_ftfr(downtime_with_issues)
    farm_level_kpi = join_FTFR_KPI_summary(farm_level_kpi, 
                                           farm_results, 
                                           kpi_farm_col='name', 
                                           ftfr_farm_col='name')
    
    print("\nFarm level summary with fault rate:")
    print("="*100)
    print(farm_level_kpi.head())
    print("="*100)
    print('\ncolumns in farm level kpi:', farm_level_kpi.columns)

    # --- Compare intervention rate target 2026 and generate comments ---
    print("\nFR target 2026 before mapping:")
    print(fr_target2026.head())
    region_mapping = get_region_mapping()
    generation_mapping = get_generation_mapping()
    fr_target2026 = map_and_create_key(
                                        fr_target2026, 
                                        generation_mapping, 
                                        region_mapping, 
                                        generation_col='generation', 
                                        region_col='region', 
                                        key_col='key')
    print("\nFR target 2026 after mapping:")
    print(fr_target2026.head())
    print('='*100)

    farm_level_kpi_with_comment = add_interventionrate_status_comment(fr_target2026, farm_level_kpi)
    print("\nFarm level KPI with comments:")
    print('='*100)
    print(farm_level_kpi_with_comment[['name', 'intervention_rate', 'target26', 'status']].head())
    farm_level_kpi_with_comment.to_csv('data/output/farm_level_kpi_with_comments.csv', index=False)
    # print("="*100)
    # print('\nkey in farm level kpi with comments:\n', farm_level_kpi_with_comment['key'].unique())
    # print("="*100)
    # print("\nkey in target df:\n", fr_target2026['key'].unique())

    # process issue and aggregate
    dbissue_rp_issue = join_db_issues_solution(db_issue_fm, rp_issue_library, 'id', 'id')
    issues_uniquefm_level = prepare_available_issue_to_unquefm_level(dbissue_rp_issue)
    issues_with_nc_mapping = join_ncmapping_sol_final(nc_mapping_combo, issues_uniquefm_level)
    issue_uniquefm_not_null = issues_with_nc_mapping[issues_with_nc_mapping['uniquefm'].notnull()].reset_index(drop=True)
    downtime_final_with_issues = join_downtime_available_sol(downtime_with_issues, issue_uniquefm_not_null)
    issue_grouped = downtime_final_with_issues.groupby(['id_','title_db_issue_', 'name', 'region_art', 'generation_art']).agg({
                                                        'turbine_fqsn': 'nunique',
                                                        'event_id': 'count',
                                                        }).reset_index()
    issues_summary = create_summary_by_issue(vm_art_master, issue_grouped)
    issues_summary['key'] = issues_summary['region'] + '-' + issues_summary['generation']
    issues_summary = issues_summary[(issues_summary['key'].isin(['LATAM-AW-3000', 'Nordics-DELTA4000', 'SAAPAC-N155', 'Central-DELTA', 'Mediterranean-GAMMA']) ) & (issues_summary['#wtg aff.'] != 0) ]
    print("\nIssue level summary:")
    print('='*100)
    print(issues_summary.head())
    print('='*100)
    print('shape of issue level summary:', issues_summary.shape)
    issues_summary.to_csv('data/output/issue_level_summary.csv', index=False)

    # Issue and solution level KPI calculation
    issues_kpi_with_intervention_rate = cal_intervention_rate_for_issue(issues_summary, master_date_table)
    print("\nIssue level summary with intervention rate:")
    print('='*100)
    print(issues_kpi_with_intervention_rate.head())
    print('='*100)
    solution_with_ir_improvement = calculate_ir_improvement(windpulse_solution, issues_kpi_with_intervention_rate)
    solution_with_ir_improvement.to_csv('data/output/solution_with_ir_improvement.csv', index=False)
    print("\nSolution level summary with intervention rate improvement:")
    print('='*100)
    print(solution_with_ir_improvement.head())
    print('='*100)

    # add solution comments
    solution_with_comments = solution_comment(solution_with_ir_improvement)
    solution_with_comments.to_csv('data/output/solution_with_ir_improvement_and_comments.csv', index=False)
    print("\nSolution level summary with intervention rate improvement and comments:")
    print('='*100)
    print(solution_with_comments.columns)
    print('='*100)

    # Get top N issues per wind farm based on intervention rate and aggregate solution comments
    top_n_issues, farm_level_top_n_issue_sol_agg = process_top_n_issues_per_windfarm(solution_with_comments, n=5)
    farm_level_top_n_issue_sol_agg.to_csv('data/output/top_5_issues_per_site_after_v1.csv', index=False)
    print("\nTop 5 issues per wind farm after filtering v1:")
    print('='*100)
    print(farm_level_top_n_issue_sol_agg.head())

    # Create materialized view for farm KPI, issue and solution level summary
    materialized_view = materialized_view_for_farm_kpi_issue_sol(farm_level_kpi_with_comment, farm_level_top_n_issue_sol_agg)
    materialized_view.to_csv('data/output/materialized_view_data.csv', index=False)
    print("\nMaterialized view for farm KPI, issue and solution level summary:")
    print('='*100)
    print(materialized_view.head())

    # Main wtgs per issue 
    wtgs_per_issue = get_wtgs_per_issue(db_issue_fm, rp_issue_library, nc_mapping_combo, downtime_cleaned, top_n_issues)
    wtgs_per_issue.to_csv('data/output/final_farm_issue_wtg_drivers.csv', index=False)
    print("\nWTGs per issue:")
    print('='*100)
    print(wtgs_per_issue.head())

    # add priority score and priority number within region and service point
    df_with_priority = priority(farm_level_kpi_with_comment, top_n_issues, solution_with_ir_improvement)
    df_with_priority.to_csv('data/output/priority_score_data.csv', index=False)
    print("\nData with priority score and priority number within region and service point:")
    print('='*100)
    print(df_with_priority.head())
    print('Priority score calculation completed and saved to data/output/priority_score_data.csv')

if __name__ == "__main__":
    main()