# The E-commerce Fraud System: Part 1 analytical design memo

Companion to `e-commerce-fraud-part-1-source-pack.md`. This memo completes Content Loop step 04. It locks the analytical model, scenarios, interaction pattern and information architecture before editorial drafting. It does not authorise repository implementation.

## 1. Publication identity and scope lock

**Series:** E-commerce Fraud: From Account Creation to Chargeback.

**Part:** 1 of 5.

**Public format:** Guide within the Default Knowledge Hub treatment.

**Working public title:** The E-commerce Fraud System: How Evidence Changes from Account Creation to Chargeback.

**Working standfirst:** Fraud signals do not keep the same meaning as an account becomes an order, a delivery, a refund and a dispute. This guide shows what each control may conclude, what it must pass forward and how later losses should change earlier decisions.

**Audience:** Merchant fraud, e-commerce risk, payments, trust and safety, customer operations, fulfilment, returns, dispute and financial-crime practitioners.

**Jurisdiction:** Operationally broad. United Kingdom law is used only for the identified payment-service and consumer-rights boundaries. European Economic Area data, United States case material and card-scheme guidance retain their source scope.

**Intelligence question:** How should a merchant preserve, qualify and relay fraud evidence across the e-commerce lifecycle when no single stage sees the full pattern?

**Locked thesis:** E-commerce fraud is a system problem. A locally defensible control can still pass risk downstream when the evidence, uncertainty and decision level do not travel with the case or the later outcome does not return to the earlier control.

**Original contribution:** The six-field Fraud Evidence Relay and the backtrace test. Lifecycle mapping, ownership allocation and generic feedback loops are not sufficient differentiation.

**Decision object:** The quality of a lifecycle handoff, assessed by whether the current owner states the correct decision level, preserves a bounded conclusion, sends the minimum evidence and uncertainty forward before an irreversible action, and defines where a later outcome must return.

**Excluded:** A master fraud taxonomy, detailed account-takeover detection, detailed device-network investigation, a fraud score, vendor comparison, payment optimisation, card-scheme manual, universal refund rulebook, consumer scam guide, criminal attribution model or employer-specific process.

## 2. Intelligence Core

| Element | Locked answer |
| --- | --- |
| Intelligence question | How should a merchant preserve, qualify and relay fraud evidence across the e-commerce lifecycle when no single stage sees the full pattern? |
| Evidence state | Established source propositions: authentication can reduce some payment fraud; credential stuffing can compromise legitimate accounts; scheme disputes have condition-specific evidence and process requirements; qualifying consumers and payment service users may have separate statutory rights; organised refund fraud is evidenced by the public United States sentencing record. Industry evidence: UK Finance loss and case data. FinCrimeRadar assessment: the Fraud Evidence Relay, decision levels, control patterns and backtrace test. Unresolved until the relevant case is assessed: customer intent, the legal result of a refund or cancellation claim, scheme response eligibility, and whether linked activity is innocent, abusive or criminal. |
| Decision object | One six-field Fraud Evidence Relay at each material handoff, followed by a backtrace when a refund, dispute or confirmed loss changes the evidence state. |
| Uncertainty | Authentication, device, account, delivery and dispute signals have different reliability and answer different questions. Legitimate customer rights can coexist with fraud indicators. Scheme rules, merchant agreements, law and factual outcomes can diverge. |
| Change condition | New evidence changes the supported decision level or bounded conclusion; an irreversible fulfilment or refund action approaches; a later dispute or loss reveals that earlier evidence was missed, misread or not relayed; applicable law or scheme requirements change. |
| Practitioner outcome | The reader can identify the correct decision level, write a bounded conclusion, construct the relay package, separate fraud assessment from legal or scheme outcomes, and backtrace a later loss to the earliest control capable of reducing recurrence. |

## 3. Lifecycle and decision levels

Part 1 uses six lifecycle stages. They are a teaching sequence, not a claim that every merchant has six teams or systems.

1. **Account and promotion:** account creation, recovery, profile change and promotion use.
2. **Checkout and authentication:** basket, payment method, authentication and transaction submission.
3. **Order review:** order-level risk assessment, manual review and release decision.
4. **Fulfilment and delivery:** picking, dispatch, address changes, carrier events and proof of delivery.
5. **Return and refund:** return initiation, receipt, inspection, credit and customer-service resolution.
6. **Dispute and outcome:** issuer or scheme dispute, merchant response, confirmed loss and control feedback.

Every conclusion must name one of these decision levels:

- event;
- account;
- order;
- linked network;
- refund;
- dispute.

A signal at one level may justify review at another. It does not automatically prove the conclusion at that other level.

## 4. Analytical model: the Fraud Evidence Relay

The six fields are fixed and must appear in this order.

1. **Decision level:** Identify whether the current decision concerns an event, account, order, linked network, refund or dispute. Do not allow a transaction signal to become an account or network verdict without separate reasoning.
2. **Evidence state:** Record what is known now, its source, time, reliability and material gaps. Separate direct facts, third-party data, inferred links and unverified customer statements.
3. **Bounded conclusion:** State what the evidence supports and what it does not support. Use reviewable language such as elevated order risk or unresolved refund inconsistency, not an unsupported claim that the customer is a fraudster.
4. **Action and owner:** Record the proportionate action, accountable role, timing, any approval requirement and the point at which the action expires or must be reconsidered.
5. **Relay package:** Send the minimum relevant evidence, uncertainty, decision history and instruction to the next owner. Raw data without its meaning, or a conclusion without its evidence, is not a complete relay.
6. **Feedback trigger:** Name the later event that must return to an earlier control, the owner who receives it and the decision, rule or process to reassess.

The model is a FinCrimeRadar control synthesis. It is not a legal test, scheme rule, vendor methodology or finding that fraud occurred.

## 5. The backtrace test

Use the backtrace after a material refund, dispute, confirmed loss or repeated near miss.

1. **Fix the outcome:** State the actual outcome without converting it into a broader fraud or blame conclusion.
2. **Rebuild the timeline:** Order the material account, checkout, review, fulfilment, return and dispute events.
3. **Find the first relevant signal:** Identify the earliest evidence that became relevant to the outcome, including evidence whose significance was visible only later.
4. **Inspect each handoff:** Test whether evidence, uncertainty, decision level and action travelled together.
5. **Locate the reversible moment:** Identify the last point at which a proportionate action could have reduced loss or preserved stronger evidence.
6. **Separate outcome types:** Keep merchant loss, statutory rights, payment-service protection, scheme result and criminal conclusion distinct.
7. **Return the learning:** Route the outcome to the named earlier owner and specify the rule, threshold, evidence capture or handoff to reassess.

The backtrace is not a hindsight exercise that assumes the final outcome was predictable. It tests whether the earlier decision was reasonable on the evidence available then and whether later evidence should change future controls.

## 6. Locked control patterns

Each pattern appears once where it is introduced and once in the closing Risk, Signal, Response grid. The two copies must be text-identical.

### Pattern 1: The Local Green Light

**Risk:** Each stage makes a reasonable local decision while unresolved cross-stage evidence accumulates into loss.

**Signal:** An order has several approvals, but no owner can state the combined evidence or residual uncertainty.

**Response:** Complete the Fraud Evidence Relay before the next irreversible action.

### Pattern 2: The Level Jump

**Risk:** A signal at one decision level becomes a fraud verdict at another without sufficient evidence.

**Signal:** An event anomaly is used to label an account, network or customer as fraudulent without a documented reasoning step.

**Response:** Name the decision level and write a bounded conclusion before selecting the action.

### Pattern 3: The Relay Drop

**Risk:** Evidence reaches the next team without its meaning, or a conclusion arrives without the evidence and uncertainty behind it.

**Signal:** The next owner must reconstruct why the case was escalated from raw logs, short labels or free-text notes.

**Response:** Send the minimum evidence, source, timing, bounded conclusion, open question and required next decision as one relay package.

### Pattern 4: The Feedback Sink

**Risk:** Refund, dispute and loss outcomes are recorded but do not change the upstream control that could prevent recurrence.

**Signal:** The same loss pattern repeats while the original account, checkout or fulfilment decision remains unreviewed.

**Response:** Define a named feedback trigger, receiving owner and specific control decision to reassess.

### Pattern 5: The Rights Collapse

**Risk:** A merchant fraud concern is treated as though it decides consumer rights, payment-service protection, scheme outcomes and criminality.

**Signal:** One fraud label automatically determines refund, dispute and account decisions without separate tests.

**Response:** Record each outcome separately, apply its own evidence and authority, and preserve uncertainty where the merchant cannot decide it.

## 7. Worked decision 1: authenticated order with fragmented evidence

**Facts:** A fictional merchant receives a high-value order from an established account. Payment authentication succeeds. Account operations hold a recent recovery event, checkout sees a new device and delivery address, and fulfilment receives an address-change request after approval. Each fact is individually explainable. No single team can establish account takeover or fraud.

**Decision:** What should happen before dispatch?

**Option A, weak:** Release the order because payment authentication succeeded.

**Option B, caution:** Cancel the order and close the account because the combined signals prove account takeover.

**Option C, strongest:** Pause the order for bounded review, assemble the cross-stage relay, verify the material change through a trusted existing channel, and make an order decision without treating the evidence as an account-level fraud finding.

**Source:** Sources S2 and S3 support the bounded role of authentication. S4 supports credential stuffing as one possible account-access mechanism. S6 supports the importance of relevant transaction, participation and fulfilment evidence in later disputes.

**Application:** Successful authentication reduces some risk but does not resolve who controlled the account, why the delivery details changed or whether dispatch is reasonable. The combined facts justify an order-level review. They do not yet prove account takeover or criminal conduct.

**Action:** Record the order decision level, evidence state and unresolved account question. Pause only for a defined review period, use a trusted pre-existing contact route where verification is proportionate, preserve the evidence and send the result to fulfilment. If the order is released, retain the bounded rationale and define the dispute or delivery outcome that must return to account and order controls.

**Counterfactual:** If the account recovery and address change were independently verified before checkout through a known channel, the new device was consistent with prior customer behaviour and no material conflict remained, release could become proportionate. The changed facts reduce order risk; they do not make authentication proof of honest intent.

**Existing-content boundary:** Do not reuse the facts, location or containment sequence from Scenario Lab `session-hijack-002`. The teaching object is the handoff, not account-takeover detection.

## 8. Worked decision 2: refund claims with a possible network pattern

**Facts:** A different fictional merchant receives several individually plausible non-delivery or return claims. Customer service can see each order, while returns, device and payment records suggest linked accounts and repeated refund outcomes. The link may indicate organised abuse, a shared household or another innocent explanation. Some claimants may still have legitimate statutory rights.

**Decision:** How should the current claim and possible network be handled?

**Option A, caution:** Process each claim through the normal refund route without considering the linked evidence because customer rights are assessed individually.

**Option B, weak:** Refuse every linked claim, close the accounts and record confirmed refund fraud.

**Option C, strongest:** Decide the individual customer's entitlement on its own facts, separately escalate the linked-network hypothesis, preserve the cross-order evidence and apply proportionate account or fulfilment controls without treating the link as proof of fraud.

**Source:** S8 and S9 establish bounded United Kingdom consumer-rights considerations. S10 evidences an organised United States refund-fraud mechanism. S6 shows that refund, fulfilment and transaction evidence can matter to a later card dispute. S5 identifies refund abuse as a merchant risk.

**Application:** The linked evidence may justify a network-level investigation but does not decide the individual refund entitlement, customer intent, scheme outcome or criminal conclusion. Treating each claim only in isolation can miss organised abuse. Treating every link as guilt can deny legitimate outcomes and contaminate the evidence record.

**Action:** Keep the refund and linked-network decisions separate. Record the evidence supporting each, preserve lawful and scheme-specific timelines, use maker-checker review for an adverse network action, and send confirmed outcomes back to the relevant account, fulfilment and returns controls.

**Counterfactual:** If the shared device is explained by a household, the delivery evidence supports the claim and the return or cancellation requirements are met, the network hypothesis weakens and the individual claim should proceed on its own facts. If independent evidence later shows coordinated false claims, the network conclusion may strengthen without rewriting what was known at the initial decision.

**Existing-content boundary:** Do not recreate Scenario Lab `device-network-006`. The teaching object is separation of an individual rights decision from a network-abuse assessment and the feedback relay between them.

## 9. Rights and outcome boundary

The public guide must keep five outcomes separate wherever they appear:

1. **Merchant fraud assessment:** the merchant's bounded operational conclusion on the evidence it holds.
2. **Consumer-rights outcome:** whether a cancellation, rejection, return or refund entitlement applies under the relevant law and facts.
3. **Payment-service outcome:** whether the payer and payment service provider meet the conditions for an unauthorised-payment remedy or related allocation.
4. **Scheme dispute outcome:** whether a dispute condition, evidence requirement and process permits a response or determines the scheme result.
5. **Criminal conclusion:** whether conduct satisfies a criminal offence, which the merchant guide does not determine.

No interface state, badge or scenario feedback may merge these outcomes into one fraud status.

## 10. Locked information architecture

The publication uses this order:

1. Hero, format label, evidence date and jurisdiction boundary.
2. How to use the guide.
3. Executive assessment and locked thesis.
4. The six-stage merchant lifecycle.
5. Decision levels and why signal meaning changes.
6. The six-field Fraud Evidence Relay.
7. Worked decision 1.
8. Local decisions and broken handoffs, including Patterns 1 to 3 inline.
9. Rights and outcome boundary, including Pattern 5 inline.
10. Worked decision 2.
11. The seven-step backtrace test, including Pattern 4 inline.
12. Practical control-owner checklist.
13. What Would Change Our Assessment.
14. Closing five-card Risk, Signal, Response grid and image export.
15. Five-question knowledge check.
16. Six-item FAQ.
17. Sources, evidence labels and methodology.
18. Related FinCrimeRadar publications.

The complete argument, both scenarios, Source, Application and Action reasoning, counterfactuals, control patterns, FAQ and sources must remain readable without JavaScript.

## 11. Visual contract

One substantive process visual is justified: a six-stage lifecycle showing the forward Fraud Evidence Relay and the reverse outcome feedback path.

The visual must answer two questions:

1. What must move forward before the next irreversible action?
2. Where must a later outcome return to change an earlier control?

The HTML must include a complete textual equivalent. The visual must not imply that all merchants use the same organisational structure or that every case traverses every stage.

No second decorative process diagram is authorised. Scenario 2 may use a compact relationship view only if the editorial draft shows that linked accounts, devices and orders cannot be understood clearly in prose and the accessible equivalent is complete.

## 12. Interaction contract

1. Each scenario uses a semantic fieldset and exactly three options: weak, caution and strongest.
2. The reader may record High, Medium or Low confidence after selecting an option and before revealing the reasoning.
3. Submission without an option produces a polite live-region instruction.
4. Every option reveals the same complete Source, Application and Action reasoning and the counterfactual already present in the HTML.
5. The counterfactual asks the reader to reconsider after one material fact changes. It does not count as a third scenario.
6. The five-question knowledge check requires all answers before scoring and reports its result through a polite live region.
7. The closing card grid is the only source for the PNG summary export.
8. Aggregate telemetry, if retained by the current site architecture, is limited to `scenario_complete`, `counterfactual_complete`, `knowledge_check_complete` and `card_export` and remains consent-gated.
9. Telemetry must not contain selected text, answer content, confidence rationales, free text, names, account details, device data, order data or other customer information.
10. No backend is required. Claude Code owns any later HTML, CSS, JavaScript, tests, metadata, ledger integration and release preparation.

## 13. Knowledge check design

The editorial draft must create five questions covering these distinct judgements:

1. Which Fraud Evidence Relay field prevents an event signal from becoming an unsupported account or network verdict?
2. What does successful payment authentication fail to decide in Scenario 1?
3. Why must the individual refund decision and linked-network assessment remain separate in Scenario 2?
4. What is the purpose of the relay package?
5. What is the correct use of a later dispute or loss in the backtrace test?

Each question has three credible choices and one unambiguous answer. Option positions must vary. At least one question must test the changed fact in a counterfactual rather than recall a label.

## 14. FAQ design

The editorial draft must answer six practitioner questions:

1. Does strong customer authentication prove that an e-commerce order is genuine?
2. Is a chargeback outcome the same as a fraud finding?
3. Can a merchant delay a refund while investigating abuse?
4. When should device or account links change an individual case decision?
5. What evidence should move from checkout to fulfilment and disputes?
6. Does the Fraud Evidence Relay require a new platform or backend?

Answers must retain the jurisdiction and scheme boundaries. The answer to question 6 is no: the method can operate through a governed static record and existing case or order systems. Any product implementation remains a separate decision.

## 15. What Would Change Our Assessment

The static section must include these triggers:

1. New evidence shows that the six-field relay duplicates an existing authoritative merchant standard.
2. Primary evidence no longer supports the separation between authentication, authorisation, consumer rights and scheme disputes used in the guide.
3. Material changes to United Kingdom payment-service or consumer-rights provisions alter either scenario boundary.
4. A current card-scheme rule or acquirer requirement contradicts a proposed dispute-evidence statement.
5. Independent review finds that a scenario action is legally overbroad, disproportionate or insufficiently qualified.
6. Repository publication of another guide occupies the same cross-stage handoff and backtrace model.

## 16. Drafting and review constraints

1. Label all scenario businesses, accounts, orders, devices, amounts and outcomes as fictional and illustrative.
2. Do not use Nisbets information or imply employer sponsorship.
3. Do not invent prevalence, loss, effectiveness or false-positive figures.
4. Do not state that authentication transfers or removes merchant liability.
5. Do not state that a scheme dispute proves fraud, merchant error or criminality.
6. Do not recommend refusal, delay or deduction of a consumer refund without a current, qualified legal basis and independent review.
7. Do not state that device, address, account or payment links prove common control or intent.
8. Keep Source, Application and Action visibly separate in both scenarios and every sensitive teaching point.
9. Use S1 to S10 for evidence and S11 to S12 only for the originality comparison.
10. Route the six claim groups in source-pack section 7 through independent adversarial review before publication.

## 17. Change control

The following are specification changes and require reopening this memo:

- renaming, removing or reordering a Fraud Evidence Relay field;
- changing the seven-step backtrace sequence;
- merging the two scenarios or replacing either with an existing Scenario Lab case;
- treating authentication, a device link, a chargeback or a refund outcome as a complete fraud verdict;
- removing the five-outcome rights boundary;
- introducing a fraud score, vendor ranking or universal decision threshold;
- adding a backend dependency;
- changing the public format from Guide;
- omitting the independent legal and scheme-review gate.

Editorial refinement that preserves the model, evidence boundaries, scenario verdicts and decision levels is not a specification change.

## 18. Workflow outcome and next gate

**Outcome:** ANALYTICAL DESIGN LOCKED.

At this gate, Part 1 remains QUALIFIED, not SPECIFIED. Under `docs/GUIDE_PRODUCTION_WORKFLOW.md`, the next step is the substantive editorial draft. The final Requirement Coverage Matrix follows that draft and becomes the single implementation contract for Claude Code. Creating that matrix before the draft would breach the repository sequence and leave exact copy, source, interaction and test requirements unresolved.

No HTML, CSS, JavaScript, backend, metadata, verification-ledger, Knowledge Hub, sitemap, asset, test, Git or release work is authorised by this memo.
