import wrds

db = wrds.Connection(wrds_username='hossainawsaf')

fwd = db.raw_sql("""
    SELECT *
    FROM optionm.fwdprd2024
    WHERE secid = 108105
      AND date = '2024-03-13'
""")

print(fwd.shape)
print(fwd.dtypes)
print(fwd.head(10))

fwd.to_parquet('data/spx_fwd_2024-03-13.parquet')

db.close()