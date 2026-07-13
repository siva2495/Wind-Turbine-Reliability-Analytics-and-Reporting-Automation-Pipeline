import pandas as pd

def farm_level_summary(art_master, downtime_final):
        names = art_master['name'].unique()
        summary = []
        for name in names:
            region = art_master.loc[art_master['name'] == name, 'region_art'].iloc[0]
            country = art_master.loc[art_master['name'] == name, 'country_art'].iloc[0]
            service_point = art_master.loc[art_master['name'] == name, 'service_point'].iloc[0]
            generation = art_master.loc[art_master['name'] == name, 'generation_art'].iloc[0]
            wtg_tot = art_master.loc[art_master['name'] == name, 'turbinefqsn'].nunique()
            wtg_aff = downtime_final.loc[downtime_final['name'] == name, 'turbine_fqsn'].nunique()
            event_count = downtime_final.loc[downtime_final['name'] == name, 'event_id'].nunique()
            summary.append({
                'name': name,
                '#wtg aff.': wtg_aff,
                '#wtg tot.': wtg_tot,
                'event_count': event_count,
                'region': region,
                'country': country,
                'service_point': service_point,
                'generation': generation
            })
        summary_df = pd.DataFrame(summary)
        summary_df['key'] = summary_df['region'] + '-' + summary_df['generation']
        return summary_df
