# Cache Directory

Provider-specific temporary files for performance optimization. **Never commit to git.**

## Structure

```
cache/
├── binance/
│   └── api_responses/     # Cached API responses
└── metadata/
    └── symbol_info.json   # Tier-1 symbol discovery cache
```

## Cache Policies

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
rm -rf cache/*/{binance,metadata}/*
```

### Automated (Future)
```bash
cargo run --bin cache-manager -- --clear-old
```

## Performance Impact

- **With cache**: API responses cached, rate limits avoided
- **Without cache**: Re-fetch on every run (slower, may hit rate limits)
- **Recommendation**: Enable for batch processing, disable for one-off queries

## Git Policy

- **NEVER** commit to git (enforced by `.gitignore`)
- Cache is **regenerable** - treat as disposable
