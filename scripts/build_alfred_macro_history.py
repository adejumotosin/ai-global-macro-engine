from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import pandas as pd
from macrofund.config import SETTINGS
from macrofund.data import fetch_macro_bundle
from macrofund.features import build_macro_features
from macrofund.vintages import (
    fetch_series_as_of,
    get_fred_api_key,
    month_end_decision_dates,
    revision_sensitive_names,
    validate_vintage_coverage,
)

OUT = Path("data/point_in_time/alfred_macro_features.csv")
META = Path("data/point_in_time/alfred_macro_metadata.json")


def _load_existing() -> pd.DataFrame:
    if not OUT.exists():
        return pd.DataFrame()
    frame = pd.read_csv(OUT, parse_dates=["decision_date"]).set_index("decision_date")
    return frame.sort_index()


def _replace_series_outer(raw: pd.DataFrame, name: str, vintage: pd.Series) -> pd.DataFrame:
    """Replace one column while preserving every date present in the vintage."""
    base = raw.drop(columns=[name], errors="ignore")
    replacement = vintage.rename(name).to_frame()
    return base.join(replacement, how="outer").sort_index()


def _force_decision_date(raw: pd.DataFrame, decision_date: pd.Timestamp) -> pd.DataFrame:
    """Extend the raw index to the calendar decision date without adding data.

    Month-end can fall on a weekend or holiday. Adding an all-NaN row forces the
    monthly resampling grid to include that calendar month while every value still
    comes from observations dated on or before the decision date.
    """
    date = pd.Timestamp(decision_date)
    if date not in raw.index:
        raw = raw.reindex(raw.index.union(pd.DatetimeIndex([date]))).sort_index()
    return raw


def _save(frame: pd.DataFrame, requested: pd.DatetimeIndex, errors: list[dict]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.sort_index().rename_axis("decision_date").reset_index().to_csv(OUT, index=False)
    coverage = validate_vintage_coverage(frame.index, requested)
    META.write_text(json.dumps({
        "status": "complete" if coverage["complete"] else "partial",
        "mode": "ALFRED point-in-time core macro series plus decision-date-truncated market/rates series",
        "revision_sensitive_series": list(revision_sensitive_names()),
        "coverage": coverage,
        "errors": errors[-50:],
        "note": "Each decision row is rebuilt using ALFRED values available on that month-end for revision-sensitive series. Calendar month-ends that fall on non-trading days are represented by an empty index row only; values still come exclusively from observations dated on or before the decision date.",
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-start", default="2010-01-31")
    parser.add_argument("--decision-end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    parser.add_argument("--sleep", type=float, default=0.08)
    parser.add_argument("--max-dates", type=int, default=0, help="0 means all dates")
    args = parser.parse_args()

    get_fred_api_key()
    requested = month_end_decision_dates(args.decision_start, args.decision_end)
    if args.max_dates > 0:
        requested = requested[: args.max_dates]
    existing = _load_existing()
    done = set(existing.index.normalize()) if not existing.empty else set()
    pending = [d for d in requested if d.normalize() not in done]
    latest_raw = fetch_macro_bundle(SETTINGS.macro_series, SETTINGS.start_date)
    rows = [] if existing.empty else [existing]
    errors: list[dict] = []

    for i, date in enumerate(pending, 1):
        try:
            raw = latest_raw.loc[:date].copy()
            for name in revision_sensitive_names():
                series_id = SETTINGS.macro_series[name]
                vintage = fetch_series_as_of(series_id, date, start=SETTINGS.start_date)
                raw = _replace_series_outer(raw, name, vintage)
                time.sleep(args.sleep)
            raw = _force_decision_date(raw.loc[:date], date)
            features = build_macro_features(raw)
            row = features.reindex([date]).copy()
            if row.empty or row.iloc[0].isna().all():
                raise RuntimeError(f"No feature row produced for {date.date()}")
            rows.append(row)
            combined = pd.concat(rows).sort_index()
            combined = combined[~combined.index.duplicated(keep="last")]
            if i % 3 == 0 or i == len(pending):
                _save(combined, requested, errors)
        except Exception as exc:
            errors.append({"decision_date": date.strftime("%Y-%m-%d"), "error": str(exc)})
            combined = pd.concat(rows).sort_index() if rows else pd.DataFrame()
            _save(combined, requested, errors)

    final = pd.concat(rows).sort_index() if rows else existing
    final = final[~final.index.duplicated(keep="last")]
    _save(final, requested, errors)
    print(META.read_text())


if __name__ == "__main__":
    main()
