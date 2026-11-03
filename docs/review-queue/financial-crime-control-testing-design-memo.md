# Financial Crime Control Testing: A Control Exists, But Does It Work?, design memo

Status: specified for Claude Code implementation on 1 November 2026. Loop: Content. Public format: Framework using the Default Knowledge Hub treatment. This memo and the source pack form the implementation contract. No public page, release date or publication approval exists yet.

## 1. Intelligence Core

| Element | Decision |
| --- | --- |
| Intelligence question | What evidence is sufficient to conclude that a financial crime control is designed appropriately, deployed across its intended scope and operating effectively? |
| Evidence state | Established: MLR and applicable SYSC requirements for effective controls, review and conditional independent audit. Guidance: FCG and FCA findings. Public-sector practice: GOV.UK fraud control testing methods and ratings. FinCrimeRadar assessment: the Control Proof Chain, the three proofs and the Not evidenced outcome. |
| Decision object | One bounded control effectiveness conclusion for a named control, scope and period, with the action that follows. |
| Uncertainty | No source read sets one sample size, failure tolerance, test frequency or rating scale across financial crime controls. Applicability varies by firm, control and regulatory perimeter. |
| Change condition | New legal or FCA testing requirements, a source that prescribes a cross-control methodology, evidence that the proposed model produces misleading conclusions, or a material change to the MLR or SYSC provisions relied upon. |
| Practitioner outcome | The reader can scope a control test, choose evidence that addresses design, deployment and operation, avoid false assurance, state a supportable conclusion and specify remediation and retest. |

## 2. Scope and non-overlap

Audience: UK financial crime practitioners in first-line control ownership, second-line monitoring, MLRO oversight and internal audit. The guide teaches a shared conclusion discipline. It does not decide organisational ownership for a particular firm.

In scope:

1. Risk and control-objective linkage.
2. Design, deployment and operating evidence.
3. Test population, period, method and sample limitations.
4. Manual, automated and outsourced controls.
5. Exceptions, root cause, remediation and retest.
6. Four conclusion states for the stated scope and period.

Out of scope:

1. A universal audit programme or sample-size table.
2. Certification, assurance opinions or legal advice.
3. A control library for every AML, fraud or sanctions process.
4. Live red-team testing instructions that could bypass real controls.
5. Scoring a firm's whole financial crime framework.
6. Detailed transaction-monitoring model validation.

Repository search on 1 November 2026 found no existing public page containing the phrases `control testing`, `design effectiveness` or `operating effectiveness`. Four pages mention internal audit or monitoring in passing. The closest publication, `customer-risk-score-decision-framework.html`, covers one scoring method's governance and change cycle. It does not teach a cross-control test method, test population design, evidence sufficiency, conclusion states or remediation retest. This publication is therefore distinct.

## 3. Originality thesis

Regulators repeatedly require or encourage effective controls and testing, but the source set does not provide a single private-sector UK method for turning documents, samples, data and exceptions into a defensible conclusion.

FinCrimeRadar contributes:

1. **The Control Proof Chain:** risk, control objective, design, deployment, operation, exceptions, remediation and retest.
2. **The three proofs:** design proof, deployment proof and operating proof.
3. **The Not evidenced outcome:** a disciplined refusal to treat missing or weak evidence as a pass or a failure.
4. **The evidence-to-conclusion rule:** every conclusion names its control, population, period, method, limitation and next action.
5. **The false-assurance tests:** policy existence, a clean sample, vendor assurance and absence of incidents are each challenged separately.

This is an operational control framework, not a regulator summary.

## 4. Format and visual design

Framework is appropriate because the reader's job is to reach and defend a difficult judgement using a structured method. Use the standard Knowledge Hub shell. Do not create a generic Framework renderer or shared CSS abstraction.

Page-specific namespace: `fct-`.

Required visuals:

1. One static Control Proof Chain diagram with an adjacent text equivalent.
2. One three-proof evidence matrix showing the question, evidence and common false assurance for each proof.
3. One conclusion ladder showing Effective, Partially effective, Ineffective and Not evidenced. It must make clear that the fourth is an evidence limitation, not a weak pass.

Do not add a calculator, maturity score, sample-size generator, heat map or animated dashboard. No source supports numerical thresholds and the subject does not need them.

## 5. The analytical model

### The Control Proof Chain

1. **Risk:** state the failure or abuse the control is intended to reduce.
2. **Control objective:** state what must happen, for which population, at what point and with what escalation.
3. **Design:** decide whether the specified control could achieve the objective if performed as written.
4. **Deployment:** verify that the control reaches the intended systems, records, staff, vendors, products and jurisdictions.
5. **Operation:** verify performance over the selected period, including exceptions and hand-offs.
6. **Exceptions:** determine their nature, extent, root cause and whether they undermine the objective.
7. **Remediation and retest:** assign action, interim protection, owner and date, then test the corrected control before closure.

### The three proofs

| Proof | Core question | Evidence examples | False assurance to reject |
| --- | --- | --- | --- |
| Design | Could this control achieve the stated objective if performed as specified? | Risk statement, objective, process map, policy, rule logic, data requirements, ownership, escalation and failure-mode analysis | A detailed policy proves the control works |
| Deployment | Is the control embedded across the full intended scope? | Population reconciliation, system and data lineage, configuration, access, training, vendor mapping, change records and walkthroughs | The system is switched on, so every item is covered |
| Operation | Did it perform consistently during the test period and handle exceptions? | Logs, case files, re-performance, data analysis, samples, alerts, decisions, QA, incidents, misses and remediation evidence | No incident or clean sample proves effectiveness |

### Conclusion record

Every conclusion must state:

1. Control and objective.
2. Population and period.
3. Test methods and evidence used.
4. Findings for each proof.
5. Limitations and sampling risk.
6. Conclusion state.
7. Immediate risk response.
8. Remediation owner and target date.
9. Retest condition.

## 6. Substantive editorial draft

The implementation should preserve the substance below while editing for page rhythm and concise practitioner prose. Every source-led paragraph must map to proposition IDs in the source pack.

### Opening thesis

The most dangerous control is not the one everyone knows is broken. It is the one recorded as effective because a policy exists, a system is enabled or a sample contained no failures.

Control testing is the work of replacing that comfort with evidence. The conclusion is not whether a document looks sensible. It is whether the control could work, reaches the population it claims to cover and actually operated during the period being tested.

This framework separates those questions. A control must pass three different proofs. If the evidence cannot answer them, the honest conclusion is Not evidenced, not Effective.

### What the authority establishes

**Source.** Regulation 19 requires relevant persons to establish and maintain proportionate, senior-management-approved policies, controls and procedures to manage the risks identified under regulation 18, review and update them, and keep records. Regulation 21 requires an independent audit function only where appropriate to the size and nature of the business, with the responsibilities stated in that provision. Applicable SYSC rules require effective systems and controls and regular adequacy assessment. [P01 to P05, P10 and P11]

**Application.** These provisions establish the need for effective controls, review and, in the circumstances specified by regulation 21, independent audit. They do not provide one sample size, pass rate or test script for every control. [P06]

**Action.** Define the control objective and testing scope before choosing documents or samples. A test method selected first will often prove only what is easiest to inspect.

### Proof 1: design

Design asks whether the control, if performed as specified, could address the stated risk. Start with the risk and objective, not the policy title.

A useful control objective names the population, action, timing and escalation. "Customers are reviewed" is not testable. "Every customer in the high-risk population receives a documented review at least at the firm's defined interval, and overdue cases are escalated to the named owner" is testable. The interval here is a firm design choice unless a specific rule or source establishes it.

Design testing should challenge the happy path. Ask what happens when data is missing, a vendor feed is late, an analyst is absent, a record moves between systems, an alert is returned or a customer changes segment. A control that works only when every dependency behaves perfectly has a design weakness even before a sample is selected.

### Proof 2: deployment

Deployment asks whether the designed control reaches the real population. This is where policy and system existence most often create false assurance.

Reconcile the population independently. Identify products, legal entities, customer segments, jurisdictions, systems, manual queues and outsourced steps that should be covered. Trace a small number of records from source to control and back. Confirm that configuration, data fields, access, training and escalation routes match the approved design.

The FCA's sanctions findings show why this proof matters. It found list-data and system-transfer problems, historic vendor settings used without reassessment and a legacy integration failure that left transactions unscreened. [P41 and P42] A control can be well designed and running somewhere while still missing the population that matters.

### Proof 3: operation

Operation asks what happened over a defined period. It needs evidence beyond inquiry. Walkthroughs show how staff say the control works. Samples, re-performance, logs, data analysis, exception records and outcome review show how it did work.

Sample design follows the objective. Define the population and period before selecting items. Include relevant risk, change and exception strata. A clean judgemental sample cannot be extrapolated to an unreconciled population, and no source in this pack supplies a universal number that fixes that weakness.

Absence of an incident is not a test result. The FCA's sanctions review recorded many firms reporting no true matches while its testing also found configuration, data and assurance weaknesses. The inference that absence alone is not proof is FinCrimeRadar's, not the FCA's wording. [P46]

### From finding to conclusion

Rate the control only for the stated objective, scope and period.

- Effective means all three proofs are supported and no material weakness undermines the objective.
- Partially effective means the control reduces risk but a bounded weakness or coverage gap remains.
- Ineffective means a weakness defeats or materially undermines the objective.
- Not evidenced means the work cannot support a conclusion because the population, period, evidence or method is insufficient.

Not evidenced is not a softer version of Partially effective. It says the assurance work failed to establish what is true. The next action is more or better testing, alongside interim protection if the uncertainty concerns a critical control.

### Remediation and closure

A finding is not closed because an owner says the action is complete. Closure needs evidence that the correction was implemented and that the affected proof now holds. A design rewrite needs deployment confirmation. A configuration fix needs data-flow and scenario testing. A training response needs evidence that the underlying process weakness was addressed, not only attendance records.

Retest the corrected control over a period capable of showing operation. If that period has not elapsed, record the action as implemented but not yet validated. Do not collapse implementation and effectiveness into one closure status.

## 7. Worked scenarios

All names, organisations, counts and dates are illustrative. They are not presented as real firms or regulatory thresholds.

### Scenario 1: the clean CDD sample

Control objective: every customer in the firm's high-risk population receives a review at the firm's defined interval, with overdue cases escalated.

Facts:

- The policy and workflow design are clear.
- Management information reports 96 percent completion.
- Compliance samples 20 completed reviews from the workflow queue and finds no errors.
- Population reconciliation then finds that 312 customers migrated from a legacy system never entered the queue.
- Eleven of those customers are high risk and overdue under the firm's policy.

Decision: what conclusion is supportable now?

| Option | Grade | Reason |
| --- | --- | --- |
| Effective, because every sampled review passed | Unsupported | The sample tests files inside the queue, not whether the intended population reached the control. Deployment proof fails. |
| Not evidenced, until every migrated customer has been reviewed | Incomplete | The missing population is already evidence of a material deployment failure. More file review is needed for exposure, but the control conclusion need not wait. |
| Ineffective for the stated population and period; protect the missed population, correct the feed, quantify impact and retest | Best | The control objective includes every high-risk customer. A known population exclusion undermines it despite sound design and clean in-queue execution. |
| Partially effective, because most customers were covered | Unsupported on the facts | The record gives no reliable denominator and the missed segment includes overdue high-risk customers. The conclusion would convert an unknown into a percentage judgement. |

Counterfactual: if reconciliation proved the population complete and found three isolated late reviews that were detected and escalated by the control itself, Partially effective could become supportable, subject to materiality and the stated tolerance.

### Scenario 2: the vendor screening assurance

Control objective: screen the intended customer and payment population against current sanctions data, including relevant name variants, and escalate potential matches before release.

Facts:

- The vendor supplies an annual assurance report and the service is enabled.
- Internal testing uses exact names only.
- A data-lineage review finds that one-word names are excluded and long names are truncated before matching.
- No exclusion was approved and no compensating control exists.
- The firm has reported no true matches or suspected breaches during the period.

Decision: what should the firm conclude?

| Option | Grade | Reason |
| --- | --- | --- |
| Effective, because the vendor is independently assured and there were no breaches | Unsupported | Vendor assurance and absence of incidents do not test the firm's data, configuration or intended coverage. |
| Not evidenced, because internal variant testing was incomplete | Incomplete | The test gap matters, but the known exclusions already show the control misses part of its stated objective. |
| Ineffective for the stated objective; apply interim protection, test the full data path and relevant variants, perform a risk-based lookback and govern any exclusion | Best | Known unapproved exclusions materially undermine intended coverage. The response addresses present risk, impact and retest. |
| Replace the vendor immediately | Incomplete | The fault may sit in firm-side transformation or configuration. Replacement before root cause can reproduce the defect and does not protect current exposure. |

Counterfactual: if the exclusions were documented, risk-assessed and covered by a tested manual control, the conclusion could move to Partially effective or Effective depending on evidence that the compensating control operated.

Each option analysis on the page must use Source, Application and Action blocks. Material reasoning must remain in the initial HTML and be visible without JavaScript.

## 8. Risk, Signal and Response cards

Use six cards inline and regroup the identical set at the end.

| Name | Risk | Signal | Response |
| --- | --- | --- | --- |
| Policy Mirage | A documented control is mistaken for an effective one. | Test evidence is limited to policy review and interviews. | Separate design, deployment and operation before concluding. |
| Population Blind Spot | Records outside the test source are never examined. | The sample denominator comes from the control output rather than an independent population. | Reconcile the intended population before sampling. |
| Vendor Assurance Substitution | Third-party assurance is treated as proof of the firm's configuration and data. | No internal lineage, configuration or scenario testing exists. | Test the firm's implementation and challenge vendor dependencies. |
| Clean Sample Comfort | A small passing sample creates a broad conclusion. | Selection excludes changes, exceptions, high-risk strata or failed items. | Match selection to the objective and state sampling limits. |
| Exception Graveyard | Findings are logged but do not change the control. | Repeated issues, extensions or accepted risks have no root-cause action. | Link exceptions to owners, interim protection, remediation and governance. |
| Closure Without Retest | An action is closed when implementation is reported. | No evidence shows the corrected control operated after the change. | Separate implementation from validation and retest before effectiveness closure. |

## 9. Knowledge check and FAQ

Five questions, each with one defensible answer and an explanatory note:

1. Which proof does independent population reconciliation primarily support? Deployment.
2. Does regulation 21 require an independent audit function in every case? No. Its paragraph (1) is conditional on size and nature, subject to the text and exception recorded in the source pack.
3. What does a clean sample from the control's own queue fail to prove? That the queue contains the full intended population.
4. When is Not evidenced the right conclusion? When the method, population, period or evidence cannot support an effectiveness conclusion.
5. What closes a remediation finding? Evidence that the action was implemented and the affected control proof was retested sufficiently.

FAQ topics:

1. How large should the sample be?
2. Can first line test its own controls?
3. Does no incident mean a control is effective?
4. Is vendor assurance enough?
5. What is the difference between Partially effective and Not evidenced?
6. Does an ineffective control prove a regulatory breach?
7. How often should a control be tested?

Answers must state where the sources are silent and avoid universal thresholds.

## 10. Interaction and accessibility contract

| Interaction | Behaviour | No-JavaScript behaviour |
| --- | --- | --- |
| Two graded scenario decisions | Native radio groups and submit buttons. Reveal full option analysis and move focus to the selected analysis. Use a polite live region. | All option analyses visible. Inert submit controls hidden. |
| Knowledge check | Five questions, one point each, live result and answer notes. | Questions and native `details` answer notes visible. |
| FAQ | Native `details` and `summary`. | Identical. |
| Save as image | Canvas export of the final six-card grid. | Button hidden. |

No free text, customer data or sensitive scenario input. No new telemetry is required. If existing aggregate telemetry is reused, it remains consent-gated and may contain only guide ID, scenario ID, fixed grade and quiz score.

## 11. Requirement Coverage Matrix

Each requirement is assigned to exactly one implementation task.

| ID | Requirement | Task |
| --- | --- | --- |
| R1 | Preserve source pack, design memo and external review brief | T1 Evidence files |
| R2 | Standard shell, metadata, JSON-LD, skip link, scope strip and Intelligence Core | T2 Page foundation |
| R3 | Source-led authority section with evidence-state labels and precise scope | T3 Authority and evidence |
| R4 | Control Proof Chain, three-proof matrix and conclusion ladder with text equivalents | T4 Static analytical visuals |
| R5 | Design, deployment, operation, sampling, conclusion and remediation sections | T5 Framework body |
| R6 | Two distinct worked scenarios, four graded options each, Source/Application/Action, counterfactuals and Decision Records | T6 Scenarios |
| R7 | Six Risk, Signal and Response cards inline and as the closing grid | T7 Pattern cards |
| R8 | Knowledge check, FAQ, operational summary, Red Team Questions and sources | T8 Closing content |
| R9 | Scenario, quiz and image-export JavaScript with progressive enhancement and reduced motion | T9 Page script |
| R10 | Knowledge Hub card and count, sitemap, content relations and social card | T10 Discovery and assets |
| R11 | Verification ledger entries and reconciliation | T11 Ledger |
| R12 | Static contract checker covering source labels, scenarios, option grades, cards, metadata, discovery and prohibited claims | T12 Static tests |
| R13 | Browser test covering keyboard, focus, no-JavaScript content, interactions, export, 320/375/390/428/768 widths, 200 percent zoom and overflow | T13 Browser tests |
| R14 | Full affected regression, diff review, sensitive-data and dash scans | T14 Integration verification |
| R15 | Real pull request, `/code-review`, delivery report and independent manual release-review pack | T15 Review routing |

## 12. Acceptance criteria

1. Every material claim maps to the source pack and a ledger record or is labelled FinCrimeRadar assessment.
2. Regulation 21's conditional wording and exception are not lost.
3. FCG and FCA examples are not presented as legal requirements.
4. The GOV.UK framework is visibly scoped to public bodies.
5. No numerical sample size, pass rate or universal frequency is invented.
6. The page distinguishes design, deployment and operation in every scenario conclusion.
7. Not evidenced is not rendered as a pass, fail or maturity level.
8. Both scenarios remain materially distinct and fully comprehensible without JavaScript.
9. Derived metadata, card copy, quiz notes and summary cards agree with the final page.
10. Publication remains blocked until the independent adversarial review is complete and material findings are resolved.

## 13. Review classification

Regulatory claim review is mandatory because the page states the scope and effect of regulations 19 and 21 and applicable SYSC rules. Grading review is mandatory because scenario options and the knowledge check grade user choices. A real pull request `/code-review` and a separate manual cross-model review are required before release. The human performs the external review.
