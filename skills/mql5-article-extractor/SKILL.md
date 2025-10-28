---
name: mql5-article-extractor
description: Extract trading strategy articles AND official documentation from mql5.com ONLY. Handles user articles, official Python API docs, TICK data research. Use when user mentions MQL5, MetaTrader, trading articles, Python MT5 API, algorithmic trading content. NOT for other websites.
allowed-tools: Read, Bash, Grep, Glob
---

# MQL5 Article Extractor

Extract technical trading articles from mql5.com for training data collection. **Scope limited to mql5.com domain only.**

## Scope Boundaries

**✅ VALID requests:**

- "Extract this mql5.com article: https://www.mql5.com/en/articles/19625"
- "Get all articles from MQL5 user 29210372"
- "Download trading articles from mql5.com"
- "Extract 5 MQL5 articles for testing"

**❌ OUT OF SCOPE:**

- "Extract from yahoo.com" → NOT SUPPORTED (mql5.com only)
- "Scrape news from reuters" → NOT SUPPORTED (mql5.com only)
- "Get stock data from Bloomberg" → NOT SUPPORTED (mql5.com only)

If user requests non-mql5.com extraction, respond: "This skill extracts articles from mql5.com ONLY. For other sites, use different tools."

## Repository Location

Working directory: `/Users/terryli/eon/mql5`

Always execute commands from this directory:

```bash
cd /Users/terryli/eon/mql5
```

## Valid Input Types

### 1. Article URL (Most Specific)

**Format**: `https://www.mql5.com/en/articles/[ID]`
**Example**: `https://www.mql5.com/en/articles/19625`
**Action**: Extract single article

### 2. User ID (Numeric or Username)

**Format**: Numeric (e.g., `29210372`) or username (e.g., `jslopes`)
**Source**: From mql5.com profile URL
**Action**: Auto-discover and extract all user's articles

### 3. URL List File

**Format**: Text file with one URL per line
**Action**: Batch process multiple articles

### 4. Vague Request

If user says "extract mql5 articles" without specifics, prompt for:

1. Article URL OR User ID
2. Quantity limit (for testing)
3. Output location preference

## Extraction Modes

### Mode 1: Single Article

**When**: User provides one article URL
**Command**:

```bash
.venv/bin/python mql5_extract.py single https://www.mql5.com/en/articles/[ID]
```

**Output**: `mql5_articles/[user_id]/article_[ID]/`

### Mode 2: Batch from File

**When**: User has URL file or wants multiple specific articles
**Command**:

```bash
.venv/bin/python mql5_extract.py batch urls.txt
```

**Checkpoint**: Auto-saves progress, resumable with `--resume`

### Mode 3: Auto-Discovery

**When**: User provides MQL5 user ID or username
**Command**:

```bash
.venv/bin/python mql5_extract.py discover-and-extract --user-id [USER_ID]
```

**Discovers**: All published articles for that user

## Official Documentation Extraction

### Mode 4: Official Docs (Single Page)

**When**: User wants official MQL5/Python MetaTrader5 documentation (not user articles)

**Scripts Location**: `/scripts/official_docs_extractor.py`

**Command**:

```bash
cd /Users/terryli/eon/mql5
curl -s "https://www.mql5.com/en/docs/python_metatrader5/mt5copyticksfrom_py" > page.html
.venv/bin/python scripts/official_docs_extractor.py page.html "URL"
```

**Output**: Markdown file with source URL, HTML auto-deleted

### Mode 5: Batch Official Docs

**When**: User wants all Python MetaTrader5 API documentation

**Scripts Location**: `/scripts/extract_all_python_docs.sh`

**Command**:

```bash
cd /Users/terryli/eon/mql5
./scripts/extract_all_python_docs.sh
```

**Result**: 32 official API function docs extracted

### Key Differences from User Articles

- Different HTML structure (div.docsContainer vs div.content)
- Inline tables and code examples preserved
- No images (documentation only)
- Simpler file naming (function_name.md)
- Source URLs embedded in markdown
- HTML files auto-deleted after conversion

## Data Sources

### User Collections

- **Primary Source**: https://www.mql5.com/en/users/29210372/publications
- **Author**: Allan Munene Mutiiria (77 technical articles)
- **Content Type**: MQL5 trading strategy implementations

### Topic Collections

#### TICK Data Research (`mql5_articles/tick_data/`)

- **Official Docs**: 3 Python MetaTrader5 TICK functions
  - `copy_ticks_from`, `copy_ticks_range`, `symbol_info_tick`
- **User Articles**: 9 articles on TICK data handling, storage, and analysis
- **Research Documentation**: `/docs/tick_research/` (4 files)

#### Python Integration (`mql5_articles/python_integration/`)

- **Official Docs**: 32 complete Python MetaTrader5 API functions
  - Connection, account info, symbol management, historical data, orders, positions
- **User Articles**: 15 implementation guides
  - ML/AI integration, trading automation, data analysis, socket communication
- **Research Documentation**: `/docs/python_research/` (1 file)

## Input Validation Workflow

When user makes vague request:

1. **Ask for domain confirmation** (if ambiguous):
   - "Is this for mql5.com articles? (This tool only works with mql5.com)"

2. **Request specific input**:
   - "Please provide one of:
     - Article URL: https://www.mql5.com/en/articles/[ID]
     - User ID: numeric or username from mql5.com profile
     - Path to file with article URLs"

3. **Suggest scope limits**:
   - "For testing, use --max-articles N to limit quantity"
   - "For production, omit limit to extract all"

4. **Confirm before large operations**:
   - If user says "all articles" → ask "User X has Y articles. Proceed with full extraction?"

## Common Usage Examples

### Example 1: Vague → Specific (Guided)

**User**: "Extract some trading articles"
**Skill**: "This extracts from mql5.com only. Please specify:

1. Article URL (https://www.mql5.com/en/articles/[ID])
2. MQL5 user ID (e.g., 29210372)
3. Path to URL file

Which do you have?"

**User**: "User 29210372"
**Skill**:

```bash
cd /Users/terryli/eon/mql5
.venv/bin/python mql5_extract.py discover-and-extract --user-id 29210372
```

### Example 2: URL Provided (Direct)

**User**: "Extract https://www.mql5.com/en/articles/19625"
**Skill**:

```bash
cd /Users/terryli/eon/mql5
.venv/bin/python mql5_extract.py single https://www.mql5.com/en/articles/19625
```

### Example 3: Out of Scope (Reject)

**User**: "Extract articles from reuters.com"
**Skill**: "This skill extracts from mql5.com ONLY. Reuters is not supported. Use general web scraping tools instead."

### Example 4: Testing (Limited)

**User**: "Test with 5 articles from user jslopes"
**Skill**:

```bash
cd /Users/terryli/eon/mql5
.venv/bin/python mql5_extract.py discover-and-extract --user-id jslopes --max-articles 5
```

## Output Structure

All extractions go to:

```
mql5_articles/
├── 29210372/                 # User collections (numeric ID or username)
│   └── article_[ID]/
│       ├── article_[ID].md
│       ├── metadata.json
│       └── images/
├── tick_data/                # Topic collections
│   ├── official_docs/        # 3 Python MT5 TICK functions
│   │   ├── copy_ticks_from.md
│   │   ├── copy_ticks_range.md
│   │   └── symbol_info_tick.md
│   └── user_articles/        # 9 articles by author
│       ├── artmedia70/article_[ID]/
│       ├── lazymesh/article_[ID]/
│       └── ...
├── python_integration/       # Topic collections
│   ├── official_docs/        # 32 MT5 Python API functions
│   │   ├── mt5initialize_py.md
│   │   ├── mt5copyticksfrom_py.md
│   │   └── ...
│   └── user_articles/        # 15 implementation articles
│       ├── dmitrievsky/article_[ID]/
│       ├── koshtenko/article_[ID]/
│       └── ...
├── extraction_summary.json
└── extraction.log
```

**Content Organization:**

- **User Collections** (e.g., `29210372/`): Articles by specific authors
- **Topic Collections** (e.g., `tick_data/`, `python_integration/`): Organized by research area
  - `official_docs/`: Official MQL5 documentation pages
  - `user_articles/`: Community-contributed articles by author

## Quality Verification

After extraction, verify outputs:

````bash
# Count articles extracted
find mql5_articles/ -name "article_*.md" | wc -l

# Check MQL5 code blocks
grep -r "```mql5" mql5_articles/ | wc -l

# View summary
cat mql5_articles/extraction_summary.json
````

## Error Handling

If extraction fails:

1. Check logs: `tail -f logs/extraction.log`
2. Verify URL is mql5.com domain
3. Check internet connection
4. For batch: use `--resume` to continue from checkpoint

## CLI Options Reference

**Global options** (before subcommand):

- `--output DIR` - Custom output directory
- `--config FILE` - Custom config file
- `--verbose` - Debug logging
- `--quiet` - Error-only logging

**Batch options**:

- `--resume` - Continue from checkpoint
- `--no-checkpoint` - Disable checkpoint system
- `--max-articles N` - Limit to N articles

**Discovery options**:

- `--user-id ID` - MQL5 user ID or username
- `--save-urls FILE` - Save discovered URLs to file
- `--max-articles N` - Limit extraction

## Input Bounding Rules

**Rule 1: Domain Validation**
Only accept `mql5.com` URLs. Reject all other domains immediately.

**Rule 2: Input Type Classification**
Classify user input as:

- URL pattern → single extraction
- Numeric/username → discovery
- File path → batch
- Ambiguous → prompt for clarification

**Rule 3: Scope Enforcement**
If user mentions keywords like "yahoo", "google", "reuters", "bloomberg" → respond with scope limitation message.

**Rule 4: Confirmation for Large Operations**
If discovery would extract >10 articles, confirm with user before proceeding.

## Security Notes

- Only executes within `/Users/terryli/eon/mql5`
- Uses virtual environment `.venv/bin/python`
- No network tools allowed (uses Playwright internally)
- Rate limiting enforced (2s between articles)
- Checkpoint files in project root only

## Typical Interaction Flow

1. User mentions MQL5 or trading articles
2. Skill activates and bounds request to mql5.com
3. If input vague → prompt for specifics (URL, user ID, or file)
4. Validate input type and domain
5. Execute appropriate command
6. Show output location and verification commands

## Success Indicators

After execution, report:

- Number of articles extracted
- Total word count
- Code blocks found
- Images downloaded
- Output directory location
- Link to extraction summary

---

**Remember**: This skill ONLY works with mql5.com. Any request for other domains is out of scope and should be rejected with a clear message.
