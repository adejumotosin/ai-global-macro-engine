from __future__ import annotations

def build_investment_memo(snapshot,signals,weights):
    conf=snapshot.get("confidence"); conf_text="n/a" if conf is None else f"{conf:.0%}"
    longs=weights[weights>0].sort_values(ascending=False).head(3); shorts=weights[weights<0].sort_values().head(3); strongest=signals.sort_values("score",ascending=False).head(3)
    fmt=lambda s:"none" if s.empty else ", ".join(f"{k} {v:+.1%}" for k,v in s.items())
    evidence="; ".join(f"{i}: score {r['score']:+.2f}, 12m momentum {r['momentum_12m']:+.1%}" for i,r in strongest.iterrows())
    macro=f"Growth {snapshot['growth']:+.2f}, inflation {snapshot['inflation']:+.2f}, liquidity {snapshot['liquidity']:+.2f}, risk {snapshot['risk']:+.2f}"
    return f"""# Global Macro Investment Committee Memo

**Regime:** {snapshot['regime']}  
**Cluster confidence:** {conf_text}  
**Macro state:** {macro}

## Positioning
Primary longs: {fmt(longs)}.  
Primary shorts: {fmt(shorts)}.

## Signal evidence
{evidence}.

## Risk interpretation
The engine combines regime, momentum, trend and liquidity signals, then scales exposure by realized volatility. A high risk-state reading reduces gross exposure. These are research signals, not investment advice.

## Thesis invalidation
A reversal in growth/inflation direction, deterioration in liquidity, or sustained trend breaks across the highest-conviction assets should reduce confidence in the current allocation.
"""
