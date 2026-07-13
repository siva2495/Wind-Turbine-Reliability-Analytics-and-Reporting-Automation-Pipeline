import pandas as pd
import numpy as np

def add_interventionrate_status_comment(target26, kpi_data):
    """
    Merges KPI and target data, and adds a status comment based on intervention rate vs target.

    Parameters:
        target26: DataFrame with target values.
        farm_kpi_data: DataFrame with farm KPI data.
        key_col: Column to merge on.
        fault_rate_col: Column for intervention rate.
        target_col: Column for target value.
        name_col: Column for farm name.
        status_col: Name of the new status column.

    Returns:
        DataFrame with status comments.
    """
    merged = pd.merge(kpi_data, target26, left_on='key', right_on='key', how='left')
    def status_comment(row):
        try:
            fault_rate = float(row['intervention_rate']) if not pd.isnull(row['intervention_rate']) else np.nan
        except Exception:
            fault_rate = np.nan
        try:
            target_rate = float(row['target26']) if not pd.isnull(row['target26']) else np.nan
        except Exception:
            target_rate = np.nan
        if pd.isnull(fault_rate) or pd.isnull(target_rate):
            return f"The {row['name']} has missing data for fault rate or target value."
        if fault_rate > target_rate:
            return (f"The {row['name']} has fault rate of {fault_rate:.2f} which is higher than the target value {target_rate:.2f}. \n"
                    f"So check the issues associated with this farm and implement solution listed in the solution column.")
        else:
            return f"The {row['name']} has fault rate of {fault_rate:.2f} which is within the target value {target_rate:.2f}."
    merged['status'] = merged.apply(status_comment, axis=1)
    return merged

def solution_comment(sol_ir_improvement):
    """
    Generates comprehensive solution comment strings combining solution details and IR improvement.

    Creates a formatted comment for each row that includes the solution ID, name, code, and
    potential intervention rate improvement. If no solution is available, returns a default message.

    Parameters:
        sol_ir_improvement (pd.DataFrame): DataFrame with solution and IR improvement metrics.
            Required columns: 'solution_id', 'solution_name', 'solution_code', 'available', 
                            'when_available', 'ir_improvement'
            - solution_id: Identifier for the solution
            - solution_name: Name/description of the solution (can be null)
            - solution_code: Code/short identifier for the solution
            - available: Availability status of the solution
            - when_available: Timeframe for solution availability
            - ir_improvement: Potential intervention rate improvement value

    Returns:
        pd.DataFrame: Input DataFrame with additional 'solution_comment' column.
            Comment format:
            - If solution_name exists: "{id}-{solution_name}-({solution_code})-ir_improvement: {ir_improvement}."
            - If solution_name is null: "{id}-No solution."

    Raises:
        ValueError: If any required column is missing from the input DataFrame.
    """
    required_cols = ['solution_id', 'solution_name', 'solution_code', 'available', 'when_available', 'ir_improvement']
    for col in required_cols:
        if col not in sol_ir_improvement.columns:
            raise ValueError(f"sol_ir_improvement must contain column '{col}'")
    def _create_comment(row):
        if pd.isnull(row['solution_name']):
            return f"{row['id']}-No solution."
        else:
            return f"{row['id']}-{row['solution_name']}-({row['solution_code']})-ir_improvement: {row['ir_improvement']}."
    sol_ir_improvement = sol_ir_improvement.copy()
    sol_ir_improvement['solution_comment'] = sol_ir_improvement.apply(_create_comment, axis=1)
    return sol_ir_improvement