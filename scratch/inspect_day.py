import pandas as pd

df = pd.read_parquet('data/spx_2024-03-13.parquet')

print(df['forward_price'].notna().sum(), 'of', len(df), 'rows have a forward price')
print(df['forward_price'].dropna().head())

print(df['am_settlement'].value_counts(dropna=False))
print(df['expiry_indicator'].value_counts(dropna=False))

print(df['exdate'].nunique(), 'distinct expiries')
