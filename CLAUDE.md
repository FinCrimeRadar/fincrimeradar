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

## Review policy

Independent adversarial review (via ChatGPT/Codex, done manually by pasting the diff, not the in-editor plugin) is RESERVED for high-stakes logic diffs: new scoring or grading logic, authentication, code that moves money or touches financial data, new API endpoints, or security or trust boundaries. For those, the reviewer is a manual step done outside the Claude Code session to avoid session-token drain from polling.

It is NOT expected for: content and guide sourcing, CSS or styling, copy edits, typos, config, or any change without new logic. Skipping review on these is correct, not a lapse.

Claude Code should NOT auto-launch the Codex plugin or set up background monitors/polling for reviews. If a diff qualifies as high-stakes logic, flag it and let the human run the review manually via ChatGPT.

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
