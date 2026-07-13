# --- Master date table ---

from dataclasses import dataclass
import pandas as pd

def master_date(downtime):
    master_date = create_master_date(start='2020-01-01', end='2027-01-31', fmt='%m/%d/%Y')
    master_date['data_available'] = data_available_flag(master_date, downtime, date_col='date', start_col='start_date', normalize_to_date=True)
    return master_date

@dataclass
class DateTableBuilder:
    start: str
    end: str
    fmt: str = '%m/%d/%Y'
    def build(self) -> pd.DataFrame:
        _rng = pd.date_range(start=self.start, end=self.end, freq='D')
        return pd.DataFrame({'date': _rng.strftime(self.fmt)})
    def save_csv(self, df: pd.DataFrame, path: str) -> None:
        df.to_csv(path, index=False)

def create_master_date(start='2020-01-01', end='2027-01-31', fmt='%m/%d/%Y') -> pd.DataFrame:
    builder = DateTableBuilder(start=start, end=end, fmt=fmt)
    master_date = builder.build()
    master_date['date'] = pd.to_datetime(master_date['date'], format=fmt, errors='coerce')
    master_date['yr'] = master_date['date'].dt.year
    master_date['month'] = master_date['date'].dt.month_name()
    master_date['mo_yr_number'] = master_date['date'].dt.strftime('%Y. %m')
    iso = master_date['date'].dt.isocalendar()
    master_date['wk_yr'] = iso['year'].astype(str) + ' W' + iso['week'].astype(str).str.zfill(2)
    master_date['mo_yr_short'] = master_date['date'].dt.strftime('%b %Y')
    return master_date

def data_available_flag(dates_master, downtimes, date_col='date', start_col='start_date', normalize_to_date=True):
    dm_dates = pd.to_datetime(dates_master[date_col], errors='coerce')
    dt_starts = pd.to_datetime(downtimes[start_col], errors='coerce')
    if normalize_to_date:
        dm_dates = dm_dates.dt.normalize()
        dt_starts = dt_starts.dt.normalize()
    start_dates_set = set(dt_starts.dropna().unique())
    return dm_dates.isin(start_dates_set).astype(int)

#master_date['data_available'] = data_available_flag(master_date, downtime, date_col='date', start_col='start_date', normalize_to_date=True)
