# Legacy Migration Checklist

**Purpose**: Systematic verification of legacy components before removal/archival.

---

## **Legacy Component Inventory**

### **Confirmed Legacy References**

- `commands/sync.md` - Legacy session migration options (`--migrate-sessions`)
- `LEGACY_ARCHIVE_NOTICE.md` - Archive documentation (502MB archived)
- `docs/standards/CLAUDE_SESSION_STORAGE_STANDARD.md` - References removed legacy symlinks

### **Potential Legacy Components**

_Requires verification:_

#### Shell Snapshots

- **Location**: `shell-snapshots/snapshot-zsh-*.sh`
- **Status**: ❓ Unknown if still active or legacy
- **Action Required**: Verify if automated or manual snapshots

#### Historical Todos

- **Location**: `todos/*.json` with TabPFN/backtest references
- **Status**: ❓ May contain legacy task references
- **Action Required**: Review for obsolete project references

#### Configuration Files

- **Location**: Multiple `settings.json`, `config.json` files
- **Status**: ❓ May contain legacy settings
- **Action Required**: Audit for obsolete configuration keys

---

## **Verification Workflow**

### **Phase 1: Component Assessment**

For each legacy component:

1. **Dependency Check**
   - [ ] Search codebase for active references
   - [ ] Check recent git history for usage
   - [ ] Verify no scripts/agents depend on it

2. **Functionality Test**
   - [ ] Test if component still operates
   - [ ] Check if removal breaks any workflows
   - [ ] Validate against current system architecture

3. **Data Analysis**
   - [ ] Assess data value/importance
   - [ ] Check for unique information not elsewhere
   - [ ] Determine archival vs. deletion approach

### **Phase 2: Safe Removal**

For verified unnecessary components:

1. **Backup Creation**
   - [ ] Create dated backup in `archive/legacy-cleanup-YYYY-MM-DD/`
   - [ ] Document removal rationale
   - [ ] Include recovery instructions

2. **Reference Cleanup**
   - [ ] Remove code references
   - [ ] Update documentation
   - [ ] Clean symlinks/shortcuts

3. **Verification**
   - [ ] Test system functionality post-removal
   - [ ] Verify no broken dependencies
   - [ ] Confirm no unintended side effects

### **Phase 3: Documentation Update**

- [ ] Update `LEGACY_ARCHIVE_NOTICE.md` with new removals
- [ ] Document lessons learned from cleanup
- [ ] Create maintenance schedule for future legacy management

---

## **Checklist Status**

### **Component-Specific Checklists**

#### Shell Snapshots

- [ ] **Assessment**: Determine if snapshots are automated system feature or legacy remnants
- [ ] **Dependencies**: Check if any scripts reference snapshot files
- [ ] **Removal Decision**: Keep active snapshots, archive old ones
- [ ] **Action**: Implement retention policy (e.g., keep last 10, archive older)

#### Legacy Todo References

- [ ] **Assessment**: Review todos for TabPFN and backtest project references
- [ ] **Dependencies**: Verify if projects are still active
- [ ] **Removal Decision**: Archive completed project todos
- [ ] **Action**: Create project-specific todo archives

#### Configuration Files

- [ ] **Assessment**: Audit all config files for obsolete keys
- [ ] **Dependencies**: Test system with cleaned configurations
- [ ] **Removal Decision**: Remove unused configs, document active ones
- [ ] **Action**: Implement configuration validation system

#### Archive Management

- [ ] **Assessment**: Review existing 502MB legacy archive
- [ ] **Dependencies**: Verify archive integrity and accessibility
- [ ] **Removal Decision**: Confirm archive completeness before full legacy removal
- [ ] **Action**: Document archive contents and recovery procedures

---

## **Automation Opportunities**

### **Legacy Detection**

- Create script to automatically identify potential legacy components
- Implement aging reports for unused files/directories
- Add git history analysis for component usage patterns

### **Cleanup Scheduling**

- Monthly legacy component review
- Quarterly archive maintenance
- Annual deep cleanup and consolidation

### **Safety Measures**

- Automated backup before any legacy removal
- Rollback procedures for accidental removal
- Integration with milestone logging for audit trail

---

**Next Steps**: Begin Phase 1 assessment starting with shell snapshots as they're most likely to be either active system components or clear legacy remnants.
