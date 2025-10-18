# Business Logic Diagrams Index

Visual representations of rangebar business logic using Mermaid diagrams.

## Organization

This folder contains business logic diagrams organized by complexity and focus area:

### Implemented Diagrams

**01 - High-Level Business Flow** ✅
- [01-high-level-business-flow.md](01-high-level-business-flow.md)
- **Purpose**: Complete end-to-end business journey from raw data to trading insights
- **Stages**: 7 major business stages with detailed sub-processes
- **Audience**: All users - start here for the big picture

### Planned Diagrams (Placeholders)

**02 - Business Use Cases by User Type** 📋
- [02-business-use-cases.md](02-business-use-cases.md)
- **Purpose**: Who uses this system and for what business objectives?
- **Coverage**: Researchers, Live Traders, Portfolio Managers
- **Status**: Placeholder - awaiting implementation

**03 - Data Acquisition Decision Tree** 📋
- [03-data-acquisition-decisions.md](03-data-acquisition-decisions.md)
- **Purpose**: Business logic for choosing data sources and markets
- **Coverage**: Crypto (Spot/UM/CM) vs Forex (Exness variants)
- **Status**: Placeholder - awaiting implementation

**04 - Processing Mode Decision Logic** 📋
- [04-processing-mode-decisions.md](04-processing-mode-decisions.md)
- **Purpose**: When to use streaming vs batch processing
- **Coverage**: Use case, memory, size, statistics needs
- **Status**: Placeholder - awaiting implementation

**05 - Threshold Selection Guide** 📋
- [05-threshold-selection-guide.md](05-threshold-selection-guide.md)
- **Purpose**: Choosing optimal threshold based on trading strategy
- **Coverage**: HFT, Intraday, Swing, Position trading
- **Status**: Placeholder - awaiting implementation

**06 - Complete Business Workflow** 📋
- [06-complete-business-workflow.md](06-complete-business-workflow.md)
- **Purpose**: Detailed end-to-end process with all decision points
- **Coverage**: All stages, all branches, all outputs
- **Status**: Placeholder - awaiting implementation

**07 - Error Recovery Business Logic** 📋
- [07-error-recovery-logic.md](07-error-recovery-logic.md)
- **Purpose**: Business decisions when failures occur
- **Coverage**: Network, disk, OOM, data errors, recovery paths
- **Status**: Placeholder - awaiting implementation

**08 - Cross-Market Comparison Workflow** 📋
- [08-cross-market-comparison.md](08-cross-market-comparison.md)
- **Purpose**: Parallel analysis across Spot/UM/CM markets
- **Coverage**: Liquidity ranking, volatility patterns, market selection
- **Status**: Placeholder - awaiting implementation

**09 - Algorithm Business Rules** 📋
- [09-algorithm-business-rules.md](09-algorithm-business-rules.md)
- **Purpose**: Core business guarantees (non-lookahead, determinism)
- **Coverage**: Breach detection, state transitions, trust factors
- **Status**: Placeholder - awaiting implementation

---

## Recommended Reading Order

### For First-Time Users
1. **Start here**: [01-high-level-business-flow.md](01-high-level-business-flow.md) - Understand the complete journey
2. Then: [02-business-use-cases.md](02-business-use-cases.md) - See who uses it for what *(coming soon)*
3. Then: [05-threshold-selection-guide.md](05-threshold-selection-guide.md) - Make practical decisions *(coming soon)*

### For Data Researchers
1. [01-high-level-business-flow.md](01-high-level-business-flow.md) - Overview
2. [03-data-acquisition-decisions.md](03-data-acquisition-decisions.md) - Data sources *(coming soon)*
3. [04-processing-mode-decisions.md](04-processing-mode-decisions.md) - Optimize workflow *(coming soon)*

### For Live Traders
1. [01-high-level-business-flow.md](01-high-level-business-flow.md) - Overview
2. [09-algorithm-business-rules.md](09-algorithm-business-rules.md) - Understand guarantees *(coming soon)*
3. [07-error-recovery-logic.md](07-error-recovery-logic.md) - Handle failures *(coming soon)*

---

## Viewing Diagrams

### On GitHub
All Mermaid diagrams render automatically on GitHub. Just click any `.md` file above.

### In VS Code
Install the [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension.

### In Other Editors
Copy the Mermaid code blocks to [Mermaid Live Editor](https://mermaid.live/) for rendering.

### In Terminal (Ghostty)
Use a Markdown preview tool like `glow`:
```bash
brew install glow
glow 01-high-level-business-flow.md
```

---

## Contributing

To add a new diagram:

1. **Create new file**: `docs/diagrams/XX-descriptive-name.md`
2. **Update this INDEX.md**: Add entry with purpose and status
3. **Use Mermaid syntax**: Follow existing diagram style
4. **Test rendering**: Verify on GitHub or Mermaid Live Editor
5. **Link from main docs**: Update [DOCUMENTATION.md](../../DOCUMENTATION.md) if needed

---

## Mermaid Diagram Tips

### Keep Business Focus
- ❌ Don't show: Technical details (crates, functions, types)
- ✅ Do show: Business stages, decisions, outcomes, value flow

### Use Clear Labels
- ❌ Avoid: "Process data" (vague)
- ✅ Prefer: "Validate schema and normalize timestamps" (specific business action)

### Style Consistently
- **Start nodes**: Light blue (`#e1f5ff`)
- **End nodes/Value**: Gold (`#ffd700`)
- **Outputs**: Light yellow (`#fff4e1`)
- **Errors/Warnings**: Light red (`#ffe1e1`)
- **Success**: Light green (`#e1ffe1`)

### Test Comprehension
Ask yourself: "Can a non-technical user understand the business logic from this diagram?"

---

## Quick Links

- **Main Documentation Hub**: [DOCUMENTATION.md](../../DOCUMENTATION.md)
- **Architecture Overview**: [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
- **Algorithm Specification**: [docs/specifications/algorithm-spec.md](../specifications/algorithm-spec.md)
- **Common Workflows**: [docs/guides/common-workflows.md](../guides/common-workflows.md)
