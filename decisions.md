## 27 Aug 2026 - Data source

Using WRDS / OptionMetrics via UofT library access.

As I need SPX and TSX index options with a long, clean daily
history including bid, ask, volume, open interest and greeks.

Free sources either lack history or lack the Canadian side.

Registration submitted 27 Aug, awaiting institutional approval.

Fallback if denied: Deribit public API, no licensing barrier
but a much shorter history.

## 28 Aug 2026

WRDS access got approved by university portal.

Working on writing my pricer code.

## 29 Aug 2026 - Decisions

**Data source.** WRDS OptionMetrics, this is because it gives me
both SPX and TSX index option with a clean daily history which has
bid, ask, volume, open interest and greeks. (note: free data
sources do not cover the TSX side.)

**Fallback data source.** Deribit, this is becuase it gives me
crypto options with a real history through a public API. So if my
SPX, TSX is not workable, I can use a crypto pipeline to make me
project work.

**Using Forward F instead of Spot S.** Even though both the formula
will give me the same identical prices, the Forward formula has a
clear advantage ie both my rates and dividends live inside F. So in
case I have to debug, my fixes work inside one function isntead of
3. Morevoer, the log-moneyness log(K/F) puts at-the-money at zero,
the ideal coordinate required for SVI.

## 3 Sep 2026

**Vega.** Added vega as its own function. I wrote it analytically instead of letting the solver work it out numerically, because the
formula is exact and faster, and I will need vega later to filter
out quotes that carry no volatility information. Checked it against
a finite difference (h = 1e-4) and the two agreed to ten
significant figures.

**Environment note.** Installing the wrds package downgraded pandas from 3.0.5 to 2.2.3. Writing this down in case something behaves oddly later.

**WRDS access.** The Duo enrollment link from the approval email had expired. Fixed it by going to the WRDS site directly and logging in there, which restarted enrollment. Connected from Python on 3 Sep and set up a .pgpass file so I do not have to type the password every time.

**Correction to the 27 and 29 Aug entries.** I assumed OptionMetrics would give me TSX index options. It does not. I checked with db list_libraries() and UofT only subscribes to optionm (US) plus European samples. There is no IvyDB Canada.

**New design.** SPX versus EWC instead of SPX versus TSX. EWC is the iShares MSCI Canada ETF.It trades on NYSE Arca, so it is inside OptionMetrics, and I confirmed it is there with a query. Its options still give me Canadian equity exposure, so the cross-market question survives.

**Limitation of that choice.** EWC options show how US investors
price Canadian equity risk, not how Canadian investors price it.
There is no currency hedge, so some of what I measure will be CAD/USD risk rather than equity risk. Liquidity is also thinner than real TSX index options on the Montreal Exchange. I am accepting this because the alternative is having no Canadian side at all, but it needs to be stated in the write-up.

## 23 Sep 2026 - Data exploration

**Tables.** Option quotes live in optionm.opprcd<year>, split one table per year.
Underlying prices are in optionm.secprd, the zero-coupon rate curve in
optionm.zerocd, index dividend yields in optionm.idxdvd, and security
identifiers in optionm.secnmd. Only the option price tables are split by year;
the others hold full history.

**Sample period.** Coverage runs to 2025, so I am using 2024 as the sample year
rather than anything more recent.

**Security IDs.** SPX is secid 108105. EWC is 106417.

**How I resolved EWC.** Querying secnmd for ticker EWC returned three different
secids: 100334, 106417, and 127690. Two of them list IOPV in the issuer name,
which is the intraday indicative value of the ETF, a calculated index rather
than a tradeable security. I did not want to guess, so I counted option rows
per secid in opprcd2024. Only 106417 returned any (77,154 rows); the two IOPV
entries returned nothing, which is what you would expect since options are not
written on an indicative value.

**Strike prices are stored times 1000.** A 5000 strike appears as 5000000.
Divide by 1000 on read. Noting this because it is silent: nothing errors, the
prices just come out wrong.

**forward_price is supplied as a column.** I do not need to derive F from spot,
rates and dividends. This validates the 29 Aug decision to build the pricer on
the forward rather than spot; the data source hands me exactly the input my
pricer wants.

**Size gap between the two markets.** opprcd2024 holds 5,889,228 rows for SPX
against 77,154 for EWC, roughly 76 to 1. That is about 23,000 quoted SPX
contracts per trading day versus about 300 for EWC.

Two consequences I need to handle rather than discover later:

1. Liquidity filters (zero bid, wide spread, low volume) will remove a much
   larger fraction of EWC than SPX. The filter log needs a per-market breakdown,
   not a single combined count, or the attrition will be invisible.
2. SVI fits five parameters per maturity. With roughly 300 contracts a day
   spread across expiries, calls and puts, some EWC maturities may not have
   enough distinct strikes for a stable fit. I will set a minimum strike count
   per maturity and report how many maturities were dropped rather than fitting
   them anyway.

**Query discipline.** opprcd2024 has 381 million rows, so every filter has to go
into the SQL and run server-side. Pulling the table and filtering in pandas is
not an option at this size.

## 26 Sept 2026 - One-day pull, forwards, and where filtering happens

**Correction to 23 Sep.** The 23 Sep entry says forward_price is supplied as
a column. It is not: on 13 Mar 2024, 0 of 21,956 SPX rows in opprcd2024 had a
value. The pricer design is unaffected, since it takes F as an input. What
changes is where F comes from.

**One-day sample.** Pulled all columns for SPX on 13 Mar 2024, an ordinary
Wednesday: 21,956 rows, 26 columns, 53 expiry dates. Dates arrive as strings
and need parsing. Saved to data/ as Parquet so inspection does not re-query
WRDS.

**Two products under one secid.** 6,790 rows are AM-settled SPX and 15,166
are PM-settled SPXW. On five dates both expire. Their time to expiry differs,
so each (expiry, settlement) pair is treated as its own maturity, and the rule
for dates where both exist becomes a named filter.

**Vendor forward table.** Forwards live in optionm.fwdprd<year>, keyed by
expiration and amsettlement. They rise by a constant 0.564 points per calendar
day, so they are model forwards (spot grown at a smooth carry of about 4%),
not market-implied. An AM expiry gets the previous day's PM forward, i.e. it
is treated as expiring at the prior close. The table includes same-day expiries,
which need a days-to-expiry filter.

**Plan.** Primary forward is market-implied, from put-call parity.
fwdprd is the independent cross-check.

**Where filtering happens.** Refines the 23 Sep query rule. The 381M rows are
the whole of opprcd2024 across all securities. Cutting by secid and year on
the server leaves about 5.9M SPX rows and 77k EWC rows, which fit in memory.
So the coarse cut runs in SQL during the pull, and the quality filters run
locally on the Parquet, each a separate named function. Why not all in SQL:
the per-filter log would need a COUNT query per step, and every threshold
change would mean re-querying WRDS.

## 28 Sep 2026 - Forward join, pricer tests, first parity forward

**Join audit.** Matched option expiries to fwdprd on (expiry, settlement) for
13 Mar 2024: 58 of 58 keys match, none missing on either side. The 53 vs 58
gap is five dates carrying both an AM and a PM expiry.

**Pricer cleanup.** Deleted a root copy of black_scholes.py after diff showed
it byte-identical to src/. Moved the four checks into
tests/test_black_scholes.py as assert-based pytest tests: 4 passed.
Tolerances: rtol 1e-4 on the call at expiry (it is still discounted), atol on
the put (a relative tolerance is meaningless at zero), rtol 1e-8 on vega
because central-difference error is order h^2 = 1e-8, so a tighter claim would
pass only by luck. This corrects the earlier "ten significant figures" claim.

**Parity forward method.** C - P = D(F - K) is linear in K, so regress C - P
on K across strikes: slope = -D, intercept = D*F. No rate input needed. Mid
prices, bid above zero, strikes within 5% of spot.

**First result, 19 Apr 2024 PM (37 days).** 95 strike pairs. D = 0.99446,
implied r = 5.48%. Parity forward 5194.34 vs fwdprd 5186.31, a gap of 8.0
points (about 15 bp). The gap implies near-zero dividends, which is
implausible for SPX. 

Leading hypothesis: non-synchronous closes, since the
index closes at 4:00 pm and SPX options trade until 4:15 pm. 

Test: a timing
effect gives a roughly constant gap in bp across expiries, while a dividend
error grows with maturity. 

