from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Settings:
    start_date: str = "2007-01-01"
    target_volatility: float = 0.10
    max_gross_exposure: float = 1.50
    max_single_weight: float = 0.35
    transaction_cost_bps: float = 10.0
    cache_ttl_seconds: int = 3600
    regime_warmup_months: int = 60
    regime_clusters: int = 4
    macro_series: dict[str, str] = field(default_factory=lambda: {
        "cpi": "CPIAUCSL", "industrial_production": "INDPRO", "unemployment": "UNRATE",
        "fed_funds": "FEDFUNDS", "yield_curve": "T10Y2Y", "financial_conditions": "NFCI",
        "usd_trade_weighted": "DTWEXBGS", "oil": "DCOILWTICO", "vix": "VIXCLS",
        "treasury_10y": "DGS10", "treasury_2y": "DGS2",
    })
    assets: dict[str, str] = field(default_factory=lambda: {
        "SPY": "US equities", "EFA": "Developed ex-US equities", "EEM": "Emerging-market equities",
        "TLT": "Long US Treasuries", "IEF": "Intermediate US Treasuries", "GLD": "Gold",
        "DBC": "Broad commodities", "UUP": "US dollar",
    })
SETTINGS = Settings()
