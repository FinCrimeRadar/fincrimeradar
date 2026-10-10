# FinCrimeRadar Backlog Board

Last queue audit: 10 October 2026.

This file is the current work queue for Claude Chat, Claude Code and Codex. It contains unresolved work, external blockers and deliberate holds, plus a compact shipped baseline needed for planning. Detailed completion narratives belong in Git history, not in this backlog.

Guide structure and presentation are governed by GUIDE_STANDARD.md. Operating, sourcing and review rules are governed by CLAUDE.md. The guide production process is governed by docs/GUIDE_PRODUCTION_WORKFLOW.md.

The approved 90-day publishing cadence, automation boundaries, release gates and initial content queue are governed by `docs/CONTENT_OPERATING_PLAN.md`. Current repository and production evidence overrides stale planning baselines in that document.

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
Completed work is removed from the active queue. Update the compact shipped baseline when completion changes the planning picture, then rely on Git history and release records for detail.

## Current shipped baseline

Repository and queue state were audited on 10 October 2026 against `main` at `368f5f7369bb818807d453a94c79cd2e954bbac6`, which matched the live remote. Live checks during this audit covered the latest guide release, Knowledge Hub inventory, FinCrime Week, Scenario Lab inventory and SAR Sandbox case inventory. This was not a full site-wide production audit; production outside the named checks was last audited independently on 14 September 2026.

### Knowledge Hub and content

- **59 publications live:** 25 parts across seven series and 34 standalone publications. The repository and live Knowledge Hub both report 59.
- **Series inventory:** UK AML 3 parts, PEP 3, SAR 3, FATF 2, MLRO 2, Cryptoasset Compliance 6, Stablecoin 6.
- **Recent releases:** Investment Scam Investigation Handbook, 3 October 2026; Financial Crime Information Sharing, 4 October 2026; Digital Identity Is Not the Whole of CDD, published 5 October and modified 6 October 2026.
- **Digital Identity release closure:** local `main`, `origin/main`, the live remote and GitHub resolve to `368f5f7369bb818807d453a94c79cd2e954bbac6`. GitHub reports the intended 17-file commit. The guide, page JavaScript, social card, Knowledge Hub, sitemap and content relations matched the committed Git blobs on 10 October. The static contract and full browser regression passed against the same revision.
- **Accepted compositions:** Framework, Case File and Intelligence Brief. Evidence Essay remains a standing opt-in treatment. The permanent publication architecture and format contracts are defined in `GUIDE_STANDARD.md` and `docs/GUIDE_PRODUCTION_WORKFLOW.md`.

### Product and publishing capability

- Scenario Lab contains 19 cases: KYC and KYB 5, Fraud Detection 6, Risk Scoring 8. The live API matched the repository's exact entity IDs and module counts on the first attempt on 10 October 2026. The local fallback remains a resilience path and must not substitute for direct API release verification.
- SAR Writing Sandbox is live with three case summaries: `sar-002`, `sar-003` and `sar-phase0-001`. Case-file validation and verified scoring projection are shipped through API pull requests 3 and 4. Red-flag credit remains model-judged and is tracked under the parked PR 5 work.
- Screening and PEP search, Knowledge Hub domain filtering, weekly digest and FinCrime Week are shipped.
- FinCrime Week issues W36 to W40 are present on `main`. W40, covering 28 September to 4 October 2026, is the current published issue.
- Quiz titles use semantic `h2` headings across the 25-page repair scope. `learn.html` retains its two distinct badges. A shared scoped rule keeps all six `article-section` quiz headings white; real-browser computed-style, contrast and representative responsive checks passed on 10 October 2026.
- The verification ledger contains 695 valid entries with no overdue entries. `scripts/check_ledger_base.py`, `scripts/check_ledger.py validate` and `scripts/check_ledger.py overdue` passed on 10 October 2026.

## Next Up

No item is currently READY. Promote only after all four queue fields are recorded and the relevant source, originality and review gates pass.

## Polish Loop

### Confirmed product and accessibility debt

- **Evidence Essay viewport restoration:** the narrow-screen source-record reparent works on both Evidence Essays, but restoration after widening has not been proven on a real device or genuine responsive-mode viewport. This is an unverified transition, not a confirmed defect.
- **Classification Asymmetry scenario depth:** the guide has one worked scenario and no formal counterfactual. Decide whether to add a second scenario, add a formal counterfactual, or document a historical exception to the current standard.
- **Scenario Lab dispatch hardening:** replace conflicting silent module fallbacks with one explicit per-module dispatch map that fails loudly for an unknown module.
- **Scenario Lab API load-crash pattern:** the live API repository at `main` commit `4e4d109` still loads `routes_scenario_lab.py` cases with unvalidated `json.load` during import. Reuse the bounded, per-file Pydantic validation pattern already shipped for SAR Sandbox.
- **Screening cold-path latency:** last measured at 6.6 to 9.9 seconds. Re-measure before changing anything. First test a smaller OpenSanctions result limit with explicit truncation escalation; parallel RSS work can only recover a minor share of the delay.
- **Skip-link focus target gap:** a repository-wide scan on 10 October found 21 pages linking to `#main-content`; 17 targets lack `tabindex="-1"`. Digital Identity, Financial Crime Information Sharing, Gambling White Label and Investment Scam already conform. Fix the remaining 17 as a separately reviewed batch.
- **Pre-existing narrow-screen overflow:** the quiz-title browser run found page-level overflow at 390px on `fatf-guide-part2.html`, `scam-compound-money-laundering-guide.html` and `screening-algorithm-tuning-guide.html`. It persisted when each converted heading was reverted to a `div` in the browser, so the semantic repair did not introduce it. Identify the overflowing elements and scope a separate fix.
- **FCTR dated-field ambiguity:** the FCTR 12 chapter page (handbook.fca.org.uk/handbook/fctr12) shows a page-level "last updated 01/11/2024", while the FCTR 12.3 section page and its individual paragraphs (12.3.6G-12.3.8G) each independently show 13/12/2018. Confirmed as two genuinely different dated fields, not an error in either reading, during de-risking-judgement-call.html sourcing (2026-09-21). Any other guide citing FCTR 12.3 by its chapter-level date rather than its paragraph-level date should be checked for the same conflation. RESEARCH until scope across guides is confirmed.

### Shared architecture and presentation debt

- **Site chrome consolidation:** navigation remains substantially hand-inlined while footer mounting is shared. Scope migration and duplicated cookie-banner styles before implementation. Do not combine this with a visual redesign.
- **Interactive helper extraction:** the cross-experiment review approved future extraction of duplicated browser-server, CDP, consent-aware telemetry and `KnowledgeCountParser` helpers. Implement only as a dedicated regression-tested change. Preserve telemetry allow-lists and never transmit case selections, decision records or free text.
- **Contextual internal links:** add only genuinely useful mid-article links, in small reviewed batches. Do not keyword-stuff.
- **End-of-guide cheat sheets:** write bespoke content for 13 pages: MLRO Part 2, Crypto Part 1, AML Parts 1 to 3, PEP Parts 1 to 3, SAR Parts 1 to 3 and FATF Parts 1 to 2. Re-baseline the work before implementation.
- **Merged-card retrofit:** Fraud Red Flags, False Positive Playbook, UBO Investigation Handbook and Source of Wealth predate the current composition. Treat this as optional quality improvement, not a publication defect or automatic retrofit requirement.
- **Delta page punctuation:** decide whether the generator should normalise em and en punctuation or whether generated sanctions delta pages receive a formal rule exception. Edit the generator, never generated pages individually.
- **Content relation reciprocity:** the De-Risking checker now allows additive reciprocal relations, but `de-risking-judgement-call.html` and `fatf-recommendation-16-intelligence-brief.html` remain unlinked. Add the reciprocal relation and run both affected static suites.

### Sourcing and ledger debt

- **Stablecoin Guide 1 absence finding:** stablecoin-series-guide-1.ddframework-category2-non-mandated-fields.001 is correctly recorded as a regulatory retained-as-estimate claim because no source can affirmatively establish the absence. Reassess this finding as part of a future editorial pass on the shipped guide; do not silently promote it to verified.
- **Legacy three-guide re-baseline:** freshly establish the remaining sourcing scope for aml-guide-part1.html, pep-guide-part1.html and sar-guide-part1.html. The prior counts in the old backlog contradicted later audit records and must not be reused.
- **Nine-guide audit reconciliation:** reconcile the 26-guide audit findings against current main for aml-guide-part3.html, pep-guide-part3.html, sar-guide-part3.html, fatf-guide-part1.html, fatf-guide-part2.html, crypto-guide-part2.html, sanctions-compliance-guide.html, screening-alerts-guide.html and adverse-media-intelligence-guide.html. Verification owner, source pack and review date remain unassigned, so this is RESEARCH, not Next Up.
- **Ledger hardening:** consider schema enforcement for source requirements by claim type, plus expiry handling that preserves original verification dates and records renewal separately. Post-proof hardening only.
- **De-Risking unreviewed wording:** six PSRs 51B conditionality sentences and the regulation 27(8) stipulation added after external Review 2 were not independently reviewed. Run the deferred manual pass against the final wording before the next editorial change to this guide.

## Build Loop

Scenario Lab expansion is not blocked by API synchronisation, but no new case has completed the queue gate. Require evidence of user value before increasing the case inventory.

### Research candidates

- **Event Driven CDD Review:** check the FCA April 2026 customer due diligence review and related primary material.
- **Failure to Prevent Fraud case:** a synthetic Scenario Lab case distinct from the shipped Failure to Prevent Fraud Evidence Essay guide (failure-to-prevent-fraud-evidence-essay.html, Experiment 04). Reuse that guide's verified ECCTA 2023 section 199, Home Office, CPS and SFO evidence pack rather than re-verifying from scratch.
- **Proliferation Financing Investigation:** establish a defensive dual-use scope and primary UK regulatory basis before promotion.

Domestic PEP Proportionality is not a candidate. Scenario Lab already contains **The PEP Who Should Not Be Declined**, grounded in MLR 2017 and FCA FG25/3.

### Other build candidates

- **Remaining SAR Writing Sandbox Phase 1+ ideas:** after the shipped `sar-003` case, separately consider a structured evidence log, Practice Case Summary export, stronger session limits or feedback against an expert answer. Do not combine them. Keep UK NCA and POCA specific. Never generate filing-ready SAR narratives. Keep deterministic scoring separate from model commentary and model the cost of every added AI call.
- **Guide chatbot:** the historical proof of concept recorded 29 sources and 1,148 chunks in the separate API repository. Before resuming, re-check the current repository state and solve the known ranking problem where literal keyword overlap can outrank the substantive answer. Scope source attribution, refusal behaviour, prompt injection, stale content and cost before any public build.
- **Stablecoin Due Diligence Assessment:** RESEARCH. Stablecoin Guide 1 has shipped, so that dependency is cleared. Remaining work is to apply the static framework to at least one real case and complete the queue-gate fields. Not READY.
- **Companies House KYB Investigation Lab:** preferred future public-data integration. Merge the "Companies House verified does not mean KYC complete" content angle and the phoenixism red-flag scenario into this one product concept.
- **Precision versus recall teaching visual:** defensive, synthetic and educational only. Keep distinct from the live screening tool.
- **Freemium API tier and API documentation:** unscoped. Treat pricing, authentication, rate limits, abuse protection and service obligations as one architecture decision before either item enters the queue.

### Parked build ideas

- **SAR Sandbox PR 5, scoring evidence and stability:** PARKED pending a decision to fund a live evaluation. Scope includes evidence-linked red flags, projector construction control, repeated evaluation on fixed narratives and prompt tightening so direct statements of suspicion are not treated as speculative.
- SEC EDGAR enrichment after the Companies House Lab has shipped and been used.
- Blockscout for a future wallet investigation lab, subject to fresh terms and rate-limit checks.
- FBI Wanted API only as clearly labelled US enrichment, never as a standalone feature.
- VATcomply, TaxID, OpenCorporates, World Bank, BINlist and Mediastack only after fresh official terms and limit verification.
- System-view architecture blueprints linking cases to controls and interfaces.
- Primary-source sanctions ingestion only if OpenSanctions cost or licensing exposure changes enough to justify a separate data platform.

## Content Loop

The ordered candidates below remain RESEARCH until all four queue fields are recorded. Evidence named in `docs/CONTENT_OPERATING_PLAN.md` must be re-verified before promotion.

### Priority research candidates

1. **Customer Risk Scores: What the Number Cannot Decide:** RESEARCH. Decision framework on factors, weightings, overrides, evidence, model changes and review triggers. Check the FCA November 2025 risk-assessment findings and prove distinct value beyond the Scenario Lab Risk Scoring module.
2. **Financial Crime Control Testing: A Control Exists, But Does It Work?:** RESEARCH. Separate design, implementation and operating effectiveness. Check the FCA 2025 and 2026 good-and-poor-practice findings on CDD, risk assessments, monitoring, testing and audit.
3. **SAR Escalation Under Commercial Pressure:** RESEARCH. Develop as a UK-first judgement guide. Read the US Senate source directly and preserve allegation versus finding, but do not convert it into a UK legal standard. Establish the NCA, POCA, governance and documentation basis before promotion.
4. **Synthetic Data for AML Model Testing:** RESEARCH. Verify the FCA and Alan Turing Institute programme from primary sources, and check whether the 2026 Solution Sprint has published outcomes before stating what synthetic data can prove about model effectiveness.
5. **Nested VASP Exposure: The Counterparty You Cannot See:** RESEARCH. Narrow Intelligence Brief on nested relationships, visibility, attribution and due-diligence limits. Replaces the broader offshore-VASP proposal. Verify the claimed FATF March 2026 publication and prove a distinct decision model beyond the six-part Crypto series, the Travel Rule guide and the Scam Compound guide.
6. **E-commerce Fraud: From Account Creation to Chargeback:** RESEARCH. Proposed five-part flagship series covering The E-commerce Fraud System; Identity, Account and Promotion Abuse; Payment and Checkout Fraud; Fulfilment, Returns and Refund Abuse; and E-commerce Fraud Investigations and Control Operations. Scope is merchant-side fraud from account creation through post-transaction dispute, not every cyberattack, consumer scam or marketplace regulatory issue. Research may not begin until the employer-conflict gate in `docs/CONTENT_OPERATING_PLAN.md` passes: review the Nisbets contract and handbook provisions on outside activities, intellectual-property assignment and confidential information; obtain written clearance if any applicable clause is unclear; and park the series if clearance remains doubtful. The first authorised scope is limited to the series-level repository and Scenario Lab non-overlap review plus the Part 1 charter. The charter must record that every scenario, taxonomy and example comes only from identified public sources. Do not build the master taxonomy, five-guide Requirement Coverage Matrix, primary-source register or 15-scenario inventory in that first scope. Reuse existing account-takeover, device-network and refund-abuse coverage by reference rather than rewriting it. Keep chargebacks, statutory refund rights, unauthorised-payment protections and merchant fraud findings distinct. No Nisbets data, systems, policies, incidents, confidential knowledge or examples.

### Deliberate hold

- **Sanctions Ownership and Control: When 50 Percent Tells You Almost Nothing:** HOLD pending the UK ownership-and-control call-for-evidence outcome. A fresh GOV.UK check on 10 October 2026 found the call closed and no published outcome. When resumed, cross-link both Shadow Fleet guides.

### Reserve and parked content

- **Repeat AML Failure as a Risk Signal:** reserve research. It depends on the FinCEN UBS action and an unverified UK comparator. Find a primary FCA comparator first and do not create a blended US and UK standard.
- Possible MLRO Handbook Part 3: resourcing benchmarks and the future professional-services AML supervisor.
- Victim, Mule or Fraudster? The First Party Fraud Decision Handbook. Prove non-overlap with the Money Mule Case File and the e-commerce series first.
- AI in AML: Where the Model Stops and the Control Begins.
- Agentic AI in AML: What Should an AI Agent Never Be Allowed to Do Alone? Prove non-overlap with ai-agent-transaction-guide.html first.
- Australia AML and CTF Tranche 2, parked until the implementation window creates renewed practitioner value.
- Cross-jurisdictional MLRO comparison across the user's six-regime footprint, parked until current UK work clears.

## Governance and external follow-ups

- **Digital Asset Attribution Standard:** the proposed four-level model was tested through the A7A5 work. The next action is a formal adoption review for CLAUDE.md and the verification ledger schema, not further informal validation.
- **Shared working-tree review safety:** move the rule "commit implementation before launching a review tool that can mutate the same working tree" into the canonical workflow. Do not leave it as backlog folklore.
- **Content guardrail migration:** decide whether the mechanism-first rule for nationality or ethnicity-labelled network topics and the defensive dual-use rule for proliferation-financing content should be added to CLAUDE.md. Neither is an active guide candidate by itself.
- **FinCrime Week recurring cadence:** each Monday, manually source and publish the completed prior ISO week, run the generator and dedicated tests, complete the required external claim review, then verify production. Automated headline discovery and unattended publication remain out of scope.
- **AdSense:** PARKED pending a Google response, account-status change or fresh production diagnostic change. The site-side consent and content-readiness work is closed; do not make speculative frontend changes for the historical Funding Choices symptom.
- **Trademark and LinkedIn slug:** PARKED because the filing remains resource-dependent and slug reclaim depends on it.
- **Anthropic Open Source Programme:** external status is unverified. Confirm directly before treating the application or support follow-up as pending action.
- **SAR Sandbox LinkedIn drafts:** repository state cannot confirm whether they were posted. Check the account before retaining or scheduling them.
- **Authority building:** continue only through legitimate practitioner contributions, citations, relevant directories and useful community participation. No guaranteed-ranking or paid-link schemes.
- **Bank of England systemic stablecoin Code of Practice:** a primary-source check on 10 October 2026 confirmed that the consultation is closed, the Code remains draft and finalisation is still targeted for the end of 2026. Revisit the affected ledger claim when the final Code is published.

Update this file when an item's state changes. Do not append a completion essay. Remove completed items, update the compact shipped baseline if the planning picture changes, and rely on Git history and release records for detail.
