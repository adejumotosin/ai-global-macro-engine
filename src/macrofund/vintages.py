from __future__ import annotations
import os
import time
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


def _retry_delay(response: requests.Response | None, attempt: int) -> float:
    if response is not None:
        raw = response.headers.get("Retry-After")
        if raw:
            try:
                return min(max(float(raw), 1.0), 90.0)
            except ValueError:
                pass
    return min(2.0 ** attempt, 60.0)


def fetch_series_as_of(
    series_id: str,
    as_of: str | pd.Timestamp,
    start: str = "2000-01-01",
    api_key: str | None = None,
    timeout: int = 30,
    max_attempts: int = 7,
) -> pd.Series:
    """Return observations available on ``as_of`` with safe rate-limit retries."""
    key = get_fred_api_key(api_key)
    vintage = pd.Timestamp(as_of).strftime("%Y-%m-%d")
    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "realtime_start": vintage,
        "realtime_end": vintage,
        "observation_start": start,
        "observation_end": vintage,
        "output_type": 1,
        "limit": 100000,
    }

    response: requests.Response | None = None
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                FRED_OBSERVATIONS,
                params=params,
                headers={"User-Agent": "MacroFundAI/0.2 point-in-time-research"},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            if attempt + 1 >= max_attempts:
                raise VintageDataError(
                    f"ALFRED transport failure for {series_id} as of {vintage}: {type(exc).__name__}"
                ) from None
            time.sleep(_retry_delay(None, attempt))
            continue

        if response.ok:
            break
        if response.status_code == 429 or 500 <= response.status_code < 600:
            if attempt + 1 >= max_attempts:
                raise VintageDataError(
                    f"ALFRED request failed for {series_id} as of {vintage}: HTTP {response.status_code} after {max_attempts} attempts"
                )
            time.sleep(_retry_delay(response, attempt))
            continue
        # Never propagate Response.url or the raw requests exception because
        # the v1 endpoint carries the API key in its query string.
        raise VintageDataError(
            f"ALFRED request failed for {series_id} as of {vintage}: HTTP {response.status_code}"
        )
    else:
        raise VintageDataError(f"ALFRED request exhausted retries for {series_id} as of {vintage}")

    try:
        payload = response.json()
    except ValueError:
        raise VintageDataError(
            f"ALFRED returned non-JSON data for {series_id} as of {vintage}"
        ) from None
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
