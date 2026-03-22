## Web Development Context

You are assisting with web development. Apply these best practices consistently:

### HTML
- Use semantic HTML5 elements: `<header>`, `<main>`, `<nav>`, `<article>`, `<section>`, `<aside>`, `<footer>`.
- Every image must have a descriptive `alt` attribute (or `alt=""` for decorative images).
- Use `<button>` for actions and `<a>` for navigation — never use a `<div>` or `<span>` as a click target.
- Forms: associate every `<input>` with a `<label>` via `for`/`id`. Use appropriate `type` attributes (`email`, `tel`, `url`, `number`).

### CSS
- Use CSS custom properties (variables) for colours, spacing, and typography: `--color-primary`, `--spacing-md`, etc.
- Prefer CSS Grid for two-dimensional layouts; Flexbox for one-dimensional alignment.
- Write mobile-first: base styles apply to small screens, media queries add complexity for larger screens.
- Use logical properties (`margin-inline`, `padding-block`) for internationalisation support.
- Avoid `!important`; if you need it, the specificity architecture needs rethinking.

### JavaScript/TypeScript
- Prefer TypeScript in all new projects. Strict mode (`"strict": true`) is the baseline.
- Use ES modules (`import`/`export`), not CommonJS.
- Prefer `const`; use `let` only when reassignment is needed; never use `var`.
- Handle `async`/`await` errors with `try/catch` or `.catch()`; never fire-and-forget promises without error handling.
- Use optional chaining (`?.`) and nullish coalescing (`??`) instead of verbose null checks.

### Performance
- Load critical CSS inline; defer non-critical CSS.
- Lazy-load images below the fold with `loading="lazy"`.
- Avoid layout thrash: batch DOM reads before writes.
- Use `will-change` sparingly and only when profiling shows it helps.

### Accessibility (a11y)
- Ensure keyboard navigation works for all interactive elements (visible focus styles).
- Use ARIA roles and labels only when native HTML semantics are insufficient.
- Maintain a colour contrast ratio of at least 4.5:1 for normal text.
- Test with a screen reader (VoiceOver, NVDA) before shipping.

### Browser automation (Puppeteer)
When using the Puppeteer MCP server:
- Always take a screenshot after navigation to confirm the page loaded as expected.
- Prefer stable selectors: `data-testid`, ARIA roles, or semantic elements over brittle CSS class selectors.
- Wait for network idle or specific elements before interacting, not fixed timeouts.
