# The De-Risking Judgement Call: design memo (Task 2)

Companion to `de-risking-judgement-call-source-pack.md`. Scope: confirm the Intelligence Core, the stage sequence and two scenarios, and propose only the Framework primitives this subject justifies. No prose drafted.

## 1. Intelligence Core

| Element | Answer for this guide |
|---|---|
| Intelligence question | When a UK bank faces a higher-risk correspondent bank or customer relationship, at what point does exit stop being a defensible AML decision and become de-risking, and can the analyst evidence that line to a supervisor? |
| Evidence state | Established: MLR regs 18, 19, 28, 31, 33 as amended, 34; PSRs regs 51B, 51C; PRIN 2A text. Established as non-binding guidance: FATF Guidance, FCA de-risking page, FCTR 12.3. Industry position: JMLSG, carrying the SI 2026/621 update caveat. FinCrimeRadar assessment: residual risk, the outcome ladder, the mapping of the Increased Monitoring list to reg 33(6)(c), Consumer Duty on exit. Provisional: JMLSG revisions awaiting HMT approval. Unknown: JMLSG conformity date, HMT rationale for the 33(1)(b) narrowing. |
| Decision object | One relationship outcome from five: ordinary continuation, enhanced continuation, conditional or restricted continuation, discretionary decline or exit, mandatory decline or termination. Plus the Decision Record that defends it. |
| Uncertainty | JMLSG has not conformed to SI 2026/621. FATF lists change each plenary. Whether Part 6 of the PSRs reaches an institutional respondent. How the FCA reads tipping-off against the 51B reasons duty. No source defines a residual risk threshold. |
| Change condition | Named facts that flip the outcome: jurisdiction moves onto the Call for Action list (33(1)(b) and 33(3A) engage), CDD becomes impossible under reg 28 (reg 31 makes the decision for the firm), a shell bank link surfaces (reg 34(2)), suspicion arises (51C(c), POCA route), mitigants stop being verifiable. |
| Practitioner outcome | The reader can sort a relationship into mandatory versus discretionary, run the mitigant and capability tests before exiting, record a defensible rationale, and know which exit overlays apply and which do not. |

Nothing above needs a dedicated visual component. Each element is answered in prose, the Decision Record, the change-condition analysis and the evidence-state labels.

## 2. Stage sequence

The backlog architecture lists nine steps. Proposed sequence, eight stages plus the Decision Record. Two changes to the backlog order, both for defensibility.

1. **Risk identification.** Customer, geography, product, channel, transaction. Regs 18(2), 28(13), 33(6).
2. **Legal constraint check.** Placed second, before any judgement, because it can end the analysis: reg 31 (inability to complete CDD, mandatory termination), reg 34(2) (shell bank), reg 33(1)(b) (Call for Action, EDD content fixed by 33(3A)). This is the only stage whose output can be mandatory.
3. **Mitigants and their effectiveness.** Merges the backlog's "available mitigants" and "control effectiveness". A mitigant that cannot be shown to work is not a mitigant. FATF para 142 and FCTR 12.3.7G.
4. **Operational capability.** Kept separate. The question is different: can this firm actually run the mitigant at the required intensity (monitoring, staff, data access). A mitigant that works in principle but exceeds the firm's capacity is a legitimate input to the outcome. FCA page: exit is "ultimately a commercial one", but FCTR 12.3.8G warns against over-weighting reputational or business issues.
5. **Residual risk assessment.** Labelled FinCrimeRadar assessment, not regulator terminology.
6. **Escalation and approval.** Senior management approval is statutory at 33(3A)(e) and 34(1)(d) for those paths, and FCTR 12.3.8G good practice for exit decisions.
7. **Relationship outcome.** The five-outcome ladder.
8. **Exit execution (conditional).** Only reached if the outcome is discretionary or mandatory exit. Overlays: PSRs 51B and 51C (vintage and user-type conditional), PARs 2015 reg 26, PRIN 2A.2.10G(3) and (5)(iv) for retail customers, tipping-off, SAR consent for repayment (reg 31(2)).
9. **Decision Record.** The documented rationale as an artefact, not a stage: facts, assumptions, indicators, mitigants, decision, rationale.

Stage 8 is the only stage that is skipped for some paths, so the sequence is not a straight line. This matters for the recurrence test: Framework's "sequential decision stages" primitive holds, but this subject needs a conditional final stage that APP scam did not.

## 3. Two materially distinct scenarios

Materially distinct in facts, decision context, risk mechanism and the practitioner judgement tested, per the Worked decisions standard.

**Scenario 1: correspondent respondent in an Increased Monitoring jurisdiction (the hard test).**
- Context: institution-to-institution. Respondent bank established in a jurisdiction on the FATF Increased Monitoring list, not on the Call for Action list. Nested access to downstream customers. Some information requests answered, some not.
- Risk mechanism: geography plus opacity of downstream customers.
- Judgement tested: the post 30 June 2026 structure. No automatic reg 33(1)(b) trigger, but reg 34(1) measures still apply for a third-country respondent and the listing is a 33(6)(c) risk factor as an application. Outcome is likely conditional or restricted continuation (for example limited payment types, enhanced monitoring, senior sign-off) rather than exit.
- Counterfactual: the jurisdiction moves onto the Call for Action list. 33(1)(b) and 33(3A) now mandate EDD content and senior approval. Exit is still not mandated by that fact alone. This isolates which fact drives the outcome.
- Overlay stage: PSRs 51B probably does not bite (institutional respondent, contract terms). Stage 8 mostly reduces to contract notice and documentation.

**Scenario 2: a UK small remittance or charity customer where CDD cannot be completed (mandatory versus discretionary boundary).**
- Context: retail or small business, account opened after 28 April 2026. Customer is in a segment the FCA page names as often de-risked (money transmitters, charities). Beneficial ownership evidence is incomplete.
- Risk mechanism: incomplete CDD at the customer level, not geography.
- Judgement tested: the line between reg 31 (mandatory, because CDD cannot be applied as reg 28 requires) and a discretionary risk exit (where CDD is complete and the risk is simply high). The analyst must first exhaust FATF para 142 alternatives and JMLSG 5.2.7 (is it a document problem, not a risk problem?). Then exit execution matters: 51C(a) exempts the 90 day notice where CDD is genuinely impossible, whereas a discretionary exit sits inside 51B with 90 days and detailed reasons, and the tipping-off tension arises only if a suspicion exists.
- Counterfactual: the customer supplies the missing evidence. The outcome flips from mandatory termination to enhanced continuation, showing that the fact driving the decision is inability to complete CDD, not the customer segment.
- Overlay stage: fully live. PRIN 2A, 51B, 51C, PARs 26(9).

These differ on entity type, decision trigger, statutory constraint that binds, and how live the exit overlay is. Neither is a re-skin of the other.

## 4. Framework primitives, and what to leave out

| Primitive | Recommendation | Reason |
|---|---|---|
| Sequential decision stages | Use | Recurs, with a conditional final stage. Note the variation. |
| Structured Decision Record | Use | The subject exists to produce a defensible record. Facts, assumptions, indicators, mitigants, decision, rationale all map cleanly. |
| Source, Application, Action reasoning | Use, prominently | The pack shows heavy risk of blurring regulator statement, FATF guidance, JMLSG position and FinCrimeRadar inference. This is where the guide earns trust. |
| Red Team Questions | Use | Genuinely contested reasoning exists: "Would a supervisor read this as commercial de-risking?" "Is this exit reason sufficiently detailed and still not tipping off?" |
| Static What Would Change My Decision | Use | Maps directly to the Intelligence Core change condition. |
| Practitioner Lens (progressive disclosure) | **Leave out unless a real need appears** | No subject content clearly needs a hidden layer. If nothing recurs here, that is a legitimate finding for the recurrence test. |
| Compact operational summary | Use | A one-screen mandatory-versus-discretionary sort plus stage checklist is directly reusable. |

New constructs justified by this subject only (Subject Specific Composition, not for reuse as Framework requirements): the five-outcome ladder, the mandatory versus discretionary gate in stage 2, the conditional exit overlay stage, and an evidence-state strip for JMLSG and FATF materials.

Excluded on purpose: any APP scam construct (Four Verdict Problem, Nominal Performance Trap, Consumer Standard of Caution logic, the Six gates structure as such, "Scope is a gate"). Also excluded: a generic Framework renderer, a risk scoring engine, an interactive score for residual risk (no source supports a threshold, so none may be invented), and any consumer-facing exit letter template.

## 5. Risks to manage in the build

- Do not hard-code the FATF list contents as current. Date-stamp them.
- Do not state the reason HM Treasury narrowed 33(1)(b).
- Do not cite FCTR 12.3 as updated in 2024.
- Keep the Consumer Duty as an overlay for retail exits only.
- Section 10 discipline for every scenario feedback string: Source, Application, Recommendation kept visibly separate, especially for reg 31 versus reg 34 and 51B versus 51C.
- Section 7 external review is required before publication for the claims listed in the source pack, part H.
