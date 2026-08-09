from __future__ import annotations
import math
import numpy as np
import pandas as pd
from .backtest import performance_metrics, run_backtest
from .specs import BASE_SPEC, CANDIDATE_SPECS, SignalSpec


def _selection_score(returns: pd.Series) -> float:
    r = pd.to_numeric(returns, errors="coerce").dropna()
    if len(r) < 24:
        return float("-inf")
    vol = float(r.std(ddof=0) * math.sqrt(12))
    if vol <= 1e-12:
        return float("-inf")
    sharpe = float(r.mean() * 12 / vol)
    eq = (1 + r).cumprod()
    mdd = float((eq / eq.cummax() - 1).min())
    return sharpe - 0.50 * abs(mdd)


def run_walkforward_selection(
    monthly_prices: pd.DataFrame,
    macro_features: pd.DataFrame,
    regimes: pd.DataFrame,
    carry_scores: pd.DataFrame | None = None,
    candidate_specs: tuple[SignalSpec, ...] = CANDIDATE_SPECS,
    target_volatility: float = 0.10,
    max_gross: float = 1.50,
    max_weight: float = 0.35,
    transaction_cost_bps: float = 10.0,
    training_months: int = 60,
    reselect_months: int = 12,
    minimum_score_edge: float = 0.10,
) -> dict:
    """Select signal specifications only from information available at the time.

    Each candidate is first converted into a fully walk-forward return stream.
    At each re-selection date the selector looks only at the trailing training
    window, compares each candidate with the incumbent BASE_SPEC, and switches
    only when the research score clears a minimum edge. The selected model is
    then frozen for the next re-selection block.
    """
    candidate_backtests: dict[str, dict] = {}
    for spec in candidate_specs:
        candidate_backtests[spec.name] = run_backtest(
            monthly_prices,
            macro_features,
            regimes,
            target_volatility=target_volatility,
            max_gross=max_gross,
            max_weight=max_weight,
            transaction_cost_bps=transaction_cost_bps,
            signal_spec=spec,
            carry_scores=carry_scores,
        )

    series = {
        name: result["strategy_returns"].rename(name)
        for name, result in candidate_backtests.items()
    }
    panel = pd.concat(series.values(), axis=1).dropna(how="all").sort_index()
    if BASE_SPEC.name not in panel.columns:
        raise ValueError("BASE_SPEC must be included in candidate_specs")
    if len(panel) <= training_months:
        raise ValueError("Insufficient history for walk-forward model selection")

    selected_returns: dict[pd.Timestamp, float] = {}
    selected_specs: dict[pd.Timestamp, str] = {}
    decisions: list[dict] = []
    dates = panel.index

    for block_start in range(training_months, len(dates), reselect_months):
        train_end_pos = block_start - 1
        train_start_pos = max(0, train_end_pos - training_months + 1)
        train = panel.iloc[train_start_pos : train_end_pos + 1]
        scores = {name: _selection_score(train[name]) for name in panel.columns}
        base_score = scores[BASE_SPEC.name]
        best_name = max(scores, key=scores.get)
        best_score = scores[best_name]
        chosen = best_name if best_score >= base_score + minimum_score_edge else BASE_SPEC.name

        apply_end = min(block_start + reselect_months, len(dates))
        for pos in range(block_start, apply_end):
            date = dates[pos]
            value = panel.at[date, chosen]
            if pd.notna(value):
                selected_returns[date] = float(value)
                selected_specs[date] = chosen

        decisions.append({
            "decision_date": dates[block_start].strftime("%Y-%m-%d"),
            "train_start": dates[train_start_pos].strftime("%Y-%m-%d"),
            "train_end": dates[train_end_pos].strftime("%Y-%m-%d"),
            "selected": chosen,
            "base_score": round(float(base_score), 4),
            "best_candidate": best_name,
            "best_score": round(float(best_score), 4),
            "candidate_scores": {k: round(float(v), 4) for k, v in scores.items()},
        })

    returns = pd.Series(selected_returns, dtype=float).sort_index()
    selection = pd.Series(selected_specs, dtype="object").sort_index()
    benchmark = candidate_backtests[BASE_SPEC.name]["benchmark_returns"].reindex(returns.index).dropna()
    aligned = returns.index.intersection(benchmark.index)
    returns = returns.reindex(aligned)
    benchmark = benchmark.reindex(aligned)

    counts = selection.value_counts().to_dict()
    return {
        "strategy_returns": returns,
        "benchmark_returns": benchmark,
        "strategy_metrics": performance_metrics(returns),
        "benchmark_metrics": performance_metrics(benchmark),
        "selection_history": selection,
        "selection_counts": {str(k): int(v) for k, v in counts.items()},
        "decisions": decisions,
        "candidate_metrics": {
            name: result["strategy_metrics"] for name, result in candidate_backtests.items()
        },
    }
