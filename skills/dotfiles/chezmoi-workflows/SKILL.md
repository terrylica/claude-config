______________________________________________________________________

## name: chezmoi-workflows description: Manage dotfiles with chezmoi via natural language. Use when user mentions dotfiles, config sync, chezmoi, track changes, sync dotfiles, check status, or push changes. allowed-tools: Read, Edit, Bash

# Chezmoi Workflows

**Purpose**: Execute common chezmoi operations via natural language prompts without requiring user to memorize commands or use shell aliases.

**Workflow Model**: AI-Assisted

- User edits configuration files normally with any editor
- User prompts Claude Code with natural language
- Claude Code executes all chezmoi/git operations
- No shell complexity or command memorization needed

**Architecture**: Two-State System

- **Source State**: `/Users/terryli/.local/share/chezmoi/` (git repository)
- **Target State**: `/Users/terryli/` (home directory)
- **Remote**: https://github.com/terrylica/dotfiles (private)

______________________________________________________________________

## Prompt Pattern 1: Track Changes

**User says**: "I edited [file]. Track the changes."

**Workflow**:

1. **Verify drift**

   ```bash
   chezmoi status
   ```

   Expected: Shows modified file(s) with 'M' indicator

1. **Show changes**

   ```bash
   chezmoi diff [file]
   ```

   Expected: Displays unified diff of changes

1. **Add to source state** (auto-commits)

   ```bash
   chezmoi add [file]
   ```

   Expected: File added to source directory, git commit created automatically
   Note: `autocommit = true` in chezmoi.toml triggers automatic commit

1. **Verify commit**

   ```bash
   cd ~/.local/share/chezmoi && git log -1 --oneline
   ```

   Expected: Shows new commit with timestamp

1. **Push to remote**

   ```bash
   cd ~/.local/share/chezmoi && git push
   ```

   Expected: Successfully pushed to https://github.com/terrylica/dotfiles

1. **Confirm to user**

   - Show commit message
   - Show files changed
   - Confirm push success

**Example**:

```
User: I edited .zshrc. Track the changes.
AI: I'll track the changes to .zshrc.
    [Runs chezmoi status]
    Modified: .zshrc
    [Runs chezmoi diff .zshrc]
    [Shows diff output]
    [Runs chezmoi add ~/.zshrc]
    [Runs git log -1]
    Commit created: "Update .zshrc"
    [Runs git push]
    Successfully pushed to remote.
```

______________________________________________________________________

## Prompt Pattern 2: Sync from Remote

**User says**: "Sync my dotfiles from remote."

**Workflow**:

1. **Pull and apply**

   ```bash
   chezmoi update
   ```

   Expected: Pulls from GitHub, applies changes to home directory
   Note: Equivalent to `git pull` + `chezmoi apply`

1. **Show what changed**

   ```bash
   chezmoi status
   ```

   Expected: Should show empty (no drift after sync)

1. **Verify SLOs**

   ```bash
   chezmoi verify
   ```

   Expected: Exit code 0 (all files match source state)

1. **Confirm to user**

   - Show files updated
   - Confirm no errors
   - Report SLO status

**Example**:

```
User: Sync my dotfiles from remote.
AI: Syncing dotfiles from GitHub...
    [Runs chezmoi update]
    Updated: .zshrc, .gitconfig
    [Runs chezmoi verify]
    SLO validation: PASSED
    All files synchronized successfully.
```

______________________________________________________________________

## Prompt Pattern 3: Push to Remote

**User says**: "Push my dotfile changes to GitHub."

**Workflow**:

1. **Check drift**

   ```bash
   chezmoi status
   ```

   Expected: Shows any untracked modifications

1. **Re-add all modified tracked files**

   ```bash
   chezmoi re-add
   ```

   Expected: Updates source state for all managed files, creates commit

1. **Show commit log**

   ```bash
   cd ~/.local/share/chezmoi && git log --oneline -3
   ```

   Expected: Shows recent commits including new auto-commit

1. **Push to remote**

   ```bash
   cd ~/.local/share/chezmoi && git push
   ```

   Expected: Successfully pushed to origin/main

1. **Confirm to user**

   - Show commit count pushed
   - Show commit messages
   - Confirm push success

**Example**:

```
User: Push my dotfile changes to GitHub.
AI: Checking for changes...
    [Runs chezmoi status]
    Found modified files: .zshrc, .zshenv
    [Runs chezmoi re-add]
    Re-added all tracked files, commit created.
    [Runs git push]
    Successfully pushed 1 commit to GitHub.
```

______________________________________________________________________

## Prompt Pattern 4: Check Status

**User says**: "Check my dotfile status."

**Workflow**:

1. **Check drift**

   ```bash
   chezmoi status
   ```

   Expected: Lists modified/added/deleted files with indicators (M/A/D)

1. **List managed files**

   ```bash
   chezmoi managed
   ```

   Expected: Shows all files tracked by chezmoi

1. **Explain drift**

   - If drift detected: Explain which files differ
   - If no drift: Confirm everything synchronized
   - Suggest next action (track changes, sync, push, etc.)

**Example**:

```
User: Check my dotfile status.
AI: Checking dotfile status...
    [Runs chezmoi status]
    M .zshrc (modified in home directory, not yet tracked)

    [Runs chezmoi managed]
    Currently tracking 21 files.

    Drift detected: .zshrc has been edited.
    Suggested action: "I edited .zshrc. Track the changes."
```

______________________________________________________________________

## Prompt Pattern 5: Track New File

**User says**: "Track [file path] with chezmoi."

**Workflow**:

1. **Add file**

   ```bash
   chezmoi add [file]
   ```

   Expected: File added to source directory, commit created

1. **Verify in managed list**

   ```bash
   chezmoi managed | grep [filename]
   ```

   Expected: File appears in managed list

1. **Push to remote**

   ```bash
   cd ~/.local/share/chezmoi && git push
   ```

   Expected: Successfully pushed

1. **Update PLAN.yaml** (if significant)

   - Add to appropriate capability section
   - Document purpose and dependencies
   - Update managed file count in observability SLO

1. **Confirm to user**

   - Show file now tracked
   - Confirm pushed to remote
   - Suggest reviewing PLAN.yaml if needed

**Example**:

```
User: Track ~/.config/helix/config.toml with chezmoi.
AI: Adding helix config to chezmoi...
    [Runs chezmoi add ~/.config/helix/config.toml]
    File added: dot_config/helix/config.toml
    Commit created automatically.
    [Runs chezmoi managed | grep helix]
    Confirmed: File now tracked.
    [Runs git push]
    Successfully pushed to GitHub.

    Note: This is a new editor configuration. Would you like me to update PLAN.yaml?
```

______________________________________________________________________

## Prompt Pattern 6: Resolve Conflicts

**User says**: "I have merge conflicts. Help resolve them."

**Workflow**:

1. **Check git status**

   ```bash
   cd ~/.local/share/chezmoi && git status
   ```

   Expected: Shows conflicted files

1. **Show conflicted files**

   - List each file with conflict markers
   - Explain the conflict (local vs. remote changes)

1. **Guide resolution**

   - Ask user which version to keep (local/remote/manual merge)
   - For manual merge: show conflict markers and guide editing

1. **Complete merge**

   ```bash
   cd ~/.local/share/chezmoi
   git add [resolved-files]
   git commit -m "Resolve merge conflict in [files]"
   ```

1. **Apply to home directory**

   ```bash
   chezmoi apply
   ```

   Expected: Resolved changes applied to home directory

1. **Push to remote**

   ```bash
   cd ~/.local/share/chezmoi && git push
   ```

1. **Verify SLOs**

   ```bash
   chezmoi verify
   ```

**Example**:

```
User: I have merge conflicts. Help resolve them.
AI: Checking for conflicts...
    [Runs git status in source directory]
    Conflict detected in: dot_zshrc.tmpl

    The conflict is between:
    - Local: Added HOMEBREW_PREFIX export
    - Remote: Added UV_PYTHON_PREFERENCE setting

    Options:
    1. Keep local changes only
    2. Keep remote changes only
    3. Keep both (manual merge)

    Which would you like?
```

______________________________________________________________________

## Configuration Reference

**chezmoi.toml** (at `~/.config/chezmoi/chezmoi.toml`):

```toml
[edit]
  command = "hx"        # Helix editor
  apply = false         # Manual apply after review

[git]
  autoadd = true        # Auto-stage changes
  autocommit = true     # Auto-commit on add/apply
  autopush = false      # Claude Code handles push

[add]
  secrets = "error"     # Fail on secret detection
```

**Key Settings**:

- `autocommit = true`: Automatic commits on `chezmoi add` and `chezmoi apply`
- `autopush = false`: Manual push for review (Claude Code handles this)
- `secrets = "error"`: Fail-fast on detected secrets (prevents SECRET-001 type issues)

______________________________________________________________________

## Template Handling

**When user edits a templated file** (files ending in `.tmpl` in source directory):

1. **Identify template**

   - Check if file is template: `ls ~/.local/share/chezmoi/dot_[filename].tmpl`

1. **Edit source template**

   ```bash
   chezmoi edit ~/.filename
   ```

   OR manually edit the template file directly

1. **Test template rendering**

   ```bash
   chezmoi execute-template < ~/.local/share/chezmoi/dot_filename.tmpl
   ```

   Expected: Valid rendered output, no template errors

1. **Apply to home directory**

   ```bash
   chezmoi apply ~/.filename
   ```

1. **Commit and push**

   ```bash
   cd ~/.local/share/chezmoi
   git add dot_filename.tmpl
   git commit -m "Update filename template"
   git push
   ```

**Template Variables**:

- `.chezmoi.os` - darwin, linux
- `.chezmoi.arch` - arm64, amd64
- `.chezmoi.homeDir` - /Users/terryli
- `.chezmoi.hostname` - m3max
- `.data.git.name`, `.data.git.email` - From chezmoi.toml

______________________________________________________________________

## Secret Detection

**Configuration**: `add.secrets = "error"` (fail-fast)

**When secret detected**:

```
chezmoi: /Users/terryli/.zshrc:283: Uncovered a GCP API key...
```

**Resolution**:

1. Operation fails immediately (fail-fast principle)
1. User must resolve:
   - Remove secret from file
   - Template it with secure source
   - Use password manager integration
1. **NEVER bypass** - secrets in git are prohibited

**Historical Example**: SECRET-001 (GEMINI_API_KEY) detected and removed from dot_zshrc.tmpl

______________________________________________________________________

## SLO Validation

After operations, validate Service Level Objectives:

1. **Availability**: `chezmoi verify` (exit code 0)
1. **Correctness**: `chezmoi diff` (empty output)
1. **Observability**: `chezmoi managed` (shows all tracked files)
1. **Maintainability**: `git log` (preserves change history)

Report SLO status to user after major operations.

______________________________________________________________________

## Progressive Disclosure

**For advanced topics, reference**:

- **Templates**: See `chezmoi-templates` skill (future)
- **Secrets Management**: See `chezmoi-secrets` skill (future)
- **Scripts and Hooks**: See `chezmoi-advanced` skill (future)

**Official Documentation**: https://www.chezmoi.io/reference/

______________________________________________________________________

## Version Compatibility

- **Chezmoi**: 2.66.1+ (tested on macOS + Linux)
- **Git**: 2.51.1+
- **Platform**: macOS (primary), Linux (secondary)
- **Shell**: zsh (oh-my-zsh framework)
