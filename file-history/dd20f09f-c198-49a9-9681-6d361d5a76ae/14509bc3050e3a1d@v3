# Documentation Index

Complete documentation hub for the rangebar project - organized from beginner to advanced.

## Quick Navigation

- [Getting Started](#getting-started) - New users start here
- [Core Concepts](#core-concepts) - Understanding the algorithm
- [Business Logic Diagrams](#business-logic-diagrams) - Visual workflow representations
- [Practical Guides](#practical-guides) - Hands-on workflows
- [Deep Dive](#deep-dive) - Crate-specific details
- [Advanced Topics](#advanced-topics) - Testing and optimization

---

## Getting Started

Start here if you're new to the project. These documents provide the essential context and architecture overview.

### [README.md](README.md)
Project overview, quick start example, basic usage, and feature summary.

### [CLAUDE.md](CLAUDE.md)
Project-specific context for AI assistants - critical conventions, data structure validation, Tier-1 instrument definition, and release workflow. **Essential reading** for understanding project conventions.

### [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
**Comprehensive architectural overview** - workspace structure, crate dependency graph, data flow pipeline, design patterns, and public APIs for all 8 crates.

---

## Core Concepts

Understanding the algorithm is fundamental to using this library effectively.

### [docs/specifications/algorithm-spec.md](docs/specifications/algorithm-spec.md)
**Authoritative algorithm specification** - mathematical formulation, breach consistency invariant, non-lookahead bias guarantees, edge cases, and implementation requirements. This is the single source of truth.

---

## Business Logic Diagrams

Visual representations of business workflows using Mermaid diagrams. These diagrams focus on **business logic** (not technical implementation) to help you understand data flow, decision points, and value creation.

### [docs/diagrams/INDEX.md](docs/diagrams/INDEX.md)
**Complete diagram catalog** - 9 business logic diagrams organized by complexity and focus area. Includes viewing instructions for GitHub, VS Code, and terminal.

### [docs/diagrams/01-high-level-business-flow.md](docs/diagrams/01-high-level-business-flow.md)
**End-to-end business journey** - 7 major stages from raw market data to actionable trading insights. Shows data transformation chain, business decision points (Need Statistics?), processing modes (Streaming vs Batch), and business guarantees (non-lookahead, deterministic, temporal integrity, precision).

**Additional diagrams** (placeholders - coming soon):
- Business Use Cases by User Type (Researchers, Live Traders, Portfolio Managers)
- Data Acquisition Decision Tree (Crypto vs Forex, market selection)
- Processing Mode Decision Logic (Streaming vs Batch based on use case, memory, size)
- Threshold Selection Guide (HFT, Intraday, Swing, Position trading)
- Complete Business Workflow (detailed decision points and error handling)
- Error Recovery Business Logic (failure modes and recovery strategies)
- Cross-Market Comparison Workflow (parallel Spot/UM/CM analysis)
- Algorithm Business Rules (state machine and core guarantees)

---

## Practical Guides

Hands-on guides for common research and production workflows.

### [docs/guides/common-workflows.md](docs/guides/common-workflows.md)
**8 production-ready workflow examples** - quick start, streaming processing, multi-symbol analysis, threshold optimization, historical backtesting, cross-market comparison, and performance benchmarking. Complete code with expected output.

### [docs/guides/error-recovery.md](docs/guides/error-recovery.md)
**Error handling for long-running jobs** - 6 failure modes (network, disk, OOM, invalid data, crashes, invariant violations), recovery strategies, checkpointing patterns, data validation, and best practices.

### [docs/guides/performance-profiling.md](docs/guides/performance-profiling.md)
**Performance optimization guide** - profiling tools (flamegraph, criterion, perf, Instruments), bottleneck identification, optimization strategies, and benchmarking. Includes performance targets: >5M trades/sec, <2GB memory.

---

## Deep Dive

Detailed documentation for each crate in the workspace.

### Core Crates

#### [crates/rangebar-core/README.md](crates/rangebar-core/README.md)
Core algorithm and types - fixed-point arithmetic (8-decimal precision), non-lookahead algorithm, minimal dependencies (only 4), `RangeBarProcessor` API, and usage examples.

#### [crates/rangebar-providers/README.md](crates/rangebar-providers/README.md)
Data providers - Binance (Spot/UM/CM Futures aggTrades), Exness (EURUSD_Raw_Spread forex ticks), Tier-1 symbol discovery, and timestamp normalization (13-digit ms ↔ 16-digit μs).

#### [crates/rangebar-io/README.md](crates/rangebar-io/README.md)
I/O operations - Polars integration for DataFrame operations, multiple export formats (CSV, Parquet, Arrow, IPC), and streaming CSV export with bounded memory.

### Engine Crates

#### [crates/rangebar-streaming/README.md](crates/rangebar-streaming/README.md)
Real-time streaming processor - bounded memory processing, circuit breaker pattern for fault tolerance, and real-time metrics collection.

#### [crates/rangebar-batch/README.md](crates/rangebar-batch/README.md)
Batch analytics engine - high-throughput batch processing with Rayon parallelism, multi-symbol parallel analysis, and comprehensive statistics generation.

### Tools & Compatibility

#### [crates/rangebar-cli/README.md](crates/rangebar-cli/README.md)
Command-line tools - 6 binaries for symbol discovery, data validation, parallel analysis, and benchmarking. All tools consolidated in `src/bin/`.

#### [crates/rangebar/README.md](crates/rangebar/README.md)
Meta-crate documentation - backward compatibility layer for v4.0.0 API, re-exports all sub-crates with legacy module paths.

---

## Advanced Topics

For researchers and contributors working on testing, validation, and optimization.

### [crates/rangebar/tests/algorithm_invariants.rs](crates/rangebar/tests/algorithm_invariants.rs)
**Integration test suite** - 20 comprehensive tests validating the breach consistency invariant across edge cases, large datasets (1M+ ticks), multiple thresholds, volatile/stable/trending market conditions, and boundary cases. All tests pass in <0.3s.

---

## Recommended Reading Order

### For New Users (First Time)

1. [README.md](README.md) - Get the big picture
2. [docs/diagrams/01-high-level-business-flow.md](docs/diagrams/01-high-level-business-flow.md) - Visualize the complete journey
3. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Understand the structure
4. [docs/specifications/algorithm-spec.md](docs/specifications/algorithm-spec.md) - Learn the algorithm
5. [docs/guides/common-workflows.md](docs/guides/common-workflows.md) - Try the examples

### For Researchers (Data Analysis)

1. [docs/guides/common-workflows.md](docs/guides/common-workflows.md) - Practical examples
2. [crates/rangebar-core/README.md](crates/rangebar-core/README.md) - Core API
3. [crates/rangebar-providers/README.md](crates/rangebar-providers/README.md) - Data sources
4. [docs/guides/error-recovery.md](docs/guides/error-recovery.md) - Production reliability
5. [docs/guides/performance-profiling.md](docs/guides/performance-profiling.md) - Optimization

### For Contributors (Development)

1. [CLAUDE.md](CLAUDE.md) - Project conventions
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Full architecture
3. [docs/specifications/algorithm-spec.md](docs/specifications/algorithm-spec.md) - Algorithm details
4. [crates/rangebar/tests/algorithm_invariants.rs](crates/rangebar/tests/algorithm_invariants.rs) - Test coverage
5. All crate-specific READMEs

---

## Quick Links by Topic

### Visual Diagrams
- [Diagram Index](docs/diagrams/INDEX.md)
- [High-Level Business Flow](docs/diagrams/01-high-level-business-flow.md)

### Algorithm & Theory
- [Algorithm Specification](docs/specifications/algorithm-spec.md)
- [Integration Tests](crates/rangebar/tests/algorithm_invariants.rs)
- [Core Algorithm Implementation](crates/rangebar-core/README.md)

### Data Sources
- [Data Providers Overview](crates/rangebar-providers/README.md)
- [Binance Data](CLAUDE.md#binance-primary---crypto)
- [Exness Forex Data](CLAUDE.md#exness-primary---forex)

### Workflows & Examples
- [Common Workflows](docs/guides/common-workflows.md)
- [Error Recovery](docs/guides/error-recovery.md)
- [Performance Profiling](docs/guides/performance-profiling.md)

### Architecture & Design
- [Workspace Architecture](docs/ARCHITECTURE.md)
- [Crate Dependency Graph](docs/ARCHITECTURE.md#crate-dependency-graph)
- [Design Patterns](docs/ARCHITECTURE.md#design-patterns)

### Tools & CLI
- [CLI Binaries](crates/rangebar-cli/README.md)
- [Streaming Processing](crates/rangebar-streaming/README.md)
- [Batch Analysis](crates/rangebar-batch/README.md)

---

## Documentation Terminology

**What is this page called?**

This type of hub page is commonly known as:
- **Documentation Index** (most common)
- **Table of Contents** (ToC)
- **Documentation Hub**
- **Documentation Portal**
- **Getting Started Guide** (when focused on onboarding)

**How to request this in the future:**

When asking an AI coding agent to create a similar page, use prompts like:

> "Create a documentation index page in the root directory that links to all project documentation, organized from beginner to advanced"

> "Generate a DOCUMENTATION.md file with a table of contents linking to all README files and guides in the repository"

> "Create a documentation hub page with GitHub Flavored Markdown links to all docs, organized by topic and difficulty level"

**Key elements to specify:**
- **Location**: Root directory, `docs/` folder, or specific path
- **Format**: Markdown, GitHub Flavored Markdown (GFM)
- **Organization**: By difficulty, by topic, chronological, or custom
- **Link style**: Relative links, absolute links, or anchor links
- **Descriptions**: Brief summary per link, or just link titles
- **Sections**: How to group the documentation (beginner/advanced, by feature, etc.)

---

## Contributing to Documentation

Found an issue or want to improve the documentation?

1. **File locations**: All documentation is in either the root directory or `docs/` folder
2. **Link format**: Use relative links (e.g., `[text](docs/file.md)`) for portability
3. **Style**: Follow [GitHub Flavored Markdown](https://github.github.com/gfm/) specification
4. **Accuracy**: Verify code examples actually compile and run
5. **Consistency**: Reference the [authoritative algorithm spec](docs/specifications/algorithm-spec.md) for algorithm details

---

## License

MIT License - See [LICENSE](LICENSE) file for details.
