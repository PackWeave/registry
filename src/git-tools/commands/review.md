Review the staged changes (or the diff provided) and produce a structured code review.

Use `git_diff_staged` to retrieve the staged diff, then analyse it across these dimensions:

## 1. Correctness
- Are there logic errors, off-by-one issues, or incorrect assumptions?
- Does the code handle edge cases and error paths?
- Are there potential panics, null-pointer issues, or unhandled exceptions?

## 2. Design & Architecture
- Is the change cohesive and focused on a single concern?
- Does it respect existing abstractions and module boundaries?
- Are new abstractions justified, or could simpler code achieve the same goal?

## 3. Security
- Are user-controlled inputs validated or sanitised?
- Are secrets, credentials, or PII handled safely?
- Could this change introduce injection vulnerabilities or privilege escalation?

## 4. Performance
- Are there obvious algorithmic inefficiencies (e.g. O(n²) where O(n) is possible)?
- Are expensive operations (I/O, network calls) performed unnecessarily in hot paths?

## 5. Test coverage
- Are new behaviours covered by tests?
- Are edge cases and failure modes tested?
- If no tests were added, is that justified?

## 6. Code style & readability
- Is the code consistent with the surrounding style?
- Are names clear and self-documenting?
- Is documentation (comments, docstrings) accurate and sufficient?

Format your review as:
- **Summary** — one paragraph overall assessment
- **Must fix** — numbered list of blocking issues (if any)
- **Suggestions** — numbered list of non-blocking improvements
- **Nits** — minor style/readability notes
