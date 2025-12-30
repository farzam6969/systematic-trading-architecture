<div align="center">

# 🏛️ Systematic Trading Architecture

**Event-Driven, Regime-Based Quantitative Trading Framework**

*Design documentation for a production systematic trading system*

[![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Kafka](https://img.shields.io/badge/kafka-streaming-orange?style=flat-square&logo=apachekafka)](https://kafka.apache.org/)
[![Architecture](https://img.shields.io/badge/architecture-event--driven-green?style=flat-square)]()
[![License](https://img.shields.io/badge/license-proprietary-red?style=flat-square)]()

---

*This repository showcases the architecture and design philosophy behind a production systematic trading framework. Implementation code is proprietary and not included.*

</div>

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SYSTEMATIC TRADING ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│   │   Exchange   │────▶│    Kafka     │────▶│    Data      │                │
│   │   Streams    │     │   Ingestion  │     │  Providers   │                │
│   │  (L2, Trades)│     │              │     │    (14)      │                │
│   └──────────────┘     └──────────────┘     └──────┬───────┘                │
│                                                     │                        │
│                              ┌──────────────────────┼──────────────────────┐ │
│                              │                      ▼                      │ │
│                              │  ┌──────────────────────────────────────┐   │ │
│                              │  │         Feature Store                │   │ │
│                              │  │    (Real-time State Management)      │   │ │
│                              │  └──────────────────┬───────────────────┘   │ │
│                              │                      │                      │ │
│                              │                      ▼                      │ │
│   ┌──────────────┐           │  ┌──────────────────────────────────────┐   │ │
│   │   Regime     │◀──────────┼──│       Signal Generators              │   │ │
│   │   Filters    │           │  │            (7)                       │   │ │
│   │  (GARCH,     │───────────┼─▶│   Multi-Factor Confluence Engines    │   │ │
│   │   Session)   │           │  └──────────────────┬───────────────────┘   │ │
│   └──────────────┘           │                      │                      │ │
│                              │                      ▼                      │ │
│                              │  ┌──────────────────────────────────────┐   │ │
│                              │  │       Execution Engines              │   │ │
│                              │  │            (6)                       │   │ │
│                              │  │   State Persistence | Risk Mgmt     │   │ │
│                              │  └──────────────────────────────────────┘   │ │
│                              └─────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Design Principles

### 1. Event-Driven Architecture
All components communicate through **immutable event streams**, enabling:
- **Temporal decoupling** between producers and consumers
- **Deterministic replay** for backtesting and debugging  
- **Natural parallelization** of processing pipelines

### 2. Regime-Based Strategy Gating
Strategies operate only under **explicitly defined market conditions**:
- Volatility regime classification (GARCH-based)
- Liquidity state monitoring
- Session timing filters (London/NY hours)
- Hard shutdowns when regime assumptions are violated

### 3. Market Microstructure Integration
Order book–derived signals serve as **diagnostic filters**, not raw predictors:
- L2 depth analysis and liquidity withdrawal detection
- Spoofing and manipulation pattern recognition
- Flow imbalance and toxicity estimation

### 4. Failure-Conscious Design
Every component has **defined failure modes and responses**:
- Data staleness → automatic strategy pause
- Regime inversion → position protection
- Process restart → state recovery from persistence

---

## ⚙️ System Components

### Data Providers (14 Production Modules)

Real-time feature extraction from market data streams:

| Category | Modules | Output Type |
|----------|---------|-------------|
| **Flow Analysis** | CVD Events, TBSR, Volume Ratio, L2 Delta | Buyer/seller imbalance, flow direction |
| **Volatility** | GARCH Forecasting, Volatility State | Regime classification, vol forecasts |
| **Microstructure** | Hidden Liquidity, Spoofing Detection, Spread Analysis | Order book anomalies, manipulation signals |
| **Information** | VPIN Z-Score, Kalman Filter, Volume Profile | Toxicity estimation, trend filtering |
| **Confluence** | Multi-VWAP, Liquidity Vacuum | Price levels, support/resistance |

Each provider:
- Consumes from dedicated Kafka topics
- Maintains internal state with bounded memory
- Publishes structured events with millisecond timestamps
- Implements graceful degradation on upstream failures

---

### Signal Generators (7 Production Strategies)

Multi-factor confluence engines combining data provider outputs:

| Signal Type | Description | Key Confluence Sources |
|-------------|-------------|------------------------|
| **Compression Breakout** | Volatility squeeze → expansion plays | Bollinger State, CVD, TBSR, VPIN |
| **Flow Inflections** | CVD regime shift detection | CVD Events, Order Book Delta, Spread |
| **Liquidity Fulcrum** | Hidden liquidity level reversals | Hidden Liquidity, Volume Profile |
| **Volatility Stress** | VPIN cluster stress events | VPIN Z-Score, GARCH, Cascade Events |
| **Level Plays** | Order book level exploitation | L2 Delta, Liquidity Vacuum |
| **Phase Timing** | Volatility cycle phase entries | Volatility State, CVD Slope |
| **Void Swept** | Liquidity void reclamation | Liquidity Vacuum, Flow Direction |

Each generator:
- Subscribes to multiple data provider topics
- Implements deduplication and anti-replay logic
- Applies regime filters before signal emission
- Outputs structured signals with full context metadata

---

### Execution Engines (6 Production Deployments)

Production-grade execution with institutional features:

| Feature | Implementation |
|---------|----------------|
| **State Persistence** | Atomic file writes with backup; survives restarts |
| **Regime Adaptation** | GARCH volatility → dynamic SL/TP sizing |
| **Session Filtering** | London/NY hours only (08:00-21:59 UTC) |
| **Cooldown Enforcement** | Configurable inter-trade minimum spacing |
| **Multi-Factor Confirmation** | Weighted scoring: CVD, TBSR, Asymmetry, Cascade |
| **Backtest Validation** | Pre-deployment replay verification |

---

## 🔬 Research Methodology

### 4-Layer Hierarchical Signal Validation

The core philosophy: **no signal fires without passing through multiple validation layers**. Every strategy follows this sequential gating architecture:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: REGIME IDENTIFICATION                             │
│  ───────────────────────────────                            │
│  • Volatility regime (GARCH-based classification)          │
│  • Market structure (trending/ranging/transitioning)        │
│  • Session timing (London/NY only)                          │
│  • Regime mismatch → HARD STOP                              │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: DIRECTION CONFIRMATION                            │
│  ───────────────────────────────                            │
│  • CVD alignment with proposed direction                    │
│  • TBSR confirmation (taker flow support)                   │
│  • Order book microstructure context                        │
│  • Direction conflict → REJECT                              │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: SCORING & WEIGHTING SYSTEM                        │
│  ────────────────────────────────────                       │
│  • Multi-factor weighted confirmation scoring               │
│  • CVD Z-score, TBSR, Asymmetry, Cascade events            │
│  • Score = Σ(Weight × Factor) / Σ(Weight)                  │
│  • Score < consensus threshold → REJECT                     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: STRUCTURAL PARAMETERS (SL/TP)                     │
│  ──────────────────────────────────────                     │
│  • ATR-based stop loss (scaled by regime)                   │
│  • Fixed reward-risk ratio for take profit                  │
│  • Position sizing based on risk budget                     │
│  • Cooldown enforcement                                     │
└─────────────────────────────────────────────────────────────┘

Signal must pass ALL layers → Valid trade queued for execution
```

### Validation Protocol

1. **Anchored Walk-Forward**: Training window expands, test window rolls
2. **Regime Robustness**: Performance verified across volatility states
3. **K-Fold Consistency**: Profitable in each training fold individually  
4. **Out-of-Sample Holdout**: Final validation on unseen data
5. **Backtest-to-Live Parity**: Kafka replay confirms execution match


---

## 📊 Quality-Adjusted Optimization

The optimization objective is not raw returns, but **risk-adjusted quality**:

```
Objective = Base_R × Quality_Multiplier

Quality_Multiplier = 
    (1 - max_drawdown_penalty) × 
    (1 - loss_cluster_penalty) × 
    (1 - profit_factor_penalty) × 
    monthly_consistency_bonus
```

This penalizes:
- Excessive drawdown
- Clustered losses (indicates regime mismatch)
- Low profit factors
- Inconsistent monthly performance

---

## 🏗️ Backtest-to-Live Determinism

The same code path is used for historical replay and live execution:

```
┌─────────────────┐     ┌─────────────────┐
│   Backtest      │     │     Live        │
│   Engine        │     │    Engine       │
├─────────────────┤     ├─────────────────┤
│  Event Replay   │     │  Kafka Stream   │
│       │         │     │       │         │
│       ▼         │     │       ▼         │
│  ┌──────────────┴─────┴──────────────┐  │
│  │       SHARED STRATEGY CORE        │  │
│  │  (Signal Logic, Risk Management)  │  │
│  └───────────────────────────────────┘  │
│       │         │     │       │         │
│       ▼         │     │       ▼         │
│  Trade Log      │     │  Execution      │
└─────────────────┘     └─────────────────┘

Any divergence between backtest and live → AUTOMATIC ABORT
```

---

## 📁 Repository Structure

```
systematic-trading-architecture/
├── README.md                 # This file
├── ARCHITECTURE.md           # Detailed system design
├── docs/
│   ├── PHILOSOPHY.md         # Design principles
│   ├── METHODOLOGY.md        # Research approach
│   ├── COMPONENTS.md         # Component documentation
│   └── GLOSSARY.md           # Terminology
└── diagrams/
    ├── system_overview.md    # Mermaid diagrams
    └── data_flow.md          # Event topology
```

> **Note**: Implementation code is proprietary and maintained separately.

---

## 🎓 Design Philosophy

> *"The system prioritizes correctness over speed, determinism over reactivity, and capital preservation over opportunity frequency."*

Key philosophical commitments:

1. **Markets are adversarial** — Assume the worst-case scenario for fills, latency, and slippage
2. **Regimes are non-stationary** — What works today may not work tomorrow; gate everything
3. **Complexity is the enemy** — Each added component must justify its cognitive overhead
4. **Failures are features** — Design for restart, stale data, and partial outages from day one

---

## 👤 Author

**Farzam Abuzar**  
Quantitative Strategy Architect

- Systematic trading system design
- Market microstructure research
- Regime-based strategy construction
- Hierarchical optimization frameworks

---

<div align="center">

*This repository demonstrates architectural thinking and engineering discipline.*  
*For inquiries, please reach out via LinkedIn or email.*

</div>
