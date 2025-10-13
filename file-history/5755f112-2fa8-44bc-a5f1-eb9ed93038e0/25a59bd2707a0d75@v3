# Dependency Management - UV vs UVX

**Date:** 2025-10-01
**Decision:** Use persistent `uv venv` instead of temporary `uvx` environments

---

## 🔍 The Problem

Initially, the project used `uvx` for running scripts:

```bash
# Old approach - temporary environment
uvx --with playwright --with beautifulsoup4 --with httpx --with pyyaml \
    python mql5_extract.py discover-and-extract
```

**Issues:**
1. ❌ Dependencies downloaded every time (slow, wasteful)
2. ❌ Playwright browsers need reinstalling each run
3. ❌ No persistent environment across sessions
4. ❌ Long command lines with all dependencies listed

---

## ✅ The Solution

Use **persistent virtual environment** with `uv venv`:

```bash
# One-time setup
./setup.sh

# Then use forever
.venv/bin/python mql5_extract.py discover-and-extract
```

---

## 📊 Comparison: UVX vs UV

| Feature | `uvx` (old) | `uv venv` (new) |
|---------|-------------|-----------------|
| **Environment** | Temporary, deleted after execution | Persistent `.venv/` directory |
| **Setup time** | Every execution (~10-30s) | Once (~30s total) |
| **Playwright browsers** | Must reinstall each time | Installed once, reused |
| **Disk usage** | No local storage | ~100 MB in `.venv/` |
| **Command length** | Long (all deps listed) | Short (just script path) |
| **Use case** | One-off scripts, testing | Production, development |
| **Best for** | Quick experiments | This project ✅ |

---

## 🚀 Quick Start

### **Option 1: Automated Setup (Recommended)**

```bash
# One command setup
./setup.sh
```

This will:
1. Create `.venv/` virtual environment
2. Install all Python dependencies
3. Install Playwright Chromium browser
4. Verify installation

### **Option 2: Manual Setup**

```bash
# 1. Create virtual environment
uv venv

# 2. Install dependencies
uv pip install --python .venv/bin/python -r requirements.txt

# 3. Install Playwright browsers
.venv/bin/python -m playwright install chromium

# 4. Verify
.venv/bin/python mql5_extract.py --help
```

---

## 📝 Daily Usage

### **Method 1: Direct Execution (Recommended)**

No activation needed - just use full path:

```bash
# Extract all articles
.venv/bin/python mql5_extract.py discover-and-extract

# Single article
.venv/bin/python mql5_extract.py single <URL>

# Batch processing
.venv/bin/python mql5_extract.py batch urls.txt
```

### **Method 2: Activate Environment**

Traditional virtual environment workflow:

```bash
# Activate (once per terminal session)
source .venv/bin/activate

# Now use python directly
python mql5_extract.py discover-and-extract
python mql5_extract.py single <URL>
python mql5_extract.py batch urls.txt

# Deactivate when done
deactivate
```

---

## 🛠️ Maintenance

### **Update Dependencies**

```bash
# Update requirements.txt first, then:
uv pip install --python .venv/bin/python -r requirements.txt --upgrade
```

### **Clean Reinstall**

```bash
# Remove virtual environment
rm -rf .venv

# Re-run setup
./setup.sh
```

### **Add New Dependencies**

```bash
# 1. Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# 2. Install
uv pip install --python .venv/bin/python -r requirements.txt
```

---

## 📂 What Gets Ignored

The `.gitignore` already excludes:

```gitignore
# Virtual environments
.venv/
venv/
env/
```

✅ Your `.venv/` directory is **never committed** to git.

---

## 🎯 Why This Matters

### **Before (uvx - temporary)**
```bash
$ time uvx --with playwright --with httpx python script.py
# Downloads dependencies... ~15s
# Runs script... ~5s
# Deletes environment... ~1s
# Total: ~21s
```

### **After (uv venv - persistent)**
```bash
$ time .venv/bin/python script.py
# Uses cached dependencies... 0s
# Runs script... ~5s
# Total: ~5s ✅ (4x faster!)
```

---

## 📚 Additional Resources

- **UV Documentation:** https://github.com/astral-sh/uv
- **Playwright Setup:** https://playwright.dev/python/docs/intro
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html

---

## 🔧 Troubleshooting

### **Issue: `uv: command not found`**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

### **Issue: Virtual environment not activating**

```bash
# Check if .venv exists
ls -la .venv/bin/

# Recreate if needed
rm -rf .venv && ./setup.sh
```

### **Issue: Playwright browsers missing**

```bash
# Reinstall browsers
.venv/bin/python -m playwright install chromium
```

### **Issue: Import errors after activation**

```bash
# Check which python is active
which python

# Should output: /path/to/mql5/.venv/bin/python
# If not, deactivate and reactivate:
deactivate
source .venv/bin/activate
```

---

## ✅ Verification

After setup, verify everything works:

```bash
# 1. Check python location
.venv/bin/python --version
# Should output: Python 3.13.6

# 2. Check dependencies installed
.venv/bin/python -c "import playwright; import httpx; import yaml; print('✅ All dependencies OK')"

# 3. Check CLI works
.venv/bin/python mql5_extract.py --help

# 4. Test extraction (dry-run)
.venv/bin/python mql5_extract.py discover-and-extract --max-articles 1 --dry-run
```

---

## 📊 Disk Usage

Persistent virtual environment uses:

- **Virtual environment:** ~50 MB (Python + pip)
- **Dependencies:** ~30 MB (playwright, httpx, etc.)
- **Playwright browsers:** ~150 MB (Chromium only)
- **Total:** ~230 MB

**Note:** This is reused across all sessions, making it much more efficient than temporary `uvx` environments.

---

## 🎉 Summary

| Before | After |
|--------|-------|
| `uvx --with ... python script.py` | `.venv/bin/python script.py` |
| Slow (~20s overhead) | Fast (~0s overhead) |
| Temporary environment | Persistent environment |
| Browsers reinstalled each time | Browsers cached |
| Not recommended for production | ✅ Production ready |
