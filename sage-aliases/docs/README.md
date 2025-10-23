# SAGE Aliases Tool

**Purpose**: Comprehensive alias system for SAGE development across dual environments

## Universal Access Commands

The tool provides global access via `~/.local/bin` (industry standard):

### Core Commands

```bash
gpu-ws           # GPU workstation connection and management
sage-dev         # SAGE development environment launcher
sage-status      # Infrastructure health monitoring
sage-sync        # Comprehensive sync tool for dual environments
```

## Command Reference

### GPU Workstation (`gpu-ws`)

```bash
gpu-ws           # SSH to GPU workstation
gpu-ws --help    # Show all available options
```

### SAGE Development (`sage-dev`)

```bash
sage-dev docs    # Documentation work (macOS)
sage-dev tirex   # TiRex GPU development
sage-dev ensemble # Full SAGE integration
sage-dev local   # Local CPU development
sage-dev status  # Models availability check
sage-dev diag    # Environment diagnostics
```

### Infrastructure Status (`sage-status`)

```bash
sage-status      # Complete health check
sage-status sync # Syncthing status
sage-status network # ZeroTier connectivity
sage-status gpu  # GPU workstation status
sage-status models # SAGE models availability
```

## Alias Categories

### Available Alias Files

- `aliases/gpu-workstation.sh` - GPU connection and monitoring
- `aliases/sage-development.sh` - SAGE-specific development workflows
- `aliases/sync-monitoring.sh` - Syncthing synchronization management
- `aliases/network-diagnostics.sh` - ZeroTier network diagnostics

## Installation

The tool follows the standard `~/.claude/tools/` pattern:

1. **Global Access**: Commands available via `~/.local/bin` (industry standard)
2. **Shell Integration**: Source alias files as needed
3. **Universal Access**: Work from any directory

## Architecture

### Directory Structure

```
sage-aliases/
├── bin/                    # Universal access executables
│   ├── gpu                # GPU workstation command
│   ├── sage-dev           # SAGE development launcher
│   └── sage-status        # Infrastructure status checker
├── aliases/               # Category-organized alias files
│   ├── gpu-workstation.sh
│   ├── sage-development.sh
│   ├── sync-monitoring.sh
│   └── network-diagnostics.sh
└── docs/                  # Documentation
    └── README.md
```

### Design Principles

- **Working Directory Preservation**: Commands work from any location
- **Environment Auto-Detection**: Optimal environment selection based on task
- **Universal Access**: Consistent command interface across workspaces
- **Modular Organization**: Logical separation of functionality

## Usage Examples

### Quick Development Session

```bash
# Check infrastructure health
sage-status

# Start GPU development if everything healthy
gpu dev
```

### SAGE Model Development

```bash
# Check model availability
sage-dev status

# Start appropriate environment based on task
sage-dev ensemble    # Full SAGE integration on GPU
sage-dev docs        # Documentation on macOS
sage-dev tirex       # TiRex GPU development
```

### Infrastructure Monitoring

```bash
# Monitor synchronization
sage-status sync

# Check network performance
sage-status network

# Verify GPU accessibility
sage-status gpu
```

## Integration

### Shell Configuration

The tool integrates with shell configuration via:

- Industry standard: `~/.local/bin` location
- Selective alias sourcing as needed
- Working directory preservation

### SAGE Development Workflow

- **Phase 0 Complete**: All infrastructure ready
- **Model Validation**: Individual model testing workflows
- **Ensemble Integration**: Full SAGE meta-framework development
- **Production Deployment**: Scalable infrastructure patterns

Part of SAGE (Self-Adaptive Generative Evaluation) development infrastructure.
