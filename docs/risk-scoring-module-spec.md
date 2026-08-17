# Scenario Lab, Risk Scoring Module Spec

**Status: approved case list, ready for build. Rebuilt from scratch 2026-08-17 after the original "master spec doc" was confirmed never committed to the repo. Commit this file so it does not go missing again.**

Guide/interaction standards: see GUIDE_STANDARD.md. Enforcement, sourcing, review triggers: see CLAUDE.md. This spec defines module content and component reuse only, it does not restate those rules.

---

## Purpose

The third Scenario Lab module after KYC/Sanctions and Fraud Detection. The analyst is shown a profile of risk signals and must choose the proportionate risk response, then a reveal separates the material factors from the noise. It teaches the risk based approach as judgement, not as a mechanical score.

## Non negotiable inheritance (from the live modules)

- One `cases.json` array, read by the existing `routes_scenario_lab.py` FastAPI router on Render. Same file, same endpoint pattern as KYC and Fraud. No new endpoint.
- Shared case fields already proven: `entity_id`, `title`, `briefing`, `correct_disposition` (always an array), `rationale`.
- No timed auto advance after a decision, ever. Every case shows a manual "Next case →" alongside "Back to case list". No `setTimeout` based advance.
- `renderCompletionBody` dedupes `state.results` by `entity_id` (last write wins) before computing accuracy and attempted count, so re attempts do not inflate stats.
- Pure static and deterministic. No LLM call at runtime, unlike the SAR Sandbox. Zero recurring API cost.
- Dark forest green brand system, brand.css tokens only. British English, no em dashes or en dashes anywhere.

## Interaction model (the one new surface)

Each case renders a **risk factor board**: a set of signal cards, facts reveal on click, the decision unlocks once every card has been seen at least once. This is the Fraud module's cross reference card component, reused, not the timeline stepper (a risk assessment is simultaneous facts, not an ordered sequence).

The decision is a **graded response**, not binary:

1. Standard monitoring
2. Enhanced Due Diligence (EDD)
3. Escalate to MLRO
4. Block or SAR

`correct_disposition` stays an array, so a case can legitimately accept more than one defensible response where the reveal explains the trade off.

After the decision, the reveal names which factors were **material** and which were **noise**, and gives the rationale in three visibly separate parts (what the source/law establishes, the guide's application to these facts, the recommended action), per CLAUDE.md's scenario reasoning distinction rule.

## Component reuse map (build faster than Fraud did)

| Case | Reuses | Net new |
|---|---|---|
| 1, 2, 6 | Fraud cross reference card component + graded decision | none |
| 3 | KYC UBO force directed tree (click holder, reveal listed status + %, module computes aggregate) | none |
| 4 | KYC live risk calculator (computes High, analyst overrides) | small override control |
| 5 | Screening panel + a payment message document view | small message view |
| all | Decision banner extended to 4 graded options, reveal pattern | 4th/3rd option only |
| module close | Guide knowledge check pattern + existing completion screen | none |

## Review triggers (flag in the delivery report)

- The deterministic scoring function that maps the analyst's response and material factor selections to a score is **high stakes logic**: `/code-review` via a real GitHub PR AND the manual ChatGPT/Codex cross model pass before ship.
- Cases 3 and 4 carry arithmetic (aggregate ownership sum, points model), the sharpest focus for that review.
- Case 3 additionally triggers the **regulatory claim adversarial review** for its OFAC versus OFSI scope distinction, even though the case is illustrative, because it makes a statutory applicability claim.

## Sourcing note

Scenario Lab cases are illustrative composites, not sourced claims, so no verification ledger entries are required (same split as KYC and Fraud). But every regulatory principle a case states must be accurate. Do not invent scenario or regulatory content beyond what this spec defines. Where a case names a real rule, the framing below is the approved framing.

---

## The six cases

### Case 1: The Country Flag That Is Not the Risk

**Signals (board cards):** a connection to a high risk third country (MLR 2017 reg 33 EDD territory), small and consistent volumes, a transparent and documented source of funds, a plausible economic rationale for the relationship, and one distractor (a common name producing a weak adverse media match on a different individual).

**Material:** the high risk third country connection, which triggers EDD under MLR 2017 reg 33. **Noise:** the weak adverse media match on a namesake, the small volumes on their own.

**Correct response:** Enhanced Due Diligence. Not Block (nothing here supports declining), not Standard (reg 33 EDD is mandatory once the jurisdiction connection exists).

**Teaches:** proportionality in both directions. A single geography flag does not auto escalate to Block, and it does not get waved through either. This deliberately sits against the de risking instinct.

**Rationale framing:** reg 33 establishes the EDD obligation for high risk third countries. The guide's application concludes the substance here is otherwise low risk. The recommendation is EDD with documented rationale, not exit.

---

### Case 2: The PEP Who Should Not Be Declined

**Signals:** a screening hit confirming the customer is a domestic PEP (or a relative or close associate of one), no adverse media, a clear and legitimate source of wealth, ordinary product usage, and a distractor (the sheer fact of being a "PEP list hit" presented as if it were an adverse finding).

**Material:** PEP/RCA status triggers EDD under MLR 2017 reg 35. **Noise:** the list hit treated as derogatory, it is a status trigger, not a finding of wrongdoing.

**Correct response:** Enhanced Due Diligence, proportionate. Not Block.

**Teaches:** PEP status is not grounds to decline. Under FCA FG17/6 and the post FSMA 2023 position, a domestic PEP starts from a lower risk baseline than a foreign PEP absent other factors. Declining a customer purely for being a domestic PEP is the common, wrong, over reaction.

**Rationale framing:** reg 35 and FG17/6 establish the EDD requirement and the lower domestic baseline. The guide's application finds no aggravating factor. The recommendation is proportionate EDD, not exit.

---

### Case 3: Clean on the Name, Blocked on the Maths

**Reuses the UBO tree.** The analyst clicks each shareholder to reveal listed status and holding.

**Structure:** the entity itself screens clean on direct matching. Two separate shareholders are each on the OFAC SDN list, holding (for example) 30% and 25%. Neither alone reaches 50%. In aggregate they hold 55%.

**Material:** aggregate OFAC listed ownership at or above 50%. **Noise:** the clean direct screen on the entity name (the trap, structured name matching never catches this).

**Correct response:** Block or SAR.

**Teaches, with the mandatory jurisdiction contrast:**
- **OFAC (US):** under the 50 Percent Rule, an entity owned 50% or more **in the aggregate** by one or more blocked persons is itself blocked, whether or not it appears on the SDN list. Two listed holders summing to 55% means the entity is blocked.
- **OFSI (UK):** the ownership and control test is applied differently. Ownership generally turns on a designated person holding **more than 50%** (assessed per designated person), plus a separate qualitative **control** test (right to appoint or remove a majority of the board, or ability to ensure the entity's affairs are conducted per their wishes). The UK does not apply the same explicit aggregate summing bright line, and the control limb is assessed case by case.

The case must state this contrast in the reveal. A UK analyst should learn the OFAC rule **and** learn not to assume it maps one to one onto OFSI.

**Carries arithmetic** (the aggregate sum) and the **regulatory claim review** (the OFAC/OFSI scope distinction).

**Rationale framing:** OFAC guidance establishes the aggregate rule expressly. The guide's application sums the two holdings to 55% and concludes the entity is blocked under OFAC. The OFSI contrast is stated as the separate UK position, not as the same rule.

---

### Case 4: The Over Scored Customer

**Reuses the live risk calculator.** An illustrative points model, **labelled on screen as a training model, not a regulatory weighting**, stacks several individually minor flags and outputs High.

**Signals feeding the model:** online only onboarding, a single low value inbound from a foreign account, a common surname producing a weak sanctions fuzzy match below any sensible threshold, a new account age. Each is minor. The naive additive model sums them to High.

**Material:** nothing here is individually material enough to justify High. **Noise:** every stacked flag, each immaterial on its own, over weighted by mechanical addition.

**Correct response:** override to Standard (or Standard with light EDD), **with documented rationale**. Not accept the model's High.

**Teaches:** the MLR 2017 risk based approach (regs 18 to 19) requires judgement. A score is an input, not a verdict. This is the false precision the SAR Sandbox PRD review flagged, made into a case. The override must be documented, silent override is also wrong.

**Carries arithmetic** (the deliberately flawed points model). The on screen model must be explicitly illustrative.

**Rationale framing:** the risk based approach establishes that judgement governs. The guide's application finds no individually material factor. The recommendation is a documented override, not blind acceptance and not silent dismissal.

---

### Case 5: The Name in the Free Text Field

**Reuses the screening panel plus a payment message view.**

**Structure:** a payment. Every structured party field (debtor, creditor, agents) screens clean. The free text remittance/reference line contains a sanctioned name, vessel, or term that structured name screening never inspected.

**Material:** the sanctioned term in the free text field. **Noise:** the clean structured screen (the trap, it looks like a pass).

**Correct response:** Escalate or Block, investigate. Do not clear on the structured pass alone.

**Teaches:** structured field name screening and free text message line screening are distinct controls. A sanctioned name typed into a reference field defeats party field matching entirely. This is a real, under taught blind spot.

**Rationale framing:** the screening obligation covers the payment, not only its structured fields. The guide's application finds the hit in free text. The recommendation is escalate/block, not clear.

---

### Case 6: The Pattern, Not the Mixer

**Reuses the cross reference board.**

**Structure:** on chain behaviour showing heavy crypto mixer usage immediately preceding a large withdrawal or off ramp. **No named mixer. No claim about any entity's current sanctions status.**

**Material:** the behavioural pattern, obfuscation of source immediately before cash out. **Noise:** any instinct to anchor on whether a specific named tool is currently designated (designations are contested and reversible, and irrelevant to the pattern).

**Correct response:** EDD or Escalate, consider a SAR on the pattern.

**Teaches:** the red flag is the behaviour, not the brand. Built entirely around the pattern per the standing correction (Tornado Cash was delisted by OFAC in March 2025 following the Fifth Circuit Van Loon ruling, and naming any mixer's current status dates the case the moment it ships).

**Rationale framing:** the behavioural pattern is the established red flag. The guide's application reads the sequence as source obfuscation before cash out. The recommendation is EDD/escalate/SAR consideration, with no reliance on any named entity's designation status.

---

## Build acceptance criteria

- All 6 cases load from the single `cases.json` via the existing FastAPI router, no new endpoint.
- Cross reference board gating works: decision locked until every signal card seen at least once (verify by triggering, not by reading CSS).
- Case 3 UBO tree computes the aggregate correctly and the reveal states the OFSI contrast.
- Case 4 model is visibly labelled illustrative and the override path works.
- Graded decision accepts the `correct_disposition` array and the reveal separates material from noise per case.
- No auto advance anywhere. Manual "Next case →" and "Back to case list" on every case.
- Completion screen dedupes by `entity_id` (re attempt does not inflate the count).
- Real mobile device width check (iframe emulation at 320/375/390/428/768), interactions triggered and verified, not inferred at rest. Browser window resize is confirmed non functional in this environment.
- Delivery report flags: the scoring function for high stakes review, and Case 3 for the regulatory claim review.
