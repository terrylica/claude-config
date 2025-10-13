# MQL5 Article Extraction System

Production-grade system for extracting MQL5 trading articles with proper formatting, syntax highlighting, and comprehensive metadata.

**Use Case:** Training data collection for algorithmic trading seq-2-seq models

---

## 🚀 Quick Start

```bash
# 1. One-time setup (creates persistent virtual environment)
./setup.sh

# 2. Extract all articles
.venv/bin/python mql5_extract.py discover-and-extract
```

That's it! 🎉

---

## ✨ Features

- ✅ **Elegant markdown formatting** with MQL5 syntax highlighting
- ✅ **Local image downloads** with descriptive filenames
- ✅ **Batch processing** with checkpoint-based resume
- ✅ **Retry logic** with exponential backoff
- ✅ **Quality validation** (word count, code blocks)
- ✅ **Comprehensive logging** (file + console)
- ✅ **Statistics generation** (word count, images, code blocks)
- ✅ **Rate limiting** (respectful to mql5.com servers)

---

## 📊 Output Structure

```
mql5_articles/
├── {user_id}/                  # User folder (numeric ID or username)
│   ├── article_{id}/
│   │   ├── article_{id}.md    # Clean markdown with syntax highlighting
│   │   ├── metadata.json      # Extraction metadata
│   │   ├── images/            # Local images
│   │   └── images_manifest.json
│   └── article_{id}/
├── extraction_summary.json     # Batch statistics
└── extraction.log             # Detailed logs
```

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete production guide
- **[docs/dependency_management.md](docs/dependency_management.md)** - UV vs UVX comparison
- **[docs/ood_authors_research.md](docs/ood_authors_research.md)** - OOD detection author research
- **[docs/attachment_extraction_design.md](docs/attachment_extraction_design.md)** - Attachment extraction architecture
- **[docs/attachment_extraction_test_results.md](docs/attachment_extraction_test_results.md)** - Test validation results

---

## 🛠️ Usage Examples

### **Extract All Articles**
```bash
.venv/bin/python mql5_extract.py discover-and-extract
```

### **Extract Single Article**
```bash
.venv/bin/python mql5_extract.py single https://www.mql5.com/en/articles/19625
```

### **Batch Processing**
```bash
# Create URL file
.venv/bin/python mql5_extract.py discover-and-extract --save-urls urls.txt --dry-run

# Extract all
.venv/bin/python mql5_extract.py batch urls.txt

# Resume interrupted extraction
.venv/bin/python mql5_extract.py batch urls.txt --resume
```

### **Custom User Extraction**
```bash
.venv/bin/python mql5_extract.py discover-and-extract --user-id jslopes
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:
- Output directory
- Browser timeout
- Retry attempts
- Rate limiting
- Quality validation thresholds
- Logging levels

---

## 🔧 Maintenance

### **Update Dependencies**
```bash
uv pip install --python .venv/bin/python -r requirements.txt --upgrade
```

### **Clean Reinstall**
```bash
rm -rf .venv && ./setup.sh
```

---

## 📊 Quality Metrics

Extracted content includes:
- **~400,000+ words** of technical articles
- **100% accurate MQL5 syntax detection** (fixed in v3.0.0)
- **Local images** with automatic naming
- **Complete metadata** (author, date, views, ratings)

---

## 🎯 Why Persistent Virtual Environment?

We use **`uv venv`** (persistent) instead of **`uvx`** (temporary):

| Feature | `uvx` | `uv venv` |
|---------|-------|-----------|
| Setup time | Every run (~15s) | Once (~30s) |
| Playwright browsers | Reinstall each time | Cached |
| Command length | Very long | Short |
| Best for | One-off scripts | **This project** ✅ |

**Result:** 4x faster execution after initial setup

See [docs/dependency_management.md](docs/dependency_management.md) for details.

---

## 📦 System Requirements

- **uv** (Python package manager)
- **Python 3.13+** (auto-installed by uv)
- **~230 MB disk space** for virtual environment
- **Internet connection** for article downloads

---

## 🆘 Troubleshooting

### **Issue: `uv: command not found`**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **Issue: Extraction fails with timeout**
```bash
# Increase timeout in config.yaml
extraction:
  timeout_ms: 60000  # 60 seconds
```

### **Issue: Browser not found**
```bash
.venv/bin/python -m playwright install chromium
```

See [CLAUDE.md](CLAUDE.md) for complete troubleshooting guide.

---

## 📈 Version History

- **v3.0.0** (2025-10-01) - Fixed MQL5 syntax detection (100% accuracy)
- **v2.0.0** (2025-09-30) - Production release with CLI, logging, retry logic
- **v1.0.0** (2025-09-29) - Initial release

---

## 📄 License

See repository license for details.

---

**Built with:** Python, Playwright, BeautifulSoup, httpx, uv
