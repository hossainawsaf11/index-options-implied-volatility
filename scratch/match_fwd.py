import pandas as pd

opt = pd.read_parquet('data/spx_2024-03-13.parquet')
fwd = pd.read_parquet('data/spx_fwd_2024-03-13.parquet')

opt_keys = opt[['exdate', 'am_settlement']].drop_duplicates()
fwd_keys = fwd[['expiration', 'amsettlement']].rename(
    columns={'expiration': 'exdate', 'amsettlement': 'am_settlement'}
)

m = opt_keys.merge(fwd_keys, how='outer', indicator=True)
print(m['_merge'].value_counts())
print(m[m['_merge'] != 'both'].sort_values('exdate'))
