# CLAUDE.md

This file is the canonical source for FinCrimeRadar enforcement rules covering sourcing, regulatory accuracy, security, component isolation, verification, correction discipline, review triggers and session tooling.

`GUIDE_STANDARD.md` owns guide structure, editorial presentation, interaction requirements and format treatments, including Evidence Essay.

Do not duplicate those standards here.

If the two files conflict on security, sourcing, regulatory accuracy, data integrity, verification or review requirements, this file takes precedence.

The historical incidents behind these rules are preserved in `docs/QUALITY_INCIDENTS.md`. It is not required reading for normal sessions. Consult it when investigating a failure that resembles a past one, or when explicitly asked to.

## 1. Operating principle

Execute rather than narrate.

Before changing anything:

1. Inspect the relevant repository files and existing conventions.
2. Identify dependencies and regression risks.
3. Make the smallest robust change.
4. Verify the result using the appropriate method.
5. Report only what materially matters.

Do not repeat the request, explain obvious work or provide lengthy reasoning unless explicitly requested.

Make reasonable non destructive decisions without asking for confirmation when repository context, existing standards or safe engineering judgement resolves the ambiguity.

## 2. Formatting

Never use em dash or en dash punctuation in responses, explanations or code comments.

Use commas, periods, parentheses or separate sentences instead.

## 3. Response discipline

For simple tasks, respond directly.

For completed repository work, normally report only:

### Verdict

What changed and whether the requested work is complete.

### Verification

What was actually checked or executed.

### Risks

Only unresolved material risks or required human actions.

For architecture, strategy or substantial review work, use:

### Verdict

### Blueprint

### Pivot

### Deliverable

Omit sections that add no useful information.

Do not paste complete repository files into chat when Claude Code can edit them directly unless explicitly requested.

## 4. Published content sourcing

Every new guide or other published factual content must complete sourcing before publication.

Classify claims into two categories.

### Material factual claims

Examples include:

1. Statistics
2. Regulatory obligations
3. Statutory requirements
4. Enforcement actions
5. Official definitions
6. Legal thresholds
7. Regulatory scope
8. Government or regulator findings

Each material claim requires either:

1. A verified authoritative source, an inline `[n]` citation, a Sources entry and a matching `verification-ledger.json` record.

or

2. Honest epistemic framing where no authoritative source genuinely exists, plus a ledger entry explicitly recording that the claim is retained as an estimate or unverified industry assertion.

Never invent or overstate a source.

Vendor content, secondary summaries and generic surveys are not primary authority merely because they contain the desired figure.

An honestly qualified estimate is preferable to a misleading citation.

### Illustrative material

Hypothetical thresholds, worked example numbers, fictional scenarios and rhetorical figures do not require citations unless presented as real world facts.

Do not over cite illustrative material.

## 5. Source pack first workflow

For any new guide or substantial regulatory rewrite, build the source pack before drafting the prose.

Workflow:

1. Identify each material statutory, regulatory or factual proposition the guide needs.
2. Retrieve the strongest available source.
3. Verify the proposition directly against the source.
4. Record the relevant scope, conditions and wording.
5. Draft the guide from the verified source pack.
6. Run `scripts/check_ledger.py scan`.
7. Classify every candidate claim.
8. Source, qualify or remove each material claim.
9. Reconcile citations and `verification-ledger.json`.
10. Run any required adversarial review.
11. Synchronise derived assets.
12. Complete final verification.

Do not draft precise regulatory claims first and attempt to find supporting citations afterwards.

## 6. Citation precision

Use only as much citation precision as the teaching point requires.

For ordinary explanatory prose, section level statutory citation is normally sufficient.

Use subsection or clause level precision where the distinction itself affects the legal or practical conclusion, especially in scenarios, knowledge checks and statutory interpretation.

Unnecessary subsection precision creates correction risk without improving practitioner value.

Accuracy remains mandatory regardless of citation density.

## 7. Regulatory claim review

Ordinary sourcing confirms that evidence exists.

It does not prove that the guide interpreted the evidence correctly.

Any new or materially revised claim concerning:

1. Which regulation applies to which entity or activity
2. Statutory applicability
3. Licence conditions
4. Legal scope
5. Regulatory obligations
6. What an authority legally established
7. Conditions that trigger an obligation
8. Definitions that determine a scenario outcome

requires external adversarial review before publication.

Run this manually outside the Claude Code session using ChatGPT or Codex.

Claude Code must identify the specific claims requiring this review in its delivery report.

Do not launch background review agents or polling for this purpose.

## 8. Regulatory correction discipline

Any correction involving a statute, regulation, regulatory guidance or legal citation requires all three checks below.

### Structural match

Verify the final wording against the primary source's actual internal structure.

Confirm:

1. Correct section or subsection
2. Correct limb of the test
3. Correct conditions
4. Correct entity scope
5. Correct exceptions
6. Correct effect

Subject matter similarity is not enough.

### Internal consistency sweep

Search the complete guide for every representation of the corrected proposition.

Check:

1. Body text
2. Stat cards
3. Tables
4. FAQs
5. Scenarios
6. Quizzes
7. Feedback strings
8. Metadata
9. Structured data
10. Summary sections

A correction applied in only one place is incomplete.

### Ledger reconciliation

If a claim changes, recheck the corresponding `verification-ledger.json` `claimText` against the final live wording.

If a correction itself is later corrected, ledger reconciliation becomes mandatory again.

Do not assume an earlier ledger entry remains accurate.

## 9. Correction rounds

For statutory or regulatory content, expect more than one verification pass.

The normal target is:

1. One complete structural review of all flagged claims.
2. One correction and reconciliation pass.
3. One final confirmation pass.

If repeated additional rounds are required, inspect whether excessive citation precision or weak source pack preparation is causing the problem before continuing claim by claim corrections.

Do not treat repeated correction cycles as the preferred drafting process.

Fix the upstream workflow.

## 10. Scenario reasoning

Every scenario, quiz verdict and feedback string must distinguish three layers.

### Source

What the law, regulator or authoritative evidence expressly establishes.

### Application

How FinCrimeRadar applies that authority to the scenario facts.

### Recommendation

The operational judgement or action FinCrimeRadar recommends.

Never describe an inference or operational recommendation as though it were the exact language or mandatory conclusion of the cited authority.

Avoid unsupported formulations such as "precisely what the law means" or "exactly what the regulator requires" unless the authority genuinely establishes that proposition directly.

For legally defined categories, confirm that the scenario facts actually satisfy the definition before using that definition as the basis for scoring, grading or teaching.

## 11. Methodology accuracy

Statements about FinCrimeRadar's own sourcing process are factual claims too.

Verify any statement claiming:

1. A source was unavailable.
2. A quotation could not be found.
3. A claim was independently verified.
4. A search produced no evidence.
5. A source supports or does not support a proposition.
6. A verification process was performed.

The Methodology section must not overstate or misdescribe the project's actual verification work.

## 12. Human writing standard

All public facing FinCrimeRadar content must read like work written by an experienced human financial crime practitioner.

Do not produce obvious AI prose.

Avoid:

1. Generic introductions.
2. Mechanical transitions.
3. Repetitive sentence structures.
4. Excessive headings.
5. Artificially polished corporate language.
6. Unnecessary summaries.
7. Formulaic conclusions.
8. Repeated stock phrases.
9. Bullet lists where natural prose communicates the point better.
10. Unsupported certainty.

Use practical judgement, nuance, varied sentence structure and realistic practitioner language.

Do not intentionally introduce errors, slang or fake informality to simulate human writing.

Human quality means credible expert reasoning, not deliberate imperfection.

Detailed editorial presentation remains governed by `GUIDE_STANDARD.md`.

## 13. Derived asset synchronisation

When any material claim, statistic, legal interpretation, case detail or conclusion changes, inspect every derived representation before publication.

This includes:

1. Summary images
2. Infographics
3. Metadata
4. Structured data
5. Social copy
6. Stat strips
7. Quiz questions
8. Scenario feedback
9. Closing cards
10. Knowledge Hub descriptions
11. Search snippets
12. Related promotional material

Publication is blocked until material derived assets agree with the final guide.

## 14. Component isolation

New components must not accidentally inherit unrelated global CSS or JavaScript behaviour.

Before shipping a component, inspect it against:

1. Bare element and generic class selectors in `brand.css`.
2. Watched or partial match selectors in `brand.js`.
3. Existing global behaviours affecting elements such as `nav`, `footer`, `table`, cards and scroll wrappers.

Prefer namespaced component classes and scoped selectors.

Avoid generic class names that can collide with existing behaviour.

Where a semantic element must be used and global rules affect it, explicitly reset every conflicting property in the component scope.

Do not assume CSS specificity will protect the component.

Verify the result in a real browser using computed styles.

## 15. High stakes logic review

External review is mandatory for changes involving:

1. Scoring or grading logic
2. Authentication
3. Authorisation
4. Financial data
5. Money movement
6. New API endpoints
7. Security boundaries
8. Trust boundaries
9. Other logic where incorrect behaviour could materially affect users or data

For this tier:

1. Run `/code-review` through a real GitHub pull request.
2. Resolve material findings.
3. Run a separate manual ChatGPT or Codex adversarial review outside Claude Code.

The manual review provides cross model independence and is not replaced by `/code-review`.

Do not auto launch Codex plugins, polling or background review monitors.

The human performs the external review.

## 16. Low risk review

External adversarial review is not required merely because a file changed.

Normally skip it for:

1. CSS
2. Styling
3. Copy edits
4. Typographical fixes
5. Configuration changes without security impact
6. Routine content sourcing
7. Mechanical refactors without behavioural logic

Skipping unnecessary review is correct.

Do not create review ceremony where the risk does not justify it.

## 17. Production verification

Local correctness does not prove production correctness.

If a change depends on:

1. Another repository
2. A separately deployed API
3. A synchronised dataset
4. A remote configuration
5. A CDN served asset
6. Another independently deployed service

identify that dependency explicitly.

Before declaring the feature verified, perform a live smoke check against the actual production dependency where access permits.

Test harness data and local fixtures do not substitute for the deployed system.

If Claude Code cannot perform the production check, state the exact outstanding check required from the human.

## 18. Verification source hierarchy

Do not treat one retrieval method as unquestionable ground truth.

When tools disagree, identify which layer is being tested.

### Repository truth

Use a fresh checkout, fresh `origin/main`, or fresh GitHub codeload archive when determining what is actually committed.

### Production truth

Use an independent live request such as `curl` or a real browser render when determining what production actually serves.

### Retrieval helpers

Tools such as `web_fetch` may be cached or stale.

Do not close a high impact verification decision solely from a `web_fetch` result when it conflicts with repository state, deployment information or another independent fetch.

A cache busting query parameter is not sufficient proof that stale behaviour has been eliminated.

Cross check material publication and correction decisions with an independent method.

## 19. Security and trust boundaries

For any change touching authentication, authorisation, APIs, sensitive data, financial data or trust decisions:

1. Validate untrusted input.
2. Enforce authorisation server side.
3. Avoid exposing secrets or sensitive configuration.
4. Preserve auditability.
5. Consider abuse and rate limiting.
6. Handle failure states explicitly.
7. Test unauthorised and malformed requests.
8. Flag the diff for high stakes review.

Never weaken security controls merely to simplify implementation.

## 20. Session tooling

Two specialist tools are available:

1. `ponytail`
2. `code-review`

### Ledger base check

Run `python scripts/check_ledger_base.py` as a required pre-flight step at the start of any session that will read, write, or continue a WIP touching `verification-ledger.json`.

It diffs the working tree's claimId set against HEAD's and fails loud if any claimId committed in HEAD is missing from the working tree, the signature of the stale-snapshot write-back bug (see `BACKLOG.md`, ledger section, third occurrence, root cause 2026-08-23): a long-running WIP built from a cached read of the ledger silently drops whatever claimIds sat at the tail of the array at snapshot time when it's later written back.

Run it again before committing a ledger change, not only at session start.

### Ponytail mode

Follow the active `BACKLOG.md` loop.

Polish Loop:

`/ponytail lite`

Use for mechanical and low risk work such as CSS corrections, formatting sweeps and token fixes.

Build Loop:

`/ponytail full`

Use for architecture, components, application logic and meaningful implementation decisions.

Content Loop:

`/ponytail full`

Use when substantive sourcing, regulatory reasoning, interaction design or content architecture is involved.

Use `/ponytail ultra` only for genuinely adversarial or unusually complex work.

Do not upgrade automatically.

### Review routing

Use `/ponytail-review` for substantive implementation or logic work when a final diff review adds value.

Do not run it automatically for trivial CSS, copy, typo or configuration changes.

`/code-review` is available for pull request based review where a second implementation pass is useful.

For the high stakes tier defined above, both `/code-review` and the manual external cross model review are mandatory.

For low risk work, neither is mandatory merely because the tools exist.

Review effort must be proportional to risk.

## 21. Definition of done

A task is not complete merely because the edited file looks correct.

Where applicable, verify:

1. Requirement implemented
2. Existing behaviour preserved
3. Sourcing completed
4. Ledger reconciled
5. Regulatory claims structurally checked
6. Derived assets synchronised
7. Component isolation confirmed
8. Tests passed
9. Build passed
10. Live dependency checked
11. Required adversarial review flagged or completed
12. No unresolved material contradiction remains

Never claim work is complete, fixed, tested, verified, production ready or publication ready unless the relevant checks actually occurred.

If a check cannot be performed, state exactly what remains unverified.

## 22. Final principle

Prefer evidence over confidence.

Prefer verified source structure over plausible wording.

Prefer namespaced components over cascade assumptions.

Prefer live production checks over local assumptions.

Prefer proportionate review over ritual.

Prefer human practitioner writing over AI shaped prose.

Inspect before changing.

Verify before claiming.
