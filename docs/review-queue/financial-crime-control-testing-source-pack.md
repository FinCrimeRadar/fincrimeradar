# Financial Crime Control Testing: A Control Exists, But Does It Work?, source pack

Status: source and originality gate passed on 1 November 2026. Proposed format: Framework using the Default Knowledge Hub treatment. This pack supports specification and build, not publication approval. Every proposition below was checked against the named source on the evidence date.

## 1. How the sources were read

| Source type | Method | Limits |
| --- | --- | --- |
| Money Laundering Regulations 2017 | Current `legislation.gov.uk` XML for regulations 19 and 21 was retrieved and read on 1 November 2026. | The legislation site can show unapplied changes separately. This guide must use the revised text actually in force and must not present pending changes as operative. |
| FCA Handbook rules and guidance | Current Handbook pages were checked for SYSC 3.2.6 and FCG 1.1. The official FCG 2.2 PDF was checked for the policy, audit and oversight examples. | SYSC scope varies by firm. FCG is general guidance, not binding, and is not a complete statement of law. |
| FCA good and poor practice | The full FCA pages were read for the 2025 risk assessment review, the 2026 CDD review and the 2026 sanctions review. | These are findings and examples. The FCA states that good practice can go beyond minimum requirements. They are not universal test specifications. |
| GOV.UK Fraud Control Testing Framework | The full HTML guidance was read on 1 November 2026. | It is principles-based recommended practice for public bodies. It is not an FCA rule, an MLR requirement or a private-sector AML testing standard. |

## 2. Source register

| Ref | Source | Version or date | Main use |
| --- | --- | --- | --- |
| S1 | Money Laundering, Terrorist Financing and Transfer of Funds (Information on the Payer) Regulations 2017, regulation 19. https://www.legislation.gov.uk/uksi/2017/692/regulation/19 | Latest revised text retrieved 1 November 2026 | Policies, controls and procedures, review, records and senior approval |
| S2 | Same instrument, regulation 21. https://www.legislation.gov.uk/uksi/2017/692/regulation/21 | Latest revised text retrieved 1 November 2026 | Conditional independent audit duty and its responsibilities |
| S3 | FCA Handbook, SYSC 3.2.6. https://handbook.fca.org.uk/handbook/sysc3/sysc3s2 | Current page checked 1 November 2026 | Effective systems and controls and regular adequacy assessment |
| S4 | FCA Handbook, FCG 1.1, What is the FCG? https://handbook.fca.org.uk/handbook/fcg1/fcg1s1 | Last updated 3 June 2025 | Status and limits of FCG guidance |
| S5 | FCA Handbook, FCG 2.2, Financial crime systems and controls. https://www.handbook.fca.org.uk/handbook/FCG/2/2.pdf | Provision dates checked in the official PDF; FCG 2.2.5 and 2.2.7 dated 13 December 2018 | Independent monitoring, consistent application and routine testing |
| S6 | FCA, Risk assessment processes and controls in firms: our findings. https://www.fca.org.uk/publications/good-and-poor-practice/risk-assessment-processes-and-controls-firms-our-findings | Published and last updated 11 November 2025 | Evidence for effectiveness conclusions and testing after change |
| S7 | FCA, Firms' customer due diligence processes and controls: our findings. https://www.fca.org.uk/publications/good-and-poor-practice/firms-customer-due-diligence-processes-and-controls-our-findings | Published and last updated 8 April 2026 | Sample monitoring, assurance independence, audit trails and remediation |
| S8 | FCA, Sanctions systems and controls in our firms: our findings. https://www.fca.org.uk/publications/good-and-poor-practice/sanctions-systems-and-controls-our-firms-our-findings | Published and last updated 28 May 2026 | Configuration, data, assurance testing, lookbacks and control failure examples |
| S9 | GOV.UK, Fraud Control Testing Framework FCTF-01. https://www.gov.uk/government/publications/international-public-sector-fraud-forum-guidance/fraud-control-testing-framework-fctf-01-html | Updated 15 June 2026 | Risk-based test selection, testing methods and conclusion discipline for public-sector fraud controls |

## 3. Proposition register

Short quotations are used only where the wording matters. The final page must distinguish Established, Guidance, Public-sector practice and FinCrimeRadar assessment.

### A. Statutory and Handbook requirements

| ID | Proposition | Locator | Scope and limits | Evidence state |
| --- | --- | --- | --- | --- |
| P01 | A relevant person must establish and maintain policies, controls and procedures to mitigate and manage effectively the money laundering and terrorist financing risks identified under regulation 18(1). | S1, regulation 19(1)(a) | Applies to relevant persons within the MLR scope. It does not prescribe a testing method. | Established |
| P02 | Those policies, controls and procedures must be regularly reviewed and updated, with written records of the controls, changes and internal communication steps. | S1, regulation 19(1)(b) and (c) | The provision does not prescribe a universal review interval. | Established |
| P03 | The policies, controls and procedures must be proportionate to the size and nature of the business, approved by senior management, and include risk management, internal controls, CDD, reliance and record keeping, and compliance monitoring and internal communication. | S1, regulation 19(2) and (3) | Do not turn the list into a claim that every control has identical testing depth. | Established |
| P04 | Where appropriate having regard to the size and nature of the business, a relevant person must establish an independent audit function responsible for examining and evaluating the adequacy and effectiveness of its MLR policies, controls and procedures, making recommendations and monitoring compliance with them. | S2, regulation 21(1)(c) | Regulation 21(1) is conditional. Regulation 21(6) disapplies paragraphs (1) and (3) where the relevant person is an individual who neither employs nor acts in association with another person. | Established |
| P05 | In deciding what is appropriate under regulation 21, the relevant person must take account of its regulation 18 and 18A risk assessments and may take account of qualifying guidance. | S2, regulation 21(10) | This supports risk-based scope. It does not prescribe a sample size. | Established |
| P06 | The MLR provisions read do not prescribe a universal control test frequency, sample size, pass threshold, rating scale or evidence taxonomy. | Absence from S1 and S2 | A statement about these provisions as read, not about every possible legal or professional standard. | Established as an absence |
| P10 | A firm within SYSC 3.2.6 must take reasonable care to establish and maintain effective financial crime systems and controls. Its money laundering systems and controls must identify, assess, monitor and manage risk and be comprehensive and proportionate. | S3, SYSC 3.2.6R and 3.2.6A R | Handbook applicability must be checked for the firm. | Established, FCA rule |
| P11 | Such a firm must carry out regular assessments of the adequacy of those systems and controls. | S3, SYSC 3.2.6C R | The rule says regular, but does not set one interval for every control. | Established, FCA rule |
| P12 | FCG says internal audit or another independent party monitoring the effectiveness of policies, procedures, systems and controls is good practice. Failure to check whether policies and procedures are applied consistently and effectively is poor practice. | S5, FCG 2.2.5 | FCG is general guidance. | Guidance |
| P13 | FCG says internal audit and compliance routinely testing defences against financial crime is good practice. It also asks how a firm ensures that review of control effectiveness is comprehensive and how remediation has progressed. | S5, FCG 2.2.7 | FCG does not specify one test programme. | Guidance |
| P14 | FCG is general guidance under section 139B FSMA, is not binding and is not a standalone statement of all requirements. Firms can comply in other ways. | S4, FCG 1.1.7, 1.1.8 and 1.1.11 | Any FCG example must remain labelled guidance. | Guidance status |

### B. FCA risk assessment findings

| ID | Proposition | Locator | Scope and limits | Evidence state |
| --- | --- | --- | --- | --- |
| P20 | The FCA saw firms conclude that controls were effective or mature without appropriate evidence. | S6, section 2.1, Lack of evidence | A finding from a multi-firm review, not a new rule. | Guidance, observed poor practice |
| P21 | The FCA says a business-wide risk assessment should feed into controls testing and the firm's wider risk-based approach. | S6, section 2.2, Risk assessments feed into firm's wider work | An example of good practice. | Guidance |
| P22 | The FCA saw rapid expansion without firms first considering and ensuring that controls remained appropriate and effective. | S6, section 2.2, Rapid expansion | The item is not a universal change-control specification. | Guidance, observed poor practice |
| P23 | The FCA saw limited or no testing and review of risk assessment processes when firms made enhancements, upgrades or introduced automation. | S6, section 2.3, Lack of testing | The wording concerns risk assessment processes. Reading it across to every financial crime control would be analysis, not a source statement. | Guidance, observed poor practice |

### C. FCA CDD findings

| ID | Proposition | Locator | Scope and limits | Evidence state |
| --- | --- | --- | --- | --- |
| P30 | The FCA assessed CDD controls using a questionnaire, policy and procedure review, customer file review and staff interviews. | S7, What we looked at | This describes the FCA's review method. It is not a mandatory firm testing method. | Guidance, methodology fact |
| P31 | The FCA observed sample-based compliance monitoring and proportionate review cycles used to help keep CDD processes effective and current. | S7, Compliance monitoring and audit | The FCA gives no universal sample size or review cycle. | Guidance, observed practice |
| P32 | Stronger firms used independent third-line testing across onboarding and due diligence, documented findings and acted on them. | S7, Compliance monitoring and audit | Independence and follow-through are observed strengths, not a statement that every test must be third line. | Guidance, observed practice |
| P33 | The FCA said the same staff onboarding customers and conducting assurance raised questions about impartiality and effectiveness. | S7, Compliance monitoring and audit | This is a finding about the arrangement reviewed. | Guidance, observed concern |
| P34 | Poor practices included insufficient detail on quality control, no independent CDD or EDD review, and no version control capable of demonstrating the audit trail of review and change. | S7, examples of poor practice | Applies to CDD findings. | Guidance, observed poor practice |

### D. FCA sanctions findings

| ID | Proposition | Locator | Scope and limits | Evidence state |
| --- | --- | --- | --- | --- |
| P40 | The FCA says sanctions screening systems and processes should be proportionate to risk, appropriately calibrated and regularly tested and reviewed. | S8, section 6.6 | FCA supervisory expectation and guidance, not a statutory testing formula. | Guidance |
| P41 | Stronger screening frameworks defined scope, frequency, escalation and governance, while poor practice included policies not embedded in daily work and historic vendor settings used without reassessment or oversight. | S8, section 6.7 | Specific to sanctions screening. | Guidance, observed practice |
| P42 | The FCA found errors, omissions and delays in list data and transfers between systems. A legacy integration failure left transactions unscreened and was not found by routine monitoring. | S8, section 6.8 and case study | This shows why policy and system existence do not prove deployment or operation. | Guidance, observed case study |
| P43 | Effective assurance practices included periodic calibration and quality assurance, retesting after list or matching-logic changes and root cause analysis after mismatches. The FCA also saw limited vendor challenge and insufficient internal testing. | S8, section 6.9 | Specific to sanctions screening. | Guidance, observed practice |
| P44 | FCA testing considered exact names, name variants and the way systems ingest, transform and interpret list data. The findings included problems with titles, one-word names, digits and long names. | S8, section 6.9 | The published percentages describe that testing programme and must not become universal pass thresholds. | Guidance, observed test coverage |
| P45 | Good practice included validation or periodic testing after material list or system changes, periodic testing and quality assurance of alert investigations, stress tests and thematic lookbacks. | S8, sections 6.9 to 6.11 | The examples are domain-specific and risk-based. | Guidance |
| P46 | The absence of identified true matches or reported breaches does not, by itself, demonstrate that a screening control is effective. | FinCrimeRadar synthesis of S8 sections 6.7 to 6.9 | S8 reports many firms identifying no true matches while also recording configuration, data and testing weaknesses. The FCA does not state this proposition in these exact words. | FinCrimeRadar assessment |

### E. GOV.UK public-sector fraud framework

| ID | Proposition | Locator | Scope and limits | Evidence state |
| --- | --- | --- | --- | --- |
| P50 | The framework recommends focusing testing on high-risk areas and critical controls rather than attempting shallow testing of every control. | S9, Choosing what areas to focus on | Recommended practice for public bodies. | Public-sector practice |
| P51 | It describes desktop review, interviews, walkthroughs, sample analysis, data analysis, technical testing and controlled scenario-based testing as different methods. | S9, Testing methods | Methods must be selected for the objective and used within lawful, authorised scope. | Public-sector practice |
| P52 | It says testing must go beyond confirming that controls exist and processes are followed, particularly where an adversary may find ways around a control. | S9, Testing methods | Fraud-focused public-sector context. | Public-sector practice |
| P53 | It uses Effective, Partially Effective and Ineffective ratings and links each to action, while allowing tolerance to depend on a control's purpose and criticality. | S9, Rating control effectiveness | This rating scheme is not an FCA or MLR requirement. | Public-sector practice |
| P54 | It separates control effectiveness from residual risk and treats test results as an input to residual-risk assessment. | S9, Assessing and measuring residual risk | Do not state that a control rating automatically determines residual risk. | Public-sector practice |

## 4. FinCrimeRadar analytical model

The sources require or encourage effective controls, evidence, testing and independent challenge, but they do not provide one cross-control method for reaching an effectiveness conclusion. The guide therefore uses a clearly labelled FinCrimeRadar model.

### The Control Proof Chain

`Risk -> Control objective -> Design -> Deployment -> Operation -> Exceptions -> Remediation and retest`

The central judgement uses three proofs:

1. **Design proof:** if performed as specified, could the control prevent, detect or respond to the stated risk at the right point?
2. **Deployment proof:** is the control actually embedded across the intended population, systems, data, people, vendors and escalation routes?
3. **Operating proof:** over the test period, did the control perform consistently, produce usable evidence, identify and handle exceptions, and trigger remediation where needed?

The labels design, deployment and operation are FinCrimeRadar's synthesis. No source read imposes this exact three-part taxonomy.

### Conclusion states

The guide uses four conclusions:

- **Effective:** all three proofs are supported for the stated scope and period, with no material weakness undermining the objective.
- **Partially effective:** the control provides material risk reduction, but a bounded weakness, coverage gap or inconsistent operation remains.
- **Ineffective:** a weakness defeats or materially undermines the stated control objective.
- **Not evidenced:** the test cannot support an effectiveness conclusion because the population, period, evidence or method is insufficient.

The first three adapt the public-sector framework in S9. Not evidenced is a FinCrimeRadar addition. It prevents missing evidence from being treated as either a pass or a failure without analysis.

## 5. Claims the guide must not make

1. That regulation 21 requires an independent audit function for every relevant person regardless of size, nature or the regulation 21(6) exception.
2. That FCA good practice examples are binding rules or legal minimums.
3. That the GOV.UK public-sector framework governs private-sector FCA firms.
4. That one sample size, test frequency, pass rate or rating threshold is prescribed across controls.
5. That a passed sample proves the population was complete or the control operated outside the sampled items.
6. That no incidents, breaches, true matches or complaints proves control effectiveness.
7. That design effectiveness alone proves implementation or operation.
8. That an ineffective control automatically establishes a regulatory breach, suspicion, loss or customer harm.
9. That a control rating alone establishes residual risk.
10. That vendor assurance replaces the firm's understanding, testing or oversight of its own configuration, data and use.

## 6. Open limits

1. No source read sets a universal sample methodology for private-sector UK financial crime control testing.
2. No source read defines an acceptable control failure rate across CDD, transaction monitoring, sanctions, fraud and SAR controls.
3. The boundary between second-line monitoring and independent audit depends on firm structure, regulatory scope and the purpose of the work.
4. The guide can teach test design and conclusion discipline, but cannot certify a firm's control environment or replace professional audit judgement.
5. Any pressure or covert testing must remain synthetic, authorised, lawful, reversible and isolated from live customer harm. The proposed publication will not provide bypass instructions for real controls.

## 7. Promotion outcome

Research verification owner: Codex.

Evidence checked: S1 to S9 above, plus repository-wide title and content searches for overlap.

Review date: 1 November 2026.

Outcome: **PASS for specification and build. NOT PASSED for publication.** The topic has a current primary-source base and a distinct practitioner problem. Release remains subject to implementation, ledger reconciliation, automated checks, a real pull request, regulatory claim review, grading review and independent adversarial release review.
