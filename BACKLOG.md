# FinCrimeRadar Backlog Board

Last fully audited: 14 September 2026.

This file is the current work queue for Claude Chat, Claude Code and Codex. It contains pending work, external blockers and deliberate holds only, plus a compact shipped baseline needed for planning. Detailed completion narratives belong in Git history, not in this backlog.

Guide structure and presentation are governed by GUIDE_STANDARD.md. Operating, sourcing and review rules are governed by CLAUDE.md. The guide production process is governed by docs/GUIDE_PRODUCTION_WORKFLOW.md.

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

- **54 publications live:** 24 parts across seven series and 30 standalone publications.
- **Series inventory:** UK AML 3 parts, PEP 3, SAR 3, FATF 2, MLRO 2, Cryptoasset Compliance 6, Stablecoin 5 live of 6 planned.
- **Stablecoin Series:** Guides 0, 2, 3, 4 and 5 are published. Guide 1 remains externally blocked and is listed under Content.
- **Current experimental formats:**
  - Framework: app-scam-decision-framework.html, Experiment 01, live.
  - Case File: money-mule-or-victim-case-file.html, Experiment 02, live.
  - Intelligence Brief: fatf-recommendation-16-intelligence-brief.html, Experiment 03, live.
  - Evidence Essay: gambling-white-label-blind-spot-guide.html, classification-asymmetry-guide.html and failure-to-prevent-fraud-evidence-essay.html, standing opt-in treatment.
- Case File and Intelligence Brief are accepted compositions following the completed cross-experiment review (see below); neither requires a second instance. Framework remains experimental: a second Framework implementation is still required to test recurrence rather than a single example.

### Product and publishing capability

- Scenario Lab is live with 17 cases: KYC and KYB 5, Fraud Detection 6, Risk Scoring 6.
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

### 1. Gambling Evidence Essay skip link

**Status: READY. Priority: small accessibility correction.**

Add the Global Core skip-to-content link to gambling-white-label-blind-spot-guide.html, matching its Evidence Essay sibling. Scope one file and run a targeted keyboard and focus check.

Verification owner: Codex backlog audit, 14 September 2026.

Repository evidence checked: GUIDE_STANDARD.md, gambling-white-label-blind-spot-guide.html, classification-asymmetry-guide.html.

Review date: 14 September 2026.

Verification outcome: confirmed. Classification Asymmetry has the skip link; Gambling does not.

## Polish Loop

### Confirmed product and accessibility debt

- **Evidence Essay viewport restoration:** the narrow-screen source-record reparent works on both Evidence Essays, but restoration after widening has not been proven on a real device or genuine responsive-mode viewport. This is an unverified transition, not a confirmed defect.
- **Classification Asymmetry scenario depth:** the guide has one worked scenario and no formal counterfactual. Decide whether to add a second scenario, add a formal counterfactual, or document a historical exception to the current standard.
- **Scenario Lab dispatch hardening:** replace conflicting silent module fallbacks with one explicit per-module dispatch map that fails loudly for an unknown module.
- **Scenario Lab stale API defence:** fetchCasesFrom accepts any non-empty array. Add response-shape and minimum-completeness checks so a stale partial API deployment cannot silently empty newer modules.
- **Scenario Lab case sync proof:** on the next real edit to scenario-lab/data/cases.json, confirm both the GitHub Action and the triggered API deployment complete. The manual deploy path is proven; the automated trigger has not yet had its first production exercise.
- **Screening cold-path latency:** last measured at 6.6 to 9.9 seconds. Re-measure before changing anything. First test a smaller OpenSanctions result limit with explicit truncation escalation; parallel RSS work can only recover a minor share of the delay.

### Shared architecture and presentation debt

- **Site chrome consolidation:** navigation remains substantially hand-inlined while footer mounting is shared. Scope migration and duplicated cookie-banner styles before implementation. Do not combine this with a visual redesign.
- **Interactive helper review:** three experiment suites now duplicate the browser server and CDP harness; all three JavaScript files duplicate consent-aware aggregate telemetry; two static checkers duplicate KnowledgeCountParser. Decide extraction only through the cross-experiment review. Preserve telemetry allow-lists and never transmit case selections, decision records or free text.
- **Contextual internal links:** add only genuinely useful mid-article links, in small reviewed batches. Do not keyword-stuff.
- **End-of-guide cheat sheets:** the old entry understated scope. Re-baseline before work. The named pages amount to 13 pages, not 8: MLRO Part 2, Crypto Part 1, AML Parts 1 to 3, PEP Parts 1 to 3, SAR Parts 1 to 3 and FATF Parts 1 to 2. Each needs bespoke content.
- **Merged-card retrofit:** Fraud Red Flags, False Positive Playbook, UBO Investigation Handbook and Source of Wealth predate the current composition. Treat this as optional quality improvement, not a publication defect or automatic retrofit requirement.
- **Delta page punctuation:** decide whether the generator should normalise em and en punctuation or whether generated sanctions delta pages receive a formal rule exception. Edit the generator, never generated pages individually.

### Sourcing and ledger debt

- **Stablecoin Guide 1 absence finding:** stablecoin-series-guide-1.ddframework-category2-non-mandated-fields.001 is correctly recorded as a regulatory retained-as-estimate claim because no source can affirmatively establish the absence. Reassess it when Guide 1 resumes; do not silently promote it to verified.
- **Stablecoin Guide 1 hybrid-stabilisation and wrapped-token clarifications:** PS26/18 (Cryptoasset Perimeter Guidance) newly clarifies at PERG 18.4.5 that products using hybrid stabilisation mechanisms (part backing assets, part algorithmic) are not qualifying stablecoins, and separately that wrapped stablecoin tokens are not automatically qualifying stablecoins. Found incidentally during the PS26/18 overseas-issuance verification; not yet in the ledger and not yet assessed against Guide 1's existing article-88g-qualifying-stablecoin.001 claim. No owner assigned, not urgent, just don't lose it.
- **Legacy three-guide re-baseline:** freshly establish the remaining sourcing scope for aml-guide-part1.html, pep-guide-part1.html and sar-guide-part1.html. The prior counts in the old backlog contradicted later audit records and must not be reused.
- **Nine-guide audit reconciliation:** reconcile the 26-guide audit findings against current main for aml-guide-part3.html, pep-guide-part3.html, sar-guide-part3.html, fatf-guide-part1.html, fatf-guide-part2.html, crypto-guide-part2.html, sanctions-compliance-guide.html, screening-alerts-guide.html and adverse-media-intelligence-guide.html. Verification owner, source pack and review date remain unassigned, so this is RESEARCH, not Next Up.
- **Ledger hardening:** consider schema enforcement for source requirements by claim type, plus expiry handling that preserves original verification dates and records renewal separately. Post-proof hardening only.

## Build Loop

Scenario Lab expansion remains **PAUSED** until real usage or engagement evidence justifies further investment. The two verified cases below remain ready research assets, but the pause blocks implementation.

### Verified but paused Scenario Lab cases

- **Sanctions Alert Surge:** grounded in OFSI's Citibank London Branch penalty notice. Verified figures: 970 payments, about GBP 19.7 million cumulative value and GBP 4,732,830.58 penalty. Verified 12 September 2026.
- **FATF Grey List Rule Change:** grounded in SI 2026/621. Verified proposition: from 30 June 2026, mandatory Regulation 33 EDD narrowed to FATF Call for Action jurisdictions, while grey-list status became a geographical risk factor. Verified 12 September 2026.

### Research candidates

- **Domestic PEP Proportionality:** check FCA FG25/3 and any necessary primary regulatory text.
- **Event Driven CDD Review:** check the FCA April 2026 customer due diligence review and related primary material.
- **Failure to Prevent Fraud case:** a synthetic Scenario Lab case distinct from the shipped Failure to Prevent Fraud Evidence Essay guide (failure-to-prevent-fraud-evidence-essay.html, Experiment 04). Reuse that guide's verified ECCTA 2023 section 199, Home Office, CPS and SFO evidence pack rather than re-verifying from scratch.
- **Proliferation Financing Investigation:** establish a defensive dual-use scope and primary UK regulatory basis before promotion.
- **OFAC aggregate ownership case:** a confirmed content gap, but US-only and paused with Scenario Lab.
- **Message and remittance-line screening case:** a confirmed content gap in the existing 17 cases, but paused with Scenario Lab.

### Other build candidates

- **Second Framework implementation:** required future work. `app-scam-decision-framework.html` (Experiment 01) is still Framework's only implementation, so its contract in GUIDE_STANDARD.md is evaluated on a single example, not on recurrence. A second Framework publication needs a topic and evidence pack verified through the normal Content Loop before this can enter Next Up, testing whether Framework's candidate primitives (sequential decision stages, Decision Record, Source/Application/Action reasoning, Red Team Questions, What Would Change My Decision, Practitioner Lens, compact operational summary) genuinely recur for a different subject rather than reflecting APP scam's specific reasoning.
- **SAR Writing Sandbox Phase 1+:** Phase 0 is already live. A later scoping session may consider more cases, a structured evidence log, Practice Case Summary export, stronger session limits and feedback against an expert answer. Keep UK NCA and POCA specific. Never generate filing-ready SAR narratives. Keep deterministic scoring separate from model commentary and model the cost of every added AI call.
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

- **Stablecoin Guide 1: UK Stablecoin Regulation 2026. Status: RESEARCH, moved from BLOCKED.** Guides 0, 2, 3, 4 and 5 are live. The overseas-issuance dependency this guide was blocked on is now resolved: FCA PS26/18 (Cryptoasset Perimeter Guidance, published September 2026) confirms the PERG chapter is PERG 18 (renumbered from PERG 19 in CP26/13), and PERG 18.3.5 states the territorial test for stablecoin issuance (carried on from, or arranged from, a UK establishment, or deemed under FSMA section 418(6B) where elements are carried out in the UK on the overseas person's behalf), with PERG 18.8.5-18.8.6 confirming an overseas issuer not caught by that test may still need dealing or arranging permission. Remaining dependency, narrower than before: the Government's still-unpublished statutory instrument, which PS26/18 confirms introduces new UKQS-specific dealing/arranging/safeguarding exclusions (lending, borrowing, collateral, payment-holding). The FCA plans to consult on the resulting PERG amendments in early Q4 2026 and publish final amended guidance in early 2027; re-check against that consultation and final guidance, not the now-superseded 30 September 2026 date, which was the authorisation-window opening, not a guidance-publication trigger.
- **Scam or Civil Dispute? The APP Fraud Decision Framework:** sources for the GBP 85,000 cap and PSR merits-based classification principle were previously verified. Refresh the evidence pack and add all four queue-gate fields before drafting. Keep distinct from the already-shipped APP Scam Framework.
- **The De-Risking Judgement Call:** test the practitioner decision angle against current FATF risk-based-approach material and UK correspondent-banking relevance.
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

## Explicitly removed from the active backlog

The 14 September 2026 audit removed completed narratives, duplicate entries and rejected proposals. Important removals include:

- the duplicate "Money Mule Is Also a Victim" guide, now shipped as the Experiment 02 Case File;
- all five published Stablecoin guide checkboxes, leaving only externally blocked Guide 1;
- the obsolete summary-snapshot candidate, superseded by the programmatic social-card standard;
- duplicate APP scam and MLRO Part 3 entries;
- the rejected Private Markets duplicate, topics-hub rebuild, nine-domain taxonomy, 14-step universal framework, 30-guide schedule, automated FinCrime Week sourcing and full learning-platform architecture;
- completed AdSense remediation history, consent fixes, guide builds, source corrections and old Polish tasks already preserved in Git history.

Update this file when an item's state changes. Do not append a completion essay. Remove the item, update the compact shipped baseline if it changes the planning picture, and rely on the implementation commit and release record for detail.
