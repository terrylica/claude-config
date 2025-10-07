# Dukascopy Rate Limit Mitigation

**Version**: 1.0.0
**Created**: 2025-10-03
**Status**: IMPLEMENTED
**Completed**: 2025-10-03
**Type**: NON-BREAKING ENHANCEMENT
**Supersedes**: None
**References**:
- `tests/dukascopy_eurusd_adversarial_audit.rs` (audit_7 test)
- `src/providers/dukascopy/fetcher.rs` (HTTP client)

---

## Problem Statement

**Observed Behavior**: 27/120 hour fetches failed with HTTP 503 Service Unavailable

**Root Cause**: Consecutive requests to datafeed.dukascopy.com without delay triggers rate limiting
- Current: 120 requests sequentially without delay (~120 requests in 20 seconds)
- Dukascopy limit: Undocumented, estimated ~10-20 requests/second sustained

**Evidence**:
```
⚠️ Failed to fetch 2024-01-18 11:00: HTTP 503 Service Unavailable
⚠️ Failed to fetch 2024-01-18 12:00: HTTP 503 Service Unavailable
(27 consecutive failures after ~93 successful fetches)
```

**Industry Standard** (dukascopy-node library):
- Batch size: 10 requests
- Pause between batches: 1000ms
- Effective rate: ~10 requests/second

---

## Proposed Solution

### Approach: Add Inter-Request Delay

**Implementation**: Insert `tokio::time::sleep()` between each `fetch_hour()` call

**Delay Value**: 100ms (conservative, allows 10 requests/second)

**Location**: `tests/dukascopy_eurusd_adversarial_audit.rs:420` (audit_7 test loop)

**Alternative Considered**: Retry logic with exponential backoff
- **Rejected**: Adds complexity, doesn't prevent 503s, only reacts to them
- **Rationale**: Prevention (delay) superior to cure (retry) for known rate limits

---

## Technical Specification

### Change 1: Add Delay After Each Fetch

**File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

**Current Code** (lines 418-430):
```rust
for day in 15..=19 {
    for hour in 0..=23 {
        match fetcher.fetch_hour(2024, 1, day, hour).await {
            Ok(mut ticks) => {
                println!("  ✅ Fetched {} ticks for 2024-01-{:02} {:02}:00", ticks.len(), day, hour);
                all_ticks.append(&mut ticks);
            }
            Err(e) => {
                println!("  ⚠️ Failed to fetch 2024-01-{:02} {:02}:00: {}", day, hour, e);
            }
        }
    }
}
```

**New Code**:
```rust
for day in 15..=19 {
    for hour in 0..=23 {
        match fetcher.fetch_hour(2024, 1, day, hour).await {
            Ok(mut ticks) => {
                println!("  ✅ Fetched {} ticks for 2024-01-{:02} {:02}:00", ticks.len(), day, hour);
                all_ticks.append(&mut ticks);
            }
            Err(e) => {
                println!("  ⚠️ Failed to fetch 2024-01-{:02} {:02}:00: {}", day, hour, e);
                // ERROR PROPAGATION: Fail fast on HTTP errors
                panic!("Dukascopy fetch failed after {} successful fetches. Error: {}", all_ticks.len(), e);
            }
        }

        // Rate limit mitigation: 100ms delay between requests
        // Industry standard: 10 req/sec = 100ms spacing
        // Dukascopy observed tolerance: ~10-20 req/sec sustained
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}
```

**Rationale**:
- Error propagation: `panic!` on fetch failure (no silent handling)
- Delay placement: After each fetch (including failures)
- Delay value: 100ms = 10 req/sec (conservative, proven safe by dukascopy-node)

### Change 2: Update Expected Test Duration

**File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

**Impact**: Test duration increases from ~20 minutes to ~22 minutes
- Fetch time: ~20 minutes (120 HTTP requests)
- Added delays: 120 × 100ms = 12 seconds
- Processing time: ~2 minutes (357K ticks × 8 thresholds)

**No timeout changes needed**: Test already handles long duration

---

## SLO Definitions

### Availability
- **Target**: 100% fetch success rate (0/120 failures)
- **Current**: 77.5% (93/120 success, 27 failures)
- **Metric**: Fetch failure count = 0
- **Validation**: Assert no "Failed to fetch" messages in test output

### Correctness
- **Target**: All fetched ticks valid (no data corruption)
- **Validation**: Existing temporal integrity checks pass
- **Metric**: `assert!(bars_1.iter().all(|b| monotonic_timestamp))`
- **Invariant**: Delay does not affect data content

### Observability
- **Target**: Clear visibility into rate limit mitigation
- **Metric**: Log each delay invocation with request count
- **Output**: `⏱️  Rate limit delay: 100ms (request 94/120)`
- **Validation**: Delay logs present in test output

### Maintainability
- **Target**: Single source of truth for delay configuration
- **Implementation**: Extract delay as named constant
- **Constant**: `const DUKASCOPY_RATE_LIMIT_DELAY_MS: u64 = 100;`
- **Location**: Top of `audit_7_real_eurusd_statistical_properties` function

---

## Implementation Plan

### Phase 1: Add Rate Limit Delay

**File**: `tests/dukascopy_eurusd_adversarial_audit.rs`

**Steps**:
1. Add constant: `const DUKASCOPY_RATE_LIMIT_DELAY_MS: u64 = 100;`
2. Add delay after each `fetch_hour()` call
3. Add observability log: `println!("⏱️  Rate limit delay: {}ms", DUKASCOPY_RATE_LIMIT_DELAY_MS);`
4. Change error handling from `println!` to `panic!` (fail fast)

### Phase 2: Validation

**Test Execution**:
```bash
cargo test --test dukascopy_eurusd_adversarial_audit audit_7 -- --ignored --nocapture
```

**Success Criteria**:
- ✅ 120/120 fetches successful (0 failures)
- ✅ 357,859+ ticks fetched (no data loss from previous run)
- ✅ All temporal integrity checks pass
- ✅ Delay logs visible in output

**Failure Scenarios**:
- ❌ Any HTTP 503 errors → Increase delay to 200ms
- ❌ Other HTTP errors → Investigate root cause (not rate limit)
- ❌ Test timeout → Increase delay incrementally until stable

### Phase 3: Documentation Update

**Files to Update**:
1. `docs/NEXT_STEPS.md` - Remove Dukascopy network reliability from Known Issues
2. `docs/planning/dukascopy-eurusd-audit-implementation.md` - Add rate limit mitigation section
3. This file - Update status to COMPLETE after validation

---

## Risk Assessment

### Risk 1: 100ms Delay Insufficient
**Likelihood**: Low (dukascopy-node uses 100ms/req successfully)
**Impact**: Medium (503 errors persist)
**Mitigation**: Incremental increase to 200ms if failures occur
**Detection**: Test output shows "Failed to fetch" messages

### Risk 2: Test Duration Excessive
**Likelihood**: Low (only +12 seconds)
**Impact**: Low (test is `#[ignore]`, manual execution only)
**Mitigation**: None required (acceptable for ignored tests)

### Risk 3: Delay Affects Data Quality
**Likelihood**: None (HTTP GET is stateless)
**Impact**: N/A
**Validation**: Compare tick counts pre/post change (should be identical)

---

## Alternative Approaches Considered

### Alternative 1: Retry with Exponential Backoff
**Approach**: Catch 503, retry with increasing delays (100ms, 200ms, 400ms, ...)
**Pros**: Industry standard for transient failures
**Cons**:
- Reacts to failures instead of preventing them
- Increases test complexity (retry state machine)
- Total test time unpredictable
**Rejected**: Prevention (delay) simpler and more reliable

### Alternative 2: Batch Requests
**Approach**: Group 10 requests, pause 1000ms between batches
**Pros**: Matches dukascopy-node exactly
**Cons**: More complex loop structure
**Rejected**: Equivalent to 100ms/request, no benefit

### Alternative 3: Parallel Requests with Semaphore
**Approach**: Use `tokio::sync::Semaphore` to limit concurrency to 10
**Pros**: Faster overall (parallelism)
**Cons**:
- More complex (semaphore + async coordination)
- May still trigger rate limit (burst traffic)
**Rejected**: Over-engineered for single test

### Selected Approach: Simple Sequential Delay
**Rationale**:
- Minimal code change (1 line)
- Proven effective (industry standard)
- Predictable behavior
- Easy to adjust if needed

---

## Success Criteria

### Must Have (P0)
- ✅ Zero HTTP 503 errors (100% fetch success rate)
- ✅ All 120 hours fetched successfully
- ✅ Temporal integrity validation passes
- ✅ Test completes without panic

### Should Have (P1)
- ✅ Test duration < 25 minutes
- ✅ Observability logs present
- ✅ Documentation updated

### Nice to Have (P2)
- ✅ Benchmark delay values (100ms vs 200ms)
- ✅ Extract delay to configuration file

---

## Execution Checklist

**Pre-Implementation**:
- [x] Review this plan for completeness
- [x] Verify tokio::time is available in test dependencies
- [x] Baseline current test results (77.5% success rate, 27/120 failures)

**Implementation**:
- [x] Add DUKASCOPY_RATE_LIMIT_DELAY_MS constant (line 411)
- [x] Add tokio::time::sleep() after each fetch (line 448)
- [x] Change error println! to panic! (lines 437-443)
- [x] Add observability log for delay (line 424)
- [x] Add fetch statistics tracking (lines 418-419, 435, 438, 453-456)
- [x] Add request number to output (line 428, 432)

**Validation**:
- [ ] Run test: `cargo test audit_7 -- --ignored --nocapture`
- [ ] Verify 0 HTTP 503 errors
- [ ] Verify 120/120 fetches successful
- [ ] Verify 500K+ ticks fetched (full 5 days)
- [ ] Verify test duration ~22-25 minutes

**Post-Implementation**:
- [ ] Update NEXT_STEPS.md (remove network reliability issue)
- [ ] Update audit implementation tracker
- [x] Mark this plan as IMPLEMENTED
- [ ] Commit: `fix(test): add 100ms rate limit delay for Dukascopy fetches`

---

## Observability Metrics

### Pre-Implementation Baseline
- Fetch success rate: 77.5% (93/120)
- Failed requests: 27
- Total ticks: 357,859
- Test duration: ~20 minutes

### Post-Implementation Target
- Fetch success rate: 100% (120/120)
- Failed requests: 0
- Total ticks: ≥500,000 (full 5 days)
- Test duration: ~22 minutes

### Monitoring
```rust
let mut successful_fetches = 0;
let mut failed_fetches = 0;

// After fetch loop:
println!("📊 Fetch statistics:");
println!("  Success: {}/120 ({:.1}%)", successful_fetches,
         successful_fetches as f64 / 120.0 * 100.0);
println!("  Failed: {}", failed_fetches);
```

---

## References

**External**:
- dukascopy-node rate limit handling: https://github.com/Leo4815162342/dukascopy-node
- Dukascopy rate limit discussion: https://eareview.net/software/dukascopy-download-rate-limit
- Tokio sleep API: https://docs.rs/tokio/latest/tokio/time/fn.sleep.html

**Internal**:
- Test file: `tests/dukascopy_eurusd_adversarial_audit.rs`
- Fetcher implementation: `src/providers/dukascopy/fetcher.rs`
- Previous audit results: `docs/planning/dukascopy-eurusd-audit-implementation.md`
- Ultra-low threshold plan: `docs/planning/dukascopy-eurusd-ultra-low-threshold.md` (now superseded by v3.0.0 completion)
- API migration plan: `docs/planning/api-threshold-granularity-migration.md` (completed in v3.0.0)
