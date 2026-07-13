import pandas as pd

# --- Farm KPI calculations ---
def add_fault_rate(
    summary_df: pd.DataFrame,
    downtime_data: pd.DataFrame,
    master_date: pd.DataFrame,
    group_col: str = 'name',
    event_id_col: str = 'event_id',
    wtg_total_col: str = '#wtg tot.',
    data_available_col: str = 'data_available',
    rate_col: str = 'intervention_rate',
    annual_factor: int = 365
) -> pd.DataFrame:
    """
    Adds a fault/intervention rate column to the summary DataFrame.

    Parameters:
        summary_df: DataFrame to add the rate to.
        downtime_data: DataFrame with downtime events.
        master_date: DataFrame with data availability info.
        group_col: Column to group by (e.g., wind farm name).
        event_id_col: Event identifier column in downtime_data.
        wtg_total_col: Column in summary_df for total turbines.
        data_available_col: Column in master_date for data availability.
        rate_col: Name of the new rate column.
        annual_factor: Factor to annualize the rate (default 365).

    Returns:
        summary_df with a new rate column.
    """
    event_counts = (
        downtime_data.groupby(group_col)[event_id_col]
        .nunique()
        .reset_index()
        .rename(columns={event_id_col: 'distinct_event_count'})
    )
    summary_df = summary_df.merge(event_counts, on=group_col, how='left')
    sum_data_available = master_date[data_available_col].sum()
    summary_df[rate_col] = round(
        summary_df['distinct_event_count'] / summary_df[wtg_total_col] / sum_data_available * annual_factor, 2
    )
    return summary_df

def add_mtbi(
    summary_df: pd.DataFrame,
    rate_col: str = 'intervention_rate',
    mtbi_col: str = 'MTBI(d)',
    annual_factor: int = 365
) -> pd.DataFrame:
    """
    Adds MTBI (Mean Time Between Interventions) column to the summary DataFrame.

    Parameters:
        summary_df: DataFrame to add MTBI to.
        rate_col: Column name for intervention rate.
        mtbi_col: Name of the new MTBI column.
        annual_factor: Factor to annualize MTBI (default 365).

    Returns:
        summary_df with a new MTBI column.
    """
    rate = summary_df[rate_col].replace(0, pd.NA)
    summary_df[mtbi_col] = round(annual_factor / rate, 2)
    return summary_df

def add_mttr(
    summary_df: pd.DataFrame,
    downtime_final: pd.DataFrame,
    group_col: str = 'name',
    duration_col: str = 'duration_h',
    code_col: str = 'code',
    mttr_col: str = 'MTTR(h)'
) -> pd.DataFrame:
    """
    Adds MTTR (Mean Time To Repair) column to the summary DataFrame.

    Parameters:
        summary_df: DataFrame to add MTTR to.
        downtime_final: DataFrame with downtime events.
        group_col: Column to group by (e.g., wind farm name).
        duration_col: Column for event duration.
        code_col: Column for event code.
        mttr_col: Name of the new MTTR column.

    Returns:
        summary_df with a new MTTR column.
    """
    mttr_df = (
        downtime_final
        .groupby(group_col)
        .agg(
            total_duration_h=(duration_col, 'sum'),
            code_count=(code_col, 'count')
        )
        .reset_index()
    )
    mttr_df[mttr_col] = round(mttr_df['total_duration_h'] / mttr_df['code_count'].replace(0, pd.NA), 2)
    summary_df = summary_df.merge(mttr_df[[group_col, mttr_col]], on=group_col, how='left')
    return summary_df

def percent_to_target(
    row: pd.Series,
    rate_col: str = 'intervention_rate',
    gen_col: str = 'generation',
    target_dict: dict = None
) -> float:
    """
    Calculates percent to target for a given row.

    Parameters:
        row: DataFrame row.
        rate_col: Column name for intervention rate.
        gen_col: Column name for generation.
        target_dict: Dictionary mapping generation to target value.

    Returns:
        Percent to target (float).
    """
    if target_dict is None:
        target_dict = {
            "GAMMA": 4,
            "AW-3000": 6,
            "DELTA": 5,
            "DELTA4000": 6
        }
    fault_rate = row.get(rate_col, 0)
    gen = row.get(gen_col, None)
    target = target_dict.get(gen, None)
    if fault_rate == 0 or target is None or pd.isna(fault_rate):
        return 0
    return round((fault_rate - target) / fault_rate, 4)

def percent_ir_impact(
    downtime_final: pd.DataFrame,
    farm_name: str,
    event_id_col: str = 'event_id',
    farm_region_col: str = 'region_art',
    farm_name_col: str = 'name'
) -> float:
    """
    Calculates the percent IR impact for a given farm.

    Parameters:
        downtime_final: DataFrame with downtime events.
        farm_name: Name of the farm to calculate impact for.
        event_id_col: Column name for event IDs.
        farm_region_col: Column name for farm region.
        farm_name_col: Column name for farm name.

    Returns:
        Percent IR impact (float).
    """
    farm_rows = downtime_final[downtime_final[farm_name_col] == farm_name]
    if farm_rows.empty:
        return 0
    numerator = farm_rows[event_id_col].nunique()
    farm_region = farm_rows[farm_region_col].iloc[0]
    denominator = downtime_final[downtime_final[farm_region_col] == farm_region][event_id_col].nunique()
    if denominator == 0:
        return 0
    return round(numerator / denominator, 4)

def calculate_ftfr(
    events_df: pd.DataFrame,
    farm_col: str = 'name',
    turbine_col: str = 'turbine_fqsn',
    alarm_col: str = 'grouped_code',
    start_col: str = 'start_time',
    end_col: str = 'end_time',
    threshold_days: int = 30
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates First Time Fix Rate (FTFR) for turbines and farms.

    Parameters:
        events_df: DataFrame with event data.
        farm_col: Column name for farm.
        turbine_col: Column name for turbine.
        alarm_col: Column name for alarm/grouped code.
        start_col: Column name for event start time.
        end_col: Column name for event end time.
        threshold_days: Days threshold for FTFR (default 30).

    Returns:
        Tuple of (turbine_results_df, farm_ftfr_df).
    """
    events_df[start_col] = pd.to_datetime(events_df[start_col])
    events_df[end_col] = pd.to_datetime(events_df[end_col])
    results = []
    for (farm, turbine, alarm), group in events_df.groupby([farm_col, turbine_col, alarm_col]):
        group = group.sort_values(start_col)
        ftf_count, ftfail_count = 0, 0
        for _, row in group.iterrows():
            start, end = row[start_col], row[end_col]
            prior = group[group[end_col] < start]
            future = group[group[start_col] > end]
            future_within_threshold = future[future[start_col] <= end + pd.Timedelta(days=threshold_days)]
            if prior.empty:
                if future_within_threshold.empty:
                    ftf_count += 1
                else:
                    ftfail_count += 1
        results.append({
            turbine_col: turbine,
            farm_col: farm,
            'First_Time_Fix': ftf_count,
            'First_Time_Fail': ftfail_count,
        })
    results_df = pd.DataFrame(results)
    farm_ftfr = results_df.groupby(farm_col).agg({
        'First_Time_Fix': 'sum',
        'First_Time_Fail': 'sum',
    }).reset_index()
    farm_ftfr['FTFR (%)'] = farm_ftfr['First_Time_Fix'] / (
        farm_ftfr['First_Time_Fix'] + farm_ftfr['First_Time_Fail']
    )
    return results_df, farm_ftfr

def join_FTFR_KPI_summary(
    kpi_summary: pd.DataFrame,
    ftfr: pd.DataFrame,
    kpi_farm_col: str = 'name',
    ftfr_farm_col: str = 'farm'
) -> pd.DataFrame:
    """
    Joins FTFR results to KPI summary.

    Parameters:
        kpi_summary: DataFrame with KPI summary.
        ftfr: DataFrame with FTFR results.
        kpi_farm_col: Column name in KPI summary for farm.
        ftfr_farm_col: Column name in FTFR results for farm.

    Returns:
        Merged DataFrame.
    """
    merged = pd.merge(
        kpi_summary,
        ftfr,
        how='left',
        left_on=kpi_farm_col,
        right_on=ftfr_farm_col
    )
    return merged

# --- Additional KPI calculations for issue level analysis ---
def cal_intervention_rate_for_issue(issue_kpi, master_date):
    """
    Calculates intervention rate per issue for each farm.

    The intervention rate is calculated as the number of events per turbine
    per year, annualized based on available data days.

    Parameters:
        issue_kpi (pd.DataFrame): DataFrame with issue-level KPI data.
            Required columns: 'name', 'issue', '#wtg aff.', 'event_count', '#wtg tot.'
            - name: Farm name
            - issue: Issue or problem code
            - #wtg aff.: Number of turbines affected
            - event_count: Number of events for the issue
            - #wtg tot.: Total number of turbines in the farm

        master_date (pd.DataFrame): DataFrame with data availability information.
            Required columns: 'date', 'yr', 'month', 'data_available'
            - data_available: Number of days data is available

    Returns:
        pd.DataFrame: Input issue_kpi DataFrame with added 'intervention_rate' column.
            intervention_rate is calculated as:
            (event_count / #wtg tot.) / total_data_days * 365

    Raises:
        ValueError: If required columns are missing from either DataFrame.
        ValueError: If no data available days are found in master_date.

    """
    required_kpi_cols = ['name', 'issue', '#wtg aff.', 'event_count', '#wtg tot.']
    required_date_cols = ['date', 'yr', 'month', 'data_available']
    for col in required_kpi_cols:
        if col not in issue_kpi.columns:
            raise ValueError(f"issue_kpi must contain column '{col}'")
    for col in required_date_cols:
        if col not in master_date.columns:
            raise ValueError(f"master_date must contain column '{col}'")
    total_data_days = master_date['data_available'].sum()
    if total_data_days == 0:
        raise ValueError("No data available days found in master_date")
    issue_kpi = issue_kpi.copy()
    issue_kpi['intervention_rate'] = round((issue_kpi['event_count'] / issue_kpi['#wtg tot.']) / total_data_days * 365, 2)
    return issue_kpi

# Solution level KPI calculation

def calculate_ir_improvement(solution, issue_kpi):
    """
    Calculates intervention rate improvement based on solution effectiveness.

    Merges solution effectiveness data with issue KPI data and calculates
    the potential intervention rate improvement by multiplying the effectiveness
    percentage by the current intervention rate.

    Parameters:
        solution (pd.DataFrame): DataFrame with solution effectiveness data.
            Required columns: 'issue_id', 'effectiveness'
            - issue_id: Identifier for the issue the solution addresses
            - effectiveness: Effectiveness percentage (float 0-1 or string format like '33%')

        issue_kpi (pd.DataFrame): DataFrame with issue-level KPI metrics.
            Required columns: 'id', 'intervention_rate'
            - id: Issue identifier (must match issue_id in solution)
            - intervention_rate: Current intervention rate for the issue

    Returns:
        pd.DataFrame: Merged DataFrame with additional 'ir_improvement' column.
            ir_improvement = effectiveness * intervention_rate
            Represents the potential reduction in intervention rate if solution is implemented.

    Raises:
        ValueError: If required columns are missing from either DataFrame.
        ValueError: If effectiveness column cannot be converted to float format.
    """
    required_solution_cols = ['issue_id', 'effectiveness']
    required_issue_kpi_cols = ['id', 'intervention_rate']
    for col in required_solution_cols:
        if col not in solution.columns:
            raise ValueError(f"solution must contain column '{col}'")
    for col in required_issue_kpi_cols:
        if col not in issue_kpi.columns:
            raise ValueError(f"issue_kpi must contain column '{col}'")
    if not pd.api.types.is_float_dtype(solution['effectiveness']):
        solution['effectiveness'] = solution['effectiveness'].str.strip('%').astype(float) / 100
        if not pd.api.types.is_float_dtype(solution['effectiveness']):
            raise ValueError("effectiveness column in solution must be float or percentage string format: e.g., '33%' or 0.33")
    if solution['issue_id'].dtype != issue_kpi['id'].dtype:
            issue_kpi['id'] = issue_kpi['id'].astype(solution['issue_id'].dtype)
    merged = pd.merge(
        issue_kpi,
        solution,
        how='left',
        left_on='id',
        right_on='issue_id'
    )
    merged['ir_improvement'] = round(merged['effectiveness'] * merged['intervention_rate'], 2)
    return merged