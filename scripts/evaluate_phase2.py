from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from src.macrofund.backtest import run_backtest
from src.macrofund.carry import build_carry_scores
from src.macrofund.config import SETTINGS
from src.macrofund.data import fetch_asset_prices, fetch_macro_bundle
from src.macrofund.features import build_macro_features
from src.macrofund.regime import expanding_regimes
from src.macrofund.specs import BASE_SPEC, CANDIDATE_SPECS
from src.macrofund.walkforward import run_walkforward_selection

OUT = Path("data/phase2/revised_data_benchmark.json")


def _promotion_decision(baseline: dict, challenger: dict, benchmark: dict) -> dict:
    sharpe_lift = float(challenger.get("sharpe", 0)) - float(baseline.get("sharpe", 0))
    challenger_mdd = abs(float(challenger.get("max_drawdown", 0)))
    baseline_mdd = abs(float(baseline.get("max_drawdown", 0)))
    drawdown_deterioration = challenger_mdd - baseline_mdd
    cagr_lift = float(challenger.get("cagr", 0)) - float(baseline.get("cagr", 0))
    benchmark_sharpe = float(benchmark.get("sharpe", 0))
    gates = {
        "minimum_sharpe_lift": 0.10,
        "maximum_drawdown_deterioration": 0.02,
        "minimum_cagr_lift": 0.00,
        "must_beat_60_40_sharpe": True,
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
    macro_raw = fetch_macro_bundle(SETTINGS.macro_series, SETTINGS.start_date)
    macro = build_macro_features(macro_raw)
    regimes = expanding_regimes(macro, SETTINGS.regime_warmup_months, SETTINGS.regime_clusters)
    daily = fetch_asset_prices(SETTINGS.assets.keys(), SETTINGS.start_date)
    monthly = daily.resample("ME").last().dropna(how="all").ffill()
    shared = macro.index.intersection(monthly.index).intersection(regimes.index)
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
    static_candidates = {}
    for spec in CANDIDATE_SPECS:
        result = run_backtest(
            monthly,
            macro,
            regimes,
            SETTINGS.target_volatility,
            SETTINGS.max_gross_exposure,
            SETTINGS.max_single_weight,
            SETTINGS.transaction_cost_bps,
            signal_spec=spec,
            carry_scores=carry,
        )
        static_candidates[spec.name] = result["strategy_metrics"]

    walk = run_walkforward_selection(
        monthly,
        macro,
        regimes,
        carry_scores=carry,
        candidate_specs=CANDIDATE_SPECS,
        target_volatility=SETTINGS.target_volatility,
        max_gross=SETTINGS.max_gross_exposure,
        max_weight=SETTINGS.max_single_weight,
        transaction_cost_bps=SETTINGS.transaction_cost_bps,
        training_months=SETTINGS.walkforward_training_months,
        reselect_months=SETTINGS.walkforward_reselect_months,
    )
    promotion = _promotion_decision(
        baseline["strategy_metrics"],
        walk["strategy_metrics"],
        baseline["benchmark_metrics"],
    )

    report = {
        "status": "completed",
        "data_mode": "latest/revised FRED with publication lags",
        "warning": "This benchmark is for model research only. Final promotion requires ALFRED point-in-time validation.",
        "months_available": int(len(shared)),
        "baseline_v1": baseline["strategy_metrics"],
        "benchmark_60_40": baseline["benchmark_metrics"],
        "static_candidates": static_candidates,
        "walkforward_phase2": walk["strategy_metrics"],
        "walkforward_selection_counts": walk["selection_counts"],
        "walkforward_decisions": walk["decisions"],
        "promotion_on_revised_data": promotion,
        "production_action": "eligible_for_alfred_validation" if promotion["promote"] else "retain_v1",
        "provider_errors": {
            "macro": macro_raw.attrs.get("provider_errors", {}),
            "market": daily.attrs.get("provider_errors", {}),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
