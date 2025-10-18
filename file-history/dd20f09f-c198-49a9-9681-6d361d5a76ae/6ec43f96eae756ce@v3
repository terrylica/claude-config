# Comprehensive Repository To-Do List
## Based on Repository Audit Findings

**Date**: 2025-10-17
**Status**: active
**Purpose**: Master action item tracking for repository audit and improvement
**Audit Baseline**: main@9286b4f (43 commits ahead of origin)
**Total Rust Files**: 51 files (~17,100 LOC)
**Repository Size**: ~3.2MB (crates: 728KB, docs: 1.2MB, test_data: 912KB, archived: 192KB)

---

## 🔴 CRITICAL PRIORITY (P0) - Do First

### Git & Version Control

- [ ] **CRITICAL: Push 43 unpushed commits to origin**
  - **Why**: Currently 43 commits ahead of origin/main
  - **Risk**: Data loss if local changes are lost
  - **Command**: `git push origin main`
  - **Estimated**: 5 minutes
  - **Blocker for**: Any collaborative work

- [ ] **Delete stale branch: `backup-before-gpu-removal`**
  - **Why**: Appears to be a backup branch that's no longer needed
  - **Command**: `git branch -d backup-before-gpu-removal`
  - **Estimated**: 1 minute

### Documentation - Status Field Missing

- [ ] **Add Status field to ALL planning documents (19 files)**
  - **Why**: No planning docs have status tracking - makes it hard to know what's active/completed
  - **Files Affected**: All 19 files in `docs/planning/`
  - **Status Options**: `pending`, `in_progress`, `completed`, `archived`
  - **Template**:
    ```markdown
    **Version**: X.X.X
    **Created**: YYYY-MM-DD
    **Status**: [pending|in_progress|completed|archived]
    **Supersedes**: [file path or N/A]
    ```
  - **Estimated**: 2-3 hours (review each doc, determine status)
  - **Blocks**: Knowing which plans are active vs historical

### Quick Wins Already Completed

- [x] ✅ Fix 1: Replace panic in data_structure_validator.rs
- [x] ✅ Fix 2: Eliminate TOCTOU unwrap in replay_buffer.rs
- [x] ✅ Fix 3: Enforce threshold validation in processor.rs

---

## 🟠 HIGH PRIORITY (P1) - Next Week

### Phase 1: Documentation Cleanup & Organization

#### 1.1 Prune Legacy Documentation

- [ ] **Review and archive/delete `docs/planning/legacy/` (7 files)**
  - `test-fake-data-audit-v1-obsolete.md` - Filename indicates obsolete
  - `exness-migration-plan.md` - Check if migration is complete
  - `phase6-data-flow-architecture.md` - Validate if Phase 6 is relevant
  - `phase6-technical-specification.yaml` - Same as above
  - `github-chart-visualization-comprehensive-plan.md` - Check relevance
  - `comprehensive-rolling14bar-system-specification.yml` - Validate status
  - `master-implementation-plan.yml` - Check if superseded
  - **Decision**: For each - Archive (add to ARCHIVED.md) or Delete
  - **Estimated**: 2 hours (requires reading each file)

- [ ] **Consolidate migration documentation**
  - Files: `workspace-migration-v5.0.0.md`, `dukascopy-cleanup-plan-v5.0.0.md`, `api-threshold-granularity-migration.md`
  - **Action**: Either consolidate into single migration guide or clearly mark completion status
  - **Estimated**: 1 hour

- [ ] **Review research documents for archival**
  - `docs/planning/research/` - 3 files (exness, pattern-continuation, critical-finding)
  - **Action**: Extract findings into main docs, then archive originals
  - **Estimated**: 1 hour

#### 1.2 Create Missing Documentation

- [ ] **Create `docs/planning/INDEX.md` - Hub for all planning docs**
  - **Content**:
    - Active plans (status=in_progress)
    - Completed plans (status=completed)
    - Archived plans (status=archived)
    - Links to all with one-sentence description
  - **Estimated**: 30 minutes

- [ ] **Create `docs/ARCHITECTURE.md` - High-level architecture overview**
  - **Content**:
    - 8 crate structure explanation
    - Dependency graph
    - Data flow diagram
    - Design decisions rationale
  - **Estimated**: 2-3 hours

- [ ] **Create `docs/API.md` - Public API documentation**
  - **Content**:
    - rangebar-core public API
    - rangebar-providers public API
    - Usage examples
    - Migration guides
  - **Estimated**: 3-4 hours

- [ ] **Create `CHANGELOG.md` (if not exists)**
  - **Why**: Track version history properly
  - **Format**: Keep-a-Changelog format
  - **Estimated**: 1 hour (extract from git history)

#### 1.3 Consolidate README Files (14 total)

- [ ] **Decision: Root README.md strategy**
  - **Current**: Root README.md exists (conflicts with .claude/ docs preference)
  - **Options**:
    1. Delete root README.md, use docs/README.md only
    2. Keep minimal root README with pointer to docs/
    3. Keep current structure
  - **Estimated**: 15 minutes (decision) + 30 minutes (implementation)

- [ ] **Review README files for redundancy**
  - Locations: examples/, cache/, data/, output/, test_data/, docs/planning/
  - **Action**: Consolidate information, delete redundant READMEs
  - **Estimated**: 1 hour

---

### Phase 2: Code Cleanup

#### 2.1 Archived Code Decision

- [ ] **Evaluate `archived_modules/` (192KB, 4 Rust files)**
  - **Files**:
    1. `experiments/rangebar_export.rs` - Contains TODO/FIXME
    2. `legacy/statistics_legacy.rs` - Contains TODO/FIXME
    3. (2 other files)
  - **Decision Point**: Delete or document why preserved?
  - **If Delete**: Gain 192KB
  - **If Keep**: Create `archived_modules/ARCHIVED.md` explaining purpose
  - **Estimated**: 1 hour (review code, extract learnings, decide)

- [ ] **Extract learnings from archived experiments**
  - **Action**: Document any valuable patterns/insights before deletion
  - **Output**: Add to main documentation or code comments
  - **Estimated**: 1 hour

#### 2.2 Binary Tools Audit

- [ ] **Document usage for each CLI binary (6 binaries)**
  - **Binaries**:
    1. `data_structure_validator` - Add --help documentation
    2. `parallel_tier1_analysis` - Add --help documentation
    3. `polars_benchmark` - Determine if one-time use or ongoing
    4. `spot_tier1_processor` - Add --help documentation
    5. `temporal_integrity_test_only` - Should this be a test, not a binary?
    6. `tier1_symbol_discovery` - Add --help documentation
  - **Estimated**: 2-3 hours (review each binary, add docs)

- [ ] **Consider consolidating binaries into subcommands**
  - **Proposal**: Single `rangebar` binary with subcommands
  - **Example**: `rangebar analyze`, `rangebar validate`, `rangebar discover`
  - **Benefits**: Simpler distribution, clearer organization
  - **Estimated**: 4-6 hours (refactoring)
  - **Priority**: Medium (nice-to-have, not urgent)

#### 2.3 Unwrap Audit

- [ ] **Review 165 unwraps across 30 files**
  - **Production code unwraps** (estimate ~50-70):
    - `rangebar-streaming/src/stats.rs`: 10
    - `rangebar-io/src/formats.rs`: 6
    - `rangebar-core/src/fixed_point.rs`: 11
    - `rangebar-io/src/polars_io.rs`: 11
    - Others: ~20-30 more
  - **Action**: Categorize as:
    1. Safe unwraps (document why with comment)
    2. Should be Result propagation (fix)
    3. Test code (acceptable)
  - **Estimated**: 3-4 hours (review each occurrence)

---

### Phase 3: Test & Example Cleanup

#### 3.1 Test Organization

- [ ] **Review 10 integration test files**
  - Check for:
    - Duplicate test coverage
    - Slow tests (identify and optimize)
    - Tests for removed features
  - **Files**: `crates/rangebar/tests/*.rs`
  - **Estimated**: 2 hours

- [ ] **Test data audit (912KB)**
  - **Files**: `test_data/BTCUSDT/`, `test_data/ETHUSDT/`, `.DS_Store`
  - **Actions**:
    - Delete `.DS_Store` (macOS artifact)
    - Verify test data files are all needed
    - Consider generating synthetic test data instead
  - **Estimated**: 30 minutes

#### 3.2 Examples Audit (14 examples)

- [ ] **Test all examples compile**
  - **Command**: `cargo build --examples`
  - **Estimated**: 15 minutes

- [ ] **Review examples for currency**
  - Directories: analysis/, educational/, interactive/, investigation/, validation/
  - **Check**:
    - Do examples work with v5.0.0 API?
    - Are examples documented in examples/README.md?
    - Should any be converted to integration tests?
  - **Estimated**: 2 hours

- [ ] **Update example READMEs (5 README files)**
  - Ensure each category (analysis, educational, etc.) has clear purpose
  - Link from main examples/README.md
  - **Estimated**: 1 hour

---

### Phase 4: Dependency Management

- [ ] **Run `cargo outdated --workspace`**
  - **Action**: Update dependencies to latest compatible versions
  - **Estimated**: 1 hour
  - **Follow-up**: Test after updates

- [ ] **Add `[workspace.dependencies]` for shared dependencies**
  - **Why**: 8 crates likely share many dependencies
  - **Benefits**: Single source of truth for versions, easier updates
  - **Estimated**: 1-2 hours

- [ ] **Set up `cargo deny` for dependency policies**
  - **Why**: Supply chain security, license compliance
  - **Config**: Create `.cargo/deny.toml`
  - **Estimated**: 30 minutes setup + testing

- [ ] **Run security audit: `cargo audit`**
  - **Action**: Fix any vulnerabilities found
  - **Add to CI**: Automated security scanning
  - **Estimated**: 1 hour (assuming no critical vulns)

---

## 🟡 MEDIUM PRIORITY (P2) - This Month

### Phase 5: Architecture Improvements

#### 5.1 Crate Documentation

- [ ] **Add crate-level documentation for all 8 crates**
  - **Crates**: rangebar-core, rangebar-providers, rangebar-io, rangebar-config, rangebar-batch, rangebar-streaming, rangebar-cli, rangebar (meta)
  - **Content**: Purpose, main types, usage examples
  - **Estimated**: 4-6 hours (30-45 min per crate)

- [ ] **Add `#![warn(missing_docs)]` to public crates**
  - **Crates**: rangebar-core, rangebar-providers
  - **Action**: Add lint, then fix all warnings
  - **Estimated**: 2-3 hours

- [ ] **Generate architecture diagram**
  - **Tools**: Mermaid.js, Graphviz, or similar
  - **Content**: Crate dependencies, data flow
  - **Location**: `docs/ARCHITECTURE.md`
  - **Estimated**: 2 hours

#### 5.2 Error Handling Consistency

- [ ] **Audit error types across crates**
  - **Find**: `rg "^pub enum.*Error" --type rust`
  - **Check**: Consistency, missing context, thiserror usage
  - **Estimated**: 1 hour

- [ ] **Create error handling guidelines documentation**
  - **Location**: `docs/ERROR_HANDLING.md`
  - **Content**: When to panic vs error, error type design, context patterns
  - **Estimated**: 1-2 hours

---

### Phase 6: CI/CD Improvements

- [ ] **Add missing CI workflows**
  - **Current**: Only `ci.yml` and `pre-commit-autoupdate.yml`
  - **Missing**:
    - Security audit workflow (cargo audit)
    - Dependency check (cargo deny)
    - Code coverage workflow
    - Benchmark regression detection
    - Release automation
  - **Estimated**: 3-4 hours (1 hour per workflow)

- [ ] **Review and optimize existing CI workflows**
  - **Check**: Caching, job parallelization, timeout settings
  - **Estimated**: 1 hour

- [ ] **Set up Dependabot (if not configured)**
  - **Config**: `.github/dependabot.yml`
  - **Frequency**: Weekly for security, monthly for dependencies
  - **Estimated**: 15 minutes

---

### Phase 7: Developer Experience

- [ ] **Create `.editorconfig`**
  - **Why**: Consistent coding style across editors
  - **Settings**: Rust-specific indentation, line endings
  - **Estimated**: 15 minutes

- [ ] **Add `rust-analyzer.toml` configuration**
  - **Why**: Better IDE experience
  - **Settings**: Clippy lints, check on save
  - **Estimated**: 15 minutes

- [ ] **Create `CONTRIBUTING.md`**
  - **Content**: How to build, test, submit PRs
  - **Estimated**: 1 hour

- [ ] **Document pre-commit hooks**
  - **Current**: `.pre-commit-config.yaml` exists
  - **Action**: Add documentation on setup/usage
  - **Estimated**: 30 minutes

---

## 🟢 LOW PRIORITY (P3) - Future Improvements

### Code Quality Enhancements

- [ ] **Add property-based testing for core algorithm**
  - **Tool**: proptest or quickcheck
  - **Target**: rangebar-core threshold calculations
  - **Estimated**: 4-6 hours

- [ ] **Add MIRI tests for unsafe code (if any)**
  - **Check**: `rg "unsafe " --type rust`
  - **Action**: Add MIRI to CI
  - **Estimated**: 1-2 hours

- [ ] **Set up code coverage reporting**
  - **Tool**: tarpaulin (Linux) or llvm-cov
  - **Target**: 80%+ coverage
  - **Estimated**: 2-3 hours

### Performance & Optimization

- [ ] **Benchmark regression testing**
  - **Tool**: criterion.rs
  - **Add to CI**: Detect performance regressions
  - **Estimated**: 3-4 hours

- [ ] **Profile and optimize hot paths**
  - **Tools**: cargo flamegraph, perf
  - **Target**: Processing functions in rangebar-core
  - **Estimated**: 4-6 hours

### Feature Additions

- [ ] **Consider: Binary consolidation into single CLI**
  - **See**: Phase 2.2 above
  - **Estimated**: 6-8 hours

- [ ] **Consider: Workspace metadata centralization**
  - **Action**: Move more config to workspace Cargo.toml
  - **Estimated**: 2-3 hours

---

## 📊 Cleanup Candidates Summary

### Immediate Deletions (Safe)

- [ ] Delete `test_data/.DS_Store` (macOS artifact)
- [ ] Delete `archived_modules/` (after extracting learnings) - **Saves 192KB**
- [ ] Delete stale git branch `backup-before-gpu-removal`

### Potential Deletions (Needs Review)

- [ ] Review `docs/planning/legacy/` - 7 files for archival/deletion
- [ ] Review redundant README files - consolidate 14 down to ~8
- [ ] Review examples - consider removing outdated ones
- [ ] Review test data - verify all files needed

### Total Potential Savings

- **Disk Space**: ~500KB-1MB (archived code + redundant docs + test data)
- **Maintenance**: Reduced by ~20-30% (fewer docs to maintain, clearer structure)
- **Cognitive Load**: Significantly reduced (clearer what's active vs historical)

---

## 📈 Success Metrics

### Documentation
- [ ] All planning docs have Status field
- [ ] Planning INDEX exists with categorized list
- [ ] Architecture docs created
- [ ] API docs created

### Code Quality
- [ ] <100 unwraps in production code (down from ~165 total)
- [ ] All binaries have --help documentation
- [ ] All crates have crate-level docs
- [ ] 80%+ test coverage

### Maintenance
- [ ] Workspace dependencies consolidated
- [ ] Security scanning in CI
- [ ] Dependency updates automated
- [ ] Pre-commit hooks documented

### Git Hygiene
- [ ] 0 commits ahead of origin (currently 43)
- [ ] 0 stale branches (currently 1)
- [ ] All completed work pushed

---

## ⏱️ Time Estimates by Priority

### P0 (Critical) - Do This Week
- Git push: 5 min
- Delete stale branch: 1 min
- Add Status to docs: 2-3 hours
**Total**: ~3 hours

### P1 (High) - Next 1-2 Weeks
- Documentation cleanup: 8-10 hours
- Code cleanup: 6-8 hours
- Test/example audit: 5-6 hours
- Dependency management: 3-4 hours
**Total**: ~25-30 hours

### P2 (Medium) - This Month
- Architecture improvements: 8-10 hours
- CI/CD improvements: 4-5 hours
- Developer experience: 2-3 hours
**Total**: ~15-20 hours

### P3 (Low) - Future
- Code quality: 8-10 hours
- Performance: 6-8 hours
- Features: 8-12 hours
**Total**: ~25-30 hours

### Grand Total: ~70-90 hours (2-3 weeks full-time)

---

## 🎯 Recommended Execution Plan

### Week 1: Foundation (P0 + Critical P1)
**Days 1-2**: Git hygiene + Documentation status audit
**Days 3-5**: Documentation cleanup and consolidation

### Week 2: Code & Tests (Remaining P1)
**Days 1-2**: Code cleanup (archived, binaries)
**Days 3-4**: Test and example audit
**Day 5**: Dependency management

### Week 3: Architecture & CI (P2)
**Days 1-2**: Architecture documentation
**Days 3-4**: CI/CD improvements
**Day 5**: Developer experience improvements

### Week 4+: Optimization (P3)
**Ongoing**: Code quality, performance, features as time permits

---

## 📝 Notes & Decisions Log

### ✅ Decisions Made (2025-10-17)

1. **Root README.md**: ✅ **KEEP as-is, update as we go along**
   - Rationale: Provides GitHub entry point, will be improved iteratively

2. **Binary consolidation**: ✅ **KEEP multiple binaries (6 separate tools)**
   - Rationale:
     - Clear separation of concerns
     - Binaries CAN invoke each other via std::process::Command
     - Easier for learning Rust (focused main.rs per tool)
     - Simpler maintenance (self-contained tools)
   - Action: Improve documentation for each binary

3. **Archived code**: ✅ **DELETE if properly committed to git history**
   - Rationale: Git history preserves all code, no need for archived_modules/
   - Action: Verify git history has all code, then delete archived_modules/

4. **Test data**: ✅ **KEEP real data, minimize synthetic generation**
   - Rationale: Real data provides authentic testing scenarios
   - Action: Only generate synthetic when absolutely necessary

### Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss from unpushed commits | High | Push immediately (P0) |
| Breaking changes during cleanup | Medium | Feature branch + review |
| Time overrun | Low | Start with P0/P1, defer P3 |
| Dependency updates break build | Medium | Test thoroughly, pin if needed |

---

## 🔄 Continuous Improvement

### After Each Phase

- [ ] Update this to-do list with actual time taken
- [ ] Document lessons learned
- [ ] Update audit plan with improvements
- [ ] Run `git push` to sync changes

### Monthly Review

- [ ] Re-run audit commands (see audit-quick-reference.md)
- [ ] Update metrics
- [ ] Adjust priorities based on project needs

---

**Last Updated**: 2025-10-17
**Next Review**: 2025-11-17 (1 month)

---

**END OF COMPREHENSIVE TO-DO LIST**
