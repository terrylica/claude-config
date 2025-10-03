# Cache Directory

Provider-specific temporary files for performance optimization. **Never commit to git.**

## Structure

```
cache/
├── binance/
│   └── api_responses/     # Cached API responses
├── dukascopy/
│   └── decompressed/      # Decompressed .bi5 → parsed ticks
└── metadata/
    └── symbol_info.json   # Tier-1 symbol discovery cache
```

## Cache Policies

### Dukascopy
- **Purpose**: Cache decompressed .bi5 files to avoid repeated LZMA decompression
- **Location**: `cache/dukascopy/decompressed/[SYMBOL]/YYYY/MM/DD/HHh_ticks.bin`
- **Retention**: 30 days (auto-cleanup recommended)
- **Size**: ~4× larger than compressed (72KB → 288KB per hour)

### Binance
- **Purpose**: Rate-limit friendly API response caching
- **Location**: `cache/binance/api_responses/[endpoint]/[params_hash].json`
- **Retention**: 7 days
- **Note**: Symbol info rarely changes, cache aggressively

### Metadata
- **Purpose**: Tier-1 symbol discovery, instrument configs
- **Location**: `cache/metadata/symbol_info.json`
- **Retention**: Refresh weekly
- **Fallback**: Re-fetch if missing (non-critical)

## Cleanup

### Manual
```bash
# Remove all cache
rm -rf cache/*/{binance,dukascopy,metadata}/*

# Remove expired Dukascopy cache (>30 days)
find cache/dukascopy/decompressed -type f -mtime +30 -delete
```

### Automated (Future)
```bash
cargo run --bin cache-manager -- --clear-old
```

## Performance Impact

- **With cache**: LZMA decompression skipped (~50ms saved per hour)
- **Without cache**: Re-decompress every run (acceptable for one-time analysis)
- **Recommendation**: Enable for batch processing, disable for one-off queries

## Git Policy

- **NEVER** commit to git (enforced by `.gitignore`)
- Cache is **regenerable** - treat as disposable
