# SSH Caching & Directory-Based Key Switching Issue

**Session Date**: October 20, 2025
**Status**: In Progress - Pending GitHub Key Registration
**Issue**: SSH ControlMaster caching blocked directory-based key switching

---

## Problem Summary

When switching between project directories frequently, SSH's ControlMaster caching prevented proper authentication key selection based on working directory.

### What Happened

1. **Initial Setup**: SSH config uses Match directives with `exec` commands to select keys based on `$PWD`

   ```bash
   Match host github.com exec "echo $PWD | grep -q '/.claude'"
       IdentityFile ~/.ssh/id_ed25519_terrylica
   ```

2. **First Connection**: SSH cached the connection via ControlMaster

   ```bash
   ControlMaster auto
   ControlPath ~/.ssh/control-%r@%h:%p
   ControlPersist 600
   ```

3. **Subsequent Connections**: SSH reused cached connection
   - Ignored Match directives (Match evaluated once at cache time)
   - Kept using first authenticated key (tainora)
   - New directories couldn't trigger key selection

4. **Result**: All git operations from `~/.claude` used wrong key (tainora instead of terrylica)

### Why This Happened

SSH's ControlMaster feature:

- Caches SSH connection multiplexing
- Evaluates Match directives only on initial connection
- Reuses cached connection for subsequent commands
- Doesn't re-evaluate directory-based conditions

**Perfect for stable environments** (same directory, same key)
**Breaks with multi-account, multi-directory workflows**

---

## Current Solution (Temporary)

**Clear control masters when switching directories:**

```bash
rm -f ~/.ssh/control-*
cd ~/.claude
ssh -T git@github.com  # Now uses correct key
```

**Limitations:**

- Manual step required
- Easy to forget
- Inefficient with frequent switching

---

## Better SSH Configuration Strategies

### **Option 1: Disable ControlMaster (Simplest)**

**File**: `~/.ssh/config`

```bash
# REMOVE or DISABLE these lines from default Host *:
# ControlMaster auto
# ControlPath ~/.ssh/control-%r@%h:%p
# ControlPersist 600

# OR explicitly disable for GitHub:
Host github.com
    ControlMaster no
    ControlPath none
```

**Pros:**

- Simple, immediate fix
- No manual cache clearing
- Works with all Match directives

**Cons:**

- Slight performance hit (new SSH connection each time)
- Loss of connection multiplexing benefits

**Recommendation**: Use this if you switch directories frequently

---

### **Option 2: Per-Host Control Master Settings**

**File**: `~/.ssh/config`

```bash
# Keep ControlMaster for stable connections
Host tca tca-zt littleblack kab
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 600

# Disable ControlMaster for GitHub (directory-based switching)
Host github.com
    ControlMaster no
    ControlPath none

    # Match directives work better without ControlMaster
    User git
```

**Pros:**

- Keeps multiplexing for stable internal hosts
- Disables only where problematic
- Best of both worlds

**Cons:**

- Requires careful configuration
- Must update if adding new hosts

**Recommendation**: Use this for hybrid workflows

---

### **Option 3: Conditional Control Master Script**

**File**: `~/.ssh/control-master-decider.sh`

```bash
#!/bin/bash
# Decide whether to use ControlMaster based on directory

PWD_PATTERN="$1"
CACHE_ENABLED="$2"

# Check if current directory matches pattern
if echo "$PWD" | grep -q "$PWD_PATTERN"; then
    # Multi-account directory - disable caching
    echo "no"
else
    # Single-account directory - enable caching
    echo "$CACHE_ENABLED"
fi
```

**File**: `~/.ssh/config`

```bash
Host github.com
    User git

    # Dynamically decide ControlMaster based on PWD
    # This requires ProxyCommand workaround (complex)

    # Better: Use separate aliases per account
```

**Pros:**

- Intelligent switching
- Fully automated

**Cons:**

- Complex to implement
- ProxyCommand workarounds needed
- SSH config doesn't support conditional ControlMaster directly

**Recommendation**: Not recommended (too complex)

---

### **Option 4: Account-Specific Hosts (Recommended)**

**File**: `~/.ssh/config`

Instead of using Match directives based on PWD, create explicit host aliases:

```bash
# GitHub accounts as separate hosts
Host gh-terrylica
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_terrylica
    IdentitiesOnly yes
    ControlMaster no

Host gh-eonlabs
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_eonlabs
    IdentitiesOnly yes
    ControlMaster no

Host gh-459ecs
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_459ecs
    IdentitiesOnly yes
    ControlMaster no

# Keep default github.com for explicit repos
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_terrylica
```

**Usage in Git:**

```bash
# terrylica repo
git remote set-url origin git@gh-terrylica:terrylica/claude-config.git

# eonlabs repo
git remote set-url origin git@gh-eonlabs:Eon-Labs/project.git

# 459ecs repo
git remote set-url origin git@gh-459ecs:459ecs/project.git
```

**Pros:**

- Explicit and clear
- No directory-based assumptions
- Works with ControlMaster
- Easy to debug (host name shows which key used)
- No magic or hidden behavior

**Cons:**

- Requires per-repo configuration
- More git remote URLs to manage
- Less "automatic" than directory matching

**Recommendation**: Use this if you manage repositories explicitly

---

## Recommended Solution for Your Workflow

Given your frequent directory switching between multiple accounts (`terrylica`, `eonlabs`, `459ecs`), **recommend Option 2 with simplification**:

### **Proposed SSH Config**

```bash
# Keep ControlMaster for internal hosts only
Host tca tca-zt littleblack kab zerotier-*
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 600

# Disable ControlMaster for ALL GitHub (simplest)
Host github.com
    User git
    ControlMaster no
```

**Then use directory-based selection:**

```bash
# ~/.ssh/config (after Host github.com section)

# Terrylica (/.claude)
Match host github.com exec "echo $PWD | grep -q '/.claude'"
    IdentityFile ~/.ssh/id_ed25519_terrylica
    IdentitiesOnly yes

# Eon-Labs (/eon/, ml-)
Match host github.com exec "echo $PWD | grep -q -E '(/eon/|ml-)'"
    IdentityFile ~/.ssh/id_ed25519_eonlabs
    IdentitiesOnly yes

# 459ecs (/459ecs)
Match host github.com exec "echo $PWD | grep -q '/459ecs'"
    IdentityFile ~/.ssh/id_ed25519_459ecs
    IdentitiesOnly yes
```

**Benefits:**

- ✅ Works with frequent directory switching
- ✅ No cache clearing needed
- ✅ Automatic key selection per directory
- ✅ Keeps ControlMaster for stable connections
- ✅ Simple to understand and debug
- ✅ No per-repo configuration needed

---

## Implementation Steps for Next Session

### **1. Update SSH Config**

```bash
# Edit ~/.ssh/config
# Remove ControlMaster settings for github.com
# Ensure Match directives are present for directory-based selection
```

### **2. Test Switching Behavior**

```bash
# From terrylica directory
cd ~/.claude && ssh -T git@github.com
# Expected: Hi terrylica! ...

# From eonlabs directory
cd ~/eon/project && ssh -T git@github.com
# Expected: Hi Eon-Labs! ... (or appropriate account)

# No manual cache clearing needed
```

### **3. Verify Git Operations**

```bash
# Each directory should automatically use correct key
cd ~/.claude && git push origin main
cd ~/eon/project && git push origin main
```

---

## Performance Considerations

### **ControlMaster Impact**

| Setting                   | First SSH | Subsequent | Switching | Multi-Account |
| ------------------------- | --------- | ---------- | --------- | ------------- |
| **With ControlMaster**    | Slower    | Fast       | Broken    | Broken        |
| **Without ControlMaster** | Normal    | Normal     | Works     | Works ✓       |

**Conclusion**: For multi-account workflows with directory switching, the performance loss is negligible and worth the reliability gain.

---

## Monitoring & Debugging

### **Check Active SSH Connections**

```bash
ls -la ~/.ssh/control-* 2>/dev/null || echo "No cached connections"
```

### **Test Which Key Is Used**

```bash
ssh -vv git@github.com 2>&1 | grep "Offering public key"
```

### **Manual Cache Clear (Emergency)**

```bash
rm -f ~/.ssh/control-*
```

---

## Session Summary

**Issue**: SSH ControlMaster caching prevented terrylica key selection
**Current State**: SSH configured but requires GitHub key registration
**Next Steps**:

1. Add SSH public key to GitHub (terrylica account)
2. Implement Option 2 (disable ControlMaster for GitHub)
3. Test directory switching without manual cache clearing
4. Monitor for caching issues

---

## Related Files

- **SSH Config**: `~/.ssh/config` (lines 34-60)
- **SSH Keys**: `~/.ssh/id_ed25519_terrylica*`
- **GitHub Settings**: https://github.com/settings/keys
- **Documentation**: `docs/setup/SSH-CONFIG-SETUP.md`

---

## Future Considerations

- **SSH Config Automation**: Create backup/restore mechanism for SSH configs
- **Key Rotation**: Implement regular SSH key rotation policy
- **Per-Repo Verification**: Add pre-push hook to verify correct key used
- **Session Tracking**: Log which SSH key used per repository

---

**Last Updated**: October 20, 2025
**Status**: Pending GitHub SSH Key Registration
**Next Session Action**: Implement recommended SSH config changes
