from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SignalSpec:
    name: str = "balanced"
    regime_weight: float = 0.50
    momentum_weight: float = 0.30
    trend_weight: float = 0.15
    liquidity_weight: float = 0.05
    carry_weight: float = 0.00
    long_threshold: float = 0.35
    short_threshold: float = -0.35

    def normalized(self) -> "SignalSpec":
        total = (
            abs(self.regime_weight)
            + abs(self.momentum_weight)
            + abs(self.trend_weight)
            + abs(self.liquidity_weight)
            + abs(self.carry_weight)
        )
        if total <= 0:
            return self
        return SignalSpec(
            name=self.name,
            regime_weight=self.regime_weight / total,
            momentum_weight=self.momentum_weight / total,
            trend_weight=self.trend_weight / total,
            liquidity_weight=self.liquidity_weight / total,
            carry_weight=self.carry_weight / total,
            long_threshold=self.long_threshold,
            short_threshold=self.short_threshold,
        )


BASE_SPEC = SignalSpec()
CANDIDATE_SPECS = (
    BASE_SPEC,
    SignalSpec(
        name="momentum_heavy",
        regime_weight=0.35,
        momentum_weight=0.45,
        trend_weight=0.15,
        liquidity_weight=0.05,
    ),
    SignalSpec(
        name="regime_heavy",
        regime_weight=0.65,
        momentum_weight=0.20,
        trend_weight=0.10,
        liquidity_weight=0.05,
    ),
    SignalSpec(
        name="carry_balanced",
        regime_weight=0.40,
        momentum_weight=0.25,
        trend_weight=0.10,
        liquidity_weight=0.05,
        carry_weight=0.20,
        long_threshold=0.30,
        short_threshold=-0.30,
    ),
)
