Explain the Rust compiler error or warning shown below (or paste the error output after this command).

For each diagnostic:

1. **What it means** — explain the error in plain English, including *why* the Rust compiler enforces this rule (ownership, lifetimes, type system, etc.).

2. **Minimal reproducing example** — show a small code snippet that triggers the same error so the cause is isolated.

3. **How to fix it** — show the corrected code. If there are multiple valid approaches (e.g. clone vs. borrow vs. restructure), show each with a brief explanation of the trade-offs.

4. **When to prefer each fix** — give guidance on which fix to choose depending on context (performance-sensitive vs. ergonomic, library vs. binary, etc.).

5. **Related patterns** — mention any Rust patterns or idioms that are relevant (e.g., "this is the classic borrow-after-move pattern; consider using `Arc<Mutex<T>>` if shared ownership is needed").

Format the response with clear headings and syntax-highlighted code blocks. Keep explanations concise but complete — the goal is that the developer understands the root cause, not just the fix.
