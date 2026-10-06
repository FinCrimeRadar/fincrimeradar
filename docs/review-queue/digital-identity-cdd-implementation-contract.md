# Digital Identity Is Not the Whole of CDD: implementation contract and Requirement Coverage Matrix

This document completes Content Loop step 06. It is the single contract for Claude Code implementation. It does not perform steps 07 or 08: Claude Code must divide the work into atomic tasks and assign every requirement below to exactly one task before changing publication files.

## 1. Authority and locked inputs

Apply requirements in this order:

1. `AGENTS.md` and `CLAUDE.md`.
2. `GUIDE_STANDARD.md`, especially the Universal Core, Intelligence Core, Guide Quality Layer and Intelligence Brief contract.
3. `docs/GUIDE_PRODUCTION_WORKFLOW.md`.
4. `docs/review-queue/digital-identity-cdd-source-pack.md`.
5. `docs/review-queue/digital-identity-cdd-design-memo.md`.
6. `docs/review-queue/digital-identity-cdd-editorial-draft.md`.
7. This Requirement Coverage Matrix.

If implementation reveals a conflict in the model, scenario verdicts or legal boundary, stop and return it for specification review. Do not silently solve it in page copy.

## 2. Expected file set

The anticipated publication files are:

- `digital-identity-cdd-intelligence-brief.html`
- `js/digital-identity-cdd-intelligence-brief.js`
- `digital-identity-cdd-intelligence-brief-social-card.png`
- `scripts/check_digital_identity_cdd_intelligence_brief.py`
- `scripts/test_digital_identity_cdd_intelligence_brief_browser.py`
- `knowledge.html`
- `sitemap.xml`
- `content-relations.json`
- `verification-ledger.json`
- `methodology.html` only if the current repository convention requires an Intelligence Brief entry

Do not create a shared component library or modify backend, account, authentication or free-text systems. Reuse the accepted Intelligence Brief composition in `fatf-recommendation-16-intelligence-brief.html` without copying its subject-specific `r16` namespace.

## 3. Locked publication identity

| Field | Locked value |
|---|---|
| File | `digital-identity-cdd-intelligence-brief.html` |
| Slug | `digital-identity-cdd-intelligence-brief` |
| Public format | Intelligence Brief |
| Knowledge Hub treatment | Default |
| Title | Digital Identity Is Not the Whole of CDD: What Verification Does and Does Not Prove |
| Visible standfirst | A certified result can establish one identity proposition. It does not decide who owns a company, why the relationship exists, whether the customer is low risk or whether the evidence remains current. |
| Evidence checked | 6 October 2026, including post-review remediation |
| Central thesis | A pass is not a customer verdict. It is a bounded evidence result. |
| Primary model | Six-field Proof Boundary Record |
| Scenarios | Two, exactly as defined in the design memo and editorial draft |
| Pattern families | Five, with identical inline and closing copies |
| Knowledge questions | Five |
| FAQ items | Six |
| Source records | Nine numbered records, with source 7 permitted to contain the linked framework and certification-scheme pair |

Search, social and structured-data descriptions may be tightened for length, but they must retain the proof-boundary thesis and must not imply that identity verification completes CDD.

## 4. Requirement Coverage Matrix

### A. Editorial and evidence

| ID | Requirement | Deterministic proof |
|---|---|---|
| E01 | Preserve the locked title, standfirst, thesis and UK MLR scope. | Static checker asserts exact strings and canonical title. |
| E02 | State that the brief concerns certified and registered digital verification services used by MLR-regulated firms. | Static checker asserts scoped language in the status or executive section. |
| E03 | Keep identification, identity verification, purpose, risk, corporate identity, authority, ownership, beneficial ownership, EDD, monitoring and records as distinct propositions where discussed. | Editorial review plus pinned key strings in static checker. |
| E04 | Present the Proof Boundary Record in the locked order: Subject, Proposition, Service scope, Assurance, Residual duties, Change trigger. | Static checker extracts labels and asserts order and uniqueness. |
| E05 | Label the Proof Boundary Record and control patterns as FinCrimeRadar assessments, not legal rules or regulator terminology. | Static checker asserts the label near the model and patterns. |
| E06 | Include the four-event 2026 timeline with dates and qualifications from the design memo. | Static checker asserts exactly four timeline events and required dates. |
| E07 | Include a settled and unresolved comparison that preserves every caveat from source-pack section 2. | Static checker asserts both groups and pinned caveat phrases. |
| E08 | Include Decision Horizon sections for Now, Next control cycle and On change. | Static checker asserts exactly three horizons and headings. |
| E09 | Include operational implications for policy, procurement and assurance, onboarding and systems, reviewers and MLRO teams, and records management. | Static checker asserts all five workstreams. |
| E10 | Include a static What Would Change Our Assessment section containing all six design-memo triggers. | Static checker asserts the section and trigger count. |
| E11 | Do not hard-code a count of registered services or present any provider or service as permanently registered. | Static checker bans service-count language and named endorsements; editorial review confirms. |
| E12 | Do not describe the February guidance as a safe harbour or transfer of liability. | Static checker bans `safe harbour` outside an explicit negation and pins responsibility wording. |
| E13 | Do not rewrite the unregistered-service caveat as a universal statutory ban. | Static checker pins the qualified formulation in the unresolved section and FAQ. |
| E14 | Do not imply that address, PEP or sanctions outputs are certified merely because they share a vendor response with the identity result. | Static checker pins the separate-propositions statement. |
| E15 | Do not imply that a director result verifies the corporate customer, authority, ownership, control or beneficial owner. | Static checker pins the director boundary in the main text and scenario. |
| E16 | Keep Source, Application and Action visibly separate in both scenario explanations. | Static checker asserts all three labels in each scenario reasoning block. |
| E17 | Include the two counterfactuals and keep them tied to separate new evidence, not an expansion of the original identity result. | Static checker asserts one counterfactual per scenario and pinned boundary language. |
| E18 | Cite every material regulatory claim to one or more of the nine public source records. | Static checker resolves every internal source link; ledger comparison and independent review provide substantive proof. |
| E19 | Use the evidence-state vocabulary consistently and distinguish established source propositions from FinCrimeRadar assessment and unresolved matters. | Static checker asserts the legend labels; editorial review confirms their application. |
| E20 | Avoid provider selection, product comparison, legal advice, identity scoring and any invented assurance threshold. | Static checker bans ranking and scoring constructs; editorial review confirms. |

### B. Information architecture and semantic HTML

| ID | Requirement | Deterministic proof |
|---|---|---|
| H01 | Implement all 18 sections in the locked information architecture and in the same order. | Static checker extracts section IDs and asserts order. |
| H02 | Include exactly one `h1` and preserve valid heading hierarchy without skipped levels. | Static checker. |
| H03 | Include a skip link targeting the main content, and make it the first visible keyboard target. | Static checker plus browser keyboard test. |
| H04 | Use semantic fieldsets and legends for both scenarios and all knowledge questions. | Static checker. |
| H05 | Use native `details` and `summary` for the six FAQ items and scenario reasoning. | Static checker plus browser keyboard test. |
| H06 | Give every section, form, field and live region a unique, page-specific ID. | Static checker rejects duplicate IDs and unresolved fragments. |
| H07 | Use a unique page namespace for CSS classes and JavaScript IDs. Do not reuse `r16` or generic experimental classes such as `card` or `btn`. | Static checker bans old and generic namespaces. |
| H08 | Keep the complete editorial substance in the HTML. JavaScript may reveal or score it but must not inject the only copy of material reasoning. | Script scan plus JavaScript-disabled browser test. |
| H09 | Render source citations as working in-page links to the numbered source list. | Static checker asserts every cited ID exists and every source is cited. |
| H10 | Include Article and BreadcrumbList JSON-LD aligned with the visible title, description, dates, canonical and image. | Static checker parses both JSON-LD objects. |

### C. Scenarios and control patterns

| ID | Requirement | Deterministic proof |
|---|---|---|
| S01 | Implement exactly two materially distinct scenarios from the editorial draft. | Static checker asserts two scenario articles and their locked facts. |
| S02 | Give each scenario exactly three options with one weak, one caution and one strongest grade. | Static checker. |
| S03 | Preserve the verdicts: Scenario 1 accepts the identity proposition while keeping purpose and risk open; Scenario 2 accepts the director result while keeping corporate propositions open. | Static checker pins strongest-option text and full reasoning. |
| S04 | Provide polite live-region feedback for no selection and every graded outcome. | Static checker plus browser tests. |
| S05 | Open the complete Source, Application and Action reasoning after any submitted option without hiding the counterfactual. | Browser test. |
| S06 | Implement exactly five pattern families with the locked titles and Risk, Signal, Response text. | Static checker. |
| S07 | Place each pattern once inline at a relevant point and once in the closing grid, with text-identical copies. | Static checker normalises and compares both copies. |
| S08 | Source the PNG summary export only from the closing pattern DOM. | Static checker plus browser export test. |

### D. Knowledge check and FAQ

| ID | Requirement | Deterministic proof |
|---|---|---|
| K01 | Implement the five editorial-draft questions with three choices and one correct answer each. | Static checker. |
| K02 | Preserve the correct-answer order B, C, A, B, C to avoid a single-position pattern. | Static checker. |
| K03 | Require all five answers before scoring and report the score through a polite live region. | Browser tests for empty, incorrect and correct paths. |
| K04 | Do not expose correctness through option length, visual styling before submission or accessible labels. | Manual content review and browser DOM inspection. |
| K05 | Implement all six FAQ questions and answers from the editorial draft. | Static checker asserts count and pinned questions. |

### E. Accessibility and responsive behaviour

| ID | Requirement | Deterministic proof |
|---|---|---|
| A01 | Meet the repository's WCAG 2.2 AA baseline, including visible focus, semantic controls, labels, contrast and polite status messages. | Static checker, browser keyboard test and contrast review. |
| A02 | Avoid horizontal overflow and clipped content at 320, 375, 390, 428, 768 and 1440 CSS pixels. | Browser regression at every width. |
| A03 | Preserve content and operation at 200 per cent zoom and under text expansion. | Browser regression. |
| A04 | Honour `prefers-reduced-motion`. | Browser regression. |
| A05 | Keep all material analysis, reasoning, patterns, FAQ answers and sources readable with JavaScript disabled. | Browser regression. |
| A06 | Make mobile navigation state and `aria-expanded` agree. | Browser regression. |
| A07 | Ensure every interactive target is keyboard reachable and has a visible focus indicator. | Browser keyboard traversal. |

### F. JavaScript, export and telemetry

| ID | Requirement | Deterministic proof |
|---|---|---|
| J01 | Use a page-specific external script and no inline interaction logic beyond permitted structured data. | Static checker. |
| J02 | Do not use `innerHTML` to reveal or construct reasoning. | Static script scan. |
| J03 | Emit only `scenario_complete`, `knowledge_check_complete` and `card_export`. | Static script scan plus browser event sequence. |
| J04 | Gate every analytics event on `fcr_cookie_consent_v2` being `accepted`. | Static scan and denied-consent browser test. |
| J05 | Limit scenario telemetry to guide ID, scenario ID and decision grade. | Browser event-schema assertion. |
| J06 | Limit knowledge telemetry to guide ID, score and total. | Browser event-schema assertion. |
| J07 | Limit export telemetry to guide ID and export type. | Browser event-schema assertion. |
| J08 | Never transmit selected text, answer content, rationale, free text, names, account details or customer data. | Static forbidden-field scan and browser payload assertion. |
| J09 | Export a non-blank 1200-pixel-wide PNG sourced from the five closing patterns and announce success or failure through a polite status region. | Browser download, image-dimension and pixel checks. Height may be set during implementation and then pinned. |
| J10 | Keep interaction failures non-destructive and understandable if Canvas, storage or analytics are unavailable. | Browser failure-path tests where deterministic; manual review otherwise. |

### G. Discovery, metadata and relationships

| ID | Requirement | Deterministic proof |
|---|---|---|
| D01 | Add one Default Knowledge Hub card with `data-date="2026-10-05"`, format `Intelligence Brief`, the locked title and a proof-boundary summary. | Static checker. |
| D02 | Update both visible Knowledge Hub guide counts to the actual declared-card total. | Shared count parser in static checker. |
| D03 | Add the canonical URL once to `sitemap.xml` with the repository's Intelligence Brief priority convention. | XML assertion. |
| D04 | Add exactly two reciprocal content relationships, preferred `kyc-onboarding-dilemma` and `perpetual-kyc-framework-guide`, after confirming they are the least redundant current choices. | JSON assertion plus rendered backlink checks in all three HTML files. |
| D05 | Include canonical, Open Graph and Twitter metadata with one 1200 by 630 social card. | Static checker plus image inspection. |
| D06 | Add or update the methodology record only if required by the current Intelligence Brief convention, with title, format, evidence date and link aligned. | Static checker if the file changes. |
| D07 | Do not expose internal workflow names, experiment labels or review notes in public content. | Static forbidden-string scan. |

### H. Ledger and regulatory review

| ID | Requirement | Deterministic proof |
|---|---|---|
| L01 | Run `python scripts/check_ledger_base.py` before ledger editing and preserve the base result. | Recorded command output. |
| L02 | Add one precise ledger record for each independently material regulatory claim rather than one record per source or paragraph. | Ledger validation plus claim-to-source review. |
| L03 | Use the public guide filename, primary-source URL, accurate claim text, verification date and review date in every new record. | Ledger checker and static page-to-ledger comparison. |
| L04 | Keep page source URLs and ledger source URLs aligned. | Static checker set comparison. |
| L05 | Run `python scripts/check_ledger_base.py` after editing and all other current ledger validation commands required by repository instructions. | Recorded command outputs. |
| L06 | Obtain independent regulatory review before publication for all six claim groups listed in source-pack section 7. | Review record with explicit pass or findings. Publication is blocked until this exists. |
| L07 | Apply any regulatory correction consistently to page copy, scenario feedback, FAQ, checker pins, ledger claims and derived assets. | Diff inspection plus full regression after remediation. |

### I. Permanent verification and release boundaries

| ID | Requirement | Deterministic proof |
|---|---|---|
| V01 | Add a dedicated static release checker covering this entire contract where deterministic. | Checker passes against the implementation. |
| V02 | Add a dedicated headless-browser regression covering widths, initial visibility, scrolling reveals, keyboard operation, scenario paths, knowledge paths, consent, export, reduced motion, zoom, text expansion, no-JavaScript reading and console errors. | Browser checker passes. |
| V03 | Run the new static and browser checkers plus every shared checker for files touched, including ledger, Knowledge Hub counts, sitemap, relationships and reading-time checks where present. | Recorded command outputs with no hidden failures. |
| V04 | Run other live experiment suites if a shared file they assert is changed. | Recorded regression list. |
| V05 | Perform an independent adversarial release review in a fresh GPT or Codex context after implementation and full integration checks. | Written review record. |
| V06 | Re-run the full relevant regression suite after remediation against the exact revision proposed for commit. | Recorded final outputs and revision SHA. |
| V07 | Inspect the exact staged file set and cached diff before commit. | `git diff --cached` and name-status evidence. |
| V08 | Do not commit, push, merge or claim production parity without separate user authorisation and the corresponding remote and live checks. | Workflow gate, not inferred from passing local tests. |

## 5. Mandatory independent review questions

The reviewer must answer each question directly.

1. Does any sentence imply that a successful identity result satisfies Regulation 28 as a whole rather than the individual identity-verification limb described in the guidance?
2. Are director, representative, beneficial owner and corporate-customer subjects kept distinct?
3. Is approved guidance described accurately without safe-harbour or immunity language?
4. Is the unregistered-service wording no broader than the February guidance supports?
5. Are identity, address, PEP and sanctions propositions kept separate unless exact certified scope is evidenced?
6. Do both scenario verdicts and every feedback string preserve the legal and evidential boundary?

## 6. Stop conditions

Stop implementation and return for specification review if:

- a source change alters the central Regulation 28 boundary;
- the live register or certification scheme no longer supports the service-specific model;
- the implementation needs a third scenario to make the model coherent;
- a proposed interaction would hide material reasoning from static or no-JavaScript readers;
- a shared-file edit would require unrelated content changes;
- the regulatory reviewer cannot approve a scenario verdict without legal advice or narrower wording.

Passing local checks does not authorise publication. Publication remains blocked by independent regulatory review, full integration regression, exact-scope staging and explicit release authority.
