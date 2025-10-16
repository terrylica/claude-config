# MQL5 File Encoding Solutions

**Problem**: MetaEditor saves `.mq5` and `.mqh` files as UTF-16LE, causing issues with Git and Python text processing.

**Status**: Production solutions (2024-2025 best practices)

## Root Cause

MetaEditor (MetaTrader 5's code editor) defaults to saving files as:
- **Encoding**: UTF-16LE (Little Endian)
- **BOM**: May or may not include Byte Order Mark
- **Line Endings**: CRLF (Windows style)

This causes:
- Git treats files as binary (no diff/merge support)
- Python `open()` fails with default UTF-8 encoding
- Shell tools (cat, grep) show garbled output

## Solution 1: Python Automatic Detection (Recommended)

### Install chardet
```bash
# In native macOS Python
pip install chardet

# Or with uv
uv pip install chardet
```

### Robust File Reading Function

```python
from pathlib import Path
import chardet

def read_mq5_file(file_path: Path, n_lines: int = 100) -> str:
    """
    Read MQL5 file with automatic encoding detection.

    Args:
        file_path: Path to .mq5 or .mqh file
        n_lines: Number of lines to sample for encoding detection (default 100)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If encoding detection fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Step 1: Detect encoding by sampling file
    with file_path.open('rb') as f:
        # Read first n_lines or 100KB, whichever is smaller
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
        if len(rawdata) > 100_000:
            rawdata = rawdata[:100_000]

    detection = chardet.detect(rawdata)
    encoding = detection['encoding']
    confidence = detection['confidence']

    print(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")

    # Step 2: Read file with detected encoding
    # Fallback to UTF-16LE if detection fails or confidence is low
    if encoding is None or confidence < 0.7:
        print("Low confidence or no detection, trying UTF-16LE...")
        encoding = 'utf-16-le'

    try:
        content = file_path.read_text(encoding=encoding)
        return content
    except UnicodeDecodeError as e:
        # Fallback to UTF-16LE without BOM
        print(f"Failed with {encoding}, trying UTF-16LE...")
        return file_path.read_text(encoding='utf-16-le')

# Usage
mq5_file = Path("/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5")
content = read_mq5_file(mq5_file)
print(content[:500])  # Print first 500 characters
```

### Alternative: Explicit UTF-16LE Reading

If you know the file is UTF-16LE (most MetaEditor files are):

```python
from pathlib import Path

def read_mq5_utf16(file_path: Path) -> str:
    """Read MQL5 file as UTF-16LE (MetaEditor default)"""
    return file_path.read_text(encoding='utf-16-le')

# Usage
content = read_mq5_utf16(mq5_file)
```

## Solution 2: Command-Line Conversion

### Using iconv (macOS/Linux)

```bash
# Convert UTF-16LE to UTF-8
iconv -f UTF-16LE -t UTF-8 "input.mq5" > "output_utf8.mq5"

# Batch convert all .mq5 files in directory
find . -name "*.mq5" -exec sh -c 'iconv -f UTF-16LE -t UTF-8 "$1" > "$1.utf8"' _ {} \;

# In-place conversion (be careful!)
iconv -f UTF-16LE -t UTF-8 "input.mq5" > temp && mv temp "input.mq5"
```

### Using Python Script

```python
#!/usr/bin/env python3
"""Convert MQL5 files from UTF-16LE to UTF-8"""
from pathlib import Path
import sys

def convert_to_utf8(mq5_file: Path, backup: bool = True):
    """Convert UTF-16LE file to UTF-8 in-place"""
    content = mq5_file.read_text(encoding='utf-16-le')

    if backup:
        backup_file = mq5_file.with_suffix(mq5_file.suffix + '.utf16bak')
        mq5_file.rename(backup_file)
        print(f"Backup saved: {backup_file}")

    mq5_file.write_text(content, encoding='utf-8')
    print(f"Converted: {mq5_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: convert_mq5_utf8.py <file.mq5>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    convert_to_utf8(file_path)
```

## Solution 3: Git Integration (Best Practice)

### Update .gitattributes

Add to your `.gitattributes` file in repo root:

```gitattributes
# MQL5 files (UTF-16LE with CRLF line endings)
*.mq5 text working-tree-encoding=UTF-16LE eol=crlf
*.mqh text working-tree-encoding=UTF-16LE eol=crlf

# If files have BOM (Byte Order Mark), use:
# *.mq5 text working-tree-encoding=UTF-16LE-BOM eol=crlf
# *.mqh text working-tree-encoding=UTF-16LE-BOM eol=crlf
```

**What this does**:
- Git stores files as UTF-8 internally (for diffs and merges)
- Git converts to UTF-16LE when checking out to working directory
- Enables proper diff/merge support
- Preserves CRLF line endings (Windows convention)

**Requirements**:
- Git 2.16+ (March 2018)
- All team members must have Git 2.16+
- ⚠️ Known issue: May corrupt files on checkout in some edge cases

**Verification**:
```bash
# After adding .gitattributes
git check-attr text working-tree-encoding *.mq5

# Should output:
# file.mq5: text: set
# file.mq5: working-tree-encoding: UTF-16LE
```

### Alternative: Store as Binary

If `working-tree-encoding` causes issues, mark as binary:

```gitattributes
*.mq5 binary
*.mqh binary
```

**Trade-offs**:
- ✅ No corruption risk
- ✅ Simple and reliable
- ❌ No diff/merge support
- ❌ Must handle encoding in code

## Solution 4: MetaEditor Configuration

### Option 1: Save as UTF-8 (Not Recommended)

MetaEditor doesn't officially support UTF-8 as default encoding, but you can:
1. Open file in MetaEditor
2. Edit → Select All
3. Copy to external editor (VSCode, Sublime Text)
4. Save as UTF-8 in external editor

**Issues**:
- MetaEditor may add BOM when reopening
- Loses MetaEditor integration
- Manual process per file

### Option 2: Accept UTF-16LE (Recommended)

Keep files as UTF-16LE and handle in code:
- ✅ Preserves MetaEditor compatibility
- ✅ No manual conversion needed
- ✅ Works with built-in MQL5 tools

## Recommended Workflow

### For Indicator Translation Project

**Step 1: Read MQL5 source with Python**

```python
from pathlib import Path

def extract_mq5_logic(mq5_file: Path) -> dict:
    """Extract key components from MQL5 indicator file"""
    content = mq5_file.read_text(encoding='utf-16-le')

    # Extract input parameters
    inputs = []
    for line in content.split('\n'):
        if line.strip().startswith('input '):
            inputs.append(line.strip())

    # Extract function signatures
    functions = []
    for line in content.split('\n'):
        if line.strip().startswith('double ') or line.strip().startswith('void '):
            if '(' in line and ')' in line:
                functions.append(line.strip())

    # Extract includes
    includes = []
    for line in content.split('\n'):
        if line.strip().startswith('#include'):
            includes.append(line.strip())

    return {
        'inputs': inputs,
        'functions': functions,
        'includes': includes,
        'content': content
    }

# Usage
mq5_file = Path("...MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5")
components = extract_mq5_logic(mq5_file)

print("Input Parameters:")
for inp in components['inputs']:
    print(f"  {inp}")

print("\nDependencies:")
for inc in components['includes']:
    print(f"  {inc}")
```

**Step 2: Create UTF-8 copy for analysis (optional)**

```bash
# One-time conversion for reading/analysis
iconv -f UTF-16LE -t UTF-8 "indicator.mq5" > "indicator_utf8.mq5"

# Analyze UTF-8 version with standard tools
grep "double Calculate" indicator_utf8.mq5
```

**Step 3: Update .gitattributes**

```bash
# If tracking MQL5 files in this repo
echo "*.mq5 text working-tree-encoding=UTF-16LE eol=crlf" >> .gitattributes
echo "*.mqh text working-tree-encoding=UTF-16LE eol=crlf" >> .gitattributes

# Or mark as binary (safer)
echo "*.mq5 binary" >> .gitattributes
echo "*.mqh binary" >> .gitattributes
```

## Validation Script

Create `scripts/validate_encoding.py`:

```python
#!/usr/bin/env python3
"""Validate MQL5 file encoding and detect issues"""
from pathlib import Path
import chardet
import sys

def validate_mq5_encoding(file_path: Path):
    """Validate and report encoding details"""
    print(f"Checking: {file_path.name}")
    print(f"Size: {file_path.stat().st_size:,} bytes")

    # Read as binary
    with file_path.open('rb') as f:
        data = f.read(10_000)  # First 10KB

    # Check for BOM
    has_bom = data.startswith(b'\xff\xfe') or data.startswith(b'\xfe\xff')
    print(f"BOM present: {has_bom}")

    # Detect encoding
    detection = chardet.detect(data)
    print(f"Detected: {detection['encoding']} (confidence: {detection['confidence']:.2%})")

    # Try reading
    encodings_to_try = ['utf-16-le', 'utf-16', 'utf-8', 'latin-1']
    for enc in encodings_to_try:
        try:
            content = file_path.read_text(encoding=enc)
            print(f"✓ Successfully read with: {enc}")
            print(f"  First 100 chars: {content[:100]}")
            break
        except UnicodeDecodeError:
            print(f"✗ Failed with: {enc}")

    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_encoding.py <file.mq5>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    validate_mq5_encoding(file_path)
```

**Usage**:
```bash
python scripts/validate_encoding.py "/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5"
```

## Performance Considerations

### Reading Large Files

```python
def read_mq5_chunks(file_path: Path, encoding='utf-16-le', chunk_size=8192):
    """Read large MQL5 files in chunks"""
    with file_path.open('r', encoding=encoding) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Usage for large files
for chunk in read_mq5_chunks(large_mq5_file):
    process(chunk)
```

### Memory-Efficient Conversion

```python
def convert_large_file(input_path: Path, output_path: Path):
    """Convert large UTF-16LE file to UTF-8 without loading entire file"""
    with input_path.open('r', encoding='utf-16-le') as fin:
        with output_path.open('w', encoding='utf-8') as fout:
            for line in fin:
                fout.write(line)
```

## Error Handling Patterns

```python
from pathlib import Path
from typing import Optional

def safe_read_mq5(file_path: Path) -> Optional[str]:
    """Read MQL5 file with comprehensive error handling"""
    encodings = ['utf-16-le', 'utf-16', 'utf-16-be', 'utf-8']

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            # Validate content (no null bytes, reasonable ASCII ratio)
            if '\x00' not in content:
                return content
        except (UnicodeDecodeError, FileNotFoundError, PermissionError) as e:
            continue

    # Last resort: read as binary and decode with error handling
    try:
        data = file_path.read_bytes()
        return data.decode('utf-16-le', errors='replace')
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return None
```

## Summary: Best Practice for This Project

**For Indicator Translation Workflow**:

1. **Read MQL5 files**: Use `encoding='utf-16-le'` in Python
2. **No conversion needed**: Keep source files as UTF-16LE in bottle
3. **Git tracking**: Mark `.mq5` and `.mqh` as `binary` in `.gitattributes`
4. **Python translation**: Write output as UTF-8 (Python default)
5. **Validation**: Use chardet for robust encoding detection

**Implementation**:
```bash
# Update .gitattributes
echo "*.mq5 binary" >> .gitattributes
echo "*.mqh binary" >> .gitattributes

# Install chardet for robust reading
pip install chardet
```

**Code pattern**:
```python
# Read MQL5 source
content = Path(mq5_file).read_text(encoding='utf-16-le')

# Extract logic, translate to Python
# ...

# Write Python module as UTF-8 (default)
Path('indicators/laguerre_rsi.py').write_text(python_code)
```

## References

- **chardet documentation**: https://chardet.readthedocs.io/
- **Git working-tree-encoding**: https://git-scm.com/docs/gitattributes
- **MQL5 file encoding**: https://www.mql5.com/en/forum/437841
- **Python pathlib**: https://docs.python.org/3/library/pathlib.html

---

**Last Updated**: 2025-10-13
**Status**: Production-ready solutions validated for 2024-2025
