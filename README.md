# AI Global Macro Hedge Fund Engine

A systematic cross-asset macro research platform that turns public macro and market data into an explainable monthly portfolio.

## Core pipeline
1. Ingest macroeconomic and cross-asset market data.
2. Build lag-aware Growth, Inflation, Liquidity and Risk factors.
3. Run expanding-window unsupervised regime clustering.
4. Translate the state into Goldilocks, Reflation, Stagflation or Deflation.
5. Combine regime priors with 3/12-month momentum, trend and liquidity.
6. Build a long/short inverse-volatility portfolio with volatility targeting, exposure caps and stress de-risking.
7. Backtest with next-period alignment and transaction costs.
8. Generate an investment-committee memo.

## Cross-asset universe
| Proxy | Exposure |
| --- | --- |
| SPY | US equities |
| EFA | Developed ex-US equities |
| EEM | Emerging-market equities |
| TLT | Long US Treasuries |
| IEF | Intermediate US Treasuries |
| GLD | Gold |
| DBC | Broad commodities |
| UUP | US dollar |

## Macro factors
- Growth: industrial production and labour-market direction.
- Inflation: CPI, inflation acceleration and oil impulse.
- Liquidity: policy-rate impulse, financial conditions and yield curve.
- Risk: VIX, dollar pressure and financial conditions.

Economic release lags are applied before features enter the model. Latest-vintage FRED data can still contain revisions, so ALFRED vintage reconstruction is the next accuracy upgrade.

## Backtest discipline
- Monthly rebalance.
- Signal formed at month-end.
- Weight applied to the next month's return.
- Transaction costs charged on turnover.
- Portfolio volatility targeted.
- 60/40 SPY/IEF benchmark.
- No historical performance number is presented as a live track record.

## API
`/health`, `/snapshot`, `/regime`, `/signals`, `/portfolio`, `/backtest`, `/memo`, `/docs`

## Data architecture
Macro data come from FRED. The MVP market adapter uses Yahoo's chart endpoint because it is convenient and keyless, but it is not institution-grade. The adapter is isolated so it can be replaced with licensed futures or total-return data.

## Phase 2 roadmap
- ALFRED vintage macro data
- multi-country growth/inflation nowcasts
- ECB, BoJ, BoE and China liquidity factors
- rates/futures carry and roll-down
- FX carry and valuation
- commodity term structure
- dynamic covariance / risk parity
- walk-forward parameter selection
- scenario stress testing

## Phase 3 roadmap
- central-bank NLP tone model
- economic surprise layer
- geopolitical risk events
- expected-shortfall constrained optimizer
- paper-trading ledger
- automated weekly macro investment committee report

## Disclaimer
Research software only. It is not investment advice, and the backtest is not a live or audited performance record.
