import numpy as np
import pandas as pd
from src.macrofund.carry import build_carry_scores
from src.macrofund.specs import BASE_SPEC, SignalSpec
from src.macrofund.walkforward import run_walkforward_selection


def _synthetic_inputs(months=108):
    rng = np.random.default_rng(7)
    idx = pd.date_range("2015-01-31", periods=months, freq="ME")
    symbols = ["SPY", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "UUP"]
    shocks = rng.normal(0.006, 0.035, size=(months, len(symbols)))
    prices = pd.DataFrame(100 * np.cumprod(1 + shocks, axis=0), index=idx, columns=symbols)
    macro = pd.DataFrame({
        "liquidity": np.sin(np.arange(months) / 10),
        "risk": np.cos(np.arange(months) / 13),
        "fed_funds": np.linspace(0.5, 4.5, months),
        "treasury_10y": np.linspace(2.0, 4.8, months),
        "treasury_5y": np.linspace(1.7, 4.5, months),
    }, index=idx)
    regimes = pd.DataFrame({
        "regime": np.where(np.arange(months) % 24 < 12, "Goldilocks", "Reflation"),
        "confidence": 0.65,
    }, index=idx)
    return prices, macro, regimes


def test_rates_carry_only_populates_supported_assets():
    prices, macro, _ = _synthetic_inputs(24)
    carry = build_carry_scores(macro, prices.columns)
    assert carry["TLT"].abs().sum() > 0
    assert carry["IEF"].abs().sum() > 0
    assert carry[["SPY", "EFA", "EEM", "GLD", "DBC", "UUP"]].abs().sum().sum() == 0


def test_walkforward_selector_uses_prior_training_window():
    prices, macro, regimes = _synthetic_inputs()
    carry = build_carry_scores(macro, prices.columns)
    momentum = SignalSpec(
        name="momentum_test",
        regime_weight=0.30,
        momentum_weight=0.50,
        trend_weight=0.15,
        liquidity_weight=0.05,
    )
    result = run_walkforward_selection(
        prices,
        macro,
        regimes,
        carry_scores=carry,
        candidate_specs=(BASE_SPEC, momentum),
        training_months=36,
        reselect_months=12,
    )
    assert not result["strategy_returns"].empty
    assert result["decisions"]
    for decision in result["decisions"]:
        assert pd.Timestamp(decision["train_end"]) < pd.Timestamp(decision["decision_date"])
