import wrds

db = wrds.Connection(wrds_username='hossainawsaf')

tables = db.list_tables(library='optionm')
print([t for t in tables if 'fwd' in t])

db.close()
