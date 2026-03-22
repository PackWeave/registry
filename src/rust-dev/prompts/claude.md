## Rust Development Context

You are assisting with Rust development. Apply these principles consistently:

### Error handling
- Use `thiserror` for defining error types in library crates. Derive `Error` on an enum; each variant gets a `#[error("...")]` message.
- Use `anyhow` for error *propagation* in binary crates and CLI handlers. Return `anyhow::Result<T>` and use the `?` operator freely.
- Never use `unwrap()` or `expect()` in production code paths unless the condition is a true invariant (e.g., a mutex that can only fail if poisoned by a panic). When you do use them, add a comment explaining why it cannot fail.
- Prefer `?` over `match` for propagating errors. Use `match` only when you need to handle specific variants differently.

### Idiomatic patterns
- Prefer iterators and combinators (`map`, `filter`, `collect`, `flat_map`) over manual loops when it aids clarity.
- Use `impl Trait` in function signatures for input parameters; use explicit generic bounds when the type must be named (e.g., for `where` clauses).
- Prefer `&str` over `&String` for function parameters; prefer `&[T]` over `&Vec<T>`.
- Use `#[derive(Debug, Clone, PartialEq)]` liberally on data types.
- Use `Default` trait when a struct has a sensible zero-value.

### Clippy and linting
- Always run `cargo clippy -- -D warnings` before considering code complete. Fix all warnings; never suppress with `#[allow(...)]` without a comment.
- Common clippy improvements to proactively apply: use `if let` instead of `match` for single-variant matches; use `?` instead of `unwrap()`; avoid needless collect/clone.
- Run `cargo fmt --all` before committing. The default rustfmt settings are the standard.

### Performance and safety
- Avoid unnecessary cloning — pass references where ownership is not needed.
- When using `Arc<Mutex<T>>`, document why shared mutable state is needed and keep lock guards short-lived.
- Prefer `Vec::with_capacity` when the final size is known.
- Use `#[must_use]` on functions whose return value must be used.

### Testing
- Unit tests go in a `#[cfg(test)] mod tests` block at the bottom of the file they test.
- Integration tests go in `tests/`.
- Use descriptive test names: `test_<function>_<scenario>_<expected_outcome>`.
- Test error paths as well as happy paths.
