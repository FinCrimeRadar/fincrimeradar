# Digital Identity Is Not the Whole of CDD: analytical design memo

Companion to `digital-identity-cdd-source-pack.md`. This memo completes Content Loop step 04. It locks the analytical model, scenarios, interaction pattern and information architecture before editorial drafting and repository implementation.

## 1. Scope lock

**Public format:** Intelligence Brief within the Default Knowledge Hub treatment.

**Jurisdiction:** United Kingdom.

**Audience:** AML, KYC, onboarding, MLRO, financial-crime systems, procurement and assurance practitioners at firms subject to the Money Laundering Regulations 2017.

**Intelligence question:** When a certified and registered digital verification service returns a successful result, exactly what has the firm established, about whom, at what assurance level, and which CDD duties remain open?

**Decision object:** One Proof Boundary Record for each material verification result, followed by a decision on whether the wider CDD file is complete, incomplete or requires enhanced measures.

**Locked thesis:** A pass is not a customer verdict. It is a bounded evidence result.

**Original contribution:** The six-field Proof Boundary Record. The brief does not earn publication by repeating that digital identity is not all of CDD. It earns publication by giving practitioners a reproducible way to state the boundary of a result and preserve it in the decision record.

**Excluded:** Vendor comparisons, product recommendations, Companies House identity verification as a substitute for MLR CDD, age assurance, right to work, right to rent, DBS checks and any suggestion that certification makes a firm's whole onboarding process compliant.

## 2. Intelligence Core

| Element | Locked answer |
|---|---|
| Intelligence question | What does the successful result prove, about which subject, through which registered service and certified role, at what assurance, and what remains open? |
| Evidence state | Established: the Regulation 28 duties, the February 2026 approved guidance, the statutory register architecture, the trust framework and certification scheme. Regulatory guidance: the FCA CDD findings and OfDIA clarification. FinCrimeRadar assessment: the Proof Boundary Record and the five control patterns. Unknown until checked on the relevant date: the current status and scope of any individual service and certificate. |
| Decision object | A six-field Proof Boundary Record plus a wider CDD completeness decision. |
| Uncertainty | Service registration, certificate scope and framework version can change. Attribute outputs may sit inside or outside certified scope. The precise supervisory significance of approved guidance and the treatment of unregistered electronic verification require careful qualification. |
| Change condition | A change to the customer, subject, service, certificate, assurance, risk, behaviour, ownership, authority, purpose or applicable guidance that makes the recorded boundary stale or incomplete. |
| Practitioner outcome | The reader can accept valid identity evidence without allowing it to stand in for corporate identity, authority, ownership, beneficial ownership, purpose, risk, EDD, monitoring or records. |

## 3. Analytical model: the Proof Boundary Record

Each result is recorded through six fields. Their order is fixed because each field constrains the next.

1. **Subject:** The natural person actually checked. Examples include an individual customer, director, representative or beneficial owner. Do not substitute a role or organisation for the person whose evidence was tested.
2. **Proposition:** The conclusion supported by the result. Usually this is identity at a stated confidence level. It is not, without separate evidence, low risk, legitimate activity, valid authority, clean screening or a complete customer relationship.
3. **Service scope:** The named service used, its current statutory-register entry, certified role, framework version, certificate status and any relevant identity profile or supplementary code at the time of the check.
4. **Assurance:** The confidence level or profile returned and the firm's recorded reason for treating it as commensurate with the assessed money-laundering and terrorist-financing risk.
5. **Residual duties:** Every separate duty or evidential proposition that remains open, including purpose and intended nature, authority, corporate identity, ownership and control, beneficial ownership, EDD, ongoing monitoring and record keeping where applicable.
6. **Change trigger:** The event that requires the boundary to be reassessed. This can arise from the customer, service, certificate, risk or observed behaviour.

The record is not a new legal test. It is a FinCrimeRadar control model for preventing evidential overreach.

## 4. Locked information architecture

The publication uses the following order.

1. Hero and intelligence-status strip.
2. How to read the brief.
3. Executive assessment.
4. Intelligence timeline.
5. What changed in 2026.
6. The proof boundary.
7. The six-field Proof Boundary Record.
8. Settled and unresolved assessment.
9. Decision horizon.
10. Operational implementation.
11. What Would Change Our Assessment.
12. Two worked decisions.
13. Five Risk, Signal, Response patterns.
14. Knowledge check.
15. FAQ.
16. Update trigger.
17. Sources and methodology.
18. Related intelligence.

The page must remain useful as a static article. Interaction reveals feedback and supports image export, but it must not contain reasoning that is otherwise absent from the markup.

## 5. Intelligence timeline

Use four dated events only. They explain why this is an Intelligence Brief without turning the page into a history of digital identity.

1. **26 February 2026:** HM Treasury and DSIT publish approved guidance on using digital identities with the MLRs.
2. **June 2026:** Trust framework 1.0 becomes final.
3. **20 August 2026:** OfDIA clarifies confidence selection and the separation of identity outcomes from additional attributes.
4. **2 September 2026:** Certification against framework 1.0 becomes live, alongside the continuing transition from gamma 0.4.

Do not infer that framework 1.0 is automatically suitable for every use case or that gamma 0.4 is automatically unsuitable.

## 6. Five locked control patterns

Each pattern appears once inline at its point of relevance and once in the closing grid. The two copies must be text-identical.

### Pattern 1: The Green Tick Halo

**Metaphor:** One successful check lights up the whole customer file.

**Risk:** A valid identity outcome is treated as evidence that the relationship is low risk and CDD is complete.

**Signal:** The case status changes to complete when the vendor returns a pass, although purpose, risk or enhanced measures remain unresolved.

**Response:** Write the Proof Boundary Record, then make a separate decision on wider CDD completeness.

### Pattern 2: The Brand-Level Shortcut

**Metaphor:** The provider's name replaces the service evidence.

**Risk:** Procurement or operations confirms a familiar provider but not the exact registered service, certified role or certificate that produced the result.

**Signal:** The file records only the vendor name or a generic statement that the provider is certified.

**Response:** Record and check the exact service, role, framework version, certificate status and relevant scope at the time of use.

### Pattern 3: Attribute Spillover

**Metaphor:** Every field in one response inherits the status of the identity result.

**Risk:** Address, PEP or sanctions outputs are assumed to be covered by identity-service certification because they appear in the same response.

**Signal:** The control record cannot map each output to a certified role, stated scope and source.

**Response:** Separate identity outcomes from attributes and screening, then evidence the status and scope of each output independently.

### Pattern 4: The Verified Director Mirage

**Metaphor:** Proof about one person is made to stand in for the company.

**Risk:** A director's successful identity check is treated as proof of the corporate customer, the director's authority, ownership, control or beneficial ownership.

**Signal:** One result is copied across several subjects or propositions in the CDD record.

**Response:** Keep the director's identity result, then verify the corporate customer, authority, ownership, control and beneficial owners as separate propositions.

### Pattern 5: The Frozen Pass

**Metaphor:** A dated result is treated as permanently current.

**Risk:** The firm retains the original pass but does not define what would make its evidential boundary stale.

**Signal:** The record has no service, certificate, customer, risk or behavioural change trigger.

**Response:** Add a change trigger and reassess when the recorded service scope, customer facts or risk context changes.

## 7. Worked decision 1: verified identity, unresolved relationship

**Facts:** An individual customer returns a valid result from a certified and registered service at an assurance level the firm selected for the initial risk. The declared business purpose is incomplete and the first funding pattern is inconsistent with the expected activity.

**Decision:** Is CDD complete?

**Option A, weak:** Complete CDD because the identity check passed.

**Option B, caution:** Reject the result and restart identity verification because the wider file is inconsistent.

**Option C, strongest:** Accept the identity result for the identity proposition, keep purpose, risk and any enhanced measures open, and record the boundary.

**Source:** The February guidance confines the relevant benefit to identity verification and says wider CDD remains with the firm. Regulation 28 separately addresses purpose and intended nature, risk-sensitive measures and ongoing monitoring.

**Application:** The identity evidence has not been displaced by the funding inconsistency. The inconsistency affects a different proposition: whether the stated purpose and risk assessment remain credible.

**Action:** Preserve the identity result. Record its subject, scope and assurance. Resolve the purpose and funding inconsistency, reassess risk and apply EDD if the facts require it. Do not mark the wider CDD file complete until those tasks are resolved.

**Counterfactual:** If coherent purpose evidence is obtained and subsequent activity matches it, the open relationship proposition may close. That change does not expand what the original identity result proved.

## 8. Worked decision 2: verified director, unresolved company

**Facts:** A director completes a registered digital identity check. The customer is a company, signing authority is unclear, ownership information is layered and a beneficial owner has not been independently established.

**Decision:** What can the firm conclude?

**Option A, weak:** Treat the company and beneficial owner as verified because the director passed.

**Option B, caution:** Treat the director's result as irrelevant because the customer is a company.

**Option C, strongest:** Use the result for the director's identity only, then separately establish the corporate customer, authority, ownership, control and beneficial ownership.

**Source:** The February guidance permits use for company directors. Regulation 28 separately addresses corporate particulars, ownership and control, beneficial owners and a person's authority to act.

**Application:** The result is relevant and bounded. It concerns one natural person. It does not establish every fact about the company or the person's relationship to it.

**Action:** Retain the director result in the correct subject record. Keep corporate identity, authority, ownership, control and beneficial ownership open until separately evidenced.

**Counterfactual:** If corporate particulars, signing authority, ownership, control and beneficial ownership are independently established, those open fields may close. They close because of that separate evidence, not because the director's earlier result changes scope.

## 9. Decision horizon

### Now

Inventory the digital verification services and outputs currently used. Match each to an exact register entry, role, certificate and framework version. Identify where a vendor pass currently closes more than the supported proposition.

### Next control cycle

Add the Proof Boundary Record to policy, procurement, onboarding configuration, case review and quality assurance. Define minimum assurance by risk rather than by provider brand. Test completed files for subject and proposition leakage.

### On change

Reassess when the service registration or certificate changes, the assurance no longer matches risk, customer facts or behaviour change, or new guidance changes the legal or supervisory boundary.

## 10. Interaction contract

1. Each scenario uses a semantic fieldset, three radio options, one strongest option, one caution option and one weak option.
2. Submission without a choice produces a polite live-region instruction.
3. Any choice opens the complete Source, Application and Action reasoning already present in the HTML.
4. The five-question knowledge check requires all questions before scoring and reports the total through a polite live region.
5. The closing Risk, Signal, Response grid is the only source for the PNG export.
6. The page emits only aggregate, consent-gated events for scenario completion, knowledge-check completion and card export.
7. No selected text, free text, rationale, name, account detail or other customer data enters telemetry.
8. With JavaScript disabled, all material analysis, scenarios, reasoning, patterns, FAQ answers and sources remain readable.

## 11. What Would Change Our Assessment

The static section must include at least these triggers:

1. HM Treasury or OfDIA amends the February guidance.
2. A relevant sector body updates approved MLR guidance.
3. The statutory register, trust framework or certification scheme changes a relevant role or field.
4. A service leaves the register, its certificate ceases to cover the service, or its role or framework version changes.
5. Regulation 28, 40 or 76 changes materially.
6. Independent review shows that a scenario verdict or statement about approved guidance, unregistered services or attribute scope is too broad.

## 12. Change control

The following are specification changes and require reopening this memo before implementation:

- removing or renaming a Proof Boundary Record field;
- allowing a successful identity outcome to imply low risk or wider CDD completion;
- treating the provider brand as a substitute for the exact service scope;
- merging the two worked decisions;
- introducing vendor rankings, a risk score or an assurance threshold not supported by the sources;
- changing the public format from Intelligence Brief;
- omitting the independent review gate.

Editorial refinement that preserves the model, evidence boundaries and decisions is not a specification change.
