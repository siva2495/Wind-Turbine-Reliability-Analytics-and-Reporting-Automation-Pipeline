import pandas as pd

def prepare_available_issue_to_unquefm_level(solution_df, uniquefm_col="uniquefm", id_col="id", title_db_col="title_db_issue", issue_col="issue", title_solution_col="title_sol", name_col="solution_name", ids_on_newline=True):
        if uniquefm_col not in solution_df.columns:
            raise ValueError(f"solution_df must contain '{uniquefm_col}'")
        df = solution_df.copy().dropna(subset=[uniquefm_col])
        for c in [uniquefm_col, name_col]:
            if c not in df.columns:
                df[c] = ""
        df = df.drop_duplicates(subset=[uniquefm_col]).sort_values([uniquefm_col])
        ids_join = "\n" if ids_on_newline else ", "
        title_db_issue_join = issue_join = names_join = codes_join = avail_join = when_join = "\n"
        def _agg(g):
            return pd.Series({
                "id": ids_join.join(g[id_col].astype(str).tolist()),
                "title_db_issue": title_db_issue_join.join(g[title_db_col].astype(str).tolist()),
                "issue": issue_join.join(g[issue_col].astype(str).tolist()),
                "title_sol": title_db_issue_join.join(g[title_solution_col].astype(str).tolist()),
            })
        out = (
            df.groupby(uniquefm_col)
              .apply(_agg)
              .reset_index()
              [[uniquefm_col, "id",  "title_db_issue", "issue"]]
        )
        return out

def create_summary_by_issue(art_master, issue_grouped):
        names = art_master['name'].unique()
        summary = []
        for name in names:
            region_vals = art_master.loc[art_master['name'] == name, 'region']
            region = region_vals.iloc[0] if not region_vals.empty else None
            country_vals = art_master.loc[art_master['name'] == name, 'country']
            country = country_vals.iloc[0] if not country_vals.empty else None
            generation_vals = art_master.loc[art_master['name'] == name, 'generation']
            generation = generation_vals.iloc[0] if not generation_vals.empty else None
            wtg_tot = art_master.loc[art_master['name'] == name, 'turbinefqsn'].nunique()
            rows = issue_grouped.loc[issue_grouped['name'] == name]
            for _, row in rows.iterrows():
                summary.append({
                    'name': name,
                    'id': row['id_'],
                    'issue': row['title_db_issue_'],
                    '#wtg aff.': row['turbine_fqsn'],
                    '#wtg tot.': wtg_tot,
                    'event_count': row['event_id'],
                    'region': region,
                    'country': country,
                    'generation': generation
                })
        return pd.DataFrame(summary)