# Phase 2 Research Validation

## Purpose

Phase 2 tests whether the V1 global-macro engine can be improved without weakening research discipline. The main upgrades are point-in-time macro vintages, a rates-carry signal, configurable signal specifications, walk-forward model selection, and predeclared promotion gates.

Production remains on the V1 specification unless a challenger passes every promotion gate.

## Data discipline

The final point-in-time panel uses ALFRED historical vintages for revision-sensitive US macro series and decision-date-truncated market/rates inputs. The validated evaluation window is 2011-05-31 through 2026-07-31.

Coverage after rate-limit-aware retries:

- Required month-ends: 183
- Available month-ends: 183
- Missing: 0
- Coverage complete: yes

The backtest uses information at month-end t to construct positions whose returns are measured at t+1. Same-period returns are not used to generate the portfolio that earns them.

## Revised-data research screen

Before point-in-time validation, the static carry-balanced specification improved the revised-data V1 Sharpe from 0.546 to 0.619. The dynamic walk-forward selector performed materially worse, with Sharpe 0.307, so dynamic model switching was rejected.

The revised-data results were treated only as a research screen, not as a production decision.

## Point-in-time benchmark

| Metric | V1 | Carry-balanced | 60/40 |
|---|---:|---:|---:|
| CAGR | 5.50% | 6.52% | 9.44% |
| Annual volatility | 8.95% | 8.90% | 9.10% |
| Sharpe | 0.644 | 0.756 | 1.040 |
| Sortino | 0.997 | 1.200 | 1.507 |
| Maximum drawdown | -17.60% | -18.43% | -20.51% |
| Calmar | 0.313 | 0.354 | 0.460 |
| Positive months | 59.8% | 61.0% | 69.5% |
| Ending growth of $1 | 2.079 | 2.372 | 3.431 |
| Average monthly turnover | 0.653 | 0.636 | n/a |

## Promotion policy

A challenger must satisfy all of the following:

1. At least +0.10 Sharpe improvement over V1.
2. No more than 0.02 deterioration in absolute maximum drawdown.
3. Non-negative CAGR improvement.
4. Sharpe greater than the 60/40 benchmark.
5. Complete point-in-time coverage.

Carry-balanced results:

- Sharpe lift: +0.112, PASS
- CAGR lift: +0.0102, PASS
- Drawdown deterioration: +0.0083, PASS
- Complete point-in-time coverage: PASS
- Sharpe versus 60/40: -0.284, FAIL

## Decision

**Production action: RETAIN V1.**

The carry-balanced specification is a meaningful research improvement over V1, but it does not clear the predeclared 60/40 Sharpe gate. It therefore remains a research challenger and is not promoted to the live strategy.

This prevents model selection from being driven by a visually better backtest or by post-hoc threshold changes.

## Security and operational controls

The ALFRED client sanitizes request failures so the FRED API key is never propagated through request URLs or raw exception strings. HTTP 429 and transient 5xx responses use bounded retry/backoff handling. Full ALFRED history generation is a manual research workflow rather than part of ordinary CI.

## Next research frontier

The next challengers should add signals that are genuinely orthogonal to the current US-centric regime/momentum structure rather than simply reweighting the same factors:

- Eurozone, UK, Japan, and China macro state blocks
- genuine cross-country FX carry
- commodity curve / term-structure signals
- economic-surprise measures
- global liquidity and cross-border credit indicators
- improved covariance and risk-budgeting methods

Each challenger should continue to use point-in-time inputs, next-period return alignment, and explicit promotion gates.
