import pandas as pd
from src.data_processing.cleaners import clean_data

def process_top_n_issues_per_windfarm(solution_with_comments, n=5):
    top_n_issues = top_n_issues_per_windfarm(solution_with_comments, n=n)
    top_n_issues_aggregated = agrregate_data_to_name_id_farm(top_n_issues)
    return top_n_issues, top_n_issues_aggregated

def top_n_issues_per_windfarm(solution_with_comments, n):
    """
    Get top N issues per wind farm based on intervention rate.

    Parameters:
        solution_with_comments (pd.DataFrame): DataFrame containing solution and intervention rate data.
        n (int): Number of top issues to retrieve per wind farm.

    Returns:
        pd.DataFrame: DataFrame with top N issues per wind farm.
    """
    required_cols = ['region', 'country', 'generation', 'name', 'id', 'issue', '#wtg aff.', '#wtg tot.', 'solution_comment']
    for col in required_cols:
        if col not in solution_with_comments.columns:
            raise ValueError(f"solution_with_comments must contain column '{col}'")
    def _agg(g):
        return pd.Series({
            '#wtg aff.': g['#wtg aff.'].mean(),
            '#wtg tot.': g['#wtg tot.'].mean(),
            'intervention_rate': g['intervention_rate'].mean(),
            'solution_comments': '\n'.join(g['solution_comment'].astype(str).tolist()),
        })
    out = (
        solution_with_comments.groupby(['region', 'country', 'generation', 'name', 'id', 'issue'])
                                .apply(_agg)
                                .reset_index()
    )

    out_sorted = out.sort_values(['name', 'intervention_rate'], ascending=[True, False]).reset_index(drop=True)
    top_n_issues = out_sorted.groupby('name').head(n).reset_index(drop=True)
    return top_n_issues

def agrregate_data_to_name_id_farm(top_n_issues):
    """
    Aggregates top N issues per wind farm into a single row per farm.

    Groups the input DataFrame by region, country, generation, and name,
    and concatenates issue IDs, issue descriptions, intervention rates,
    and solution comments as newline-separated strings for each farm.

    Parameters:
        top_n_issues (pd.DataFrame): DataFrame with top N issues per wind farm.
            Required columns: 'region', 'country', 'generation', 'name', 'id', 'issue', 
                              'solution_comments', 'intervention_rate'

    Returns:
        pd.DataFrame: Aggregated DataFrame with one row per wind farm, containing
            concatenated issue IDs, issues, intervention rates, and solution comments.

    Raises:
        ValueError: If any required column is missing from the input DataFrame.
    """
    required_cols = ['region', 'country', 'generation', 'name', 'id', 'issue', 'solution_comments', 'intervention_rate']
    for col in required_cols:
        if col not in top_n_issues.columns:
            raise ValueError(f"top_n_issues must contain column '{col}'")
    def _agg(g):
        return pd.Series({
            'issue_id': '\n'.join(g['id'].astype(str).tolist()),
            'issue': '\n'.join(g['issue'].astype(str).tolist()),
            'intervention_rate': '\n'.join(g['intervention_rate'].astype(str).tolist()),
            'solution_comments': '\n'.join(g['solution_comments'].astype(str).tolist()),
        })
    out = (
        top_n_issues.groupby(['region', 'country', 'generation', 'name'])
                                .apply(_agg)
                                .reset_index()
    )
    return out 
   