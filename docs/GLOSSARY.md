# Glossary

*Key terminology used throughout this architecture.*

---

## Market Microstructure

| Term | Definition |
|------|------------|
| **L2 / Level 2** | Order book data showing bid and ask prices with quantities at multiple price levels |
| **Order Book** | The list of all outstanding buy and sell orders for an asset, organized by price |
| **Bid-Ask Spread** | The difference between the best (highest) bid and best (lowest) ask price |
| **Market Depth** | The volume of orders at each price level in the order book |
| **Iceberg Order** | A large order split into smaller visible portions to hide true size |
| **Hidden Liquidity** | Orders not fully visible in the order book (icebergs, dark pools) |
| **Spoofing** | Placing orders with intent to cancel before execution to manipulate price |
| **Adverse Selection** | The risk of trading against informed participants |
| **Market Impact** | The price movement caused by executing a trade |
| **Slippage** | The difference between expected and actual execution price |

---

## Flow Analysis

| Term | Definition |
|------|------------|
| **CVD (Cumulative Volume Delta)** | Running sum of (buy volume - sell volume), indicating net buying/selling pressure |
| **Delta Flip** | A reversal in the direction of CVD, signaling potential trend change |
| **TBSR (Taker Buy-Sell Ratio)** | Ratio of market buy orders to market sell orders over a window |
| **Taker** | A trader whose order immediately matches with existing orders (market order or aggressive limit) |
| **Maker** | A trader whose order adds liquidity to the book (passive limit order) |
| **Flow Imbalance** | Asymmetry between buying and selling pressure |
| **Buyer Maker** | A trade where the buyer's order was sitting in the book (seller was the aggressor) |

---

## Volatility

| Term | Definition |
|------|------------|
| **GARCH** | Generalized Autoregressive Conditional Heteroskedasticity - a model for forecasting volatility |
| **Annualized Volatility** | Standard deviation of returns scaled to a yearly basis |
| **Volatility Regime** | Classification of current volatility state (low, medium, high) |
| **Bollinger Bands** | Price bands set at standard deviations from a moving average |
| **BBW (Bollinger Band Width)** | (Upper Band - Lower Band) / Middle Band, measuring price compression |
| **Compression** | Period of low volatility where price range narrows |
| **Expansion** | Period following compression where volatility increases |
| **Regime Transition** | The period when market moves from one volatility state to another |

---

## Information & Toxicity

| Term | Definition |
|------|------------|
| **VPIN (Volume-Synchronized PIN)** | Real-time estimate of probability of informed trading |
| **Informed Trading** | Trading based on private information not yet reflected in price |
| **Order Flow Toxicity** | The degree to which order flow contains informed trades |
| **Z-Score** | Number of standard deviations from the mean |
| **Kalman Filter** | Statistical method for estimating true value from noisy observations |

---

## Trading Strategy

| Term | Definition |
|------|------------|
| **Alpha** | Excess returns not explained by market movements; the trading edge |
| **Signal** | A trigger indicating a potential trading opportunity |
| **Confluence** | Multiple indicators aligning in the same direction |
| **Confirmation** | Secondary evidence supporting a primary trading signal |
| **Entry** | The act of opening a position |
| **Exit** | The act of closing a position |
| **Stop Loss (SL)** | A price level at which a losing position is automatically closed |
| **Take Profit (TP)** | A price level at which a winning position is automatically closed |
| **Risk-Reward Ratio (RR)** | Distance to TP divided by distance to SL |
| **Cooldown** | Minimum time required between trades |
| **R-Multiple** | Profit or loss expressed as multiples of initial risk |

---

## Backtesting & Optimization

| Term | Definition |
|------|------------|
| **Backtest** | Simulation of a strategy on historical data |
| **Walk-Forward** | Optimization technique where training and test windows move through time |
| **Anchored Walk-Forward** | Walk-forward where training window start is fixed |
| **Out-of-Sample (OOS)** | Data not used in parameter optimization |
| **In-Sample (IS)** | Data used for parameter optimization |
| **Overfitting** | Tuning parameters too closely to historical data, reducing future performance |
| **Profit Factor** | Gross profit divided by gross loss |
| **Maximum Drawdown** | Largest peak-to-trough decline in equity |
| **Win Rate** | Percentage of trades that are profitable |
| **K-Fold Validation** | Dividing data into K parts, training on K-1 and testing on 1, rotating |

---

## Event-Driven Architecture

| Term | Definition |
|------|------------|
| **Event** | An immutable record of something that happened |
| **Event Stream** | An ordered sequence of events |
| **Kafka** | Distributed event streaming platform |
| **Topic** | A category or feed name to which events are published |
| **Producer** | Component that publishes events to a topic |
| **Consumer** | Component that subscribes to and processes events from a topic |
| **Partition** | A subset of a topic for parallelization |
| **Offset** | The position of an event within a partition |
| **Consumer Group** | A set of consumers that divide topic partitions among themselves |
| **Commit** | Recording that messages up to an offset have been processed |

---

## Risk Management

| Term | Definition |
|------|------------|
| **Position Sizing** | Determining how much capital to allocate to a trade |
| **Risk per Trade** | Maximum loss acceptable on a single trade |
| **ATR (Average True Range)** | Measure of volatility based on price range |
| **Regime Gating** | Only allowing trades when market conditions match strategy assumptions |
| **Capital Preservation** | Prioritizing protection of capital over maximizing returns |

---

## System Reliability

| Term | Definition |
|------|------------|
| **State Persistence** | Saving system state to survive restarts |
| **Atomic Write** | File operation that either fully succeeds or fully fails |
| **Graceful Degradation** | System continues operating with reduced functionality during failures |
| **Hard Shutdown** | Immediate cessation of operations when critical conditions are violated |
| **Health Check** | Periodic verification that a component is functioning correctly |
| **Idempotent** | Operation that produces the same result regardless of how many times it's applied |
| **Deduplication** | Preventing duplicate processing of the same event |

---

## Session Timing

| Term | Definition |
|------|------------|
| **London Session** | 08:00 - 12:59 UTC, corresponding to London market hours |
| **New York Session** | 13:00 - 21:59 UTC, corresponding to New York market hours |
| **Asian Session** | 00:00 - 07:59 UTC, corresponding to Asian market hours |
| **Session Overlap** | Period when two major sessions are both active |

---

*This glossary provides definitions for terms as they are used within this specific architecture. Some terms may have different meanings in other contexts.*
