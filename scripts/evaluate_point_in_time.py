from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from macrofund.backtest import run_backtest
from macrofund.carry import build_carry_scores
from macrofund.config import SETTINGS
from macrofund.data import fetch_asset_prices
from macrofund.regime import expanding_regimes
from macrofund.specs import BASE_SPEC, CANDIDATE_SPECS

FEATURES = Path("data/point_in_time/alfred_macro_features.csv")
META = Path("data/point_in_time/alfred_macro_metadata.json")
OUT = Path("data/phase2/point_in_time_benchmark.json")


def _spec(name: str):
    return next(s for s in CANDIDATE_SPECS if s.name == name)


def _promotion_decision(baseline: dict, challenger: dict, benchmark: dict) -> dict:
    sharpe_lift = float(challenger.get("sharpe", 0)) - float(baseline.get("sharpe", 0))
    cagr_lift = float(challenger.get("cagr", 0)) - float(baseline.get("cagr", 0))
    drawdown_deterioration = abs(float(challenger.get("max_drawdown", 0))) - abs(float(baseline.get("max_drawdown", 0)))
    benchmark_sharpe = float(benchmark.get("sharpe", 0))
    gates = {
        "minimum_sharpe_lift": 0.10,
        "maximum_drawdown_deterioration": 0.02,
        "minimum_cagr_lift": 0.00,
        "must_beat_60_40_sharpe": True,
        "requires_complete_point_in_time_coverage": True,
    }
    checks = {
        "sharpe_lift": sharpe_lift >= gates["minimum_sharpe_lift"],
        "drawdown": drawdown_deterioration <= gates["maximum_drawdown_deterioration"],
        "cagr": cagr_lift >= gates["minimum_cagr_lift"],
        "benchmark_sharpe": float(challenger.get("sharpe", 0)) > benchmark_sharpe,
    }
    return {
        "promote": all(checks.values()),
        "gates": gates,
        "checks": checks,
        "observed": {
            "sharpe_lift": round(sharpe_lift, 4),
            "cagr_lift": round(cagr_lift, 4),
            "drawdown_deterioration": round(drawdown_deterioration, 4),
            "challenger_vs_60_40_sharpe": round(float(challenger.get("sharpe", 0)) - benchmark_sharpe, 4),
        },
    }


def main() -> None:
    if not FEATURES.exists() or not META.exists():
        raise SystemExit("ALFRED point-in-time files are missing")
    metadata = json.loads(META.read_text())
    if metadata.get("status") != "complete" or not metadata.get("coverage", {}).get("complete"):
        raise SystemExit("ALFRED point-in-time coverage is incomplete; refusing to benchmark")

    macro = pd.read_csv(FEATURES, parse_dates=["decision_date"]).set_index("decision_date").sort_index()
    macro = macro[~macro.index.duplicated(keep="last")]
    regimes = expanding_regimes(macro, SETTINGS.regime_warmup_months, SETTINGS.regime_clusters)

    daily = fetch_asset_prices(SETTINGS.assets.keys(), SETTINGS.start_date)
    monthly = daily.resample("ME").last().dropna(how="all").ffill()
    shared = macro.index.intersection(monthly.index).intersection(regimes.index).sort_values()
    macro = macro.reindex(shared)
    regimes = regimes.reindex(shared)
    monthly = monthly.reindex(shared).ffill()
    carry = build_carry_scores(macro, monthly.columns)

    baseline = run_backtest(
        monthly,
        macro,
        regimes,
        SETTINGS.target_volatility,
        SETTINGS.max_gross_exposure,
        SETTINGS.max_single_weight,
        SETTINGS.transaction_cost_bps,
        signal_spec=BASE_SPEC,
        carry_scores=None,
    )
    challenger = run_backtest(
        monthly,
        macro,
        regimes,
        SETTINGS.target_volatility,
        SETTINGS.max_gross_exposure,
        SETTINGS.max_single_weight,
        SETTINGS.transaction_cost_bps,
        signal_spec=_spec("carry_balanced"),
        carry_scores=carry,
    )
    promotion = _promotion_decision(
        baseline["strategy_metrics"],
        challenger["strategy_metrics"],
        baseline["benchmark_metrics"],
    )

    report = {
        "status": "completed",
        "data_mode": "ALFRED point-in-time core macro series with decision-date-truncated market/rates data",
        "coverage": metadata.get("coverage"),
        "months_available": int(len(shared)),
        "baseline_v1_point_in_time": baseline["strategy_metrics"],
        "carry_balanced_point_in_time": challenger["strategy_metrics"],
        "benchmark_60_40": baseline["benchmark_metrics"],
        "promotion": promotion,
        "production_action": "promote_carry_balanced" if promotion["promote"] else "retain_v1",
        "market_provider_errors": daily.attrs.get("provider_errors", {}),
        "interpretation": (
            "A challenger is eligible only if it clears every predeclared gate on point-in-time data. "
            "Failure to clear the gates keeps production on V1 regardless of revised-data performance."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
