# The E-commerce Fraud System: Part 1 implementation contract and Requirement Coverage Matrix

This document completes Content Loop step 06. It is the single contract for Claude Code implementation. It does not perform steps 07 or 08: Claude Code must divide the work into atomic tasks and assign every requirement below to exactly one task before changing publication files.

## 1. Authority and locked inputs

Apply requirements in this order:

1. `AGENTS.md` and `CLAUDE.md`.
2. `GUIDE_STANDARD.md`, especially the Universal Core, Intelligence Core, Guide Quality Layer and Default Knowledge Hub Guide contract.
3. `docs/GUIDE_PRODUCTION_WORKFLOW.md`.
4. `docs/review-queue/e-commerce-fraud-series-non-overlap-review.md`.
5. `docs/review-queue/e-commerce-fraud-part-1-charter.md`.
6. `docs/review-queue/e-commerce-fraud-part-1-source-pack.md`.
7. `docs/review-queue/e-commerce-fraud-part-1-design-memo.md`.
8. `docs/review-queue/e-commerce-fraud-part-1-editorial-draft.md`.
9. This Requirement Coverage Matrix.

If implementation reveals a conflict in the model, scenario verdicts, evidence boundary or consumer-rights treatment, stop and return it for specification review. Do not silently solve it in page copy.

## 2. Implementation ownership and expected file set

Claude Code owns all repository implementation, tests, Git operations and release preparation. Codex performs the later independent review.

The anticipated implementation files are:

- `e-commerce-fraud-system-guide.html`
- `js/e-commerce-fraud-system-guide.js`
- `e-commerce-fraud-system-guide-social-card.png`
- `scripts/check_ecommerce_fraud_system_guide.py`
- `scripts/test_ecommerce_fraud_system_guide_browser.py`
- `knowledge.html`
- `sitemap.xml`
- `content-relations.json`
- `fraud-red-flags-guide.html`
- `fraud-investigation-playbook.html`
- `verification-ledger.json`

Do not add a backend, API, database, account system, authentication system, free-text collection, shared renderer or generic fraud-decision engine. Do not modify `methodology.html`; the current standard Guide convention does not require an entry.

Use page namespace `ecf` for page-specific classes and IDs. Reuse the accepted shared navigation, scenario, FAQ and export families without copying another guide's subject-specific namespace.

## 3. Locked publication identity

| Field | Locked value |
| --- | --- |
| File | `e-commerce-fraud-system-guide.html` |
| Slug | `e-commerce-fraud-system-guide` |
| Public format | Guide |
| Knowledge Hub treatment | Default |
| Category | Fraud |
| Title | The E-commerce Fraud System: How Evidence Changes from Account Creation to Chargeback |
| Visible standfirst | Fraud signals do not keep the same meaning as an account becomes an order, a delivery, a refund and a dispute. This guide shows what each control may conclude, what it must pass forward and how later losses should change earlier decisions. |
| Evidence checked | 18 October 2026 |
| Central thesis | Move the evidence, its uncertainty and its decision level together. |
| Primary model | Six-field Fraud Evidence Relay |
| Secondary model | Seven-step backtrace test |
| Lifecycle stages | Six |
| Decision levels | Six |
| Outcome boundaries | Five |
| Scenarios | Two, exactly as defined in the design memo and editorial draft |
| Pattern families | Five, with text-identical inline and closing copies |
| Knowledge questions | Five |
| FAQ items | Six |
| Numbered public source records | Ten |
| Related items | Exactly two reciprocal relationships: `fraud-red-flags-guide` and `fraud-investigation-playbook` |

Search, social and structured-data descriptions may be shortened for platform limits. They must retain the cross-stage evidence-relay thesis and must not imply that the guide determines fraud, legal rights or card-scheme outcomes.

## 4. Requirement Coverage Matrix

### A. Editorial and evidence

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| E01 | Preserve the locked title, standfirst, evidence date, format and Fraud category. | Static checker asserts exact visible strings and metadata parity. |
| E02 | State the intelligence question, current assessment, evidence status, jurisdiction boundary and next trigger from the editorial draft. | Static checker pins all five elements. |
| E03 | Preserve the locked thesis that evidence, uncertainty and decision level move together. | Static checker asserts the exact thesis in the visible guide. |
| E04 | Present exactly six lifecycle stages in this order: Account and promotion; Checkout and authentication; Order review; Fulfilment and delivery; Return and refund; Dispute and outcome. | Static checker extracts labels and asserts order and uniqueness. |
| E05 | Present exactly six decision levels: event, account, order, linked network, refund and dispute. | Static checker asserts labels and count. |
| E06 | Present the Fraud Evidence Relay in the locked order: Decision level, Evidence state, Bounded conclusion, Action and owner, Relay package, Feedback trigger. | Static checker extracts labels and asserts order and uniqueness. |
| E07 | Label the Fraud Evidence Relay, backtrace test, decision-level model and control patterns as FinCrimeRadar assessments rather than legal rules, scheme terminology or vendor methods. | Static checker pins the attribution in the model and methodology sections. |
| E08 | Present the seven backtrace steps in the locked order: Fix the outcome; Rebuild the timeline; Find the first relevant signal; Inspect each handoff; Locate the reversible moment; Separate outcome types; Return the learning. | Static checker extracts labels and asserts order and uniqueness. |
| E09 | State that the backtrace tests reasonableness on evidence available at the time and is not hindsight blame. | Static checker pins the boundary sentence. |
| E10 | Keep the five outcomes separate: merchant fraud assessment, consumer-rights outcome, payment-service outcome, scheme dispute outcome and criminal conclusion. | Static checker asserts all labels and the no-merger statement. |
| E11 | Preserve the UK Finance figures and limitations exactly: £423.5 million, 3.2 million cases, 2025, industry-reported card or account incidents, not total e-commerce fraud or total merchant loss. | Static checker pins figures and caveat in the same section. |
| E12 | State that strong customer authentication can reduce some payment fraud without proving account control, honest intent, delivery, refund legitimacy or a later dispute result. | Static checker pins the bounded statement in the main text and FAQ. |
| E13 | Describe credential stuffing only as one possible route to legitimate-account access, not proof that any recovery event or new device is compromise. | Static checker pins mechanism and limitation. |
| E14 | Preserve Visa's boundary: its merchant guide does not replace Visa Rules, merchant agreements, acquirer requirements or applicable law and does not guarantee outcomes. | Static checker pins the caveat wherever scheme guidance is applied. |
| E15 | Preserve the Payment Services Regulations distinction among payer consent, authentication evidence and payment service provider refund duties, with source record 7 linking regulations 67, 74, 75 and 76 and source record 3 linking the FCA technical standards on application and exemptions. | Static checker asserts the three propositions, the merchant-rule caveat and the source links. |
| E16 | Preserve the Consumer Rights Act and Consumer Contracts Regulations boundary: rights depend on statutory conditions and are not automatically extinguished by a merchant fraud concern. | Static checker pins the qualified formulation. |
| E17 | Present the Artemis record as a United States sentencing case with guilty pleas, not a UK authority, prevalence measure or allegation-only source. | Static checker pins status and jurisdiction in Scenario 2 or the source record. |
| E18 | Label all fictional merchant, customer, account, order, device and outcome facts clearly as fictional and illustrative. | Static checker asserts the disclaimer at both scenarios and bans real-employer framing. |
| E19 | Do not name, describe or imply any Nisbets system, process, incident, customer, control or sponsorship. | Static forbidden-string and editorial review. The governance disclaimer may name Nisbets only if the public guide does not carry it; preferred public copy contains no employer name. |
| E20 | Keep Source, Application and Action visibly separate in both scenarios. | Static checker asserts the three labels in each scenario block. |
| E21 | Preserve one counterfactual per scenario and explain which conclusion changes and which evidence boundary does not. | Static checker asserts count and pinned outcome language. |
| E22 | Include the seven role-based control-owner checklist groups from the editorial draft. | Static checker asserts headings and required bullet count floor. |
| E23 | Include all six What Would Change Our Assessment triggers. | Static checker asserts the section and exact trigger count. |
| E24 | Cite each material factual, legal and scheme proposition to one or more of the ten numbered public source records. | Static checker resolves internal citations; ledger comparison and independent review prove substance. |
| E25 | Keep UK Finance as industry evidence, Europol as law-enforcement prevention guidance, Visa as scheme guidance, and the DOJ record as United States case evidence. | Static checker asserts source-type labels. |
| E26 | Mention Microsoft and Stripe only in the methodology originality note and do not use them as authority for law, regulation, prevalence or mandatory control claims. | Static checker asserts placement and bans their citation IDs in the substantive guide. |
| E27 | Do not invent fraud prevalence, control-effectiveness, false-positive, conversion, chargeback-win or loss-reduction figures. | Static forbidden-pattern scan plus editorial review. |
| E28 | Do not introduce vendor rankings, product recommendations, a fraud score, a universal risk threshold or an automatic guilt label. | Static forbidden-string scan plus editorial review. |
| E29 | Do not present the guide as legal advice or recommend refusing, delaying or reducing a refund without the qualified legal and scheme boundary in the editorial draft. | Static checker pins the FAQ qualification; independent review confirms. |
| E30 | Do not reproduce existing Scenario Lab facts from `session-hijack-002` or `device-network-006`. | Static checker bans known unique case strings; editorial comparison confirms distinct facts and decisions. |

### B. Information architecture and semantic HTML

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| H01 | Implement all 18 locked information-architecture sections in the same order. | Static checker extracts section IDs and asserts order. |
| H02 | Include exactly one `h1` and a valid heading hierarchy without skipped levels. | Static checker. |
| H03 | Include a skip link targeting main content and make it the first visible keyboard target. | Static checker and browser keyboard test. |
| H04 | Use semantic lists for lifecycle stages, decision levels, relay fields, backtrace steps, outcome boundaries and checklist groups. | Static checker and accessibility-tree inspection. |
| H05 | Use semantic fieldsets and legends for both scenarios, confidence controls and all knowledge questions. | Static checker. |
| H06 | Use native `details` and `summary` for the six FAQ items and scenario reasoning disclosure. | Static checker and browser keyboard test. |
| H07 | Give every section, form control, field and live region a unique `ecf`-namespaced ID. | Static checker rejects duplicate IDs, generic IDs and unresolved fragments. |
| H08 | Use page-specific `ecf` classes and do not reuse subject namespaces from existing guides. | Static checker bans known subject namespaces and generic experimental classes. |
| H09 | Keep complete editorial substance in the HTML. JavaScript may reveal, score or export it but must not inject the only copy of material reasoning. | Script scan and JavaScript-disabled browser test. |
| H10 | Render every citation as a working in-page link to a numbered source record. | Static checker asserts every citation target exists and every source is cited where expected. |
| H11 | Include Article and BreadcrumbList JSON-LD aligned with visible title, description, dates, canonical and image. | Static checker parses both JSON-LD objects. |
| H12 | Include the six-stage forward relay and reverse feedback visual with a complete textual equivalent. | Static checker asserts visual and accessible equivalent; browser review confirms reading order. |
| H13 | Do not add a second decorative process diagram. A Scenario 2 relationship view is allowed only if Claude Code stops for specification approval first. | File and DOM inspection. |

### C. Scenarios and control patterns

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| S01 | Implement exactly two materially distinct scenarios with the locked fictional facts. | Static checker asserts two scenario articles and pinned facts. |
| S02 | Scenario 1 must concern an authenticated established-account order, recovery event, new device and address, and post-approval address-change request before dispatch. | Static checker pins facts and decision question. |
| S03 | Scenario 2 must concern individually plausible claims, linked account or device evidence, alternative innocent explanation and separate individual-rights and network decisions. | Static checker pins facts and decision question. |
| S04 | Give each scenario exactly three choices with one weak, one caution and one strongest grade. | Static checker. |
| S05 | Preserve Scenario 1 grade order A weak, B caution, C strongest. | Static checker pins labels and option text. |
| S06 | Preserve Scenario 2 grade order A caution, B weak, C strongest. | Static checker pins labels and option text. |
| S07 | Preserve Scenario 1's strongest decision: bounded pause, cross-stage relay, trusted existing verification route and order-level conclusion without an account-fraud finding. | Static checker pins strongest option and Action reasoning. |
| S08 | Preserve Scenario 2's strongest decision: individual entitlement on its facts, separate linked-network assessment, retained evidence and no link-as-proof shortcut. | Static checker pins strongest option and Action reasoning. |
| S09 | After an option is selected, allow High, Medium or Low confidence before reasoning is revealed. | Static checker and browser path test. |
| S10 | Submission without a choice or confidence produces polite, specific live-region guidance and does not lose state. | Browser tests. |
| S11 | Any scenario choice reveals the complete Source, Application and Action reasoning and counterfactual already present in HTML. | Browser tests for all six option paths. |
| S12 | Counterfactual reconsideration must not overwrite the original answer and must explain what changed. | Browser state and live-region tests. |
| S13 | Implement exactly five pattern families with the locked titles and exact Risk, Signal, Response text. | Static checker. |
| S14 | Place each pattern once inline and once in the closing grid, with normalised text-identical copies. | Static checker compares both copies. |
| S15 | Source the PNG summary export only from the closing five-pattern DOM. | Static checker and browser export test. |

### D. Knowledge check and FAQ

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| K01 | Implement the five editorial-draft knowledge questions with three choices and one correct answer each. | Static checker. |
| K02 | Preserve correct-answer order B, C, A, B, C. | Static checker. |
| K03 | Require all five answers before scoring and report score and total through a polite live region. | Browser tests for empty, partial, incorrect and correct paths. |
| K04 | Question 5 must test the Scenario 1 counterfactual rather than label recall. | Static checker pins question and correct explanation. |
| K05 | Do not expose correctness through option length, pre-submit styling, DOM classes or accessible labels. | Static scan and browser DOM inspection. |
| K06 | Implement all six FAQ questions and complete answers from the editorial draft. | Static checker asserts count and pinned questions. |
| K07 | Preserve the qualified refund-delay answer: no universal answer, internal review does not automatically suspend timelines, and current legal and acquirer guidance is required. | Static checker pins the three qualifications. |
| K08 | Preserve the no-backend FAQ answer and do not turn it into a product recommendation. | Static checker pins the answer. |

### E. Visual, accessibility and responsive behaviour

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| A01 | Meet the repository WCAG 2.2 AA baseline, including semantic controls, labels, contrast, visible focus and polite status messages. | Static checker, keyboard test and contrast review. |
| A02 | Make the lifecycle visual understandable without colour and provide an equivalent ordered textual description. | Accessibility-tree and visual review. |
| A03 | Avoid horizontal overflow and clipped content at 320, 375, 390, 428, 768 and 1440 CSS pixels. | Browser regression at each width. |
| A04 | Preserve content and operation at 200 per cent zoom. | Browser regression. |
| A05 | Preserve layout under text expansion, including long source titles, scenario feedback and card labels. | Browser regression. |
| A06 | Honour `prefers-reduced-motion` and do not require animation to understand direction or feedback. | Browser regression. |
| A07 | Keep all analysis, reasoning, counterfactuals, patterns, FAQ answers and sources readable with JavaScript disabled. | Browser regression. |
| A08 | Make mobile navigation state and `aria-expanded` agree. | Browser regression. |
| A09 | Ensure every interactive target is keyboard reachable, has a visible focus indicator and is not obscured. | Keyboard traversal and focus screenshot review. |
| A10 | Keep control targets comfortably usable on touch devices and avoid hover-only explanations. | Browser inspection at mobile widths. |

### F. JavaScript, export and telemetry

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| J01 | Use only the page-specific external script `js/e-commerce-fraud-system-guide.js` for interaction logic. | Static checker. |
| J02 | Do not use `innerHTML` or string-built HTML to construct or reveal material reasoning. | Static script scan. |
| J03 | Do not make network calls, submit forms to a server or introduce any backend dependency. | Static script scan and browser network assertion. |
| J04 | Emit only `scenario_complete`, `counterfactual_complete`, `knowledge_check_complete` and `card_export`. | Static script scan and browser event sequence. |
| J05 | Gate every event on `fcr_cookie_consent_v2` being `accepted`. | Static scan and accepted, denied and missing-consent browser tests. |
| J06 | Limit scenario telemetry to guide ID, scenario ID, decision grade and confidence band. | Browser payload assertion. |
| J07 | Limit counterfactual telemetry to guide ID, scenario ID and whether the reader reconsidered. | Browser payload assertion. |
| J08 | Limit knowledge telemetry to guide ID, score and total. | Browser payload assertion. |
| J09 | Limit export telemetry to guide ID and export type. | Browser payload assertion. |
| J10 | Never transmit selected text, answer content, rationale, names, account details, order details, device data, addresses or other customer data. | Static forbidden-field scan and browser payload assertion. |
| J11 | Export a non-blank 1200-pixel-wide PNG sourced from the five closing cards and announce success or failure through a polite status region. | Browser download, dimension and pixel checks. Height is pinned after implementation. |
| J12 | Keep scenario, knowledge, counterfactual and export failures non-destructive if storage, Canvas or analytics is unavailable. | Deterministic browser failure paths and manual review. |
| J13 | Do not collect free text or persist scenario choices beyond what the existing page architecture needs for the current session. | Static DOM and storage inspection. |
| J14 | Pass `node --check js/e-commerce-fraud-system-guide.js`. | Recorded command output. |

#### Telemetry audit against product questions (18 October 2026)

Audited by reading `js/e-commerce-fraud-system-guide.js` at `f544c4477b93e0b4e2afaf3eaf5e5584c084e6ec` and running `scripts/check_ecommerce_fraud_system_guide.py`. The browser suite `scripts/test_ecommerce_fraud_system_guide_browser.py` was not re-run for this audit. No contradiction with J04 to J10 was found, so neither the guide nor its script changed.

| Event | Payload | Product question | Limitation |
| --- | --- | --- | --- |
| `scenario_complete` | `guide_id`, `scenario_id`, `decision_grade`, `confidence_band` | Are readers selecting evidence-bounded decisions, and at what confidence band? | Records the decision grade (weak, caution or strongest), not answer text or the chosen option. |
| `counterfactual_complete` | `guide_id`, `scenario_id`, `reconsidered` | Do readers say they would reconsider when a material fact changes? | Records self-reported reconsideration, not whether the reconsideration was correct. |
| `knowledge_check_complete` | `guide_id`, `score`, `total` | What is aggregate understanding across the five questions? | Cannot identify which individual boundary was misunderstood. |
| `card_export` | `guide_id`, `export_type` | Is the closing-pattern summary export used? | Records successful exports only, not attempts or failure rates. |

Consent gating and payload boundaries are unchanged: `emitAggregateEvent` sends nothing unless `localStorage.getItem('fcr_cookie_consent_v2') === 'accepted'` and `window.gtag` is a function, it is the only `window.gtag` call site, and the static checker pins the four event names and the four payload field sets. No selected answer text, rationale, customer information or free text is sent.

### G. Discovery, metadata and relationships

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| D01 | Add one Default Knowledge Hub card with `data-date="2026-10-18"`, category Fraud, format Guide, the locked title and a cross-stage evidence-relay summary. | Static checker. |
| D02 | Update both visible Knowledge Hub guide counts to the actual declared-card total. | Shared count parser and static checker. |
| D03 | Add the canonical URL once to `sitemap.xml` with the current Guide priority and change-frequency convention. | XML assertion. |
| D04 | Add exactly two reciprocal content relationships: `fraud-red-flags-guide` and `fraud-investigation-playbook`. | JSON set assertion and rendered backlink checks in all three pages. |
| D05 | Add the new guide's Related Topics section with exactly those two items. | Static checker. |
| D06 | Do not add a reciprocal relationship to `synthetic-identity-device-network-guide`; reference it only through normal editorial linking if useful. | JSON assertion and diff inspection. |
| D07 | Include canonical, Open Graph and Twitter metadata aligned with the visible title and description. | Static checker. |
| D08 | Create one 1200 by 630 social card with readable safe-area title and FinCrimeRadar branding. | Image-dimension and visual inspection. |
| D09 | Keep title, description, evidence date, canonical and image aligned across visible copy, metadata, JSON-LD, Knowledge Hub and social card. | Static cross-file comparison. |
| D10 | Do not expose internal workflow labels, queue states, source IDs, review notes or Claude Code instructions in public content. | Static forbidden-string scan. |
| D11 | Do not modify `methodology.html`. | Exact diff-scope check. |
| D12 | Calculate and display reading time using the current repository convention rather than a guessed value. | Existing reading-time checker or deterministic word-count comparison. |

### H. Ledger and independent review

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| L01 | Run `python scripts/check_ledger_base.py` before ledger editing and retain the result. | Recorded command output. |
| L02 | Create precise ledger records for the UK Finance figures, EBA and ECB authentication proposition, UK SCA boundary, credential-stuffing mechanism, Europol refund-abuse proposition, Visa evidence and limitation, regulations 67, 74, 75 and 76 as distinct claims, Consumer Rights Act boundary, Consumer Contracts boundary and DOJ sentencing facts. | Ledger validation and claim-to-source review. |
| L03 | Use the public guide filename, exact primary or official source URL, accurate claim text, verification date and review date in every new record. | Ledger checker and page-to-ledger comparison. |
| L04 | Keep page source URLs and ledger source URLs aligned, allowing separate precise regulation URLs where the public source record groups them. | Static set comparison with documented grouping rule. |
| L05 | Do not create ledger records for the Fraud Evidence Relay, pattern names or other clearly labelled FinCrimeRadar assessments as if they were sourced regulatory claims. | Ledger content review. |
| L06 | Run the current ledger baseline, scan, overdue and validate commands required by repository instructions after editing. | Recorded outputs with no hidden failures. |
| L07 | Obtain independent review before publication for the six claim groups in source-pack section 7. | Written review record with explicit pass or findings. |
| L08 | The reviewer must inspect both scenario verdicts, counterfactuals, all FAQ answers and every statement about delaying, refusing or reducing a refund. | Review checklist evidence. |
| L09 | Apply any correction consistently to guide copy, options, feedback, counterfactuals, FAQ, checker pins, ledger records, metadata and derived assets. | Diff inspection and full regression after remediation. |
| L10 | Publication remains blocked if the reviewer cannot approve the legal or scheme boundary without narrower wording or specialist advice. | Workflow gate recorded in review outcome. |

### I. Permanent verification and release boundaries

| ID | Requirement | Deterministic proof |
| --- | --- | --- |
| V01 | Add a dedicated static checker covering every deterministic requirement in this contract. | Checker passes against implementation and contains requirement-labelled assertions. |
| V02 | Add a dedicated headless-browser regression covering all named widths, keyboard operation, scenario paths, confidence, counterfactuals, knowledge paths, consent states, export, reduced motion, zoom, text expansion, JavaScript-disabled reading and console errors. | Browser checker passes. |
| V03 | Test all six scenario option paths, both no-selection paths and all confidence bands without reducing coverage to only the strongest answers. | Browser test inventory and output. |
| V04 | Test knowledge-check empty, partial, incorrect and fully correct paths. | Browser test output. |
| V05 | Test accepted, denied and missing-consent states and assert no event leakage. | Browser network and event assertions. |
| V06 | Run the new static and browser checkers plus every shared checker for changed files, including ledger, Knowledge Hub counts, sitemap, relationships and reading time. | Recorded regression list and outputs. |
| V07 | Run other live guide suites if a shared file they assert changes. | Recorded regression list. |
| V08 | Perform a fresh independent Codex release review after implementation and full integration regression. | Written review record. |
| V09 | Claude Code performs one consolidated remediation pass, then reruns the complete relevant suite. | Remediation diff and final outputs. |
| V10 | Inspect the exact staged file set and cached diff before commit. | `git diff --cached` and name-status evidence. |
| V11 | Do not include unrelated existing tracked or untracked work in the change set. | Status, staged-file and cached-diff inspection. |
| V12 | Do not commit, push, merge, publish or claim production parity without separate user authorisation and the corresponding remote and live checks. | Workflow gate, not inferred from passing local tests. |

## 5. Mandatory independent review questions

The fresh reviewer must answer each question directly.

1. Does any sentence imply that successful authentication proves account control, honest intent, delivery or a genuine order?
2. Are event, account, order, linked-network, refund and dispute conclusions kept distinct?
3. Does any device, address, account or payment link become proof of common control or dishonesty without adequate evidence?
4. Are consumer rights, payment-service protections, scheme outcomes, merchant fraud assessment and criminal conclusions kept separate?
5. Is the treatment of regulations 67, 74, 75 and 76 accurate about payer consent, authentication evidence, supporting evidence and payment service provider duties?
6. Does the refund-delay FAQ avoid implying that internal investigation suspends statutory or scheme timelines?
7. Does Visa guidance remain guidance rather than being presented as the rules, law or a guaranteed result?
8. Is the DOJ case described as a United States sentencing record and used only to evidence a mechanism?
9. Are both fictional scenarios materially distinct from existing Scenario Lab cases and clearly labelled illustrative?
10. Do both strongest options remain proportionate, bounded and reversible where appropriate?
11. Does every counterfactual change the relevant facts without expanding what authentication or a device link proves?
12. Does the public guide remain usable without JavaScript or backend services?

## 6. Stop conditions

Stop implementation and return for specification review if:

- a current primary source changes the authentication, consumer-rights, payment-service or scheme boundary;
- the legal reviewer cannot approve a scenario action or FAQ answer without materially different reasoning;
- implementation would require a backend, account integration, new personal-data flow or free-text collection;
- the current site architecture cannot support confidence and counterfactual interactions without hiding static reasoning;
- a shared-file change would require unrelated content changes;
- the two scenarios cannot remain distinct from existing Scenario Lab cases;
- the relationship graph cannot remain reciprocal without displacing unrelated links;
- the guide needs a fraud score, vendor recommendation or universal threshold to make the model coherent.

Passing local checks does not authorise publication. Publication remains blocked by independent legal and scheme review, full integration regression, exact-scope staging and explicit release authority.
