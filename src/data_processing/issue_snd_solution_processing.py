import pandas as pd

def process_solutions(windpulse_solution, rp_issue_library, db_issue_fm, nc_mapping_combo):
    windpulse_sol_cleaned = aggregate_issue_solutions_separate_cols(windpulse_solution)
    issue_library_solution_cleaned = join_issues_solution(rp_issue_library, windpulse_sol_cleaned, 'id', 'issue_id')
    issue_library_solution_cleaned = issue_library_solution_cleaned.drop(['generation', 'fmcodes', 'fmdescriptions', 'issue_id'], axis=1)
    issue_solution_final = join_db_issues_solution(db_issue_fm, issue_library_solution_cleaned, 'id', 'id')
    sol_final = prepare_available_solutions_to_unquefm_level(issue_solution_final)
    issue_with_available_sol = join_ncmapping_sol_final(nc_mapping_combo, sol_final)
    uniquefm_not_null = issue_with_available_sol[issue_with_available_sol['uniquefm'].notnull()].reset_index(drop=True)
    return issue_with_available_sol, uniquefm_not_null

# --- Merge and process solution data ---
def aggregate_issue_solutions_separate_cols(df, issue_col='issue_id', sol_id_col='solution_id', 
                                            name_col='solution_name', sol_code='solution_code', 
                                            available_col='available', when_col='when_available', 
                                            ids_on_newline=True):
    for c in [sol_id_col, name_col, available_col, when_col]:
        if c not in df.columns:
            df[c] = ""
    df = df.drop_duplicates(subset=[issue_col, sol_id_col]).sort_values([issue_col, sol_id_col])
    ids_join = "\n" if ids_on_newline else ", "
    names_join = codes_join = avail_join = when_join = "\n"
    def _agg(g):
        return pd.Series({
            "solution_ids":  ids_join.join(g[sol_id_col].astype(str).tolist()),
            "solution_name": names_join.join(g[name_col].fillna("").astype(str).tolist()),
            "solution_code": codes_join.join(g[sol_code].fillna("").astype(str).tolist()),
            "available":     avail_join.join(g[available_col].fillna("").astype(str).tolist()),
            "when_available":when_join.join(g[when_col].fillna("").astype(str).tolist()),
        })
    out = (
        df.groupby(issue_col)
            .apply(_agg)
            .reset_index()
            [[issue_col, "solution_ids", "solution_name", "solution_code", "available", "when_available"]]
    )
    return out

# --- Join issue library with solution ---
def join_issues_solution(issues_df, solution_df, col1, col2):
    merged = pd.merge(
            issues_df,
            solution_df,
            how='left',
            left_on= col1,
            right_on= col2,
            suffixes=['_issue', '_sol']
        )
    return merged

def join_db_issues_solution(db_issue_fm, solution_df, col1, col2):
    merged = pd.merge(
            db_issue_fm,
            solution_df,
            how='left',
            left_on= col1,
            right_on= col2,
            suffixes=['_db_issue', '_sol']
        )
    return merged

# --- Prepare available solutions to uniquefm level ---
def prepare_available_solutions_to_unquefm_level(solution_df, uniquefm_col="uniquefm", id_col="id", title_db_col="title_db_issue", issue_col="issue", title_solution_col="title_sol", solution_ids_col="solution_ids", name_col="solution_name", sol_code="solution_code", available_col="available", when_col="when_available", ids_on_newline=True):
    if uniquefm_col not in solution_df.columns:
        raise ValueError(f"solution_df must contain '{uniquefm_col}'")
    df = solution_df.copy().dropna(subset=[uniquefm_col])
    for c in [uniquefm_col, name_col, available_col, when_col]:
        if c not in df.columns:
            df[c] = ""
    df = df.drop_duplicates(subset=[uniquefm_col, solution_ids_col]).sort_values([uniquefm_col, solution_ids_col])
    ids_join = "\n" if ids_on_newline else ", "
    title_db_issue_join = issue_join = names_join = codes_join = avail_join = when_join = "\n"
    def _agg(g):
        return pd.Series({
            "id": ids_join.join(g[id_col].astype(str).tolist()),
            "title_db_issue": title_db_issue_join.join(g[title_db_col].astype(str).tolist()),
            "issue": issue_join.join(g[issue_col].astype(str).tolist()),
            "title_sol": title_db_issue_join.join(g[title_solution_col].astype(str).tolist()),
            #"solution_ids":  ids_join.join(g[solution_ids_col].astype(str).tolist()),
            "solution_ids": ids_join.join([str(x) for x in g[solution_ids_col] if pd.notnull(x)]),
            "solution_name": names_join.join(g[name_col].fillna("").astype(str).tolist()),
            "solution_code": codes_join.join(g[sol_code].fillna("").astype(str).tolist()),
            "available":     avail_join.join(g[available_col].fillna("").astype(str).tolist()),
            "when_available":when_join.join(g[when_col].fillna("").astype(str).tolist()),
        })
    out = (
        df.groupby(uniquefm_col)
            .apply(_agg)
            .reset_index()
            [[uniquefm_col, "id", "solution_ids", "title_db_issue", "issue", "title_sol", "solution_name", "solution_code", "available", "when_available"]]
    )
    return out

# --- Join nc mapping with solution ---
def join_ncmapping_sol_final(ncmapping, sol_final):
    merged = pd.merge(
            ncmapping,
            sol_final,
            how='left',
            left_on='unique_gc',
            right_on='uniquefm',
            suffixes=['_ncmap', '_sol_final']
        )
    return merged