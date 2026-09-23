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

## Current shipped baseline

Repository main and origin/main matched 99ba8608307d0c54a9a003d5a907bc4116c9ca9a during this audit. Production was checked independently on 14 September 2026.

### Knowledge Hub

- **56 publications live:** 25 parts across seven series and 31 standalone publications.
- **Series inventory:** UK AML 3 parts, PEP 3, SAR 3, FATF 2, MLRO 2, Cryptoasset Compliance 6, Stablecoin 6.
- **Stablecoin Series:** Guides 0 through 5 are published. All six guides are live.
- **Current experimental formats:**
  - Framework: app-scam-decision-framework.html (Experiment 01) and de-risking-judgement-call.html, both live. Second implementation confirms the Framework contract's candidate primitives (sequential decision stages, Decision Record, Source/Application/Action, Red Team Questions, What Would Change My Decision, compact operational summary) recur across a distinct subject (UK AML relationship decisioning vs. APP scam). Framework promoted from experimental to accepted, per GUIDE_STANDARD.md's own promotion criteria (a second instance testing recurrence, now complete). GUIDE_STANDARD.md's Framework contract table entry should be updated to reflect this at the next standards edit.
  - Case File: money-mule-or-victim-case-file.html, Experiment 02, live.
  - Intelligence Brief: fatf-recommendation-16-intelligence-brief.html, Experiment 03, live.
  - Evidence Essay: gambling-white-label-blind-spot-guide.html, classification-asymmetry-guide.html and failure-to-prevent-fraud-evidence-essay.html, standing opt-in treatment.
- Case File, Intelligence Brief and Framework are all now accepted compositions. Framework's recurrence test (a second implementation, distinct subject) is complete as of de-risking-judgement-call.html.

### Product and publishing capability

- Scenario Lab's static production release contains 19 cases: KYC and KYB 5, Fraud Detection 6, Risk Scoring 8. The live API still returns the previous 17-case payload, so the page currently exposes all 19 through its completeness-checked local fallback.
- SAR Writing Sandbox Phase 0 is live on the API service.
- Screening and PEP search, Knowledge Hub domain filtering, weekly digest and FinCrime Week are shipped.
- FinCrime Week W36 and W37 are present on main; W37 is the current issue in fincrime-week.html.
- Verification ledger contains 589 valid entries. python scripts/check_ledger.py validate passed during this audit.

### Experiment 03 shipment

Experiment 03 shipped through seven atomic commits from 7ae03c5 to a0e2402. It added the FATF Recommendation 16 Intelligence Brief, page JavaScript, social card, discovery surfaces, eight verified ledger records and permanent static and browser regression checks. Production serves the guide and the Knowledge Hub count is 53. No backend, account model, free-text collection or new shared component library was introduced.

### Experiment 04 shipment

Experiment 04 shipped through nine atomic commits from d98a717 to 3d87db3, merged into main via eb80299 (pull request #7). It added the Failure to Prevent Fraud Evidence Essay, page JavaScript, social card, discovery surfaces, 18 verified ledger records and permanent static and browser regression checks, following the Evidence Essay treatment already standing for gambling-white-label-blind-spot-guide.html and classification-asymmetry-guide.html rather than a new experimental shell. A completed manual adversarial review and a separate PR-based /code-review each found and closed real defects before merge: two statutory-scope overstatements of the section 199(3) victim exclusion, a citation-click handler that let native anchor navigation undermine the enhanced source panel, an unreciprocated content-relations.json entry, and one source record conflating sections 201 and 202 that needed splitting into two precise primary-source citations. Production serves the guide and the Knowledge Hub count is 54. No backend, account model, free-text collection or new shared component library was introduced.

### Cross-experiment review of Experiments 01 to 03

Completed. The permanent publication architecture (Universal Evidence Core, Intelligence Core, Public Format Contract, Subject Specific Composition), the standard evidence vocabulary, and the Framework, Case File and Intelligence Brief contracts are now defined in GUIDE_STANDARD.md. The production workflow, the GPT/Codex and Claude Code responsibility split, and the regression-scope discipline proven by Experiments 02 and 03 are now defined in docs/GUIDE_PRODUCTION_WORKFLOW.md, which also records the browser-harness and telemetry-helper extraction decisions (approved for future extraction, not extracted during this review). Case File and Intelligence Brief are accepted compositions; neither required a second instance. Framework remains experimental: a second Framework implementation is still required to test recurrence and remains open work, tracked below.

## Next Up

### Scenario Lab cases 7 and 8 release

- **Status:** BLOCKED. Commit ca5e3ac is on main and origin/main. The GitHub sync workflow succeeded and requested Render deploy dep-dap6bjijnfac73amjlbg, but the live API still returns 17 cases. The external API deployment state prevents release closure.
- **Verification owner:** Codex research session, 12 September 2026; primary sources rechecked during implementation on 22 September 2026.
- **Primary sources or repository evidence checked:** OFSI's Citibank N.A. London Branch penalty notice; SI 2026/621 regulation 19; HM Treasury's June 2026 Money Laundering Advisory Notice; the existing Risk Scoring schema and live-payload fallback contract.
- **Review date:** 22 September 2026.
- **Verification outcome:** source propositions confirmed; two deterministic cross-reference cases committed and pushed; local schema, JavaScript syntax, ledger and browser checks passed. Static production serves the 19-case data and the live page shows Risk Scoring cases 7 and 8 through its local fallback. GitHub Actions run 35721418857 succeeded, but the API remained at 17 cases after the triggered deployment, so API sync is not verified.

### SAR Writing Sandbox Phase 1A: third practice case (`sar-003`)

- **Status:** READY for release closure. **The Information Request** is built and deployed; closure pending the gate confirmation below. Do not add an evidence-log interface, export, session-limit redesign, expert-answer comparison, new endpoint, shared engine or extra AI call.
- **Verification owner:** Claude Code implementation and verification session, with Pratik as release approver. Independent regulatory review and remediation recheck completed before implementation.
- **Primary sources or repository evidence checked:** UKFIU SARs Best Practice Guidance, Chapter 2, version 1.1; NCA SARs in Action Issue 36; current official POCA sections 330 and 340 XML; both live SAR case payloads; `fincrimeradar-api` case schema, whitelist, extraction, answer-key and rate-limit paths; `scenario-lab.js` SAR picker, editor and results paths. The source pack is `C:\Users\prats\Documents\Codex\2026-09-22\sar-is-a-separate-product-from\outputs\SAR_Sandbox_Phase_1A_Source_Pack.md`.
- **Review date:** 23 September 2026.
- **Verification outcome:** PASS. The corrected regulatory source pack, synthetic-fact application, six-item answer key and proposed L1 to L4 ledger records passed a fresh independent remediation recheck. The build must still use a real GitHub pull request, `/code-review` and a separate post-implementation ChatGPT or Codex adversarial review because the answer key affects grading. fincrimeradar-api pull request 1 merged 22 September 2026 at commit 6e6787555d185ddf389658d875cabd94a11fc711, and the L1 to L4 ledger records are present; on the 23 September 2026 check date the live endpoint served sar-003 under the title The Information Request, the case display payload showed no answer-key field leakage, a live scoring submission returned a scored response in the expected shape without scoring the law-enforcement enquiry itself as a red flag, and the SAR picker on fincrimeradar.org showed and opened the case with no new console errors; a `/code-review` trigger comment is recorded on both merged pull requests but no review or findings were posted back on either; both pull request bodies state that a post-implementation Codex adversarial review passed, though this is a self-reported claim in the PR description rather than a separately posted review, so owner confirmation is still required; the Render deployed commit SHA was not read directly.

## Polish Loop

### Confirmed product and accessibility debt

- **Evidence Essay viewport restoration:** the narrow-screen source-record reparent works on both Evidence Essays, but restoration after widening has not been proven on a real device or genuine responsive-mode viewport. This is an unverified transition, not a confirmed defect.
- **Classification Asymmetry scenario depth:** the guide has one worked scenario and no formal counterfactual. Decide whether to add a second scenario, add a formal counterfactual, or document a historical exception to the current standard.
- **Scenario Lab dispatch hardening:** replace conflicting silent module fallbacks with one explicit per-module dispatch map that fails loudly for an unknown module.
- **Scenario Lab stale API defence:** fetchCasesFrom accepts any non-empty array. Add response-shape and minimum-completeness checks so a stale partial API deployment cannot silently empty newer modules.
- **Scenario Lab case sync proof:** the first production exercise completed the GitHub Action and triggered Render deploy dep-dap6bjijnfac73amjlbg, but the API continued to serve the old 17-case payload. Inspect the Render deployment result and build-time case fetch before treating the automated sync path as proven.
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

Scenario Lab expansion is no longer under a blanket pause. Cases 7 and 8 are in the release queue above. Further expansion remains gated by the queue rules and evidence of user value.

### Research candidates

- **Domestic PEP Proportionality:** check FCA FG25/3 and any necessary primary regulatory text.
- **Event Driven CDD Review:** check the FCA April 2026 customer due diligence review and related primary material.
- **Failure to Prevent Fraud case:** a synthetic Scenario Lab case distinct from the shipped Failure to Prevent Fraud Evidence Essay guide (failure-to-prevent-fraud-evidence-essay.html, Experiment 04). Reuse that guide's verified ECCTA 2023 section 199, Home Office, CPS and SFO evidence pack rather than re-verifying from scratch.
- **Proliferation Financing Investigation:** establish a defensive dual-use scope and primary UK regulatory basis before promotion.

### Other build candidates

- **Remaining SAR Writing Sandbox Phase 1+ ideas:** after the scoped `sar-003` case above, a later scoping session may separately consider a structured evidence log, Practice Case Summary export, stronger session limits or feedback against an expert answer. Do not combine them. Keep UK NCA and POCA specific. Never generate filing-ready SAR narratives. Keep deterministic scoring separate from model commentary and model the cost of every added AI call.
- **Guide chatbot:** proof of concept indexed 29 sources into 1,148 chunks in the separate API repository. Before resuming, re-check that repository and solve the known ranking problem where literal keyword overlap can outrank the substantive answer. Scope source attribution, refusal behaviour, prompt injection, stale content and cost before any public build.
- **Stablecoin Due Diligence Assessment:** blocked until Stablecoin Guide 1 ships and the static framework has been applied to at least one real case.
- **Companies House KYB Investigation Lab:** retain as the preferred future public-data integration. Merge the "Companies House verified does not mean KYC complete" content angle and the phoenixism red-flag scenario into this one product concept.
- **Precision versus recall teaching visual:** defensive, synthetic and educational only. Keep distinct from the live screening tool.
- **Freemium API tier and API documentation:** unscoped. Treat pricing, authentication, rate limits, abuse protection and service obligations as one architecture decision before either item enters the queue.

### Parked build ideas

- SEC EDGAR enrichment after the Companies House Lab has shipped and been used.
- Blockscout for a future wallet investigation lab, subject to fresh terms and rate-limit checks.
- FBI Wanted API only as clearly labelled US enrichment, never as a standalone feature.
- VATcomply, TaxID, OpenCorporates, World Bank, BINlist and Mediastack only after fresh official terms and limit verification.
- System-view architecture blueprints linking cases to controls and interfaces.
- Primary-source sanctions ingestion only if OpenSanctions cost or licensing exposure changes enough to justify a separate data platform.

## Content Loop

There is no verified content candidate in Next Up. Every item below is RESEARCH, BLOCKED or PARKED.

### Priority research candidates

- **Scam or Civil Dispute? The APP Fraud Decision Framework:** sources for the GBP 85,000 cap and PSR merits-based classification principle were previously verified. Refresh the evidence pack and add all four queue-gate fields before drafting. Keep distinct from the already-shipped APP Scam Framework.
- **Sanctions Ownership and Control: When 50 Percent Tells You Almost Nothing:** HOLD until the UK ownership-and-control consultation outcome. When resumed, cross-link with both Shadow Fleet guides.
- **Synthetic Data for AML Model Testing:** verify the FCA and Alan Turing Institute programme and the 2026 solution sprint from primary sources before drafting.
- **Offshore VASPs, Nested Exchanges and Invisible Crypto Counterparties:** verify the claimed FATF March 2026 publication and prove non-overlap with the six-part Crypto series and Travel Rule guide.
- **Repeat AML Failure as a Risk Signal:** verify the FinCEN UBS action and find a primary FCA comparator. Do not create a blended US and UK standard.
- **SAR Escalation Under Commercial Pressure:** read the US Senate source directly, preserve allegation versus finding, then prove a defensible UK NCA and POCA angle.

### Reserve and parked content

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
- **FinCrime Week recurring cadence:** each Monday, manually source and publish the completed prior ISO week, run the generator and dedicated tests, complete the required external claim review, then verify production. Automated headline discovery and unattended publication remain out of scope.
- **AdSense:** resubmitted 7 September 2026. FinCrimeRadar-side consent and content-readiness fixes are closed. Google's Funding Choices displayStatus hidden symptom remained external and unexplained at the last authenticated review. Make no speculative frontend change. Revisit only after a Google response, account-status change or fresh production diagnostic change.
- **Trademark and LinkedIn slug:** trademark filing remains resource-dependent; slug reclaim depends on it.
- **Anthropic Open Source Programme application:** submission and support follow-up were previously recorded, but current external status was not available in this repository audit. Confirm externally before treating it as pending action.
- **SAR Sandbox LinkedIn drafts:** repository state cannot confirm whether they were posted. Check the account before retaining or scheduling them.
- **Authority building:** continue only through legitimate practitioner contributions, citations, relevant directories and useful community participation. No guaranteed-ranking or paid-link schemes.
- **Bank of England systemic stablecoin Code of Practice consultation:** closes 2026-09-22. No owner, no urgency, just don't lose the date. Once resolved, it may affect overseas-stablecoin-perimeter.boe-multi-issuance-unsuitable.001, which currently describes the Code of Practice as still in draft.

## Explicitly removed from the active backlog

The 14 September 2026 audit removed completed narratives, duplicate entries and rejected proposals. Important removals include:

- the duplicate "Money Mule Is Also a Victim" guide, now shipped as the Experiment 02 Case File;
- all five published Stablecoin guide checkboxes, leaving only externally blocked Guide 1;
- the obsolete summary-snapshot candidate, superseded by the programmatic social-card standard;
- duplicate APP scam and MLRO Part 3 entries;
- the rejected Private Markets duplicate, topics-hub rebuild, nine-domain taxonomy, 14-step universal framework, 30-guide schedule, automated FinCrime Week sourcing and full learning-platform architecture;
- completed AdSense remediation history, consent fixes, guide builds, source corrections and old Polish tasks already preserved in Git history.

Update this file when an item's state changes. Do not append a completion essay. Remove the item, update the compact shipped baseline if it changes the planning picture, and rely on the implementation commit and release record for detail.
