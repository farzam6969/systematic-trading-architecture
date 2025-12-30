# Detailed Architecture

*Technical deep-dive into system design and data flow.*

---

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph Exchange["📡 Exchange Data"]
        L2["L2 Order Book"]
        Trades["Raw Trades"]
        Klines["Klines 1m"]
    end

    subgraph Ingestion["📥 Kafka Ingestion Layer"]
        KI1["raw-trades-btcusdt"]
        KI2["depth-btcusdt"]
        KI3["kline-1m-btcusdt"]
    end

    subgraph DataProviders["⚙️ Data Providers (14)"]
        subgraph Flow["Flow Analysis"]
            CVD["CVD Events"]
            TBSR["TBSR"]
            VR["Volume Ratio"]
            L2D["L2 Delta"]
        end
        subgraph Volatility["Volatility"]
            GARCH["GARCH Forecast"]
            VS["Volatility State"]
        end
        subgraph Micro["Microstructure"]
            HL["Hidden Liquidity"]
            SD["Spoofing Detection"]
            SA["Spread Analysis"]
            LV["Liquidity Vacuum"]
        end
        subgraph Info["Information"]
            VPIN["VPIN Z-Score"]
            KF["Kalman Filter"]
            VP["Volume Profile"]
            VWAP["Multi-VWAP"]
        end
    end

    subgraph SignalGen["🎯 Signal Generators (7)"]
        CB["Compression Breakout"]
        FI["Flow Inflections"]
        LFR["Liquidity Fulcrum"]
        VSS["Volatility Stress"]
        LP["Level Plays"]
        PT["Phase Timing"]
        VOS["Void Swept"]
    end

    subgraph RegimeLayer["🛡️ Regime & Validation"]
        RF["Regime Filters"]
        SF["Session Filter"]
        CF["Confirmation"]
        CD["Cooldown"]
    end

    subgraph Execution["🚀 Execution Engines (6)"]
        EE["Validated Trade Execution"]
        SP["State Persistence"]
    end

    Exchange --> Ingestion
    Ingestion --> DataProviders
    DataProviders --> SignalGen
    SignalGen --> RegimeLayer
    RegimeLayer --> Execution
```

---

## Event Flow Architecture

### Data Provider to Signal Generator Flow

```mermaid
sequenceDiagram
    participant Exchange
    participant Kafka
    participant DP as Data Provider
    participant SG as Signal Generator
    participant EE as Execution Engine

    Exchange->>Kafka: Raw trade event
    Kafka->>DP: Consume trade
    DP->>DP: Update internal state
    DP->>DP: Check for event condition
    
    alt Event detected
        DP->>Kafka: Publish structured event
        Kafka->>SG: Consume event
        SG->>SG: Update feature state
        SG->>SG: Evaluate confluence
        
        alt Signal conditions met
            SG->>Kafka: Publish signal
            Kafka->>EE: Consume signal
            EE->>EE: Validate (session, cooldown, regime)
            
            alt Validation passed
                EE->>EE: Wait for next bar open
                EE->>Kafka: Publish execution command
                EE->>EE: Persist state
            end
        end
    end
```

---

## State Management

### Data Provider State

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Ready: State loaded
    Ready --> Processing: Message received
    Processing --> Ready: Success
    Processing --> Error: Failure
    Error --> Ready: Error handled
    Ready --> Shutdown: Signal received
    Shutdown --> [*]: Cleanup complete
```

### Execution Engine State

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> Idle: State restored
    Loading --> Idle: No state (fresh start)
    
    Idle --> Evaluating: Signal received
    Evaluating --> Idle: Rejected (validation)
    Evaluating --> Pending: Signal accepted
    
    Pending --> Executing: Next bar open
    Executing --> Cooldown: Trade executed
    
    Cooldown --> Idle: Cooldown expired
    
    Idle --> Shutdown: Graceful stop
    Pending --> Shutdown: Graceful stop
    Cooldown --> Shutdown: Graceful stop
    
    Shutdown --> [*]: State persisted
```

---

## Confirmation Flow

```mermaid
flowchart TD
    Signal["Signal Received"] --> Session{"Session Filter"}
    Session -->|"Outside London/NY"| Reject1["❌ Reject"]
    Session -->|"In Session"| Cooldown{"Cooldown Check"}
    
    Cooldown -->|"Still in cooldown"| Reject2["❌ Reject"]
    Cooldown -->|"Cooldown expired"| Stress{"Stress Filter"}
    
    Stress -->|"Outside bounds"| Reject3["❌ Reject"]
    Stress -->|"Valid stress"| Confirm{"Confirmation Score"}
    
    Confirm -->|"Score < threshold"| Reject4["❌ Reject"]
    Confirm -->|"Score ≥ threshold"| Dedup{"Deduplication"}
    
    Dedup -->|"Already processed"| Reject5["❌ Reject"]
    Dedup -->|"New signal"| Queue["✅ Queue for Execution"]
    
    Queue --> Wait["Wait for Next Bar"]
    Wait --> GARCH["Get GARCH Regime"]
    GARCH --> SL["Calculate SL (regime-based)"]
    SL --> TP["Calculate TP (fixed RR)"]
    TP --> Execute["🚀 Execute Trade"]
    Execute --> Persist["💾 Persist State"]
```

---

## GARCH Regime Adaptation

```mermaid
flowchart LR
    subgraph Input["GARCH Forecast"]
        GV["Annualized Vol %"]
    end
    
    subgraph Classification["Regime Classification"]
        GV --> Low{"< 30%"}
        GV --> Med{"30-45%"}
        GV --> High{"> 45%"}
    end
    
    subgraph Sizing["Stop Loss Sizing"]
        Low -->|"LOW_VOL"| SL1["Tighter SL"]
        Med -->|"MEDIUM_VOL"| SL2["Baseline SL"]
        High -->|"HIGH_VOL"| SL3["Wider SL"]
    end
    
    subgraph TakeProfit["Take Profit"]
        SL1 --> TP["TP = SL × RR Ratio"]
        SL2 --> TP
        SL3 --> TP
    end
```

---

## Kafka Topic Topology

```mermaid
flowchart TD
    subgraph Raw["Raw Data Topics"]
        R1["raw-trades-btcusdt"]
        R2["kline-1m-btcusdt"]
        R3["depth-btcusdt"]
    end
    
    subgraph Data["Data Provider Topics"]
        D1["event-cvd-deltaflip-btcusdt"]
        D2["data-tbsr-btcusdt"]
        D3["data-garch-volatility-forecast-5min-btcusdt"]
        D4["data-volatility-state-btcusdt"]
        D5["data-vpin-zscore-btcusdt"]
        D6["data-hidden-liquidity-btcusdt"]
        D7["..."]
    end
    
    subgraph Signal["Signal Topics"]
        S1["signal-cse-compressionbreakout-btcusdt"]
        S2["signal-cse-flowinflections-btcusdt"]
        S3["signal-uso-ald-btcusdt"]
        S4["..."]
    end
    
    subgraph Exec["Execution Topics"]
        E1["execution-commands-ald"]
        E2["execution-commands-cpbc"]
        E3["..."]
    end
    
    Raw --> Data
    Data --> Signal
    Signal --> Exec
```

---

## Failure Handling

### Data Staleness Detection

```mermaid
flowchart TD
    Msg["Message Received"] --> TS{"Check Timestamp"}
    TS -->|"Age > threshold"| Stale["⚠️ Stale Data"]
    TS -->|"Age ≤ threshold"| Fresh["✅ Fresh Data"]
    
    Stale --> Inc["Increment stale counter"]
    Inc --> Check{"Counter > max?"}
    Check -->|"Yes"| Pause["⏸️ Pause Processing"]
    Check -->|"No"| Log["Log warning"]
    Log --> Continue["Continue with caution"]
    
    Fresh --> Reset["Reset stale counter"]
    Reset --> Process["Normal processing"]
```

### State Recovery

```mermaid
flowchart TD
    Start["Engine Start"] --> Load{"Load State File"}
    
    Load -->|"Success"| Restore["Restore State"]
    Load -->|"Corrupt"| Backup{"Load Backup"}
    Load -->|"Missing"| Fresh["Start Fresh"]
    
    Backup -->|"Success"| Restore
    Backup -->|"Fail"| Fresh
    
    Restore --> Validate["Validate Cooldown"]
    Fresh --> Init["Initialize Defaults"]
    
    Validate --> Ready["Ready for Trading"]
    Init --> Ready
```

---

## Processing Pipeline

### Batch Processing with Safe Commits

```mermaid
sequenceDiagram
    participant K as Kafka
    participant P as Processor
    participant O as Output
    participant S as State

    K->>P: Consume batch (N messages)
    loop For each message
        P->>P: Process message
        alt Success
            P->>P: Track as successful
            P->>O: Produce output
        else Failure
            P->>P: Stop batch
            Note over P: Commit up to last success
        end
    end
    P->>O: Flush producer
    P->>S: Flush CSV buffer
    P->>K: Commit offset (last success + 1)
```

---

## Performance Monitoring

```mermaid
flowchart LR
    subgraph Metrics["Tracked Metrics"]
        M1["Messages/hour"]
        M2["Avg latency (ms)"]
        M3["P99 latency"]
        M4["Error count"]
        M5["Memory usage"]
        M6["Batch success rate"]
    end
    
    subgraph Alerts["Health Alerts"]
        A1["Memory > 400MB"]
        A2["Errors > threshold"]
        A3["Latency spike"]
    end
    
    subgraph Output["Outputs"]
        O1["Console logs"]
        O2["Log files"]
        O3["Health check summary"]
    end
    
    Metrics --> Alerts
    Metrics --> Output
    Alerts --> Output
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │  Exchange   │     │   Kafka     │     │  Zookeeper  │      │
│   │   Feed      │────▶│   Broker    │◀───▶│   Cluster   │      │
│   └─────────────┘     └──────┬──────┘     └─────────────┘      │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│   ┌───────────┐        ┌───────────┐        ┌───────────┐      │
│   │    DP     │        │    DP     │        │    DP     │      │
│   │  Process  │        │  Process  │        │  Process  │      │
│   │   (1-5)   │        │  (6-10)   │        │ (11-14)   │      │
│   └─────┬─────┘        └─────┬─────┘        └─────┬─────┘      │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│                  ┌───────────────────────┐                      │
│                  │   Signal Generator    │                      │
│                  │      Processes        │                      │
│                  └───────────┬───────────┘                      │
│                              │                                   │
│                              ▼                                   │
│                  ┌───────────────────────┐                      │
│                  │   Execution Engines   │                      │
│                  │  (Stateful, HA-ready) │                      │
│                  └───────────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

*This architecture prioritizes reliability, debuggability, and deterministic behavior over raw performance.*
