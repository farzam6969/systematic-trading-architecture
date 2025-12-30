# System Components

*Detailed documentation of the system's modular architecture.*

---

## Component Overview

The system is organized into three primary layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                      COMPONENT LAYERS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                   DATA PROVIDERS (14)                      │ │
│   │         Real-time feature extraction from streams          │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                 SIGNAL GENERATORS (7)                      │ │
│   │         Multi-factor confluence engines                    │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                 EXECUTION ENGINES (6)                      │ │
│   │         Production trade execution                         │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Providers

Data providers transform raw market data into structured features.

### Design Pattern

Each data provider follows a consistent architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA PROVIDER TEMPLATE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   INPUT                                                         │
│   ─────                                                         │
│   • Kafka topic subscription                                    │
│   • Raw market data (trades, L2, klines)                       │
│                                                                  │
│   STATE MANAGEMENT                                              │
│   ────────────────                                              │
│   • Rolling windows with bounded memory                         │
│   • Incremental computation                                     │
│   • Graceful handling of gaps                                   │
│                                                                  │
│   OUTPUT                                                        │
│   ──────                                                        │
│   • Structured events to Kafka topic                            │
│   • CSV logging for analysis                                    │
│   • Millisecond-precision timestamps                            │
│                                                                  │
│   RELIABILITY                                                   │
│   ───────────                                                   │
│   • Manual commit after processing                              │
│   • Performance monitoring                                      │
│   • Health check logging                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Provider Catalog

#### Flow Analysis

| Provider | Input | Output | Description |
|----------|-------|--------|-------------|
| **CVD Events** | Raw trades | Delta flip events | Detects cumulative volume delta reversals using Z-score thresholds |
| **TBSR** | Raw trades | Buy/sell ratio | Computes taker buy-sell ratio over configurable windows |
| **Volume Ratio** | Raw trades | Volume metrics | Tracks volume distribution and anomalies |
| **L2 Delta** | Order book | Depth changes | Monitors bid/ask depth changes and imbalances |

#### Volatility Analysis

| Provider | Input | Output | Description |
|----------|-------|--------|-------------|
| **GARCH Volatility** | Klines | Vol forecast | GARCH(1,1) model with 5-minute forecasting horizon |
| **Volatility State** | Klines | Regime label | Bollinger-based compression/expansion classification |

#### Microstructure Analysis

| Provider | Input | Output | Description |
|----------|-------|--------|-------------|
| **Hidden Liquidity** | L2 + trades | HL events | Detects iceberg orders and hidden liquidity levels |
| **Spoofing Detection** | L2 | Spoof events | Identifies order book manipulation patterns |
| **Spread Analysis** | L2 | Spread metrics | Tracks bid-ask spread dynamics |
| **Liquidity Vacuum** | L2 | Void events | Detects liquidity withdrawals creating price gaps |

#### Information Analysis

| Provider | Input | Output | Description |
|----------|-------|--------|-------------|
| **VPIN Z-Score** | Trades | Toxicity score | Volume-synchronized probability of informed trading |
| **Kalman Filter** | Prices | Trend estimate | Filtered price level with noise reduction |
| **Volume Profile** | Trades | VP levels | Intraday volume distribution and POC |
| **Multi-VWAP** | Trades | VWAP levels | Multiple timeframe VWAP calculations |

---

## Signal Generators

Signal generators consume data provider outputs and emit trading signals.

### Design Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   SIGNAL GENERATOR TEMPLATE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   INPUTS (Multiple)                                             │
│   ────────────────                                              │
│   • Subscribe to multiple data provider topics                  │
│   • Maintain synchronized state across inputs                   │
│                                                                  │
│   CONFLUENCE LOGIC                                              │
│   ────────────────                                              │
│   • Primary condition (edge hypothesis)                         │
│   • Confirmation factors (alignment checks)                     │
│   • Context filters (regime gates)                              │
│   • Deduplication (prevent signal spam)                         │
│                                                                  │
│   OUTPUT                                                        │
│   ──────                                                        │
│   • Signal event with full context                              │
│   • Direction, price, timestamp                                 │
│   • All contributing factor values                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Generator Catalog

| Generator | Primary Edge | Confirmations | Context Filters |
|-----------|--------------|---------------|-----------------|
| **Compression Breakout** | Bollinger squeeze → expansion | CVD slope, Taker volume spike, TBSR | VPIN not extreme |
| **Flow Inflections** | CVD regime shift | Order book delta, Spread stability | Volatility state |
| **Liquidity Fulcrum** | Hidden liquidity touch | Volume profile confluence, Flow direction | Session timing |
| **Volatility Stress** | VPIN cluster events | GARCH regime, Cascade conditions | Liquidity present |
| **Level Plays** | L2 level exploitation | Delta imbalance, Vacuum proximity | Spread acceptable |
| **Phase Timing** | Volatility cycle phase | CVD slope direction, TBSR alignment | Regime match |
| **Void Swept** | Liquidity void reclaim | Flow direction, Volume confirmation | Not extreme vol |

### Signal Output Structure

```
Signal Event:
├── timestamp_ms         # Millisecond precision
├── symbol              # Trading pair
├── direction           # LONG / SHORT
├── signal_source       # Generator identifier
├── price_context       # Price at signal time
├── key_metrics         # Contributing factor values
│   ├── primary_value   # Edge metric
│   ├── confirmation_1  # First confirmation
│   ├── confirmation_2  # Second confirmation
│   └── context_score   # Aggregate quality
└── metadata           # Full diagnostic context
```

---

## Execution Engines

Execution engines translate signals into trades with risk management.

### Design Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   EXECUTION ENGINE TEMPLATE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   VALIDATION LAYER                                              │
│   ────────────────                                              │
│   • Session filter (London/NY hours)                            │
│   • Cooldown enforcement                                        │
│   • Regime gate verification                                    │
│   • Signal deduplication                                        │
│                                                                  │
│   CONFIRMATION LAYER                                            │
│   ──────────────────                                            │
│   • Multi-factor confirmation scoring                           │
│   • Minimum consensus threshold                                 │
│   • Stress metric filtering                                     │
│                                                                  │
│   RISK CALCULATION                                              │
│   ────────────────                                              │
│   • GARCH regime → SL sizing                                    │
│   • Fixed RR ratio → TP calculation                             │
│   • Position sizing based on risk budget                        │
│                                                                  │
│   STATE PERSISTENCE                                             │
│   ─────────────────                                             │
│   • Last trade time                                             │
│   • Processed signal IDs                                        │
│   • Atomic file writes                                          │
│                                                                  │
│   EXECUTION                                                     │
│   ─────────                                                     │
│   • Wait for next bar open                                      │
│   • Publish execution command                                   │
│   • Log trade details                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Engine Features

| Feature | Description |
|---------|-------------|
| **State Persistence** | Survives process restarts; atomic writes with backup |
| **Cooldown Enforcement** | Configurable minimum time between trades |
| **Session Filtering** | Only trades during London/NY overlap (08:00-21:59 UTC) |
| **GARCH Adaptation** | Stop loss sizing adapts to volatility regime |
| **Confirmation Scoring** | Weighted multi-factor validation before entry |
| **Deduplication** | Prevents re-processing of same signal events |

### Volatility Regime Adaptation

```
┌─────────────────────────────────────────────────────────────────┐
│                    GARCH REGIME MAPPING                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   GARCH Forecast         Regime          Stop Loss Sizing       │
│   ──────────────         ──────          ────────────────       │
│   < 30%                  LOW_VOL         Tighter stops          │
│   30% - 45%              MEDIUM_VOL      Baseline stops         │
│   > 45%                  HIGH_VOL        Wider stops            │
│                                                                  │
│   Take Profit = Stop Loss × Reward-Risk Ratio                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Inter-Component Communication

All components communicate via Kafka topics:

```
                        KAFKA TOPIC TOPOLOGY

Exchange Data ──────────────────────────────────────────────────────
     │
     ├──▶ raw-trades-{symbol}
     ├──▶ kline-1m-{symbol}
     └──▶ depth-{symbol}

Data Providers ─────────────────────────────────────────────────────
     │
     ├──▶ event-cvd-deltaflip-{symbol}
     ├──▶ data-tbsr-{symbol}
     ├──▶ data-garch-volatility-{symbol}
     ├──▶ data-volatility-state-{symbol}
     ├──▶ data-vpin-zscore-{symbol}
     └──▶ ... (14 total)

Signal Generators ──────────────────────────────────────────────────
     │
     ├──▶ signal-cse-compressionbreakout-{symbol}
     ├──▶ signal-cse-flowinflections-{symbol}
     └──▶ ... (7 total)

Execution Engines ──────────────────────────────────────────────────
     │
     └──▶ execution-commands-{strategy}
```

---

## Reliability Features

### Batch Processing with Manual Commits

```
┌─────────────────────────────────────────────────────────────────┐
│                  SAFE PROCESSING PATTERN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Consume batch of messages                                  │
│   2. Process each message, tracking last successful             │
│   3. On any error → stop batch, commit up to last success       │
│   4. Flush producers before commit                              │
│   5. Atomic commit to Kafka                                     │
│                                                                  │
│   Result: No data loss, no duplicate processing                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Monitoring

Each component tracks:
- Messages processed per hour
- Processing latency (avg, p99)
- Error counts by type
- Memory usage
- Batch success rate

### Health Checks

Periodic health check logs include:
- Uptime
- Message throughput
- Error summary
- Memory pressure warnings

---

*This modular architecture enables independent development, testing, and deployment of each component while maintaining system-wide coherence.*
