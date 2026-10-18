# The E-commerce Fraud System: Part 1 charter

**Series:** E-commerce Fraud: From Account Creation to Chargeback<br>
**Part:** 1 of 5<br>
**Working title:** The E-commerce Fraud System<br>
**Charter date:** 18 October 2026<br>
**Queue state:** RESEARCH<br>
**Current authority:** Source-pack research only after charter approval. No editorial draft or implementation is authorised by this document.

## 1. Employer-separation gate

The project owner confirmed on 18 October 2026 that Nisbets is aware of FinCrimeRadar, its operations and its content, and authorised this work to proceed.

This charter records the following non-negotiable boundary:

- all scenarios, taxonomies, examples and control models must derive only from identified public sources or clearly labelled fictional material;
- no Nisbets data, systems, policies, incidents, customers, controls, confidential knowledge or employer-specific examples may be used;
- the repository must not contain the employment contract, handbook or employer correspondence;
- FinCrimeRadar must not imply Nisbets sponsorship, endorsement or authorship.

This is a project-governance record of the owner's confirmation. It is not a legal interpretation of employment terms.

## 2. Scope lock

**Public format:** Guide within the Default Knowledge Hub treatment.

**Audience:** Merchant fraud, e-commerce risk, payments, trust and safety, customer operations, fulfilment, returns, dispute and financial-crime practitioners.

**Operational scope:** Merchant-side fraud and abuse from account creation through post-transaction dispute.

**Jurisdiction treatment:** Operationally broad. Any legal, regulatory, card-scheme or consumer-rights proposition must be jurisdiction-labelled and source-scoped. The guide must not blend different regimes into one universal rule.

**Intelligence question:** How can a merchant preserve and interpret fraud evidence across account creation, promotion, checkout, fulfilment, refund and chargeback when no single stage shows the complete pattern?

**Locked thesis:** E-commerce fraud is a system problem. A control can make a locally defensible decision and still pass risk into the next stage when evidence, ownership and feedback are fragmented.

**Original contribution:** A practitioner method for following evidence and control ownership across the complete merchant lifecycle, showing what each stage knows, what it cannot conclude and what must be handed forward.

**Decision object:** A lifecycle-level fraud assessment that links the event, evidence available at each stage, decision owner, action taken, residual uncertainty and downstream consequence.

**Excluded:** A general cybercrime guide, consumer scam taxonomy, marketplace regulatory handbook, vendor comparison, fraud-product review, card-scheme manual, universal chargeback rulebook, master typology catalogue or replacement for the existing fraud investigation playbook.

## 3. Part 1 practitioner outcome

After reading Part 1, a practitioner should be able to:

1. identify where a fraud signal first appeared and where it changed meaning;
2. distinguish an event-level decision from an account-level, order-level, network-level or dispute-level conclusion;
3. state what evidence should move with the case to the next control owner;
4. identify a broken feedback loop where a later loss did not improve an earlier control;
5. separate merchant loss findings from chargeback outcomes, refund rights, unauthorised-payment protections and criminal conclusions.

## 4. Content boundary against existing FinCrimeRadar work

Part 1 must use the companion non-overlap review as a hard boundary.

It may reference existing work on account takeover, synthetic identity, device networks, transaction laundering, card testing, refund abuse, agentic commerce and investigation files. It must not reteach those typologies as its original contribution.

Part 1 earns publication only if the source pack supports the lifecycle evidence-continuity thesis and the eventual guide gives readers a reusable cross-stage decision method.

## 5. Case-study and scenario policy

One recurring fictional composite may be used as the series anchor. Its purpose is continuity, not realism by implication.

The anchor must:

- use a fictional merchant, customers, accounts, orders, amounts and outcomes;
- be labelled clearly as fictional and illustrative;
- avoid facts derived from Nisbets or any other employer or client;
- avoid invented prevalence figures, legal holdings, regulatory findings or card-scheme rules;
- disclose which public sources informed any non-obvious fraud mechanism or control proposition.

Public case studies may also be used where the facts are directly sourced and the difference between allegation, finding, settlement and commentary is preserved.

Under `GUIDE_STANDARD.md`, Part 1 requires at least two materially distinct worked scenarios. The recurring composite can count as one only if it contains a genuine Part 1 decision point with graded options and complete Source, Application and Action reasoning. The second scenario must differ materially in facts, decision context, risk mechanism or practitioner judgement. A later chapter in the same fictional story is not automatically a distinct scenario.

This charter does not select the scenarios or create a series-wide scenario inventory.

## 6. Evidence and accuracy rules

Before editorial drafting:

1. Build the Part 1 source pack from current public sources.
2. Map every load-bearing factual, legal, scheme and industry proposition to its strongest source.
3. Separate primary authority, scheme rule, regulator guidance, industry position and FinCrimeRadar assessment.
4. Mark fictional facts as illustrative.
5. Record material claims in `verification-ledger.json` only when the wording and source mapping are ready.
6. Route new or materially revised legal-scope claims for independent adversarial review before publication.

Source, Application and Action must remain visibly separate in every legally or regulatorily sensitive teaching point and worked decision.

## 7. Required next deliverable

The next authorised deliverable is a Part 1 source pack and originality check. It may propose, but must not yet implement:

- the precise Part 1 analytical model;
- the two Part 1 scenario candidates;
- the Part 1 information architecture;
- the Part 1 Requirement Coverage Matrix;
- the claims requiring independent legal or regulatory review.

The next phase must not create the five-guide Requirement Coverage Matrix, master taxonomy, primary-source register for the whole series or 15-scenario inventory.

## 8. Implementation ownership

Part 1 is expected to remain static-first under the current FinCrimeRadar architecture. No backend is authorised or required by this charter.

If later requirements justify backend, API, schema, build or repository implementation work:

- Claude Code owns that implementation, tests, Git operations and release preparation;
- Codex performs independent overlap, regulatory, logic, security and verification review only;
- the human owner approves sources, material editorial judgements, publication, push and merge;
- implementation must not begin merely because this charter exists.

## 9. Acceptance gates before drafting

Editorial drafting remains blocked until all of the following are recorded:

- current public-source pack completed;
- Part 1 originality proposition confirmed against the repository and current external material;
- two distinct Part 1 scenario candidates identified;
- jurisdiction and payment-method boundaries fixed;
- verification owner, evidence date, review date and outcome recorded;
- material legal and scheme-rule claims identified for later independent review.

## 10. Explicitly out of scope for this charter

- external subject-matter conclusions;
- final terminology or taxonomy;
- full-series source research;
- full-series scenario planning;
- editorial prose;
- HTML, CSS or JavaScript;
- backend or API work;
- metadata, schema, sitemap or Knowledge Hub integration;
- verification-ledger changes;
- social card or distribution copy;
- commit, push, pull request, merge or publication.

## 11. Charter outcome

**Outcome:** APPROVED BOUNDARY FOR PART 1 SOURCE-PACK RESEARCH.

The guide remains RESEARCH. It is not READY, specified, built or publication-ready.
