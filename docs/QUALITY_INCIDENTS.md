# Quality Incidents

This file preserves the historical postmortems behind the standing rules in `CLAUDE.md`. It is not required reading for normal sessions.

Consult it when investigating a failure that looks similar to one of these, or when explicitly asked to.

Each entry: date, what failed, the root cause, the permanent control it produced, and the `CLAUDE.md` rule that control now lives in. `CLAUDE.md` is the current numbered section references as of the 2026-08-26 rewrite; if the file is renumbered later, treat the rule name as the anchor, not the number.

---

## 1. Component CSS isolation collisions

**Date:** three separate occurrences, prior to 2026-08-26.

**Failure:** Three unrelated new components each silently inherited a sitewide CSS or JS rule meant for something else: the Knowledge Hub flagship nav inherited the sitewide `nav{position:sticky;height:72px}` rule, certifications-dilemma.html's compare table collided with a `brand.js` scroll-wrap selector, and a guide breadcrumb inherited the same sitewide sticky-nav rule a third time.

**Root cause:** Each new component used a generic or semantic HTML tag, or a plain class name (`nav`, `table`, `compare-table`), that collided with `brand.css`'s bare-element and generic-class selectors or `brand.js`'s partial-match watched selectors (for example `[class*="card"]`), without checking for the collision first.

**Permanent control:** Before shipping any new component, check its markup against `brand.css`'s generic selectors and `brand.js`'s watched selectors. Prefer namespaced component classes. Where a semantic element must be reused and a global rule affects it, explicitly reset every conflicting property in the component's own scope, and verify the result via computed styles in a real browser rather than assuming CSS specificity protects it.

**CLAUDE.md rule:** Section 14, Component isolation.

---

## 2. gambling-white-label-blind-spot-guide.html regulatory-precision errors

**Date:** 2026-08-13.

**Failure:** The guide shipped with three regulatory-precision errors that had already passed the project's normal build verification: an overstated Money Laundering Regulations 2017 scope claim (MLR 2017 applies directly to casinos, not gambling operators generally, who are governed through POCA, the Gambling Act and the LCCP instead), an unsupported inference drawn from an "unchanged" risk rating, and an absolute legal claim stated as universal when it was actually scenario-specific.

**Root cause:** The project's sourcing checklist and in-browser verification are built to catch missing citations and broken interactions, not scope errors in what an existing, correctly-cited source actually supports. None of the three errors involved a missing citation or a broken interaction, so neither check caught them.

**Permanent control:** Any new guide making a regulatory-obligation, legal-scope, or statutory-applicability claim requires external adversarial review of those specific claims before publication, run manually outside the session. Claude Code must identify which claims fall into this category in its own delivery report.

**CLAUDE.md rule:** Section 7, Regulatory claim review.

---

## 3. Risk Scoring module broken-premise scenario (Case 2)

**Date:** 2026-08-17.

**Failure:** A Scenario Lab Risk Scoring module case described its PEP subject as "an elected local councillor." The case's intended lesson, a domestic PEP's lower risk baseline under MLR 2017 regulation 35(12) and, at build time, FCA guidance FG17/6, depended on the subject genuinely meeting the domestic PEP definition. An elected local councillor does not meet it.

**Root cause:** Neither the sourcing checklist nor in-browser verification checks whether a scenario's underlying stated facts actually satisfy the legal definition its own lesson depends on. The tool would have confidently graded analysts against a premise that never held, a broken premise rather than an imprecisely taught correct one.

**Permanent control:** Same external adversarial review requirement as the gambling incident, extended explicitly to cover whether a scenario's stated facts satisfy the legal or regulatory definition being taught, not only whether the citations supporting it exist.

**CLAUDE.md rule:** Section 7, Regulatory claim review; Section 10, Scenario reasoning (definitional fit).

---

## 4. pep-guide-part1.html and sar-guide-part1.html structural correction failures

**Date:** week preceding 2026-08-19.

**Failure:** pep-guide-part1.html's Regulation 35(12)/(14) categories claim and sar-guide-part1.html's Section 342 offence structure each survived a first correction round while still misstating their actual statutory structure.

**Root cause:** The correction was checked against a summary of the source's general subject matter rather than against the primary source's actual clause-by-clause structure, which subsection governs what, which limb of a disjunctive test applies, what conditions gate an obligation. Subject-matter similarity is not the same as structural correctness.

**Permanent control:** Any correction involving a statutory or regulatory citation requires three checks: structural match against the primary source's actual internal structure (section, limb, conditions, entity scope, exceptions, effect), an internal consistency sweep across every representation of the claim in the guide, and ledger-to-live-text reconciliation. Budget at least two correction rounds as the normal expectation for statutory or regulatory content, not a sign something went wrong the first time.

**CLAUDE.md rule:** Section 8, Regulatory correction discipline; Section 9, Correction rounds.

---

## 5. aml-guide-part1.html citation-density correction cycle

**Date:** 2026-08-19.

**Failure:** aml-guide-part1.html required two full correction rounds across two separate batches, twenty-two individual regulatory claims corrected, several needing a second round even after external review had already run once.

**Root cause:** Dense, subsection-level citation throughout ordinary body prose created many small opportunities for structural mismatch, each one requiring its own verification round. This was a drafting-density problem upstream of review, not primarily a review-thoroughness problem.

**Permanent control:** Build a verified source pack before drafting guide prose, not after. Calibrate citation density to what the reader needs, section-level for ordinary explanatory prose, subsection-level only where the distinction itself affects the conclusion. Cap external review at two rounds as the default target; a third round needed is a signal to fix the drafting workflow, not to keep correcting claim by claim.

**CLAUDE.md rule:** Section 5, Source pack first workflow; Section 6, Citation precision; Section 9, Correction rounds.

---

## 6. classification-asymmetry-guide.html Methodology misstatement

**Date:** 2026-08-14.

**Failure:** The guide's own Methodology section wrongly declared a quote unverifiable when it was genuinely present in the source, a false statement about the guide's own sourcing rigor sitting inside the one section whose job is to prove that rigor.

**Root cause:** Neither the sourcing checklist nor in-browser verification checks whether a guide's narrative about its own verification process is itself accurate. Both check for missing citations and broken interactions, not for the accuracy of the guide's own self-description.

**Permanent control:** Verify that every statement a guide makes about its own sourcing, search process, source availability, verification result, or inability to confirm a claim is itself accurate and supported by the retained verification record.

**CLAUDE.md rule:** Section 11, Methodology accuracy.

---

## 7. MLRO Handbook and classification-asymmetry-guide.html stale derived assets

**Date:** found independently twice, prior to 2026-08-14.

**Failure:** MLRO Handbook Part 2 shipped with a stale CFP Management fine figure in a derived asset. Separately, classification-asymmetry-guide.html's summary snapshot shipped before a corrective text pass had caught up to it.

**Root cause:** In both cases a material-claim change did not propagate to a derived representation, a summary image, stat strip, quiz, scenario feedback string, or Knowledge Hub description.

**Permanent control:** When any material claim, figure, legal interpretation, case detail, or conclusion changes, review and synchronise every derived representation before publication. Publication is blocked until the synchronisation check passes.

**CLAUDE.md rule:** Section 13, Derived asset synchronisation.

---

## 8. Risk Scoring module production/local verification gap

**Date:** built 2026-08-17, discovered approximately six weeks later.

**Failure:** `fincrimeradar-api`'s `cases.json`, backing the live `/scenario-lab/cases` endpoint that `fincrimeradar.org` actually calls in production, was a manually maintained mirror of `fincrimeradar`'s `scenario-lab/data/cases.json`. It had been silently stale since a single commit on 2026-07-07, through two later module launches, discovered by a user's screenshot of an empty case picker, not by this project's own process.

**Root cause:** Every in-browser check that build session ran, including extensive device-width and interaction testing, exercised frontend logic against local or test-harness data. It never once touched the real deployed API.

**Permanent control:** For any change that depends on a separately deployed service or a second repository actually being current, flag that dependency explicitly and run a live smoke check against the real, deployed endpoint before considering the change verified. Local and test-harness verification, however thorough, does not substitute for it.

**CLAUDE.md rule:** Section 17, Production verification.

---

## 9. scam-compound-money-laundering-guide.html web_fetch staleness

**Date:** 2026-08-25.

**Failure:** During this guide's build and correction rounds, `web_fetch` served stale content in both directions, on three separate occasions: stale hero stat cards showing `$0bn` after a real fix had already deployed; a false 404 on a UNODC press release URL that both a browser render and `curl` confirmed was live; and, most seriously, content showing zero of two full rounds of applied corrections on the guide's live page, while a fresh GitHub tarball pull of `origin/main` showed every correction genuinely committed.

**Root cause:** `web_fetch` results were treated as ground truth for what production or the repository actually contained. A cache-busting query string resolved the first instance but did not resolve the third, so the same fix could not be assumed to generalise.

**Permanent control:** Do not close a high-impact verification decision solely from a `web_fetch` result when it conflicts with repository state, deployment information, or another independent fetch. Cross-check with a fresh `origin/main` or `codeload.github.com` tarball pull (repository truth) or an independent live request such as `curl` or a real browser render (production truth).

**CLAUDE.md rule:** Section 18, Verification source hierarchy.
