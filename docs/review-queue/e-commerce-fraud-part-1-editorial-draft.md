# The E-commerce Fraud System: Part 1 substantive editorial draft

This document completes Content Loop step 05. It is publication copy for Claude Code implementation, subject to the independent legal, scheme and factual review listed in the source pack and implementation contract. Citation numbers refer to the source list at the end.

## Page title

The E-commerce Fraud System: How Evidence Changes from Account Creation to Chargeback

## Standfirst

Fraud signals do not keep the same meaning as an account becomes an order, a delivery, a refund and a dispute. This guide shows what each control may conclude, what it must pass forward and how later losses should change earlier decisions.

## Evidence status

**Evidence checked:** 18 October 2026.

**Current assessment:** E-commerce fraud is a system problem. Authentication, account, device, order, fulfilment, refund and dispute evidence answer different questions. A merchant can make several locally defensible decisions and still suffer preventable loss when the evidence, uncertainty and decision level do not move with the case.

**Status of this guide:** The public sources support the lifecycle problem and the need to keep authentication, consumer rights, payment-service protections and scheme outcomes distinct. The Fraud Evidence Relay, backtrace test and five control patterns are FinCrimeRadar assessments, not legal rules or card-scheme terminology.

**Jurisdiction boundary:** The operating model is broadly applicable to merchants. United Kingdom law is used only for the identified payment-service and consumer-rights boundaries. European Economic Area data, United States case material and Visa guidance retain their own scope.

**Next trigger:** A material change to United Kingdom payment-service or consumer-rights provisions, the card-scheme guidance relied on, or evidence showing that the Fraud Evidence Relay duplicates an authoritative merchant standard.

## How to use this guide

Use this guide when a fraud signal passes from one team or system to another, or when a later refund, dispute or loss raises the question: where was the first useful evidence, and what happened to it?

For sensitive conclusions, the guide separates three layers:

1. **Source:** What the authority or public record establishes.
2. **Application:** How FinCrimeRadar applies that evidence to the merchant facts.
3. **Action:** The proportionate operational response FinCrimeRadar recommends.

The core rule is simple: **move the evidence, its uncertainty and its decision level together.**

## Executive assessment

E-commerce fraud is often described as a checkout problem. That is too narrow.

The account may contain an earlier recovery event. Checkout may see a new device. Payment authentication may succeed. Order review may approve because each signal is individually explainable. Fulfilment may receive an address change. Customer service may later process a refund. The dispute team may see only the final cardholder claim.

Every stage can follow its own procedure and still miss the complete pattern.

Current evidence supports the importance of the problem without producing one universal fraud figure. UK Finance members reported £423.5 million of remote purchase card fraud losses and 3.2 million cases for 2025, but those are industry-reported card or account incidents, not total e-commerce fraud or total merchant loss.[1] The European Banking Authority and European Central Bank report that strong customer authentication remains effective, particularly for card payments, while fraud methods continue to adapt.[2]

That distinction matters. Authentication can reduce fraud without proving who controlled an account, whether a customer acted honestly, whether goods were delivered, whether a refund is due or whether a later dispute can be answered successfully.

Visa's October 2026 merchant guide makes the downstream evidence problem visible. Different disputes depend on different conditions, time limits and evidence. Relevant records may concern cardholder linkage, participation, processing, fulfilment, cancellation or refund.[6] Evidence needed at the end of the lifecycle is often created near the beginning.

Part 1 therefore does not teach another fraud typology list. It teaches two operational methods:

- the **Fraud Evidence Relay**, used before the next material handoff or irreversible action;
- the **backtrace test**, used after a refund, dispute, confirmed loss or repeated near miss.

## The six-stage merchant lifecycle

The lifecycle below is a teaching sequence. It does not assume that every merchant has six separate teams or systems.

### 1. Account and promotion

Account creation, recovery, profile changes, saved details and promotion use create early evidence about access, continuity and behaviour. Credential stuffing is one route by which reused credentials can give an attacker access to a legitimate account.[4] That mechanism is relevant, but a recovery event or new device is not proof of compromise.

### 2. Checkout and authentication

Checkout brings together the basket, payment method, authentication result, customer-entered details and transaction submission. Strong customer authentication can reduce payment fraud.[2][3] It does not settle every merchant question about the account, order, customer intent or later fulfilment.

### 3. Order review

Order review decides whether the available evidence supports release, bounded review, cancellation or another proportionate action. The decision concerns the order. It should not silently become an account-level or customer-level fraud verdict.

### 4. Fulfilment and delivery

Picking, dispatch, address changes, carrier events and proof of delivery can confirm or challenge earlier assumptions. Once goods are dispatched, the merchant may lose a practical opportunity to prevent loss. Fulfilment therefore needs the relevant evidence and uncertainty before release, not after a dispute arrives.

### 5. Return and refund

Return initiation, receipt, inspection, credit and customer-service resolution create a different evidence set. Europol identifies refund abuse as an e-commerce risk, including misuse of refund routes.[5] A refund claim can also be legitimate. The individual entitlement and any wider abuse hypothesis require separate reasoning.

### 6. Dispute and outcome

The final stage may include an issuer or scheme dispute, merchant response, refund, confirmed loss or another operational outcome. Visa uses the term dispute, although merchants may use chargeback operationally.[6] A dispute outcome is not automatically a finding that fraud occurred, that the merchant acted wrongly or that a crime was committed.

## Decision levels: name the question before judging the evidence

The same fact can matter differently depending on the decision being made.

- **Event:** Is this recovery, login, address change or return event unusual enough to review?
- **Account:** Is there sufficient evidence to restrict, recover or monitor this account?
- **Order:** Should this order be released, paused, changed or cancelled?
- **Linked network:** Do several accounts, devices, orders or refunds justify a coordinated-abuse hypothesis?
- **Refund:** What should happen to this return, cancellation or refund request on its facts?
- **Dispute:** What does the dispute condition require, what evidence is relevant and is a response supported?

A signal can justify moving to another decision level. It does not prove the conclusion at that level.

For example, a new device is an event-level fact. It may contribute to an order review. It does not by itself prove account takeover, common control across accounts or dishonest intent. Likewise, a lost dispute is a dispute outcome. It may expose a control weakness, but it does not retrospectively make every earlier signal obvious.

## The six-field Fraud Evidence Relay

The Fraud Evidence Relay is a FinCrimeRadar control model. It can be recorded in an existing order, case or investigation system, or in a governed static record. It does not require a new platform.

The six fields must appear in this order.

### 1. Decision level

State whether the current question concerns an event, account, order, linked network, refund or dispute.

Do not write only “fraud review”. The level determines what the evidence can support and who should own the action.

### 2. Evidence state

Record what is known now, its source, time, reliability and material gaps.

Separate:

- direct merchant facts;
- third-party or scheme data;
- inferred links;
- customer statements that have not been independently verified;
- evidence that became meaningful only after a later event.

### 3. Bounded conclusion

State what the evidence supports and what it does not support.

“Elevated order risk with unresolved account access” is reviewable. “Customer is fraudulent” usually claims more than the merchant evidence can establish.

### 4. Action and owner

Record the proportionate action, accountable role, timing, required approval and the point at which the action expires or must be reconsidered.

Temporary review should have a defined endpoint. An adverse network action should not be left to an unreviewed free-text label.

### 5. Relay package

Send the next owner the minimum relevant evidence, uncertainty, decision history and required next decision.

Raw data without its meaning is incomplete. A conclusion without its evidence is also incomplete.

### 6. Feedback trigger

Name the later event that must return to an earlier control, the owner who receives it and the decision, rule or process to reassess.

“Review if chargeback” is too vague. A better trigger identifies which dispute or delivery outcome returns to which account, checkout, order or fulfilment control.

## Worked decision 1: authenticated order with fragmented evidence

**Fictional and illustrative.** The merchant, account, order and events below are invented. They do not describe any employer or client.

A merchant receives a high-value order from an established account. Payment authentication succeeds. Account operations hold a recent recovery event. Checkout sees a new device and delivery address. Fulfilment then receives an address-change request after approval.

Each fact is individually explainable. No single team can establish account takeover or fraud.

**What should happen before dispatch?**

**A. Release the order because payment authentication succeeded.** Weak. It allows one payment control to decide the wider order and account questions.

**B. Cancel the order and close the account because the combined signals prove account takeover.** Caution. It recognises the combined risk but turns an unresolved hypothesis into an account-level finding.

**C. Pause the order for bounded review, assemble the cross-stage relay, verify the material change through a trusted existing channel, and make an order decision without treating the evidence as an account-level fraud finding.** Strongest.

### Source, Application and Action reasoning

**Source:** The European Banking Authority and European Central Bank evidence supports the effectiveness of strong customer authentication while recognising continuing and adapting fraud.[2] FCA material establishes the United Kingdom payment-service authentication framework, subject to its scope and exemptions.[3] NCSC guidance explains credential stuffing as one possible route to legitimate-account access.[4] Visa guidance shows that transaction, participation and fulfilment evidence can matter to later disputes.[6]

**Application:** Successful authentication reduces some payment risk. It does not resolve who controlled the account, why the delivery details changed or whether dispatch is reasonable. The combined facts justify an order-level review. They do not yet prove account takeover, dishonest intent or criminal conduct.

**Action:** Record the order decision level, evidence state and unresolved account question. Pause only for a defined review period. Where proportionate, verify the material change through a trusted pre-existing contact route rather than contact details introduced by the suspicious event. Preserve the evidence and send the decision to fulfilment. If the order is released, record why and define the delivery or dispute outcome that must return to the account and order controls.

**Counterfactual:** Assume instead that the recovery and address change were independently verified before checkout through a known channel, the new device was consistent with prior customer behaviour and no material conflict remained. Release could become proportionate. Those changed facts reduce the order risk. They do not make authentication proof of honest intent.

### Risk, Signal, Response: The Local Green Light

**Risk:** Each stage makes a reasonable local decision while unresolved cross-stage evidence accumulates into loss.

**Signal:** An order has several approvals, but no owner can state the combined evidence or residual uncertainty.

**Response:** Complete the Fraud Evidence Relay before the next irreversible action.

## Where local decisions break

The Fraud Evidence Relay addresses three common handoff failures.

### The decision level is missing

Without a named level, teams can discuss the same evidence while answering different questions. Checkout may be deciding whether to attempt payment. Order review may be deciding whether to dispatch. Account operations may be deciding whether to restrict the account. A single “approve” or “decline” status hides those differences.

### Risk, Signal, Response: The Level Jump

**Risk:** A signal at one decision level becomes a fraud verdict at another without sufficient evidence.

**Signal:** An event anomaly is used to label an account, network or customer as fraudulent without a documented reasoning step.

**Response:** Name the decision level and write a bounded conclusion before selecting the action.

### Evidence and meaning become separated

A fraud system may send device, address and transaction data to another team without explaining which fact changed the risk. The opposite can also happen: a short label such as “high risk” moves forward without the underlying facts or open question.

Neither is a complete handoff. The next owner must know what happened, why it matters, what remains unresolved and which decision is now required.

### Risk, Signal, Response: The Relay Drop

**Risk:** Evidence reaches the next team without its meaning, or a conclusion arrives without the evidence and uncertainty behind it.

**Signal:** The next owner must reconstruct why the case was escalated from raw logs, short labels or free-text notes.

**Response:** Send the minimum evidence, source, timing, bounded conclusion, open question and required next decision as one relay package.

## Keep fraud, rights and dispute outcomes separate

One of the most damaging shortcuts is allowing the merchant's fraud concern to determine every other outcome.

The guide keeps five decisions separate.

### 1. Merchant fraud assessment

This is the merchant's bounded operational conclusion on the evidence it holds. It can justify proportionate controls. It does not decide every legal or scheme question.

### 2. Consumer-rights outcome

United Kingdom consumers may have cancellation, rejection, return or reimbursement rights where the statutory conditions apply.[8][9] A merchant fraud concern does not automatically extinguish those rights. Equally, the existence of consumer rights does not require the merchant to ignore evidence of organised abuse.

### 3. Payment-service outcome

Under the Payment Services Regulations 2017, payer consent, authentication evidence and payment service provider refund duties are separate matters with statutory conditions and exceptions.[7] These rules concern payment-service relationships. They are not a universal merchant chargeback rule.

### 4. Scheme dispute outcome

A card dispute depends on the applicable scheme category, condition, evidence, timing and merchant arrangement. Visa's merchant guide expressly says it does not replace the Visa Rules, merchant agreements, acquirer requirements or applicable law, and does not guarantee outcomes.[6]

### 5. Criminal conclusion

Whether conduct satisfies a criminal offence is not determined by a merchant fraud label, refund decision or lost dispute. Public criminal cases can evidence mechanisms, but the guide does not convert similarity into guilt.

### Risk, Signal, Response: The Rights Collapse

**Risk:** A merchant fraud concern is treated as though it decides consumer rights, payment-service protection, scheme outcomes and criminality.

**Signal:** One fraud label automatically determines refund, dispute and account decisions without separate tests.

**Response:** Record each outcome separately, apply its own evidence and authority, and preserve uncertainty where the merchant cannot decide it.

## Worked decision 2: refund claims with a possible network pattern

**Fictional and illustrative.** The merchant, customers, accounts, orders and outcomes below are invented. The mechanism is informed by public sources, including the United States Artemis Refund Group sentencing record.[10]

A different merchant receives several individually plausible non-delivery or return claims. Customer service can see each order. Returns, device and payment records suggest linked accounts and repeated refund outcomes.

The link may indicate organised abuse, a shared household or another innocent explanation. Some claimants may still have legitimate statutory rights.

**How should the current claim and possible network be handled?**

**A. Process each claim through the normal refund route without considering the linked evidence because customer rights are assessed individually.** Caution. It protects the individual decision but can miss material network evidence.

**B. Refuse every linked claim, close the accounts and record confirmed refund fraud.** Weak. It treats a link as proof of common control, dishonest intent and the result of each claim.

**C. Decide the individual customer's entitlement on its own facts, separately escalate the linked-network hypothesis, preserve the cross-order evidence and apply proportionate account or fulfilment controls without treating the link as proof of fraud.** Strongest.

### Source, Application and Action reasoning

**Source:** The Consumer Rights Act 2015 and Consumer Contracts Regulations 2013 establish bounded rejection, cancellation and reimbursement rights where their conditions apply.[8][9] Europol identifies refund abuse as an e-commerce risk.[5] In the Artemis case, defendants pleaded guilty and were sentenced in a scheme where customers obtained fraudulent refunds while retaining goods.[10] Visa guidance shows that fulfilment, cancellation and refund evidence may be relevant to later disputes.[6]

**Application:** Linked evidence may justify a network-level investigation. It does not by itself decide the individual refund entitlement, customer intent, scheme outcome or criminal conclusion. Treating each claim only in isolation can miss organised abuse. Treating every link as guilt can deny legitimate outcomes and damage the evidence record.

**Action:** Keep the individual refund decision and linked-network assessment separate. Record the evidence supporting each. Preserve applicable legal and scheme timelines rather than assuming an internal fraud review pauses them. Apply maker-checker review before a material adverse network action. Send confirmed outcomes back to the account, fulfilment and returns controls that can reduce recurrence.

**Counterfactual:** Assume instead that the shared device is explained by a household, the delivery evidence supports the claim and the applicable return or cancellation conditions are met. The network hypothesis weakens and the individual claim should proceed on its own facts. If independent evidence later shows coordinated false claims, the network conclusion may strengthen without rewriting what was known at the initial decision.

## The seven-step backtrace test

Use the backtrace after a material refund, dispute, confirmed loss or repeated near miss.

### 1. Fix the outcome

State what actually happened. “Dispute lost” is an outcome. “Customer committed fraud” is a wider conclusion that requires different evidence.

### 2. Rebuild the timeline

Order the material account, checkout, review, fulfilment, return and dispute events. Use the time known to the original decision-maker, not only the time discovered later.

### 3. Find the first relevant signal

Identify the earliest evidence that became relevant to the outcome. Include evidence whose significance was visible only after a later event.

### 4. Inspect each handoff

Test whether evidence, uncertainty, decision level and action travelled together. Record where the relay became incomplete.

### 5. Locate the reversible moment

Identify the last point at which a proportionate action could have reduced loss or preserved stronger evidence. Do not assume cancellation was the only useful action. A verified address change, better delivery instruction, retained communication or timely escalation may matter.

### 6. Separate outcome types

Keep merchant loss, consumer rights, payment-service protection, scheme result and criminal conclusion distinct.

### 7. Return the learning

Route the outcome to the named earlier owner and specify the rule, threshold, evidence capture or handoff to reassess.

The backtrace is not hindsight blame. It asks whether the earlier decision was reasonable on the evidence available then, and whether the later evidence should change future controls.

### Risk, Signal, Response: The Feedback Sink

**Risk:** Refund, dispute and loss outcomes are recorded but do not change the upstream control that could prevent recurrence.

**Signal:** The same loss pattern repeats while the original account, checkout or fulfilment decision remains unreviewed.

**Response:** Define a named feedback trigger, receiving owner and specific control decision to reassess.

## Practical control-owner checklist

### Account and promotion owner

- Record recovery, profile and promotion events with their time and source.
- State whether the conclusion is event-level or account-level.
- Send unresolved access questions forward without declaring takeover unless the evidence supports it.

### Checkout and payments owner

- Preserve the authentication result, transaction details and relevant exemptions or routing context available to the merchant.
- Do not present authentication as proof of customer intent or fulfilment.
- Identify which evidence must reach order review before release.

### Order-review owner

- Combine the relevant account, checkout and order evidence.
- State the bounded order conclusion and the evidence that would change it.
- Give fulfilment a clear release, hold or escalation instruction with an expiry point.

### Fulfilment and delivery owner

- Treat post-approval changes as new evidence, not merely administrative updates.
- Preserve dispatch, delivery and customer-contact records needed by later refund or dispute teams.
- Return failed verification, unusual delivery and proof-of-delivery outcomes to the order owner.

### Returns and customer-service owner

- Decide the individual claim on its facts and applicable process.
- Preserve return, inspection, communication and credit evidence.
- Escalate linked patterns separately rather than using an untested network label to decide every claim.

### Dispute owner

- Match evidence to the specific dispute condition and time limit.
- Prefer relevant evidence over document volume.[6]
- Send final outcomes to the earlier control capable of changing future loss.

### Governance and quality-assurance owner

- Test whether completed cases contain all six relay fields.
- Sample whether event, account, order, network, refund and dispute conclusions remain distinct.
- Review whether feedback triggers produced an actual control decision rather than a report that no one owned.

## What Would Change Our Assessment

Reopen the assessment if:

1. new evidence shows that the six-field relay duplicates an existing authoritative merchant standard;
2. primary evidence no longer supports the separation between authentication, authorisation, consumer rights and scheme disputes used in the guide;
3. material changes to United Kingdom payment-service or consumer-rights provisions alter either scenario boundary;
4. a current card-scheme rule or acquirer requirement contradicts a proposed dispute-evidence statement;
5. independent review finds that a scenario action is legally overbroad, disproportionate or insufficiently qualified; or
6. another FinCrimeRadar publication occupies the same cross-stage handoff and backtrace model.

## Five control patterns

The closing grid must reproduce these five cards exactly as they appear inline.

### The Local Green Light

**Risk:** Each stage makes a reasonable local decision while unresolved cross-stage evidence accumulates into loss.

**Signal:** An order has several approvals, but no owner can state the combined evidence or residual uncertainty.

**Response:** Complete the Fraud Evidence Relay before the next irreversible action.

### The Level Jump

**Risk:** A signal at one decision level becomes a fraud verdict at another without sufficient evidence.

**Signal:** An event anomaly is used to label an account, network or customer as fraudulent without a documented reasoning step.

**Response:** Name the decision level and write a bounded conclusion before selecting the action.

### The Relay Drop

**Risk:** Evidence reaches the next team without its meaning, or a conclusion arrives without the evidence and uncertainty behind it.

**Signal:** The next owner must reconstruct why the case was escalated from raw logs, short labels or free-text notes.

**Response:** Send the minimum evidence, source, timing, bounded conclusion, open question and required next decision as one relay package.

### The Feedback Sink

**Risk:** Refund, dispute and loss outcomes are recorded but do not change the upstream control that could prevent recurrence.

**Signal:** The same loss pattern repeats while the original account, checkout or fulfilment decision remains unreviewed.

**Response:** Define a named feedback trigger, receiving owner and specific control decision to reassess.

### The Rights Collapse

**Risk:** A merchant fraud concern is treated as though it decides consumer rights, payment-service protection, scheme outcomes and criminality.

**Signal:** One fraud label automatically determines refund, dispute and account decisions without separate tests.

**Response:** Record each outcome separately, apply its own evidence and authority, and preserve uncertainty where the merchant cannot decide it.

## Knowledge check

### Question 1

Which Fraud Evidence Relay field most directly prevents an event signal from becoming an unsupported account or network verdict?

A. Evidence state.

B. Decision level.

C. Feedback trigger.

**Correct answer:** B. The decision level identifies the question being answered before the evidence is interpreted.

### Question 2

Payment authentication succeeds in the first fictional scenario. What does that result fail to decide?

A. Whether an authentication process was completed.

B. Whether the transaction reached the merchant's order process.

C. Who controlled the account, why the delivery details changed and whether dispatch is reasonable.

**Correct answer:** C. Authentication is relevant but does not settle the account and fulfilment questions.[2][3]

### Question 3

Why must the individual refund decision and linked-network assessment remain separate?

A. They answer different questions, rely on different evidence and may lead to different outcomes while legitimate rights remain possible.

B. Device links always prove common control and should be kept out of refund decisions.

C. The card scheme decides whether an account network is fraudulent.

**Correct answer:** A. The link can justify investigation without deciding the individual entitlement or customer intent.[8][9][10]

### Question 4

What is the purpose of the relay package?

A. To copy every available data field to the next team.

B. To preserve the relevant evidence, its meaning, uncertainty, decision history and the next decision required.

C. To replace accountable ownership with an automated risk label.

**Correct answer:** B. A useful handoff carries both evidence and its bounded interpretation.

### Question 5

In Scenario 1, the recovery and address change are independently verified through a known channel and the new device fits prior behaviour. What changes?

A. The authentication result now proves honest intent.

B. The account can never be reviewed again.

C. Release may become proportionate because the evidence state changed, while the scope of authentication remains bounded.

**Correct answer:** C. The counterfactual changes the order risk, not what authentication proves.

## FAQ

### Does strong customer authentication prove that an e-commerce order is genuine?

No. It can reduce payment fraud and provide relevant authentication evidence.[2][3] It does not by itself prove who controlled an account, honest intent, delivery, refund legitimacy or the result of a later dispute.

### Is a chargeback outcome the same as a fraud finding?

No. A scheme dispute follows its applicable category, condition, evidence and process. Visa's merchant guidance distinguishes fraud, authorisation, processing-error and consumer-dispute categories and warns that its guide does not replace the rules or guarantee outcomes.[6] The scheme result should be recorded separately from merchant, legal and criminal conclusions.

### Can a merchant delay a refund while investigating abuse?

There is no universal answer. It depends on the legal basis for the claim, the facts, applicable timing rules, the payment method and any scheme or acquirer requirements. An internal fraud review does not automatically suspend statutory or scheme timelines. Use current legal and acquirer guidance before delaying, refusing or reducing a refund.[6][8][9]

### When should device or account links change an individual case decision?

When the links are relevant, sufficiently reliable and capable of changing the bounded decision being made. A link may justify review or a network hypothesis without proving common control or dishonest intent. Record the alternative innocent explanations and the evidence needed to distinguish them.

### What evidence should move from checkout to fulfilment and disputes?

Only the evidence material to the next decision, together with its source, timing, bounded conclusion, open question and required action. Depending on the case, this may include authentication context, account changes, material address changes, communication, dispatch and delivery evidence. Minimise irrelevant personal data and follow the merchant's lawful retention framework.

### Does the Fraud Evidence Relay require a new platform or backend?

No. It can be implemented as a governed record in an existing order, case or investigation system, or as a controlled static form. Technology may improve routing and reporting, but the essential control is the quality of the evidence boundary and handoff. Any system implementation is a separate design and governance decision.

## Update trigger

Recheck this guide before publication and when United Kingdom payment-service or consumer-rights provisions change materially, a relied-on card-scheme guide or rule changes, materially newer payment-fraud evidence becomes available, or repository coverage changes the originality boundary.

## Sources and methodology

1. UK Finance, [Fraud remains a national security threat as criminals steal almost £1.3 billion](https://www.ukfinance.org.uk/news-and-insight/press-release/fraud-report-2026-press-release), 15 June 2026. Industry evidence, not regulatory authority.
2. European Banking Authority and European Central Bank, [Joint report on payment fraud press release](https://www.eba.europa.eu/publications-and-media/press-releases/joint-eba-ecb-report-payment-fraud-strong-authentication-remains-effective-fraudsters-are-adapting) and [full joint report](https://www.eba.europa.eu/sites/default/files/2025-12/1709846a-84d9-47cf-86a0-b155efb34d66/EBA%20and%20ECB%20Report%20on%20Payment%20Fraud.pdf), 15 December 2025. European Economic Area scope.
3. Financial Conduct Authority, [Strong Customer Authentication](https://www.fca.org.uk/firms/strong-customer-authentication), with the applicable technical standards on [application](https://handbook.fca.org.uk/technical-standards/provision/s140c1221sn0p1814) and [exemptions](https://handbook.fca.org.uk/technical-standards/s140c1226). United Kingdom payment-service scope.
4. National Cyber Security Centre, [Use of credential stuffing tools](https://www.ncsc.gov.uk/news/use-credential-stuffing-tools), 19 November 2018.
5. Europol, [Safe sales, safe revenue](https://www.europol.europa.eu/operations-services-and-innovation/public-awareness-and-prevention-guides/safe-sales-safe-revenue). Law-enforcement prevention guidance, not a legal rule or prevalence source.
6. Visa, [Dispute Management Guide for Merchants](https://usa.visa.com/content/dam/VCOM/global/support-legal/documents/merchants-dispute-management-guidelines.pdf), October 2026. Official merchant guidance that does not replace Visa Rules, merchant agreements, acquirer requirements or applicable law.
7. Payment Services Regulations 2017: [regulation 67](https://www.legislation.gov.uk/uksi/2017/752/regulation/67), [regulation 74](https://www.legislation.gov.uk/uksi/2017/752/regulation/74), [regulation 75](https://www.legislation.gov.uk/uksi/2017/752/regulation/75) and [regulation 76](https://www.legislation.gov.uk/uksi/2017/752/regulation/76). Current revised legislation checked 18 October 2026.
8. [Consumer Rights Act 2015, section 20](https://www.legislation.gov.uk/ukpga/2015/15/section/20). Current revised legislation checked 18 October 2026.
9. Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013: [regulation 29](https://www.legislation.gov.uk/uksi/2013/3134/regulation/29) and [regulation 34](https://www.legislation.gov.uk/uksi/2013/3134/regulation/34). Current revised legislation checked 18 October 2026.
10. United States Department of Justice, [Eleven Sentenced for Refund Fraud Scheme Causing Millions of Dollars in Losses to Online Retailers](https://www.justice.gov/usao-ndok/pr/eleven-sentenced-refund-fraud-scheme-causing-millions-dollars-losses-online-retailers), 29 April 2026. United States public sentencing record.

The guide uses primary legislation, regulator material, public-sector guidance, an official card-scheme guide, industry data and a public sentencing record. Sources 1, 5 and 6 retain their industry, law-enforcement and scheme boundaries. Sources 2 and 10 retain their European Economic Area and United States scope. The fictional scenarios do not prove prevalence or control effectiveness.

The Fraud Evidence Relay, backtrace test, decision-level model and five control patterns are FinCrimeRadar assessments. The originality check also considered published Microsoft and INFORMS research and current Stripe vendor material. Those sources are not used as authority for legal, regulatory or prevalence claims.

## Related FinCrimeRadar publications

Implementation should add exactly two reciprocal relationships after checking current page copy:

- `fraud-red-flags-guide`, for existing account-takeover and transaction-laundering coverage;
- `fraud-investigation-playbook`, for generic hypothesis, chronology and case-file discipline.

The synthetic-identity and device-network guide may be linked editorially where useful, but it should not receive another reciprocal Related Topics entry because its current relationship cluster is already dense. Part 1 must not reproduce any of those guides' typology or investigation content.
