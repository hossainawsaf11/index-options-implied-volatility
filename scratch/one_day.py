from pathlib import Path
import wrds

db = wrds.Connection(wrds_username='hossainawsaf')

df = db.raw_sql("""
    SELECT *
    FROM optionm.opprcd2024
    WHERE secid = 108105
      AND date = '2024-03-13'
""")

df['strike_price'] = df['strike_price'] / 1000

print(df.shape)
print(df.dtypes)
print(df.head())

Path('data').mkdir(exist_ok=True)
df.to_parquet('data/spx_2024-03-13.parquet')

db.close()