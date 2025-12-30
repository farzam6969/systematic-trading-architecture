# Research Methodology

*A systematic approach to strategy development and validation.*

---

## Overview

Strategy development follows a rigorous, multi-stage process designed to:
- **Minimize overfitting** through constrained optimization
- **Ensure robustness** across market regimes
- **Validate reproducibility** before capital allocation

---

## Strategy Development Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │  HYPOTHESIS  │  Market microstructure observation           │
│   │  FORMATION   │  Statistical analysis of L2 data             │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │   FEATURE    │  Build data provider to extract signal       │
│   │ ENGINEERING  │  Validate feature stability across regimes   │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │   SIGNAL     │  Multi-factor confluence design              │
│   │ CONSTRUCTION │  Parameter sensitivity analysis              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ HIERARCHICAL │  Three-layer optimization framework          │
│   │ OPTIMIZATION │  Walk-forward with anchored windows          │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │   REGIME     │  Performance across volatility states        │
│   │  ROBUSTNESS  │  Drawdown analysis during transitions        │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │  PRODUCTION  │  Backtest replay validation                  │
│   │  DEPLOYMENT  │  Gradual capital allocation                  │
│   └──────────────┘                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Hypothesis Formation

### Observation-Driven Research

Strategies originate from **observed market behavior**, not parameter mining:

1. **Microstructure Analysis**
   - Order book dynamics during specific events
   - Flow imbalance patterns preceding price moves
   - Liquidity withdrawal signatures

2. **Statistical Validation**
   - Is the pattern statistically significant?
   - Does it persist across different time periods?
   - Is the sample size sufficient?

### Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Mining indicators for correlations | Finds spurious relationships |
| Optimizing entry conditions | Overfits to historical noise |
| Chasing recent performance | Captures regime-specific behavior |

---

## Phase 2: Feature Engineering

### Data Provider Development

Each observation becomes a **dedicated data provider**:

```
Observation: "CVD reversals precede price reversals"
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              DATA PROVIDER: dp_cvd_events           │
├─────────────────────────────────────────────────────┤
│  Input:   Raw trade stream                          │
│  State:   Rolling CVD with Z-score normalization    │
│  Output:  Delta flip events with direction/magnitude│
│  Validation: Feature stability across 6+ months     │
└─────────────────────────────────────────────────────┘
```

### Feature Stability Requirements

Before a feature enters the signal generation layer:

- [ ] Consistent distribution across time periods
- [ ] No regime-dependent drift
- [ ] Bounded memory consumption
- [ ] Graceful handling of missing data

---

## Phase 3: Signal Construction

### Multi-Factor Confluence

Signals require **multiple confirmations**, not single indicators:

```
Signal Generation = 
    Primary Edge (e.g., CVD reversal)
    × Confirmation 1 (e.g., TBSR alignment)
    × Confirmation 2 (e.g., Volume spike)
    × Context Filter (e.g., VPIN not extreme)
    × Regime Gate (e.g., Volatility state)
```

### Confirmation Scoring

Each factor contributes to a weighted confirmation score:

| Factor | Weight | Threshold |
|--------|--------|-----------|
| CVD Z-Score alignment | w₁ | Direction matches signal |
| TBSR confirmation | w₂ | Above/below directional threshold |
| Cascade events | w₃ | ≥2 of 3 cascade conditions |
| Asymmetry type | w₄ | Spoofing/Withdrawal detected |

Signal fires only if: `Σ(weights × scores) / Σ(weights) ≥ min_consensus`

---

## Phase 4: Hierarchical Optimization

### Three-Layer Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTIMIZATION LAYERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAYER 1: ALPHA GENERATION                               FIXED  │
│  ─────────────────────────────────────────────────────────────  │
│  • Signal detection logic                                        │
│  • Entry conditions                                              │
│  • Confluence requirements                                       │
│                                                                  │
│  WHY FIXED: Optimizing "when to trade" leads to overfitting     │
│             to historical patterns that don't persist            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAYER 2: EXECUTION MECHANICS                            FIXED  │
│  ─────────────────────────────────────────────────────────────  │
│  • Entry: Open of next bar after signal                          │
│  • Exit: SL/TP levels or time expiry                            │
│  • Fill assumptions: Worst-case slippage                         │
│                                                                  │
│  WHY FIXED: Execution optimization doesn't translate to live    │
│             (adverse selection, market impact)                   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAYER 3: RISK EXPRESSION                            OPTIMIZED  │
│  ─────────────────────────────────────────────────────────────  │
│  • ATR multiplier for stop loss sizing                          │
│  • Reward-risk ratio for take profit                            │
│  • Cooldown period between trades                               │
│  • Volatility regime thresholds                                 │
│                                                                  │
│  WHY OPTIMIZED: Risk parameters legitimately adapt to           │
│                 volatility conditions                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Walk-Forward Validation

```
Training Window (Expanding)          Test Window (Rolling)
──────────────────────────          ──────────────────────

Round 1:  [====TRAIN====]           [TEST]
Round 2:  [======TRAIN======]             [TEST]
Round 3:  [========TRAIN========]               [TEST]
Round 4:  [==========TRAIN==========]                 [TEST]

Key Properties:
• Training window ANCHORED to start date (no peeking forward)
• Test window always follows training (no overlap)
• Parameters from each round evaluated on out-of-sample data
```

---

## Phase 5: Regime Robustness

### Multi-Regime Validation

Performance must be validated across volatility states:

| Regime | Characteristics | Validation Requirement |
|--------|-----------------|----------------------|
| **Low Vol** | Tight ranges, mean reversion | Positive expectancy |
| **Medium Vol** | Trending with pullbacks | Baseline profitability |
| **High Vol** | Expanded ranges, fast moves | Controlled drawdown |

### Transition Analysis

Critical focus on **regime transitions**:
- Performance during volatility spikes
- Drawdown behavior when regime assumptions break
- Recovery time after adverse events

---

## Phase 6: Quality-Adjusted Optimization

### Objective Function

```python
def objective(trial_results):
    base_r = trial_results.total_r_multiple
    
    # Penalties for low-quality returns
    drawdown_penalty = calculate_drawdown_penalty(max_dd)
    cluster_penalty = calculate_loss_cluster_penalty(trades)
    pf_penalty = calculate_profit_factor_penalty(pf)
    
    # Bonus for consistency
    consistency_bonus = calculate_monthly_consistency(monthly_returns)
    
    quality_multiplier = (
        (1 - drawdown_penalty) *
        (1 - cluster_penalty) *
        (1 - pf_penalty) *
        consistency_bonus
    )
    
    return base_r * quality_multiplier
```

### Penalty Details

| Metric | Threshold | Penalty |
|--------|-----------|---------|
| Max Drawdown > 15R | Linear scale | Up to 50% |
| Consecutive losses > 3 | Per cluster | 5% each |
| Profit Factor < 1.5 | Linear scale | Up to 30% |
| Monthly win rate < 60% | Per losing month | 10% each |

---

## Phase 7: Production Deployment

### Pre-Deployment Validation

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT CHECKLIST                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  □ Backtest replay matches live engine output                   │
│  □ State persistence verified (restart recovery)                │
│  □ Cooldown enforcement validated                               │
│  □ Regime filter behavior confirmed                             │
│  □ SL/TP calculations match across volatility states            │
│  □ Session filtering correct (UTC hours)                        │
│                                                                  │
│  ANY FAILURE → ABORT DEPLOYMENT                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Capital Allocation Ramp

```
Week 1-2:  Paper trading with full logging
Week 3-4:  Minimum position size (0.1x)
Week 5-8:  Quarter size (0.25x)
Week 9-12: Half size (0.5x)
Week 13+:  Full allocation (1x)

At each stage:
• Verify live matches expected performance
• Check for execution artifacts (slippage, rejects)
• Monitor regime filter behavior
```

---

## Summary

| Phase | Goal | Output |
|-------|------|--------|
| Hypothesis | Identify exploitable pattern | Research thesis |
| Feature Engineering | Extract signal from data | Data provider module |
| Signal Construction | Define entry conditions | Signal generator |
| Optimization | Tune risk parameters | Optimal configuration |
| Robustness | Validate across regimes | Regime analysis |
| Deployment | Go live safely | Production system |

---

*This methodology prioritizes robustness over raw performance, ensuring strategies survive regime changes and maintain edge over time.*
