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

Data Source - WRDS OptionMetrics, this is because it gives me both SPX and TSX index option with a clean daily history which has bid, ask, volume, open interest and greeks. (note: free data sources do not cover the TSX side.)

Fallback Data Source - Deribit, this is becuase it gives me crypto options with a real history through a public API. So if my SPX, TSX is not workable, I can use a crypto pipeline to make me project work.

Using Forward F, instead of Spot S, formula - Even though both the formula will give me the same identical prices, the Forward formula has a clear advantage ie both my rates and dividends live inside F. So in case I have to debug, my fixes work inside one function isntead of 3. Morevoer, the log-moneyness log(K/F) puts at-the-money at zero, the ideal coordinate required for SVI.
