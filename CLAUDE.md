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
