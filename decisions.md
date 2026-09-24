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

<<<<<<< HEAD
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

=======
Data Source - WRDS OptionMetrics, this is because it gives me both SPX and TSX index option with a clean daily history which has bid, ask, volume, open interest and greeks. (note: free data sources do not cover the TSX side.)

Fallback Data Source - Deribit, this is becuase it gives me crypto options with a real history through a public API. So if my SPX, TSX is not workable, I can use a crypto pipeline to make me project work.

Using Forward F, instead of Spot S, formula - Even though both the formula will give me the same identical prices, the Forward formula has a clear advantage ie both my rates and dividends live inside F. So in case I have to debug, my fixes work inside one function isntead of 3. Morevoer, the log-moneyness log(K/F) puts at-the-money at zero, the ideal coordinate required for SVI.
>>>>>>> fd16f9a931516d2362f726139f41518cfa0b65dd
