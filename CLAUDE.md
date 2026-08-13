# CLAUDE.md

## Formatting rule

Never use em dashes or en dashes in any response, explanation, or code comment. Use commas, periods, parentheses, or separate sentences instead.

## Response structure

Always structure answers using these four sections, in this order:

- **Verdict**: the direct answer or conclusion.
- **Blueprint**: the reasoning or plan behind it.
- **Pivot**: what could change, alternatives, or risks to watch for.
- **Deliverable**: the concrete output (code, file, command, etc.).

## Content sourcing standard

Every new guide or piece of published content must be sourced before it ships. Apply the material versus illustrative split:

- Material factual claims (statistics, regulatory obligations, enforcement actions, official definitions) get EITHER a real primary source (inline [n] marker plus a Sources section entry, and a verification-ledger.json entry) OR, where no primary source genuinely exists, honest in-text epistemic framing ("industry estimates commonly cite", "not independently benchmarked") plus a retained-as-estimate ledger entry.
- Never invent a source. A vendor blog or generic "industry survey" is not a primary source. A wrong or overclaimed citation is worse than an honest "industry estimate".
- Illustrative numbers (worked-example thresholds, hypothetical scenarios, rhetorical figures) get NO citation. Over-citing these is its own error.

Sourcing is a required build phase, not an afterthought: run scripts/check_ledger.py scan, classify candidates, source or reword each material claim, add ledger entries and on-page citations, then, for high-stakes logic only, an optional independent adversarial review before commit (see Review policy below). The verification ledger is the single source of truth and grows with each guide.

## New component CSS isolation

Three separate bugs have come from the same root cause: a new component using a generic or semantic HTML tag (a bare `<nav>`, a plain class name like `table` or `compare-table`) silently inherits an unrelated sitewide rule meant for something else. Examples: the Knowledge Hub flagship nav inheriting the sitewide `nav{position:sticky;height:72px}` rule, the certifications-dilemma.html compare table colliding with a brand.js scroll-wrap selector, and the guide breadcrumb inheriting the same sitewide sticky nav rule a third time.

Before shipping any new component, check its markup against two known collision sources:
- `brand.css`'s bare-element and generic-class selectors (`nav`, `footer`, `table`, and similar), which apply sitewide by design and will catch anything using the same tag or a name that matches.
- `brand.js`'s watched selectors (currently includes `[class*="card"]` for scroll-reveal and table auto-wrapping), which match on partial class names, not just exact ones.

Either avoid the generic tag or class name entirely, or add an explicit reset in the new component's own rule for every property the sitewide selector sets, don't rely on assuming a more specific selector will win the cascade without checking. Confirm the reset in-browser via computed styles, not just by reading the CSS.

## Review policy

Independent adversarial review (via ChatGPT/Codex, done manually by pasting the diff, not the in-editor plugin) is RESERVED for high-stakes logic diffs: new scoring or grading logic, authentication, code that moves money or touches financial data, new API endpoints, or security or trust boundaries. For those, the reviewer is a manual step done outside the Claude Code session to avoid session-token drain from polling.

It is NOT expected for: content and guide sourcing, CSS or styling, copy edits, typos, config, or any change without new logic. Skipping review on these is correct, not a lapse.

Claude Code should NOT auto-launch the Codex plugin or set up background monitors/polling for reviews. If a diff qualifies as high-stakes logic, flag it and let the human run the review manually via ChatGPT.

## Regulatory-claim adversarial review

The gambling-white-label-blind-spot-guide.html revision (2026-08-13) found three real regulatory-precision errors that had already passed the guide's normal build verification: an overstated Money Laundering Regulations scope claim (MLR 2017 applies directly to casinos, not gambling operators generally, who are governed through POCA/Gambling Act/LCCP instead), an unsupported inference drawn from an "unchanged" risk rating, and an absolute legal claim stated as universal when it was actually scenario-specific. All three were only caught by an external adversarial review with domain expertise, not by this project's own sourcing checklist or in-browser verification, both of which are built to catch missing citations and broken interactions, not scope errors in what a citation actually supports.

This is the same class of gap the Review policy already exists to close for scoring and grading logic, extended to a different kind of risk: not code correctness, but claim correctness.

Any new guide making a specific regulatory-obligation, legal-scope, or statutory-applicability claim (which regulation applies to which entity type, what a licence condition actually requires, what an authority's finding does or does not establish) requires an external adversarial review of those specific claims before publication, run manually outside the Claude Code session, same as the existing high-stakes logic review. This applies regardless of the guide's visual format or interactivity level, it is about the claims, not the layout.

Claude Code should flag which claims in a new guide fall into this category as part of its own delivery report, the same way it already flags new scoring/grading logic requiring review, so the human knows what needs the external pass before shipping, rather than discovering the gap after publication.

## Session tooling

Two plugins are installed: `ponytail` (minimal-code discipline) and `code-review` (Anthropic's PR-based multi-agent reviewer).

Ponytail mode follows the active BACKLOG.md loop:

- Polish Loop: `/ponytail lite`. Mechanical, low-risk work (CSS, dash sweeps, token fixes) doesn't need full ladder deliberation.
- Build Loop and Content Loop: `/ponytail full` (default). Real architecture and component decisions benefit from the full ladder.
- `/ponytail ultra` is reserved for genuine adversarial situations, not a default upgrade from full.

Review routing:

- `/ponytail-review` is the default end-of-session check for every loop, every session. It runs on the current diff directly, no PR required.
- `/code-review` is available for any PR you want a second pass on, general purpose, not gated by tier.
- For the high-stakes tier defined under Review policy above (scoring or grading logic, authentication, code that moves money or touches financial data, new API endpoints, security or trust boundaries), both checks apply: `/code-review` via a real GitHub PR, AND the manual ChatGPT/Codex adversarial review outside the session. `/code-review` does not replace the manual step, it is same-model multi-agent review and does not provide the cross-model independence the manual step exists for. Run `/code-review` first to catch obvious issues cheaply, then do the manual cross-model pass on what remains.

Do not run either review tool as a default habit on content, CSS, or config changes. That duplicates work the Review policy above already says to skip.
