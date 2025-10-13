//! Rangebar meta-crate
//!
//! Complete range bar toolkit with backward compatibility.
//!
//! Re-exports all sub-crates for convenience.

// Re-export core (always available)
pub use rangebar_core as core;

// Re-export optional crates
#[cfg(feature = "providers")]
pub use rangebar_providers as providers;

#[cfg(feature = "config")]
pub use rangebar_config as config;

#[cfg(feature = "io")]
pub use rangebar_io as io;

#[cfg(feature = "streaming")]
pub use rangebar_streaming as streaming;

#[cfg(feature = "batch")]
pub use rangebar_batch as batch;

// Legacy compatibility modules (will be populated in Phase 2)
// pub use rangebar_core::*;
// pub mod fixed_point { pub use rangebar_core::fixed_point::*; }
// pub mod types { pub use rangebar_core::types::*; }
