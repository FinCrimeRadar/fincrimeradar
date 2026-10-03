# FinCrimeRadar Backlog Board

Last fully audited: 14 September 2026.

This file is the current work queue for Claude Chat, Claude Code and Codex. It contains pending work, external blockers and deliberate holds only, plus a compact shipped baseline needed for planning. Detailed completion narratives belong in Git history, not in this backlog.

Guide structure and presentation are governed by GUIDE_STANDARD.md. Operating, sourcing and review rules are governed by CLAUDE.md. The guide production process is governed by docs/GUIDE_PRODUCTION_WORKFLOW.md.

The approved 90-day publishing cadence, automation boundaries, release gates and initial content queue are governed by `docs/CONTENT_OPERATING_PLAN.md`.

## Queue rules

Work rotates through Polish, Build and Content. One working session should normally advance one loop only.

No item may enter **Next Up** unless all four fields are present:

1. Verification owner
2. Primary sources or repository evidence checked
3. Review date
4. Verification outcome

Items without those fields remain Research Candidates. A missed review date without a refreshed outcome demotes the item automatically. Do not invent owners, dates or outcomes to preserve queue position.

Status meanings:

- **READY:** verified and suitable for the next scoped session.
- **RESEARCH:** evidence or originality work remains incomplete.
- **BLOCKED:** a named external dependency prevents progress.
- **PAUSED:** valid work deliberately held pending evidence of user value or a specific decision.
- **PARKED:** not scheduled and not part of the active rotation.
- **COMPLETE:** closed work retained as an evidence record; it is not an active queue item.

## Current shipped baseline

Production outside the Scenario Lab synchronisation was last checked independently on 14 September 2026. Repository-derived facts below were refreshed from the working tree on 3 October 2026 at HEAD 125045a; that refresh was not a full production audit. The Scenario Lab API was separately verified on 3 October 2026 and served the repository's 19 unique cases exactly.

### Knowledge Hub

- **56 publications live:** 25 parts across seven series and 31 standalone publications.
- **Series inventory:** UK AML 3 parts, PEP 3, SAR 3, FATF 2, MLRO 2, Cryptoasset Compliance 6, Stablecoin 6.
- **Stablecoin Series:** Guides 0 through 5 are published. All six guides are live.
- **Experiment formats (all now accepted compositions or standing treatments):**
  - Framework (accepted composition): app-scam-decision-framework.html (Experiment 01) and de-risking-judgement-call.html, both live. The second implementation confirmed the contract's primitives recur across a distinct subject, completing the recurrence test in GUIDE_STANDARD.md.
  - Case File: money-mule-or-victim-case-file.html, Experiment 02, live.
  - Intelligence Brief: fatf-recommendation-16-intelligence-brief.html, Experiment 03, live.
  - Evidence Essay: gambling-white-label-blind-spot-guide.html, classification-asymmetry-guide.html and failure-to-prevent-fraud-evidence-essay.html, standing opt-in treatment.
- Case File, Intelligence Brief and Framework are all accepted compositions.

### Product and publishing capability

- Scenario Lab's static production release contains 19 cases: KYC and KYB 5, Fraud Detection 6, Risk Scoring 8. The live API served the same 19 unique cases at the 3 October 2026 synchronisation closure recorded under Next Up. The page's local fallback remains in place but is no longer masking a stale API.
- SAR Writing Sandbox is live on the API service with three practice cases. Case files are schema validated at load; five W, transaction and speculative scoring use only learner-verified evidence. Red-flag credit remains model-judged (see Build Loop).
- Screening and PEP search, Knowledge Hub domain filtering, weekly digest and FinCrime Week are shipped.
- FinCrime Week issues W36 to W39 are present on main; W39 (21 to 27 September 2026) is the current issue per the latest content commit.
- Verification ledger contains 643 valid entries. python scripts/check_ledger.py validate and scripts/check_ledger_base.py passed on 3 October 2026.

### Experiment 03 shipment

Experiment 03 shipped through seven atomic commits from 7ae03c5 to a0e2402. It added the FATF Recommendation 16 Intelligence Brief, page JavaScript, social card, discovery surfaces, eight verified ledger records and permanent static and browser regression checks. Production serves the guide and the Knowledge Hub count is 53. No backend, account model, free-text collection or new shared component library was introduced.

### Experiment 04 shipment

Experiment 04 shipped through nine atomic commits from d98a717 to 3d87db3, merged into main via eb80299 (pull request #7). It added the Failure to Prevent Fraud Evidence Essay, page JavaScript, social card, discovery surfaces, 18 verified ledger records and permanent static and browser regression checks, following the Evidence Essay treatment already standing for gambling-white-label-blind-spot-guide.html and classification-asymmetry-guide.html rather than a new experimental shell. A completed manual adversarial review and a separate PR-based /code-review each found and closed real defects before merge: two statutory-scope overstatements of the section 199(3) victim exclusion, a citation-click handler that let native anchor navigation undermine the enhanced source panel, an unreciprocated content-relations.json entry, and one source record conflating sections 201 and 202 that needed splitting into two precise primary-source citations. Production serves the guide and the Knowledge Hub count is 54. No backend, account model, free-text collection or new shared component library was introduced.

### Cross-experiment review of Experiments 01 to 03

Completed. The permanent publication architecture (Universal Evidence Core, Intelligence Core, Public Format Contract, Subject Specific Composition), the standard evidence vocabulary, and the Framework, Case File and Intelligence Brief contracts are now defined in GUIDE_STANDARD.md. The production workflow, the GPT/Codex and Claude Code responsibility split, and the regression-scope discipline proven by Experiments 02 and 03 are now defined in docs/GUIDE_PRODUCTION_WORKFLOW.md, which also records the browser-harness and telemetry-helper extraction decisions (approved for future extraction, not extracted during this review). Case File and Intelligence Brief are accepted compositions; neither required a second instance. Framework has since been accepted too, after de-risking-judgement-call.html completed its recurrence test.

## Next Up

### Scenario Lab API synchronisation: COMPLETE, 3 October 2026

Closes the Scenario Lab cases 7 and 8 release. No other item is in Next Up.

- **Status:** COMPLETE. The live API serves the repository's cases exactly. The blocker is removed and Build Loop gating may resume. This record does not gate or approve any new case.
- **Evidence:**
  - GitHub Actions run 37151431128 passed (https://github.com/FinCrimeRadar/fincrimeradar/actions/runs/37151431128).
  - Render deployment dep-db0m932d0e5s73c8i8ug succeeded in 1 minute 27 seconds.
  - The deployed API commit was the approved SHA 00a69a2f342f53760af569bb3d64b93c0531a84c.
  - Render logged "cases.json synced from fincrimeradar main".
  - The workflow's exact repository versus production comparison passed after four polling attempts.
  - A subsequent independent live API check passed on its first attempt.
  - Production contains 19 unique cases: KYC 5, Fraud 6, Risk Scoring 8. The previously missing risk-fatf-grey-list-change-108 and risk-sanctions-alert-surge-107 are live.
- **Root cause:** the Render dashboard build-command override installed dependencies but did not fetch the frontend cases.json, so the render.yaml fetch never ran. Triggering a deployment was therefore not proof of synchronisation. The earlier deploy dep-dap6bjijnfac73amjlbg and run 35721418857 had succeeded without syncing.
- **Control outcome:** the corrected Render build command fetches the source file and is guarded against deploying an unapproved API commit. FINCRIMERADAR_API_DEPLOY_REF is set to the same approved SHA in GitHub and Render. Future API releases must update both values. A mismatch fails closed rather than deploying an unintended commit.
- **Release proof standard:** direct API inventory comparison (sorted entity_id set and per-module counts, scripts/verify_scenario_lab_sync.py) is the release proof for Scenario Lab case changes. Browser display alone is insufficient because the frontend fallback can mask a stale API.

## Polish Loop

### Confirmed product and accessibility debt

- **Evidence Essay viewport restoration:** the narrow-screen source-record reparent works on both Evidence Essays, but restoration after widening has not been proven on a real device or genuine responsive-mode viewport. This is an unverified transition, not a confirmed defect.
- **Classification Asymmetry scenario depth:** the guide has one worked scenario and no formal counterfactual. Decide whether to add a second scenario, add a formal counterfactual, or document a historical exception to the current standard.
- **Scenario Lab dispatch hardening:** replace conflicting silent module fallbacks with one explicit per-module dispatch map that fails loudly for an unknown module.
- **Scenario Lab API load-crash pattern:** routes_scenario_lab.py `_load_cases` can crash app import on one bad file; reuse the fincrimeradar-api PR #3 pydantic validation.
- **Screening cold-path latency:** last measured at 6.6 to 9.9 seconds. Re-measure before changing anything. First test a smaller OpenSanctions result limit with explicit truncation escalation; parallel RSS work can only recover a minor share of the delay.
- **Quiz-title heading gap (fleet-wide, found and confirmed fixable 2026-09-17):** the Knowledge Check title renders as a plain `<div class="quiz-title">`, not a heading, breaking the h1 to h2 outline for screen-reader navigation. Fixed on stablecoin-series-guide-1.html the same day, verified live at 320px and 768px: change to `<h2 class="quiz-title">`, and where the quiz-section wrapper also carries the article-section class, add a scoped `.quiz-section h2 { color:#fff; }` override, since without it the heading inherits `.article-section h2`'s navy color against the quiz section's own navy background and renders invisible, confirmed with a computed-style check before and after the fix. Confirmed by wrapper class and live computed-style check, not assumed, across 25 shipped guides in two groups. Five guides carry `class="quiz-section article-section"` and need both the tag change and the override: a7a5-sanctions-evasion-guide.html, freezing-a-stablecoin-guide.html, stablecoin-financial-crime-guide.html, systemic-stablecoins-guide.html, why-stablecoins-compliance-priority-guide.html. The remaining twenty carry `class="quiz-section"` alone, with no competing `.article-section h2` rule, so the tag change alone should suffice, confirmed live on adverse-media-intelligence-guide.html: adverse-media-intelligence-guide.html, ai-agent-transaction-guide.html, crypto-travel-rule-sunrise-guide.html, deepfake-onboarding-guide.html, false-positive-playbook.html, fatf-guide-part1.html, fatf-guide-part2.html, fraud-investigation-playbook.html, fraud-red-flags-guide.html, kyc-onboarding-dilemma.html, money-mule-financial-crime-networks-handbook.html, perpetual-kyc-framework-guide.html, private-markets-financial-crime-investigation-handbook.html, scam-compound-money-laundering-guide.html, screening-algorithm-tuning-guide.html, shadow-fleet-guide-part1.html, shadow-fleet-guide-part2.html, source-of-wealth-investigation-handbook.html, synthetic-identity-device-network-guide.html, ubo-investigation-handbook.html. learn.html also matches the quiz-title class name but is a visually distinct inline badge component with its own already-legible blue-on-white styling, not part of this bug. CSS-only, no logic change, so this does not need external review before execution, just a scripted batch pass with a spot-check on at least one guide from each group before and after, since the two groups need different treatment and the adverse-media-intelligence-guide.html result should not be assumed to generalise to all twenty untested.
- **Fleet-wide skip-link focus target gap:** classification-asymmetry-guide.html's #main-content skip-link target has no tabindex="-1", so activating the skip link scrolls but does not move focus, a WCAG failure. Found while fixing gambling-white-label-blind-spot-guide.html (18 September 2026, commit 36907ab, confirmed via production browser check). Likely affects every guide sharing this skip-link pattern. Needs a scan across all guides using #main-content as a skip target, then a scripted batch fix, same shape as the quiz-title heading gap entry above. RESEARCH until scope is confirmed across guides, not Next Up.
- **FCTR dated-field ambiguity:** the FCTR 12 chapter page (handbook.fca.org.uk/handbook/fctr12) shows a page-level "last updated 01/11/2024", while the FCTR 12.3 section page and its individual paragraphs (12.3.6G-12.3.8G) each independently show 13/12/2018. Confirmed as two genuinely different dated fields, not an error in either reading, during de-risking-judgement-call.html sourcing (2026-09-21). Any other guide citing FCTR 12.3 by its chapter-level date rather than its paragraph-level date should be checked for the same conflation. RESEARCH until scope across guides is confirmed.

### Shared architecture and presentation debt

- **Site chrome consolidation:** navigation remains substantially hand-inlined while footer mounting is shared. Scope migration and duplicated cookie-banner styles before implementation. Do not combine this with a visual redesign.
- **Interactive helper review:** three experiment suites now duplicate the browser server and CDP harness; all three JavaScript files duplicate consent-aware aggregate telemetry; two static checkers duplicate KnowledgeCountParser. Decide extraction only through the cross-experiment review. Preserve telemetry allow-lists and never transmit case selections, decision records or free text.
- **Contextual internal links:** add only genuinely useful mid-article links, in small reviewed batches. Do not keyword-stuff.
- **End-of-guide cheat sheets:** the old entry understated scope. Re-baseline before work. The named pages amount to 13 pages, not 8: MLRO Part 2, Crypto Part 1, AML Parts 1 to 3, PEP Parts 1 to 3, SAR Parts 1 to 3 and FATF Parts 1 to 2. Each needs bespoke content.
- **Merged-card retrofit:** Fraud Red Flags, False Positive Playbook, UBO Investigation Handbook and Source of Wealth predate the current composition. Treat this as optional quality improvement, not a publication defect or automatic retrofit requirement.
- **Delta page punctuation:** decide whether the generator should normalise em and en punctuation or whether generated sanctions delta pages receive a formal rule exception. Edit the generator, never generated pages individually.
- **content-relations.json exact-relation-set checker:** de-risking-judgement-call.html's relations exclude fatf-recommendation-16-intelligence-brief.html because that guide's own checker pins an exact relation set and would fail if a new inbound relation were added without updating it. Update that checker to allow additive relations, then add the reciprocal relation.

### Sourcing and ledger debt

- **Stablecoin Guide 1 absence finding:** stablecoin-series-guide-1.ddframework-category2-non-mandated-fields.001 is correctly recorded as a regulatory retained-as-estimate claim because no source can affirmatively establish the absence. Reassess this finding as part of a future editorial pass on the shipped guide; do not silently promote it to verified.
- **Legacy three-guide re-baseline:** freshly establish the remaining sourcing scope for aml-guide-part1.html, pep-guide-part1.html and sar-guide-part1.html. The prior counts in the old backlog contradicted later audit records and must not be reused.
- **Nine-guide audit reconciliation:** reconcile the 26-guide audit findings against current main for aml-guide-part3.html, pep-guide-part3.html, sar-guide-part3.html, fatf-guide-part1.html, fatf-guide-part2.html, crypto-guide-part2.html, sanctions-compliance-guide.html, screening-alerts-guide.html and adverse-media-intelligence-guide.html. Verification owner, source pack and review date remain unassigned, so this is RESEARCH, not Next Up.
- **Ledger hardening:** consider schema enforcement for source requirements by claim type, plus expiry handling that preserves original verification dates and records renewal separately. Post-proof hardening only.
- **De-Risking Judgement Call, unreviewed wording:** six PSRs 51B-conditionality sentences and the regulation 27(8) stipulation (added in the wording-only delta after external Review 2, commit range 25e8d1e..8d67fb6) were not independently reviewed by either the manual cross-model process or /code-review. All primary-text checks passed internally, but this content has not had the same external scrutiny as the rest of the guide. Flag for the next editorial pass on this guide, or run the deferred optional manual pass against review-paste-8d67fb6/ if it still exists locally.

## Build Loop

Scenario Lab expansion is no longer under a blanket pause. Cases 7 and 8 are released and the API synchronisation blocker closed on 3 October 2026, so queue-rule gating may resume. Further expansion remains gated by the queue rules and evidence of user value. No new case has been gated or approved.

### Research candidates

- **Domestic PEP Proportionality:** check FCA FG25/3 and any necessary primary regulatory text.
- **Event Driven CDD Review:** check the FCA April 2026 customer due diligence review and related primary material.
- **Failure to Prevent Fraud case:** a synthetic Scenario Lab case distinct from the shipped Failure to Prevent Fraud Evidence Essay guide (failure-to-prevent-fraud-evidence-essay.html, Experiment 04). Reuse that guide's verified ECCTA 2023 section 199, Home Office, CPS and SFO evidence pack rather than re-verifying from scratch.
- **Proliferation Financing Investigation:** establish a defensive dual-use scope and primary UK regulatory basis before promotion.

### Other build candidates

- **Remaining SAR Writing Sandbox Phase 1+ ideas:** after the scoped `sar-003` case above, a later scoping session may separately consider a structured evidence log, Practice Case Summary export, stronger session limits or feedback against an expert answer. Do not combine them. Keep UK NCA and POCA specific. Never generate filing-ready SAR narratives. Keep deterministic scoring separate from model commentary and model the cost of every added AI call.
- **Guide chatbot:** proof of concept indexed 29 sources into 1,148 chunks in the separate API repository. Before resuming, re-check that repository and solve the known ranking problem where literal keyword overlap can outrank the substantive answer. Scope source attribution, refusal behaviour, prompt injection, stale content and cost before any public build.
- **Stablecoin Due Diligence Assessment:** RESEARCH. Stablecoin Guide 1 has shipped, so that dependency is cleared. Remaining work is to apply the static framework to at least one real case and complete the queue-gate fields. Not READY.
- **Companies House KYB Investigation Lab:** retain as the preferred future public-data integration. Merge the "Companies House verified does not mean KYC complete" content angle and the phoenixism red-flag scenario into this one product concept.
- **Precision versus recall teaching visual:** defensive, synthetic and educational only. Keep distinct from the live screening tool.
- **Freemium API tier and API documentation:** unscoped. Treat pricing, authentication, rate limits, abuse protection and service obligations as one architecture decision before either item enters the queue.

### Parked build ideas

- PARKED 24 September 2026, pending a decision to schedule the live evaluation. **SAR Sandbox PR #5, scoring evidence and stability:** (1) red-flag evidence as {id, quote}, verified with the tokenised single-section rule; (2) ProjectedExtraction non-constructible outside the projector; (3) live evaluation, sampling fixed narratives A, B and one full-quality sar-003 narrative repeatedly, logging raw model outputs in the eval harness only, and comparing median-count versus 2-of-3 identity speculative aggregation on the same runs; (4) tighten the speculative-language prompt so that direct statements of suspicion are not flagged. Observed 24 September 2026: live A/B1/B2 scored 10/25/20 against single-run recordings of 5/25/25, and B2 flagged "we consider the account activity suspicious" as speculative.
- SEC EDGAR enrichment after the Companies House Lab has shipped and been used.
- Blockscout for a future wallet investigation lab, subject to fresh terms and rate-limit checks.
- FBI Wanted API only as clearly labelled US enrichment, never as a standalone feature.
- VATcomply, TaxID, OpenCorporates, World Bank, BINlist and Mediastack only after fresh official terms and limit verification.
- System-view architecture blueprints linking cases to controls and interfaces.
- Primary-source sanctions ingestion only if OpenSanctions cost or licensing exposure changes enough to justify a separate data platform.

## Content Loop

Queue order follows docs/CONTENT_OPERATING_PLAN.md section 8. There is no verified content candidate in Next Up. Every item below is RESEARCH, BLOCKED or PARKED until all four queue-rule fields are recorded. Evidence named below comes from the operating plan and has not been re-verified here.

### Priority research candidates

1. **Digital Identity Is Not the Whole of CDD: What Verification Does and Does Not Prove:** RESEARCH. Intelligence Brief. Check the February 2026 HM Treasury and DSIT guidance, the statutory digital verification services register and the line between identity verification and the wider CDD obligation.
2. **Customer Risk Scores: What the Number Cannot Decide:** RESEARCH. Decision framework on factors, weightings, overrides, evidence, model changes and review triggers. Check the FCA November 2025 risk-assessment findings. Link to the Scenario Lab Risk Scoring module.
3. **Financial Crime Control Testing: A Control Exists, But Does It Work?:** RESEARCH. Separate design, implementation and operating effectiveness. Check the FCA 2025 and 2026 good-and-poor-practice findings on CDD, risk assessments, monitoring, testing and audit.
4. **SAR Escalation Under Commercial Pressure:** RESEARCH. Develop as a UK-first judgement guide. Read the US Senate source directly and preserve allegation versus finding, but do not convert it into a UK legal standard. Establish the NCA, POCA, governance and documentation basis before promotion.
5. **Synthetic Data for AML Model Testing:** RESEARCH. Verify the FCA and Alan Turing Institute programme from primary sources, and check whether the 2026 Solution Sprint has published outcomes before stating what synthetic data can prove about model effectiveness.
6. **Nested VASP Exposure: The Counterparty You Cannot See:** RESEARCH. Narrow Intelligence Brief on nested relationships, visibility, attribution and due-diligence limits. Replaces the broader offshore-VASP proposal. Verify the claimed FATF March 2026 publication and prove a distinct decision model beyond the six-part Crypto series, the Travel Rule guide and the Scam Compound guide.

### Deliberate hold

- **Sanctions Ownership and Control: When 50 Percent Tells You Almost Nothing:** HOLD until the UK ownership-and-control consultation outcome. When resumed, cross-link with both Shadow Fleet guides.

### Reserve and parked content

- **Repeat AML Failure as a Risk Signal:** moved from the priority list to reserve research. It depends on the FinCEN UBS action and an unverified UK comparator. Find a primary FCA comparator first and do not create a blended US and UK standard.
- Possible MLRO Handbook Part 3: resourcing benchmarks and the future professional-services AML supervisor.
- Victim, Mule or Fraudster? The First Party Fraud Decision Handbook. Run an originality check against the shipped Money Mule Case File first.
- Investment Scam Investigation Handbook.
- Financial Crime Information Sharing: Can I Tell Another Bank?
- AI in AML: Where the Model Stops and the Control Begins.
- Agentic AI in AML: What Should an AI Agent Never Be Allowed to Do Alone? Prove non-overlap with ai-agent-transaction-guide.html first.
- Australia AML and CTF Tranche 2, parked until the implementation window creates renewed practitioner value.
- Cross-jurisdictional MLRO comparison across the user's six-regime footprint, parked until current UK work clears.

## Governance and external follow-ups

- **Digital Asset Attribution Standard:** the proposed four-level model was tested through the A7A5 work. The next action is a formal adoption review for CLAUDE.md and the verification ledger schema, not further informal validation.
- **Shared working-tree review safety:** move the rule "commit implementation before launching a review tool that can mutate the same working tree" into the canonical workflow. Do not leave it as backlog folklore.
- **Content guardrail migration:** decide whether the mechanism-first rule for nationality or ethnicity-labelled network topics and the defensive dual-use rule for proliferation-financing content should be added to CLAUDE.md. Neither is an active guide candidate by itself.
- **OPEN DECISION, Scenario Lab cadence:** docs/CONTENT_OPERATING_PLAN.md section 1 sets "two Scenario Lab cases per fortnight" while section 9 limits days 1 to 30 to two cases during the month. These conflict. Decide which governs, then amend the plan. Neither is edited here. Both remain gated by a proven API sync path.
- **FinCrime Week recurring cadence:** each Monday, manually source and publish the completed prior ISO week, run the generator and dedicated tests, complete the required external claim review, then verify production. Automated headline discovery and unattended publication remain out of scope.
- **AdSense:** resubmitted 7 September 2026. FinCrimeRadar-side consent and content-readiness fixes are closed. Google's Funding Choices displayStatus hidden symptom remained external and unexplained at the last authenticated review. Make no speculative frontend change. Revisit only after a Google response, account-status change or fresh production diagnostic change.
- **Trademark and LinkedIn slug:** trademark filing remains resource-dependent; slug reclaim depends on it.
- **Anthropic Open Source Programme application:** submission and support follow-up were previously recorded, but current external status was not available in this repository audit. Confirm externally before treating it as pending action.
- **SAR Sandbox LinkedIn drafts:** repository state cannot confirm whether they were posted. Check the account before retaining or scheduling them.
- **Authority building:** continue only through legitimate practitioner contributions, citations, relevant directories and useful community participation. No guaranteed-ranking or paid-link schemes.
- **Bank of England systemic stablecoin Code of Practice:** a primary-source recheck on 3 October 2026 confirmed that the consultation closed on 22 September 2026, the Code remains draft, and finalisation is still targeted for the end of 2026. Ledger claim overseas-stablecoin-perimeter.boe-multi-issuance-unsuitable.001 remains materially accurate, so no ledger edit is required. Revisit it once the Code is finalised. No owner, no urgency.

## Explicitly removed from the active backlog

The 14 September 2026 audit removed completed narratives, duplicate entries and rejected proposals. Important removals include:

- Scam or Civil Dispute? The APP Fraud Decision Framework, removed from the active queue because the shipped APP Scam Decision Framework already covers the civil-dispute boundary, partial or nominal performance, the GBP 85,000 cap and the PSR decision factors;
- the duplicate "Money Mule Is Also a Victim" guide, now shipped as the Experiment 02 Case File;
- all Stablecoin guide checkboxes: all six guides are live and the obsolete Guide 1 blocker has been removed;
- the obsolete summary-snapshot candidate, superseded by the programmatic social-card standard;
- duplicate APP scam and MLRO Part 3 entries;
- the rejected Private Markets duplicate, topics-hub rebuild, nine-domain taxonomy, 14-step universal framework, 30-guide schedule, automated FinCrime Week sourcing and full learning-platform architecture;
- completed AdSense remediation history, consent fixes, guide builds, source corrections and old Polish tasks already preserved in Git history.

Update this file when an item's state changes. Do not append a completion essay. Remove the item, update the compact shipped baseline if it changes the planning picture, and rely on the implementation commit and release record for detail.
