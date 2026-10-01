import numpy as np
import pandas as pd

df = pd.read_parquet('data/spx_2024-03-13.parquet')
fwd = pd.read_parquet('data/spx_fwd_2024-03-13.parquet')
spot = fwd.loc[fwd.expiration == '2024-03-13', 'forwardprice'].iloc[0]

q = df[df.best_bid > 0].copy()
q['mid'] = (q.best_bid + q.best_offer) / 2

rows = []
for (exp, am), g in q.groupby(['exdate', 'am_settlement']):
    c = g[g.cp_flag == 'C'].set_index('strike_price')['mid']
    p = g[g.cp_flag == 'P'].set_index('strike_price')['mid']
    pair = pd.concat([c, p], axis=1, keys=['C', 'P']).dropna()
    pair = pair[(pair.index > 0.95 * spot) & (pair.index < 1.05 * spot)]
    T = (pd.Timestamp(exp) - pd.Timestamp('2024-03-13')).days / 365
    if len(pair) < 5 or T <= 0:
        continue
    K = pair.index.to_numpy(dtype=float)
    y = (pair.C - pair.P).to_numpy(dtype=float)
    slope, intercept = np.polyfit(K, y, 1)
    F = intercept / -slope
    vf = fwd.loc[(fwd.expiration == exp) & (fwd.amsettlement == am), 'forwardprice'].iloc[0]
    rows.append({'exdate': exp, 'am': am, 'T': round(T, 3), 'n': len(pair),
                 'F_parity': round(F, 2), 'F_vendor': round(vf, 2),
                 'gap_bp': round((F / vf - 1) * 1e4, 1)})

out = pd.DataFrame(rows)
print(out.to_string(index=False))