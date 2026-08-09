from __future__ import annotations
import os
from typing import Iterable
import pandas as pd
import requests

FRED_OBSERVATIONS = "https://api.stlouisfed.org/fred/series/observations"


class VintageDataError(RuntimeError):
    pass


def get_fred_api_key(explicit: str | None = None) -> str:
    key = explicit or os.getenv("FRED_API_KEY", "")
    if not key:
        raise VintageDataError(
            "FRED_API_KEY is required for ALFRED point-in-time observations. "
            "The live engine may use keyless latest-vintage FRED data, but the "
            "historical vintage backfill must not silently fall back."
        )
    return key


def fetch_series_as_of(
    series_id: str,
    as_of: str | pd.Timestamp,
    start: str = "2000-01-01",
    api_key: str | None = None,
    timeout: int = 30,
) -> pd.Series:
    """Return the observations that were actually available on ``as_of``."""
    key = get_fred_api_key(api_key)
    vintage = pd.Timestamp(as_of).strftime("%Y-%m-%d")
    response = requests.get(
        FRED_OBSERVATIONS,
        params={
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
            "realtime_start": vintage,
            "realtime_end": vintage,
            "observation_start": start,
            "observation_end": vintage,
            "output_type": 1,
            "limit": 100000,
        },
        headers={"User-Agent": "MacroFundAI/0.2 point-in-time-research"},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    observations = payload.get("observations") or []
    if not observations:
        raise VintageDataError(f"No ALFRED observations for {series_id} as of {vintage}")
    frame = pd.DataFrame(observations)
    dates = pd.to_datetime(frame.get("date"), errors="coerce")
    values = pd.to_numeric(frame.get("value"), errors="coerce")
    series = pd.Series(values.to_numpy(), index=dates, name=series_id).dropna().sort_index()
    series = series[~series.index.isna()]
    if series.empty:
        raise VintageDataError(f"No numeric ALFRED observations for {series_id} as of {vintage}")
    return series


def month_end_decision_dates(start: str, end: str | pd.Timestamp) -> pd.DatetimeIndex:
    return pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="ME")


def revision_sensitive_names() -> tuple[str, ...]:
    return (
        "cpi",
        "industrial_production",
        "unemployment",
        "financial_conditions",
        "fed_funds",
    )


def validate_vintage_coverage(
    available_dates: Iterable[str | pd.Timestamp],
    required_dates: Iterable[str | pd.Timestamp],
) -> dict:
    available = {pd.Timestamp(d).normalize() for d in available_dates}
    required = {pd.Timestamp(d).normalize() for d in required_dates}
    missing = sorted(required - available)
    return {
        "required": len(required),
        "available": len(required & available),
        "missing": [d.strftime("%Y-%m-%d") for d in missing],
        "complete": not missing,
    }
