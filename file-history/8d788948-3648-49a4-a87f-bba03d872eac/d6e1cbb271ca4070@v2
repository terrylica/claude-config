//! Infrastructure modules
//!
//! Supporting systems for I/O, configuration, and API services.
//!
//! ## Modules
//!
//! - `io` - Polars-powered data I/O (Parquet, CSV, Arrow) - requires `polars-io` feature
//! - `config` - Application configuration and settings
//! - `api` - REST API service integration - requires `api` feature

#[cfg(feature = "polars-io")]
pub mod io;

pub mod config;

#[cfg(feature = "api")]
pub mod api;
