# Digital Identity Is Not the Whole of CDD: source pack and qualification record

Compiled 5 October 2026 on `main` at `6f62fdcc0eb6a0298802213d01bedf21c3e9b73c`. Regulatory and temporal claims rechecked after independent review on 6 October 2026.

**Queue decision:** PASS for promotion to READY. This is approval to proceed with analytical design and drafting, not a publication-readiness decision.

**Verification owner:** Codex.

**Public format:** Intelligence Brief within the Default Knowledge Hub treatment.

**Scope:** United Kingdom. The brief concerns use of certified and registered digital verification services by persons subject to the Money Laundering Regulations 2017. Its central question is what an identity verification result establishes, about whom, at what assurance level, and which CDD duties remain with the regulated firm.

**Excluded from the central claim:** national digital identity policy generally, age assurance, right to work, right to rent, DBS checks, Companies House identity verification as a substitute for MLR CDD, vendor comparisons, and any claim that certification makes the firm's whole onboarding process compliant.

**Retrieval method:** Current GOV.UK pages, the live statutory DVS register and current legislation.gov.uk XML were read directly on 5 October 2026 and the material regulatory and temporal claims were rechecked on 6 October 2026. The current Regulation 28 XML identifies the revised text as valid from 30 June 2026 and modified on 3 July 2026. Search results and secondary commentary were used only for the originality comparison, not as authority for legal propositions.

**Status key:** VERIFIED means the primary text was read and supports the proposition. CAVEAT means the proposition is supportable only with the stated boundary. REVIEW means the final wording or scenario conclusion requires independent adversarial review under `CLAUDE.md` section 7.

## 1. Primary source pack

### S1. HM Treasury and DSIT, Using digital identities with the Money Laundering Regulations

- URL: https://www.gov.uk/government/publications/using-digital-identities-with-the-money-laundering-regulations/using-digital-identities-with-the-money-laundering-regulations
- Published: 26 February 2026.
- Status: VERIFIED. Primary government guidance. The page states that it is approved guidance for MLR compliance.
- Supports:
  - Certified services on the DVS register can be treated as reliable and independent sources with anti-impersonation assurance.
  - For customers who are individuals, a regulated entity may use a certified and registered service to verify the customer's identity for Regulation 28 purposes.
  - Certified and registered services may also be used to verify company directors.
  - A digital identity does not fulfil all CDD. The firm must still assess customer risk, apply EDD where appropriate, assess and where appropriate maintain information on purpose and intended nature, meet record-retention requirements, and remains ultimately liable for CDD failures.
  - A service that is not certified and not on the register cannot reliably be deemed suitable for MLR identity verification under this guidance.
- CAVEAT: Do not rewrite the final point as a statutory ban on all unregistered electronic verification. The guidance uses the narrower formulation above.
- REVIEW: Keep “fulfil Regulation 28 obligations” confined to the identity verification limb for an individual. It does not mean every obligation within Regulation 28 is fulfilled.

### S2. Money Laundering Regulations 2017, Regulation 28, current revised text

- URL: https://www.legislation.gov.uk/uksi/2017/692/regulation/28
- XML checked: https://www.legislation.gov.uk/uksi/2017/692/regulation/28/data.xml
- Status: VERIFIED. Primary legislation.
- Supports the residual-duty boundary:
  - Regulation 28(2) separately requires identification, verification, and assessment of the purpose and intended nature of the relationship or occasional transaction.
  - Regulation 28(3), 28(3A) and 28(4) address corporate particulars, ownership and control, and beneficial owners.
  - Regulation 28(9) says beneficial-owner requirements are not satisfied by relying solely on information delivered to the registrar.
  - Regulation 28(10) separately requires authority, identification and verification where a person purports to act for a customer.
  - Regulation 28(11) requires ongoing monitoring and keeping CDD information current.
  - Regulation 28(12) and 28(16) keep the extent of CDD risk-sensitive and demonstrable to the supervisor.
  - Regulation 28(18) defines verification by reference to documents or information from a reliable source independent of the person being verified.
  - Regulation 28(19) permits electronic identification where the process is secure from fraud and misuse and provides the assurance necessary to manage ML and TF risks effectively.
- REVIEW: The brief must distinguish identity of an individual director from verification of the corporate customer, the director's authority, beneficial ownership and the ownership and control structure.

### S3. Money Laundering Regulations 2017, Regulation 40

- URL: https://www.legislation.gov.uk/uksi/2017/692/regulation/40
- XML checked: https://www.legislation.gov.uk/uksi/2017/692/regulation/40/data.xml
- Status: VERIFIED. Primary legislation.
- Supports: the regulated firm must retain copies of documents and information obtained to satisfy CDD requirements, plus sufficient supporting transaction records. The normal period is five years from the specified transaction or relationship endpoint, subject to the detailed statutory conditions and deletion rule.
- CAVEAT: The guide should not imply that retaining a vendor pass result alone is necessarily enough to reconstruct the firm's CDD decision.

### S4. Money Laundering Regulations 2017, Regulation 76

- URL: https://www.legislation.gov.uk/uksi/2017/692/regulation/76
- XML checked: https://www.legislation.gov.uk/uksi/2017/692/regulation/76/data.xml
- Status: VERIFIED. Primary legislation.
- Supports: when deciding whether a relevant requirement was contravened, the designated supervisory authority must consider whether the person followed relevant FCA guidance or guidance issued by another supervisory authority or appropriate body and approved by the Treasury.
- REVIEW: Do not describe the February guidance as a safe harbour. Its precise enforcement significance must be reviewed before publication.

### S5. Data (Use and Access) Act 2025, Part 2

- URL: https://www.legislation.gov.uk/ukpga/2025/18/part/2
- XML checked: https://www.legislation.gov.uk/ukpga/2025/18/part/2/data.xml
- Status: VERIFIED. Primary legislation.
- Supports:
  - Section 28 requires the Secretary of State to publish and maintain the DVS trust framework and permits different rules, commencement and transitional treatment for different services.
  - Section 32 requires a public DVS register.
  - Section 33 ties registration to a certificate for specified services and requires the register to record the services for which a person is registered.
  - Sections 42 to 44 require register changes when a service ceases, a certificate no longer covers it, or supplementary-code coverage changes.
- Application: registration is service-specific and change-sensitive. A provider name by itself is not enough evidence that the service used, role performed or certificate relied on was within current registration.

### S6. Statutory digital verification services register

- URL: https://www.access-dvs-register.service.gov.uk/register/all-services
- Guidance: https://www.access-dvs-register.service.gov.uk/register/guidance
- Updates: https://www.access-dvs-register.service.gov.uk/register/update-logs
- Evidence checked: 6 October 2026. The register itself showed a last-updated date of 30 September 2026.
- Status: VERIFIED. Live statutory register.
- Supports:
  - Entries are for named services, not only providers.
  - Entries expose role types, trust-framework version, certificate issue and expiry dates, identity profiles where applicable, and supplementary codes.
  - The register separates Identity, Attribute, Orchestration, Holder and Component roles.
  - Current entries demonstrate that services under one provider can have materially different roles.
- CAVEAT: Do not hard-code the number of registered services or name a service as current without a dated register check. The update log shows frequent changes.

### S7. UK digital verification services trust framework 1.0 and certification scheme

- Trust framework: https://www.gov.uk/government/publications/uk-digital-verification-services-trust-framework-1-0
- Current versions: https://www.gov.uk/government/collections/uk-digital-verification-services-trust-framework
- Certification scheme: https://www.gov.uk/guidance/certification-scheme-for-the-uk-digital-identity-and-attributes-trust-framework
- Status: VERIFIED. Primary government framework and scheme.
- Supports:
  - Version 1.0 is the latest framework. The certification scheme table records scheme 1.0.1 as live from 2 September 2026. It also records Gamma scheme 0.4.4 as live from 1 July 2025 with an expiry date of 1 December 2028.
  - The framework is now focused on natural-person identities and attributes.
  - Identity outcomes use GPG 45 levels of confidence.
  - Certified service roles and exact service scope matter.
  - The framework expressly warns that a bank using a certified identity service for one part of onboarding must not represent the whole onboarding process as certified.
  - The register is a managed list of providers with specified certified services.
- CAVEAT: The existence of two live framework versions is temporal context, not evidence that one service is weak or unsuitable. Use the exact register entry and certificate that applied when the check was performed.

### S8. OfDIA clarification on DVS and the MLRs

- URL: https://enablingdigitalidentity.blog.gov.uk/2026/08/20/how-digital-verification-services-can-help-businesses-meet-their-obligations-under-the-money-laundering-regulations/
- Published: 20 August 2026.
- Status: VERIFIED. Official OfDIA clarification, not legislation.
- Supports:
  - The regulated firm selects the GPG 45 level of confidence commensurate with customer risk.
  - An identity outcome must be distinguished from additional attributes such as address information, PEP checks or sanctions screening.
  - Attribute coverage depends on the service's certified role and scope.
  - The MLR guidance relates specifically to identity verification, not to every additional attribute a vendor returns.
- REVIEW: The final brief must not imply that sanctions or PEP screening is certified merely because it appears in the same vendor response as a certified identity outcome.

### S9. FCA multi-firm CDD review

- URL: https://www.fca.org.uk/publications/good-and-poor-practice/firms-customer-due-diligence-processes-and-controls-our-findings
- Published: 8 April 2026.
- Status: VERIFIED. Primary regulator good-and-poor-practice publication.
- Supports the practitioner problem, not a new legal rule:
  - Most reviewed firms had documented identity-verification procedures, but few gave staff enough practical detail.
  - Separately, several firms distinguished standard CDD from EDD, while most tailored CDD to customer risk.
  - The FCA presented clear differentiation and risk-tailored CDD as examples of good practice.
  - Weaknesses included insufficient alternatives for customers without standard identity evidence, unclear review cycles and failure to follow procedures.
- CAVEAT: The review is evidence about observed practice and FCA expectations. Do not generalise its sample into a statistic about all regulated firms.

## 2. Settled and unresolved assessment

### Settled enough to teach

1. A certified and registered DVS may satisfy the individual customer identity verification limb described in the February guidance.
2. That outcome does not complete every CDD duty.
3. The exact registered service, its certified role and the assurance returned matter more than the vendor brand.
4. The regulated firm selects an assurance level appropriate to risk and remains responsible for the CDD conclusion.
5. Identity verification, attribute checks and wider customer-risk decisions are different evidential propositions.

### Material matters to keep qualified

1. Unregistered electronic verification is not described as universally unlawful. The February guidance says it cannot reliably be deemed suitable under that guidance.
2. A digital check on an individual director is not proof of the corporate customer's identity, ownership, control, beneficial owners or the director's authority for the transaction.
3. Certification of an identity service does not certify a relying firm's whole onboarding process.
4. Attribute outputs may be inside or outside certified scope depending on the service and role.
5. The guidance is not a transfer of liability and must not be presented as a safe harbour.
6. Register status, certificate scope, framework version and service configuration can change.

## 3. Originality check

### Existing FinCrimeRadar coverage

- `kyc-onboarding-dilemma.html` addresses risk-based onboarding decisions and identity evidence gaps.
- `synthetic-identity-device-network-guide.html` addresses fabricated identities and device-network evidence.
- `deepfake-onboarding-guide.html` addresses suspected synthetic-media verification sessions and secondary verification.
- `perpetual-kyc-framework-guide.html` addresses ongoing and event-driven review.
- None provides a service-scope and proposition-level method for deciding what a successful certified digital identity result does and does not establish.

### External overlap

The February government guidance, Law Society material and legal-sector commentary already state that digital identity verification does not discharge all CDD. A publication that only repeats this point would fail the originality gate.

### FinCrimeRadar differentiator: the Proof Boundary Record

The brief should teach one operational record with six fields:

1. **Subject:** exactly who was checked, such as the individual customer, director, representative or beneficial owner.
2. **Proposition:** exactly what the result establishes, such as identity at a stated confidence level, not low risk or legitimate activity.
3. **Service scope:** the named registered service, certified role, framework version, certificate status and any relevant attribute scope at the time of the check.
4. **Assurance:** the returned GPG 45 level or profile and why it was commensurate with the assessed risk.
5. **Residual duties:** purpose and intended nature, authority, corporate identity, ownership and control, beneficial ownership, EDD, ongoing monitoring and record keeping that remain open.
6. **Change trigger:** the customer, service, certificate, risk or behavioural change that requires reassessment.

This converts a vendor pass into an auditable evidence boundary. It is materially different from a regulator summary, a vendor-selection checklist and FinCrimeRadar's existing identity-fraud publications.

**Originality verdict:** PASS only with the Proof Boundary Record as the central analytical model. Without it, the topic reverts to RESEARCH.

## 4. Required worked decisions

### Scenario 1: the verified individual with an unexplained relationship

An individual customer returns a valid registered-service identity result at an assurance level the firm has selected for the initial risk. The declared business purpose and expected account activity are incomplete or inconsistent with the first funding pattern.

Decision point: whether the identity result is enough to complete CDD, whether to reject the result, or whether to accept the identity proposition while keeping purpose, risk and any enhanced measures open.

Teaching distinction: the identity proposition may be established while the relationship proposition remains unresolved.

### Scenario 2: the verified director of an unresolved company

A director completes a registered digital identity check. The customer is a company, the signing authority is unclear, ownership information is layered and the beneficial owner has not been independently established.

Decision point: whether the director's identity result completes company CDD, is irrelevant, or is valid evidence for one subject while corporate identity, authority, ownership, control and beneficial ownership remain separate tasks.

Teaching distinction: verifying a natural person associated with a company is not the same as verifying the corporate customer or the relationship between them.

Both scenarios require graded options and full Source, Application and Action reasoning. The second scenario must not become a general Companies House identity-verification guide.

## 5. Intelligence Brief fit

The format is justified because the position changed during 2026:

- February: HM Treasury and DSIT published the MLR guidance.
- June: trust framework 1.0 became final.
- August: OfDIA clarified confidence levels and the separation of identity outcomes from attributes.
- September: certification scheme 1.0.1 became live on 2 September 2026, while Gamma scheme 0.4.4 remained live during transition.

The brief must include a dated intelligence assessment, evidence checked date, settled versus unresolved treatment, decision horizon, reassessment triggers, and a static What Would Change Our Assessment section.

## 6. Reassessment triggers

Recheck before publication and after any of these events:

1. HM Treasury or OfDIA amends the February MLR guidance.
2. OfDIA changes the trust framework, certification scheme or register fields.
3. A relevant sector body updates its approved MLR guidance.
4. The selected examples change registration, role, certificate or framework version.
5. Primary legislation changes the relevant Regulation 28 or Regulation 40 duties.

## 7. Claims requiring independent adversarial review

1. The boundary between satisfying individual identity verification and satisfying Regulation 28 as a whole.
2. The treatment of directors, representatives, beneficial owners and corporate customers as distinct subjects.
3. Any explanation of the legal or supervisory weight of the February approved guidance.
4. Any conclusion about unregistered electronic verification.
5. Any inference from a service's certified role to the status of PEP, sanctions, address or other attribute outputs.
6. Every scenario verdict and feedback string that states whether a CDD duty is complete or remains open.

## 8. Queue-gate outcome

- **Verification owner:** Codex.
- **Primary sources and repository evidence checked:** 6 October 2026. Sources S1 to S9 and the repository overlap set above.
- **Review date:** 6 October 2026.
- **Verification outcome:** PASS. The primary evidence supports a narrow Intelligence Brief, the Proof Boundary Record clears the originality gate, and two materially distinct practitioner decisions are available. Legal interpretations and scenario verdicts remain subject to independent adversarial review before publication.
