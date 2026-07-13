import pandas as pd

def get_generation_mapping():
    generation_mapping ={
                        'Alpha': 'ALPHA',
                        'Beta': 'BETA',
                        'Delta': 'DELTA',
                        'Gamma': 'GAMMA',
                        'AW-3000': 'AW-3000',
                        'Delta4000': 'DELTA4000',
                        'N155': 'N155',
                        'AW-1500': 'AW-1500'
                    }
    return generation_mapping

def get_region_mapping():
    region_mapping = {
                    'Central': 'Central', 
                    'TR&ME': 'Turkey and Middle East', 
                    'Nordics': 'Nordics', 
                    'LATAM': 'LATAM', 
                    'EE': 'Eastern Europe', 
                    'MED': 'Mediterranean', 
                    'NAM': 'North America', 
                    'SAAPAC': 'SAAPAC', 
                    'UK&IE': 'UK and Ireland'}
    return region_mapping


def map_and_create_key(
    df: pd.DataFrame,
    generation_mapping: dict,
    region_mapping: dict,
    generation_col: str = 'generation',
    region_col: str = 'region',
    key_col: str = 'key'
) -> pd.DataFrame:
    """
    Maps generation and region values and creates a combined key column.

    Parameters:
        df: DataFrame to process.
        generation_mapping: Dict for generation value mapping.
        region_mapping: Dict for region value mapping.
        generation_col: Name of the generation column.
        region_col: Name of the region column.
        key_col: Name of the new key column.

    Returns:
        DataFrame with mapped columns and new key column.
    """
    df = df.copy()
    df[generation_col] = df[generation_col].replace(generation_mapping)
    df[region_col] = df[region_col].replace(region_mapping)
    df[key_col] = df[region_col].astype(str) + '-' + df[generation_col].astype(str)
    return df