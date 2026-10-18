# E-commerce Fraud series: repository and Scenario Lab non-overlap review

**Review date:** 18 October 2026<br>
**Repository revision reviewed:** `5750aeafc9793ce9a3bb5b93723a5b1954365d7f`<br>
**Status:** First-scope review complete. No external subject-matter research performed.<br>
**Scope:** Current repository publications, Knowledge Hub records and `scenario-lab/data/cases.json` only.

## 1. Decision

The proposed series has a defensible gap if it remains a merchant-side lifecycle series. Its distinctive value is not another list of fraud typologies. It is the continuity of evidence, ownership and controls from account creation through checkout, fulfilment, refund and chargeback.

Part 1 may proceed to source-pack research after approval of its charter. Later parts remain unqualified. This review does not create a master taxonomy, a five-guide Requirement Coverage Matrix, a primary-source register or a scenario inventory.

## 2. Series boundary

The series is limited to merchant-side fraud and abuse across the e-commerce lifecycle. It must not expand into every cyberattack, consumer scam, marketplace obligation or payment-services dispute.

The five proposed parts remain:

1. The E-commerce Fraud System.
2. Identity, Account and Promotion Abuse.
3. Payment and Checkout Fraud.
4. Fulfilment, Returns and Refund Abuse.
5. E-commerce Fraud Investigations and Control Operations.

The series-level proposition is that fragmented controls can each appear locally reasonable while the complete fraud pattern is visible only across stages. Each part must contribute a distinct decision or control model, not repeat the same typologies under a new lifecycle heading.

## 3. Direct overlap map

| Existing publication or case | Existing contribution | Series treatment |
|---|---|---|
| `fraud-red-flags-guide.html` and Scenario Lab `session-hijack-002` | Account takeover at checkout, impossible travel, device change and session containment | Reference for the account-takeover mechanism. Do not recreate the Lagos checkout or treat the same facts as a new scenario. |
| `fraud-red-flags-guide.html` and Scenario Lab `storefront-mimicry-003` | Transaction laundering, card testing and abnormal merchant-processing behaviour | Keep outside the core consumer checkout path unless needed to explain merchant or payment-channel abuse. Cross-link rather than reproduce the Candle Shop scenario. |
| `synthetic-identity-device-network-guide.html` and Scenario Lab `synthetic-identity-005` | Fabricated identity and the distinction between a false person and a genuine person misusing accounts | Reuse the distinction by reference. A later identity chapter must focus on the merchant lifecycle and avoid reteaching the identity taxonomy. |
| `synthetic-identity-device-network-guide.html` and Scenario Lab `device-network-006` | Linked accounts, shared devices, empty-box claims and network-level refund abuse | Direct overlap with Part 4. The Device Network remains the canonical existing exercise. Part 4 needs a different decision context and evidence chain. |
| `ai-agent-transaction-guide.html` | Agent takeover, mandate evidence, erroneous purchases and friendly-fraud disputes | Treat agentic commerce as a bounded edge case. Do not let it become the series' general payment or chargeback model. |
| `fraud-investigation-playbook.html` | Hypothesis testing, chronology, disclosure boundaries and reviewable case files | Part 5 must specialise this for merchant evidence and cross-team hand-offs. Do not restate the generic investigation process. |
| `tm-guide.html` | Rules, alert triage, tuning and monitoring programme design | Distinguish merchant fraud decisioning from bank transaction monitoring. Reuse programme-control concepts only where the merchant context changes the judgement. |
| `app-scam-decision-framework.html` | APP scam classification, reimbursement scope, civil-dispute boundary and defensibility | Keep APP reimbursement separate from card, merchant and chargeback outcomes. Cross-link only where a payment-method boundary needs explanation. |
| `investment-scam-investigation-handbook.html` | Proposition, identity, journey and money-route investigation | Do not reuse its four-stream model as the e-commerce series architecture. It may inform evidence discipline, not content structure. |
| `money-mule-or-victim-case-file.html`, `money-mule-financial-crime-networks-handbook.html` and `scam-compound-money-laundering-guide.html` | Customer intent, mule networks, receiving accounts and laundering after fraud | These sit downstream or outside the merchant loss decision. Cross-link when proceeds movement matters, without turning the series into a money-laundering guide. |

## 4. Scenario Lab findings

Four current cases are direct reuse constraints:

1. `session-hijack-002`, account takeover during checkout.
2. `storefront-mimicry-003`, transaction laundering and card testing.
3. `synthetic-identity-005`, fabricated identity.
4. `device-network-006`, linked-account empty-box and refund abuse.

`app-scam-001` is adjacent but not a merchant-side e-commerce case. The remaining current cases do not materially occupy the proposed lifecycle architecture.

The gap is therefore not new typology coverage. It is a system-level explanation of how evidence changes meaning across stages, how one team's local decision affects the next control, and how the final dispute should be traced back to earlier signals.

## 5. Reuse rules

1. Existing scenarios may be linked or briefly summarised, but must not be republished as new scenarios.
2. An existing Scenario Lab case does not satisfy a new guide's worked-scenario requirement merely because it is referenced.
3. Each new guide still requires at least two materially distinct worked scenarios under `GUIDE_STANDARD.md`.
4. The recurring fictional composite may supply continuity across the series. It can count as a worked scenario in a guide only where that guide presents a discrete decision with its own full reasoning. A second materially distinct scenario remains mandatory.
5. Public case-study facts require direct sourcing. Fictional facts must be labelled illustrative and must not carry invented statistics, legal outcomes or attributed organisational practices.
6. Chargebacks, statutory refund rights, unauthorised-payment protections and merchant fraud findings must remain separate decisions.

## 6. Conditions for Part 1 research

Part 1 research may begin only from the approved charter and must:

- create a public-source pack before editorial drafting;
- test the lifecycle evidence-continuity proposition against existing publications and current external material;
- define the Part 1 decision object without creating the full-series taxonomy;
- select or design two materially distinct worked decisions for Part 1 only;
- label jurisdiction-specific law, scheme rules and industry positions precisely;
- keep all employer information outside the repository and research record;
- route any repository or backend implementation to Claude Code;
- reserve Codex for independent review and verification rather than implementation.

## 7. Outcome

**Outcome:** QUALIFIED FOR PART 1 SOURCE-PACK RESEARCH ONLY.

The wider five-part series remains at RESEARCH. No publication, source register, scenario inventory, implementation or release work is authorised by this review.
