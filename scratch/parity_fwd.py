import numpy as np
import pandas as pd

df = pd.read_parquet('data/spx_2024-03-13.parquet')
fwd = pd.read_parquet('data/spx_fwd_2024-03-13.parquet')

exp, am = '2024-04-19', 0
d = df[(df.exdate == exp) & (df.am_settlement == am) & (df.best_bid > 0)].copy()
d['mid'] = (d.best_bid + d.best_offer) / 2

c = d[d.cp_flag == 'C'].set_index('strike_price')['mid']
p = d[d.cp_flag == 'P'].set_index('strike_price')['mid']
pair = pd.concat([c, p], axis=1, keys=['C', 'P']).dropna()

spot = fwd.loc[fwd.expiration == '2024-03-13', 'forwardprice'].iloc[0]
pair = pair[(pair.index > 0.95 * spot) & (pair.index < 1.05 * spot)]

K = pair.index.to_numpy(dtype=float)
y = (pair.C - pair.P).to_numpy(dtype=float)
slope, intercept = np.polyfit(K, y, 1)

D = -slope
F = intercept / D
T = (pd.Timestamp(exp) - pd.Timestamp('2024-03-13')).days / 365

print(len(pair), 'strike pairs used')
print('Discount factor D:', D, ' implied r:', -np.log(D) / T)
print('Parity forward:', F)
print(fwd[(fwd.expiration == exp) & (fwd.amsettlement == am)])
