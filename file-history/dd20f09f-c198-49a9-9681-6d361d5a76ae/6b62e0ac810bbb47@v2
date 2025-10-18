# Business Logic Diagram Proposals

Survey and proposals for Mermaid diagrams to visualize business logic (not technical implementation).

## Proposed Diagram Types

### Option 1: High-Level Business Flow (Recommended First)

**Purpose**: Show the complete business journey from raw data to insights

```mermaid
graph LR
    A[Raw Tick Data] --> B[Data Validation]
    B --> C[Range Bar Generation]
    C --> D[Statistical Analysis]
    D --> E[Trading Insights]

    style A fill:#e1f5ff
    style E fill:#fff4e1
```

**What This Shows**:
- 5 major business stages
- Data transformation flow
- End-to-end value chain

---

### Option 2: Business Use Cases by User Type

**Purpose**: Who uses this system for what business objectives?

```mermaid
graph TD
    subgraph "Researchers"
        R1[Historical Backtesting]
        R2[Multi-Symbol Comparison]
        R3[Threshold Optimization]
    end

    subgraph "Live Traders"
        L1[Real-Time Bar Generation]
        L2[Market Stress Detection]
        L3[Entry/Exit Signals]
    end

    subgraph "Portfolio Managers"
        P1[Cross-Market Analysis]
        P2[Liquidity Assessment]
        P3[Volatility Forecasting]
    end

    System[Range Bar System]

    R1 --> System
    R2 --> System
    R3 --> System
    L1 --> System
    L2 --> System
    L3 --> System
    P1 --> System
    P2 --> System
    P3 --> System

    style System fill:#ffd700
```

**What This Shows**:
- 3 user personas
- 9 distinct business use cases
- How different users interact with the system

---

### Option 3: Data Acquisition Decision Tree

**Purpose**: Business logic for choosing data sources and markets

```mermaid
graph TD
    Start[Need Market Data] --> Q1{Asset Class?}

    Q1 -->|Cryptocurrency| Q2{Which Market?}
    Q1 -->|Forex| Exness[Exness EURUSD_Raw_Spread]

    Q2 -->|Spot Trading| Binance_Spot[Binance Spot]
    Q2 -->|Futures USDT| Binance_UM[Binance UM Futures]
    Q2 -->|Futures Coin| Binance_CM[Binance CM Futures]

    Binance_Spot --> Validate[Data Validation]
    Binance_UM --> Validate
    Binance_CM --> Validate
    Exness --> Validate

    Validate --> Process[Range Bar Processing]

    style Start fill:#e1f5ff
    style Process fill:#fff4e1
```

**What This Shows**:
- Business decision: asset class selection
- Available data sources per asset class
- Unified validation regardless of source

---

### Option 4: Processing Mode Decision Logic

**Purpose**: Business logic for choosing streaming vs batch mode

```mermaid
graph TD
    Start[Need Range Bars] --> Q1{Use Case?}

    Q1 -->|Live Trading| Q2{Memory Constraints?}
    Q1 -->|Historical Analysis| Q3{Dataset Size?}

    Q2 -->|Tight Memory| Streaming[Streaming Mode]
    Q2 -->|Adequate Memory| Streaming

    Q3 -->|>10GB Data| Streaming2[Streaming Mode]
    Q3 -->|<10GB Data| Q4{Need Statistics?}

    Q4 -->|Yes| Batch[Batch Mode]
    Q4 -->|No| Simple[Simple Processing]

    Streaming --> Output[Range Bars]
    Streaming2 --> Output
    Batch --> Stats[Statistics + Bars]
    Simple --> Output

    style Start fill:#e1f5ff
    style Output fill:#fff4e1
    style Stats fill:#e1ffe1
```

**What This Shows**:
- Business decision factors (use case, memory, size, needs)
- 3 processing modes (streaming, batch, simple)
- Different outputs per mode

---

### Option 5: Threshold Selection Guide

**Purpose**: Business logic for choosing optimal threshold based on trading strategy

```mermaid
graph TD
    Start[Choose Threshold] --> Q1{Trading Style?}

    Q1 -->|High-Frequency| HFT[0.1-0.5 bps]
    Q1 -->|Intraday| Intra[0.5-5 bps]
    Q1 -->|Swing Trading| Swing[5-25 bps]
    Q1 -->|Position Trading| Position[25-100 bps]

    HFT --> Freq1[1000-5000 bars/day]
    Intra --> Freq2[200-1000 bars/day]
    Swing --> Freq3[50-200 bars/day]
    Position --> Freq4[10-50 bars/day]

    Freq1 --> Strategy[Execute Strategy]
    Freq2 --> Strategy
    Freq3 --> Strategy
    Freq4 --> Strategy

    style Start fill:#e1f5ff
    style Strategy fill:#fff4e1
```

**What This Shows**:
- 4 trading styles
- Threshold ranges per style
- Expected bar frequency (business outcome)

---

### Option 6: Complete Business Workflow (Detailed)

**Purpose**: Comprehensive end-to-end business process with all decision points

```mermaid
graph TD
    Start[Business Need: Trading Insights] --> Discover[1. Discover Symbols]

    Discover --> Validate[2. Validate Data Structure]
    Validate --> Fetch[3. Fetch Historical Data]

    Fetch --> Decision1{Processing Mode?}
    Decision1 -->|Real-Time| Stream[Streaming Processor]
    Decision1 -->|Historical| Batch[Batch Processor]

    Stream --> Bars1[Range Bars Generated]
    Batch --> Bars2[Range Bars + Statistics]

    Bars1 --> Decision2{Need Analysis?}
    Bars2 --> Analysis[Statistical Analysis]

    Decision2 -->|Yes| Analysis
    Decision2 -->|No| Export1[Export Bars]

    Analysis --> Insights[Trading Insights]
    Insights --> Export2[Export Results]

    Export1 --> End[Business Value Delivered]
    Export2 --> End

    style Start fill:#e1f5ff
    style End fill:#ffd700
```

**What This Shows**:
- 7 business stages
- 2 major decision points
- Multiple paths to business value

---

### Option 7: Error Recovery Business Logic

**Purpose**: Business decisions when things go wrong

```mermaid
graph TD
    Process[Processing Data] --> Error{Error?}

    Error -->|No Error| Success[Continue]
    Error -->|Network Timeout| Retry[Retry 3x with Backoff]
    Error -->|Disk Full| Alert1[Alert: Free Space]
    Error -->|Invalid Data| Skip[Skip Symbol + Log]
    Error -->|OOM| Reduce[Reduce Batch Size]
    Error -->|Breach Violation| Stop[STOP: Algorithm Bug]

    Retry --> Retry_Result{Success?}
    Retry_Result -->|Yes| Success
    Retry_Result -->|No| Skip

    Alert1 --> Manual[Manual Intervention]
    Skip --> Continue[Continue Next Symbol]
    Reduce --> Restart[Restart with Smaller Batch]
    Stop --> Fix[Fix Required]

    Success --> Done[Processing Complete]
    Continue --> Done
    Restart --> Process

    style Process fill:#e1f5ff
    style Done fill:#e1ffe1
    style Stop fill:#ffe1e1
```

**What This Shows**:
- 6 failure scenarios
- Business-appropriate responses per scenario
- Recovery paths vs. stop conditions

---

### Option 8: Cross-Market Comparison Workflow

**Purpose**: Business logic for comparing liquidity and volatility across markets

```mermaid
graph TD
    Start[Compare Markets] --> Select[Select Symbol e.g. BTC]

    Select --> Fetch1[Fetch Spot Data]
    Select --> Fetch2[Fetch UM Futures Data]
    Select --> Fetch3[Fetch CM Futures Data]

    Fetch1 --> Process1[Generate Bars: Spot]
    Fetch2 --> Process2[Generate Bars: UM]
    Fetch3 --> Process3[Generate Bars: CM]

    Process1 --> Stats1[Calculate: Volume, Duration, Count]
    Process2 --> Stats2[Calculate: Volume, Duration, Count]
    Process3 --> Stats3[Calculate: Volume, Duration, Count]

    Stats1 --> Compare[Compare Metrics]
    Stats2 --> Compare
    Stats3 --> Compare

    Compare --> Insight1[Liquidity Ranking]
    Compare --> Insight2[Volatility Patterns]
    Compare --> Insight3[Optimal Market Selection]

    style Start fill:#e1f5ff
    style Insight1 fill:#fff4e1
    style Insight2 fill:#fff4e1
    style Insight3 fill:#ffd700
```

**What This Shows**:
- Parallel data fetching (business efficiency)
- Unified processing across markets
- 3 business insights derived

---

### Option 9: Algorithm Business Rules (Non-Lookahead)

**Purpose**: Core business logic guarantees (what makes this system trustworthy)

```mermaid
graph TD
    Tick[New Tick Arrives] --> Rule1{Breach Check}

    Rule1 -->|No Breach| Update[Update Current Bar]
    Rule1 -->|Breach Detected| Close[Close Current Bar]

    Update --> Wait[Wait for Next Tick]
    Close --> Include[Include Breach Tick in Bar]

    Include --> Output[Output Completed Bar]
    Output --> NewBar[Start New Bar with Next Tick]

    NewBar --> Wait
    Wait --> Tick

    subgraph "Business Guarantees"
        G1[No Future Information Used]
        G2[Fixed Thresholds from Open]
        G3[Breach Tick Always Included]
        G4[Deterministic Output]
    end

    style Tick fill:#e1f5ff
    style Output fill:#ffd700
```

**What This Shows**:
- 4 business guarantees (trust factors)
- Decision logic: breach vs. no breach
- State machine: update → close → new

---

## Recommended Diagram Combinations

### For New Users (Business Overview)
1. **Option 1**: High-Level Business Flow (see the big picture)
2. **Option 2**: Business Use Cases (understand who uses it for what)
3. **Option 5**: Threshold Selection Guide (practical decision making)

### For Researchers (Data Analysis Focus)
1. **Option 3**: Data Acquisition Decision Tree (choose data sources)
2. **Option 4**: Processing Mode Decision Logic (optimize for your use case)
3. **Option 8**: Cross-Market Comparison Workflow (analytical workflows)

### For Live Traders (Production Focus)
1. **Option 9**: Algorithm Business Rules (understand guarantees)
2. **Option 4**: Processing Mode Decision Logic (real-time considerations)
3. **Option 7**: Error Recovery Business Logic (handle failures)

### For Portfolio Managers (Strategic Focus)
1. **Option 8**: Cross-Market Comparison Workflow (market analysis)
2. **Option 6**: Complete Business Workflow (end-to-end process)
3. **Option 2**: Business Use Cases (strategic applications)

---

## Implementation Recommendation

**Proposed Location**: `docs/diagrams/business-logic.md`

**Structure**:
```
docs/diagrams/
├── business-logic.md          # All business logic diagrams
├── data-flow.md               # Data transformation focus
├── decision-trees.md          # All decision logic
└── workflows.md               # Complete workflows
```

**Or Single File**: `docs/BUSINESS_LOGIC.md` (simpler, all diagrams in one place)

---

## Next Steps

**Please indicate your preference**:

1. **Which diagram types** are most valuable for your understanding? (Pick 3-5)
2. **Organization preference**: Single file or multiple files?
3. **Additional business logic** you want visualized?
4. **Diagram style preference**:
   - More colors/styling?
   - More detailed?
   - Simpler/cleaner?

Once you confirm, I'll create the full documentation with your selected diagrams in proper Mermaid format.
