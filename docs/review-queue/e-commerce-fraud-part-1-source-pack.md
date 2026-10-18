# The E-commerce Fraud System: Part 1 source pack and qualification record

Compiled 18 October 2026 on `main` at `5750aeafc9793ce9a3bb5b93723a5b1954365d7f`.

**Queue decision:** PASS for promotion of Part 1 to QUALIFIED. This permits analytical design and a Part 1 Requirement Coverage Matrix. It does not authorise editorial drafting, implementation or publication. Parts 2 to 5 remain at RESEARCH.

**Verification owner:** Codex.

**Public format:** Guide within the Default Knowledge Hub treatment.

**Scope:** Merchant-side fraud and abuse from account creation through post-transaction dispute. The operational model is broad, but every legal, regulatory, card-scheme and statistical claim must retain its source jurisdiction and evidence boundary.

**Excluded from the central claim:** a fraud typology catalogue, general cybercrime guidance, a universal chargeback manual, consumer scam classification, vendor selection, fraud-model design and any employer-specific process or example.

**Retrieval method:** Current primary legislation, regulator material, public-sector guidance, law-enforcement records and official card-scheme guidance were read on 18 October 2026. UK Finance data is treated as industry evidence. Published practitioner research and vendor material are used only to test originality or provide bounded operational context. No Nisbets material was used.

**Status key:** VERIFIED means the source was read and supports the proposition within the stated boundary. CAVEAT means the proposition is supportable only with the stated limitation. REVIEW means the final wording or scenario conclusion requires independent adversarial review under `CLAUDE.md` section 7. ORIGINALITY ONLY means the source must not be used as authority for a legal or regulatory proposition.

## 1. Evidence pack

### S1. UK Finance, Annual Fraud Report 2026 press release

- URL: https://www.ukfinance.org.uk/news-and-insight/press-release/fraud-report-2026-press-release
- Published: 15 June 2026.
- Status: VERIFIED as industry evidence, not regulatory authority.
- Supports:
  - UK Finance members reported £703.4 million of unauthorised fraud losses and 3.81 million cases for 2025.
  - Remote purchase card fraud accounted for £423.5 million and 3.2 million cases within that dataset.
  - UK Finance separately reports authorised push payment fraud and purchase scams. These must not be blended into card-not-present merchant fraud.
  - The data is supplied by members including issuers and acquirers, and an incident means an affected card or account rather than necessarily one victim.
- CAVEAT: These figures do not measure total e-commerce fraud, total merchant losses or global prevalence. UK Finance is an industry body.

### S2. European Banking Authority and European Central Bank, joint report on payment fraud

- Press release: https://www.eba.europa.eu/publications-and-media/press-releases/joint-eba-ecb-report-payment-fraud-strong-authentication-remains-effective-fraudsters-are-adapting
- Report: https://www.eba.europa.eu/sites/default/files/2025-12/1709846a-84d9-47cf-86a0-b155efb34d66/EBA%20and%20ECB%20Report%20on%20Payment%20Fraud.pdf
- Published: 15 December 2025.
- Status: VERIFIED. Joint supervisory and central-bank evidence for the European Economic Area.
- Supports:
  - Strong customer authentication remains associated with lower fraud rates, particularly for card payments.
  - Authentication does not remove payment fraud and fraud methods adapt.
  - The report records materially higher card-fraud rates where the recipient is outside the European Economic Area and strong customer authentication is often not applied.
- CAVEAT: This is European Economic Area evidence. It does not establish a universal merchant control standard or a UK merchant loss measure.

### S3. Financial Conduct Authority, Strong Customer Authentication

- URL: https://www.fca.org.uk/firms/strong-customer-authentication
- Technical standards, application (Chapter -3): https://handbook.fca.org.uk/technical-standards/provision/s140c1221sn0p1814
- Technical standards, exemptions (Chapter 3, Articles 10 to 21): https://handbook.fca.org.uk/technical-standards/s140c1226
- Status: VERIFIED. Primary UK regulator material and technical standards.
- Supports: UK payment service providers have strong customer authentication obligations, subject to the detailed scope and exemptions. The technical standards (checked 18 October 2026) apply to payment service providers authorised or registered in the UK or Gibraltar (Chapter -3) and set out the exemptions in Chapter 3, Articles 10 to 21. The technical standards (checked 18 October 2026) apply to payment service providers authorised or registered in the UK or Gibraltar (Chapter -3) and set out the exemptions in Chapter 3, Articles 10 to 21.
- CAVEAT: A successful authentication result is not a complete merchant fraud decision, proof that the customer is acting honestly, or a guarantee against a later dispute.
- REVIEW: Any explanation of exemptions, merchant-initiated transactions, liability allocation or the merchant's role requires fresh specialist review before publication.

### S4. National Cyber Security Centre, Use of credential stuffing tools

- URL: https://www.ncsc.gov.uk/news/use-credential-stuffing-tools
- Published: 19 November 2018.
- Status: VERIFIED. Official cyber-security guidance on a continuing attack mechanism.
- Supports: credential stuffing exploits reused username and password combinations to gain access to legitimate accounts.
- Application boundary: Part 1 may use this only to explain how an account signal can acquire later merchant-fraud significance. Existing FinCrimeRadar account-takeover material remains the canonical typology coverage.

### S5. Europol, Safe sales, safe revenue

- URL: https://www.europol.europa.eu/operations-services-and-innovation/public-awareness-and-prevention-guides/safe-sales-safe-revenue
- Status: VERIFIED as law-enforcement prevention guidance, not a legal rule or prevalence source.
- Supports: Europol's merchant-facing material identifies account takeover, clean fraud, phishing, spoofing, refund abuse and laundering through refunds to a different payment source as relevant e-commerce risks. It also identifies device and location information as potential fraud indicators.
- CAVEAT: The guide lists prevention practices. It does not prove that any one signal is fraud or that a control is proportionate for every merchant.

### S6. Visa, Dispute Management Guide for Merchants

- URL: https://usa.visa.com/content/dam/VCOM/global/support-legal/documents/merchants-dispute-management-guidelines.pdf
- Current edition read: October 2026.
- Status: VERIFIED as official Visa merchant guidance.
- Supports:
  - Disputes have different categories, conditions, evidential requirements and time limits.
  - Relevant evidence may concern cardholder linkage, participation or benefit, processing, fulfilment, cancellation and refunds.
  - Accurate transaction information and retained documentation matter from processing through post-sale dispute handling.
  - Merchants should monitor dispute patterns across condition, sales ratio, response effectiveness and channel to identify recurring issues and control gaps.
  - Evidence volume does not substitute for relevance to the specific dispute condition.
- CAVEAT: The guide expressly does not replace the Visa Rules, a merchant agreement, acquirer requirements, applicable law or independent assessment. It does not guarantee outcomes and does not apply identically in every country.
- REVIEW: Scheme terminology and any statement about response rights, eligibility, evidence or deadlines require a current rule and acquirer check before publication.

### S7. Payment Services Regulations 2017, regulations 67, 74, 75 and 76

- Regulation 67: https://www.legislation.gov.uk/uksi/2017/752/regulation/67
- Regulation 74: https://www.legislation.gov.uk/uksi/2017/752/regulation/74
- Regulation 75: https://www.legislation.gov.uk/uksi/2017/752/regulation/75
- Regulation 76: https://www.legislation.gov.uk/uksi/2017/752/regulation/76
- Status: VERIFIED. Primary UK legislation.
- Supports:
  - Authorisation depends on the payer's consent under regulation 67.
  - Under regulation 75, recorded use of a payment instrument is not necessarily sufficient by itself to prove authorisation or that the payer acted fraudulently or with intent or gross negligence.
  - Under regulation 74(1), redress under regulation 76 is available only if the payment service user notifies the payment service provider without undue delay, and in any event no later than 13 months after the debit date, on becoming aware of the unauthorised or incorrectly executed transaction, subject to regulation 74(2) where required information was not provided under Part 6.
  - Subject to regulations 74 and 75, regulation 76 places the stated refund and account-restoration duties for an unauthorised transaction on the payment service provider.
- Application boundary: These rules concern payment-service relationships and must not be rewritten as a merchant's universal chargeback rule or a finding that the merchant committed an error.
- REVIEW: The statutory conditions, exceptions, territorial application and distinction between payer, payment service provider, issuer, acquirer and merchant require independent legal review before public wording is locked.

### S8. Consumer Rights Act 2015, section 20

- URL: https://www.legislation.gov.uk/ukpga/2015/15/section/20
- Status: VERIFIED. Primary UK legislation.
- Supports: where the statutory right to reject applies and is exercised, the section sets out the consumer's refund entitlement and related duties.
- Application boundary: A legitimate rejection and refund are not fraud merely because they create merchant loss or resemble an abuse pattern.
- REVIEW: The final guide must not summarise section 20 without its conditions, related sections and factual application.

### S9. Consumer Contracts Regulations 2013, regulations 29 and 34

- Regulation 29: https://www.legislation.gov.uk/uksi/2013/3134/regulation/29
- Regulation 34: https://www.legislation.gov.uk/uksi/2013/3134/regulation/34
- Status: VERIFIED. Primary UK legislation.
- Supports: qualifying distance and off-premises contracts may carry cancellation rights, and regulation 34 governs reimbursement timing, method and specified deductions after cancellation.
- Application boundary: Statutory cancellation and reimbursement must remain analytically separate from refund abuse and payment disputes.
- REVIEW: Scope exclusions, goods-return conditions, deductions and current amendments require independent legal review before a scenario recommends withholding or reducing a refund.

### S10. United States Department of Justice, Artemis Refund Group sentencing record

- URL: https://www.justice.gov/usao-ndok/pr/eleven-sentenced-refund-fraud-scheme-causing-millions-dollars-losses-online-retailers
- Published: 29 April 2026.
- Status: VERIFIED as a public record of guilty pleas and sentencing, not an allegation-only case.
- Supports:
  - The group targeted multiple online retailers and advertised refund-fraud services through online messaging forums.
  - Customers bought goods, supplied order information, obtained fraudulent refunds and retained the goods.
  - The group charged a percentage of the refunded value and some goods were resold.
- CAVEAT: This is a United States criminal case. It can inform a fictional mechanism or provide a bounded public case study, but it does not establish UK legal outcomes, prevalence or a standard retailer control.

### S11. Microsoft and INFORMS, machine learning and optimisation research

- URL: https://pubsonline.informs.org/doi/abs/10.1287/inte.2019.1017
- Published online: 24 January 2020.
- Status: ORIGINALITY ONLY. Published practitioner research authored by Microsoft personnel.
- Supports the originality comparison: existing work already describes dynamic fraud patterns, decisions by merchants, issuers and manual reviewers, and feedback interactions within an e-commerce fraud-management system.
- CAVEAT: The paper reports a specific Microsoft implementation. Its performance and architecture are not universal merchant evidence.

### S12. Stripe, Fraud risk management: a framework for businesses

- URL: https://stripe.com/resources/more/fraud-risk-management
- Current page read: 18 October 2026.
- Status: ORIGINALITY ONLY. Vendor material.
- Supports the originality comparison: current vendor guidance already maps account creation, checkout, stored payment methods, refunds and disputes, and already recommends assigning ownership across that transaction map.
- CAVEAT: This source is not used for law, prevalence or a claim that its controls are suitable for every merchant.

## 2. Settled and unresolved assessment

### Settled enough to teach

1. E-commerce fraud and abuse can surface at account, payment, fulfilment, refund and dispute stages.
2. A locally defensible decision at one stage may leave material uncertainty for a later owner.
3. Authentication can reduce some payment fraud without settling customer intent, fulfilment facts, refund legitimacy or a later scheme dispute.
4. Dispute evidence is condition-specific and may depend on information created long before the dispute arrives.
5. Later refunds, disputes and confirmed losses can reveal upstream evidence or control gaps.
6. Legitimate statutory cancellation, rejection and unauthorised-payment protections are different decisions from a merchant fraud assessment.

### Material matters to keep qualified

1. UK Finance figures are industry-reported card and account incidents, not a complete e-commerce or merchant-loss measure.
2. European Economic Area payment-fraud evidence is not automatically a United Kingdom rule or global benchmark.
3. Strong customer authentication is not proof of honest customer intent or a guaranteed defence to a later dispute.
4. Card-scheme guidance is not legislation, does not replace current scheme rules or merchant agreements, and does not guarantee a result.
5. A dispute outcome is not automatically a finding of fraud, criminal liability or merchant wrongdoing.
6. A merchant fraud concern does not extinguish statutory consumer rights or payment service protections.
7. A fictional composite can demonstrate decision quality but cannot prove prevalence, causation or control effectiveness.

## 3. Originality check

### Existing FinCrimeRadar coverage

The companion non-overlap review identifies direct existing coverage of account takeover, synthetic identity, device networks, transaction laundering, card testing, refund abuse, agentic commerce and investigation files. Part 1 must reference those mechanisms rather than teach them again.

### External overlap

- Stripe already provides a lifecycle transaction map and recommends ownership allocation.
- Microsoft and INFORMS already describe multi-party decisions, dynamic patterns and feedback interactions.
- Visa already connects transaction data, fulfilment, refund handling, evidence readiness and dispute monitoring.

A guide whose contribution is merely to map the lifecycle, assign owners or recommend feedback loops would therefore fail the originality gate.

### FinCrimeRadar differentiator: the Fraud Evidence Relay

Part 1 should teach one cross-stage record with six fields:

1. **Decision level:** event, account, order, linked network, refund or dispute.
2. **Evidence state:** what is known at this stage, its source, time and reliability.
3. **Bounded conclusion:** what the evidence supports and what it does not support.
4. **Action and owner:** the action taken, the accountable role and any review or expiry point.
5. **Relay package:** the minimum evidence, uncertainty and instruction that must move to the next owner.
6. **Feedback trigger:** the later outcome that must return to a named earlier control, with the specific decision or rule to reassess.

The record is paired with a **backtrace test**: begin with a later refund, dispute or confirmed loss and trace which earlier stage first held relevant evidence, whether it was relayed, how its meaning changed and whether the outcome returned to improve that control.

This is a FinCrimeRadar analytical synthesis. It is not regulator, law-enforcement or card-scheme terminology.

**Originality verdict:** PASS only if the Fraud Evidence Relay and backtrace test are the central analytical model. Without them, Part 1 returns to RESEARCH.

## 4. Proposed Part 1 analytical boundary

The model should explain evidence movement, not prescribe a universal fraud score or recreate each typology. Its decision object is the quality of the lifecycle handoff:

- Did the current owner identify the correct decision level?
- Did the owner state a bounded conclusion rather than convert a signal into a fraud finding?
- Did relevant evidence and residual uncertainty reach the next control before an irreversible action?
- Did the final outcome return to the stage capable of changing future loss?

The model must work without a backend. A static table, printable record and worked backtrace are sufficient for Part 1. Any later backend, API, schema or implementation is owned by Claude Code and requires separate authorisation.

## 5. Required worked decisions

### Scenario 1: authenticated order, fragmented pre-fulfilment evidence

A fictional merchant receives a high-value order from an established account. Payment authentication succeeds. Account operations hold a recent recovery event, checkout sees a new device and delivery address, and fulfilment receives an address-change request after approval. Each signal is individually explainable and no single team can establish fraud.

Decision point: whether to release, pause for bounded review or cancel, and what evidence and uncertainty must be relayed before dispatch.

Teaching distinction: successful payment authentication, an account-level concern and an order-level fulfilment decision answer different questions. The scenario must not reuse the facts or locations from Scenario Lab `session-hijack-002`.

Source boundary: fictional facts. The credential-access mechanism may be informed by S4, the authentication boundary by S2 and S3, and dispute-evidence implications by S6.

### Scenario 2: apparently isolated refund requests forming a network pattern

A separate fictional merchant receives several individually plausible non-delivery or return claims. Customer service can see only each order, while returns, device and payment records reveal linked accounts and repeated refund outcomes. Some customers may still have legitimate statutory rights.

Decision point: whether to process the individual claim, escalate a linked-network review or restrict the account while preserving legitimate refund and cancellation rights.

Teaching distinction: customer-service resolution, network-level abuse assessment, statutory consumer rights and any later dispute are separate decisions.

Source boundary: fictional facts. The organised refund mechanism may be informed by S10, the consumer-rights boundary by S8 and S9, and the dispute boundary by S6. The facts must not recreate Scenario Lab `device-network-006`.

The scenarios are materially distinct in lifecycle stage, decision level and risk mechanism. Both require graded options and complete Source, Application and Action reasoning during design.

## 6. Part 1 information architecture candidate

This is a design input, not an editorial draft:

1. Why local controls miss system-level fraud.
2. The six lifecycle stages relevant to Part 1.
3. Decision levels and bounded conclusions.
4. The Fraud Evidence Relay.
5. Worked decision 1 and its forward relay.
6. Worked decision 2 and its rights boundary.
7. The backtrace test from loss to first signal.
8. Control-owner checklist and What Would Change Our Assessment.

The guide should link to existing typology guides where needed and keep their detailed detection content out of Part 1.

## 7. Claims requiring independent adversarial review

1. The scope and practical effect of strong customer authentication, including exemptions and merchant versus payment service provider responsibilities.
2. The distinction among payer consent, authentication evidence, unauthorised-payment reimbursement and merchant or scheme outcomes under regulations 67, 75 and 76.
3. Consumer cancellation, rejection, return, refund and deduction rights under the Consumer Rights Act 2015 and Consumer Contracts Regulations 2013.
4. Every statement that translates Visa or another scheme's current rules into merchant response rights, evidence requirements, deadlines or liability consequences.
5. Any scenario recommendation to delay fulfilment, restrict an account, refuse or reduce a refund, or allege fraud.
6. Any cross-jurisdiction comparison or claim that a control represents standard industry practice.

## 8. Reassessment triggers

Recheck before drafting and after any of these events:

1. Changes to UK strong customer authentication rules or Payment Services Regulations relevant to the teaching point.
2. Changes to applicable UK consumer cancellation, rejection or refund provisions.
3. A new edition of the card-scheme guidance or rules relied upon.
4. Materially newer UK or European payment-fraud data.
5. Repository publication of another guide that occupies the Fraud Evidence Relay or backtrace model.

## 9. Queue-gate outcome

- **Verification owner:** Codex.
- **Evidence checked:** 18 October 2026. Sources S1 to S12 and the repository overlap set recorded in `e-commerce-fraud-series-non-overlap-review.md`.
- **Review date:** 18 October 2026.
- **Verification outcome:** PASS for Part 1 to move from RESEARCH to QUALIFIED. The evidence supports the merchant lifecycle problem, the Fraud Evidence Relay clears the originality gate, and two materially distinct practitioner decisions are available.
- **Unreleased work:** The Requirement Coverage Matrix, editorial draft, implementation, tests, Git operations and publication remain unapproved. Claude Code owns any later backend or repository implementation. Codex remains the independent review layer.
