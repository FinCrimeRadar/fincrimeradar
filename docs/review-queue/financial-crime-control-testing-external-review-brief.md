# Financial Crime Control Testing, external review brief

For Pratik's manual ChatGPT or Codex adversarial review outside the Claude Code implementation session, after the page is built and before merge. This is a CLAUDE.md section 7 regulatory review and section 15 grading review. `/code-review` does not replace it.

Proposed page: `financial-crime-control-testing-framework.html`.

Evidence date: 1 November 2026.

Source pack: `financial-crime-control-testing-source-pack.md`.

Design memo: `financial-crime-control-testing-design-memo.md`.

## 1. Primary sources to reopen independently

1. https://www.legislation.gov.uk/uksi/2017/692/regulation/19
2. https://www.legislation.gov.uk/uksi/2017/692/regulation/21
3. https://handbook.fca.org.uk/handbook/sysc3/sysc3s2
4. https://handbook.fca.org.uk/handbook/fcg1/fcg1s1
5. https://www.handbook.fca.org.uk/handbook/FCG/2/2.pdf
6. https://www.fca.org.uk/publications/good-and-poor-practice/risk-assessment-processes-and-controls-firms-our-findings
7. https://www.fca.org.uk/publications/good-and-poor-practice/firms-customer-due-diligence-processes-and-controls-our-findings
8. https://www.fca.org.uk/publications/good-and-poor-practice/sanctions-systems-and-controls-our-firms-our-findings
9. https://www.gov.uk/government/publications/international-public-sector-fraud-forum-guidance/fraud-control-testing-framework-fctf-01-html

Do not rely on the source-pack summaries for the independent check. Confirm the live wording, scope, status and current version.

## 2. Regulatory and source-status checks

For each row return Confirmed, Confirmed with edit, or Rejected.

| ID | Claim to test | Source-pack basis | Specific risk |
| --- | --- | --- | --- |
| A1 | Regulation 19 requires relevant persons in scope to establish and maintain proportionate, senior-management-approved policies, controls and procedures, review and update them, and keep the stated records. | P01 to P03 | Do not omit conditions or turn all listed control areas into identical testing duties. |
| A2 | Regulation 21(1)(c) requires the independent audit function only where appropriate having regard to size and nature, with the three stated responsibilities. | P04 and P05 | Confirm the opening condition, regulation 21(6) exception and regulation 21(10) factors. |
| A3 | Regulations 19 and 21, as read, prescribe no universal test frequency, sample size, pass threshold or rating scale. | P06 | This is a negative claim limited to the provisions read. |
| A4 | SYSC 3.2.6 requires covered firms to maintain effective, comprehensive and proportionate systems and controls and conduct regular adequacy assessments. | P10 and P11 | Confirm applicability is not generalised to every reader. |
| A5 | FCG is non-binding general guidance and not a complete statement of requirements. | P14 | Every FCG example on the page must retain that status. |
| A6 | The 2025 FCA findings identify unsupported conclusions that controls were effective or mature and limited testing after changes as poor practice. | P20 to P23 | Keep the exact subject and scope of each finding. |
| A7 | The 2026 CDD findings describe sample monitoring, independent testing, action on findings and the independence concern. | P30 to P34 | Do not convert observed stronger practice into a rule for every test. |
| A8 | The 2026 sanctions findings support the stated examples on data lineage, configuration, testing, vendor challenge, variants and lookbacks. | P40 to P45 | Keep sanctions-specific findings within their domain. |
| A9 | The GOV.UK framework is recommended public-sector practice and not an FCA or MLR standard. | P50 to P54 | The page must not blur public-body and private-firm scope. |

## 3. FinCrimeRadar assessments

Confirm that each appears as analysis, not authority wording:

1. The Control Proof Chain.
2. The three proofs: design, deployment and operation.
3. The claim that absence of incidents or true matches is not, by itself, proof of effectiveness.
4. The four conclusion states and the added Not evidenced state.
5. The conclusion-record fields.
6. The scenario decisions, interim protection and remediation actions.
7. The separation of implementation closure from effectiveness validation.

Reject any wording that says a regulator requires this exact model, taxonomy, conclusion scale or sample approach.

## 4. Scenario grading review

### Scenario 1, the clean CDD sample

Check whether the known population exclusion justifies grading the control Ineffective for the stated population and period. Challenge whether Partially effective could be a defensible competing answer on the facts. If it could, the scenario facts must be tightened before release rather than relying on explanatory prose to rescue the grade.

### Scenario 2, the vendor screening assurance

Check whether known unapproved exclusions of one-word and long names justify Ineffective for the stated objective. Challenge whether Not evidenced is also defensible. The intended distinction is that incomplete testing creates uncertainty, but the known exclusions are affirmative evidence of a material coverage failure.

For both scenarios:

1. Confirm one option is clearly best.
2. Confirm no distractor is legally or operationally equivalent to the best answer.
3. Confirm Source, Application and Action remain distinct.
4. Confirm the counterfactual changes a decision-determining fact.
5. Confirm all figures and entities are visibly illustrative.

## 5. Implementation and release checks

1. Every load-bearing claim has a matching ledger record and precise source target.
2. All material reasoning is present in initial HTML and readable without JavaScript.
3. Scenario option grades in HTML, JavaScript and tests match.
4. The page does not expose control-bypass instructions or suggest testing against live customer data without authority.
5. The two scenarios are materially distinct.
6. Mobile, keyboard, focus, zoom, reduced-motion and overflow checks cover the actual interactions.
7. Knowledge Hub count, sitemap, content relations, metadata and social card match the exact release revision.
8. The diff contains no unrelated files from the dirty primary checkout.

## 6. Requested review output

Return:

1. A1 to A9 verdicts.
2. Any FinCrimeRadar assessment that reads as a source statement.
3. Any scenario grade that should change, with the exact reason.
4. Any release-blocking accessibility, test, source, ledger, metadata or scope defect.
5. A final PASS or HOLD. PASS means no unresolved material finding remains. It does not authorise merge or publication.

## 7. Independent review result, 1 November 2026

Reviewer: Codex, independently of the Claude Code implementation session.

The nine primary sources listed in section 1 were reopened from their official publishers. Regulations 19 and 21 were checked against the current revised XML on legislation.gov.uk. The FCA Handbook provisions and FCA findings were checked against the current Handbook and FCA pages. The GOV.UK framework was checked against the current HTML publication.

### A1 to A9 verdicts

| ID | Verdict | Review note |
| --- | --- | --- |
| A1 | Confirmed | Regulation 19 supports the page's account of establishment, maintenance, regular review, written records, proportionality, senior management approval and the listed control areas. The page does not turn those areas into identical testing duties. |
| A2 | Confirmed | Regulation 21 keeps the size and nature condition, the three audit responsibilities, the sole-individual exception in paragraph (6), and the risk assessment and guidance factors in paragraph (10). |
| A3 | Confirmed | Neither regulation 19 nor regulation 21 supplies a universal test frequency, sample size, pass threshold, rating scale or evidence taxonomy. The page limits this negative claim to those provisions as read. |
| A4 | Confirmed | SYSC 3.2.6R, 3.2.6A R and 3.2.6C R support the systems, controls and regular adequacy-assessment claims. The page expressly limits them to firms within scope. |
| A5 | Confirmed | FCG 1.1.7, 1.1.8 and 1.1.11 support the description of FCG as non-binding general guidance and not a complete statement of requirements. FCG examples remain labelled as guidance. |
| A6 | Confirmed | The 2025 FCA findings support the statements about effectiveness or maturity conclusions made without appropriate evidence and limited testing after changes. The page keeps the risk-assessment-process scope where it matters. |
| A7 | Confirmed | The 2026 CDD findings support the statements on sample monitoring, proportionate cycles, independent testing, action on findings and the independence concern. The page presents them as observed practice, not universal rules. |
| A8 | Confirmed | The 2026 sanctions findings support the examples on data lineage, configuration, exclusions, vendor challenge, variant handling, assurance testing and lookbacks. The page keeps those findings within sanctions screening or labels any wider use as application. |
| A9 | Confirmed | The GOV.UK framework is expressly for public bodies and describes recommended best practice. The page states that it is not an FCA rule, MLR requirement or private-sector AML testing standard. |

### FinCrimeRadar assessments

No analytical model reads as regulator wording. The Control Proof Chain, three proofs, absence-of-incidents inference, four conclusion states, Not evidenced addition, conclusion record, scenario actions and implementation-versus-validation distinction are labelled as FinCrimeRadar assessment or design. No regulator is said to require the taxonomy, scale or sample approach.

### Scenario grading

Scenario 1 remains Ineffective as the only best-supported answer. The stated objective covers every high-risk customer, while reconciliation establishes that eleven high-risk customers are overdue and excluded from the control. Partially effective is not equally defensible because the population denominator and boundary of the weakness are unknown. The counterfactual changes those decision-determining facts.

Scenario 2 remains Ineffective as the only best-supported answer. Known, unapproved exclusions remove names covered by the stated objective and no compensating control exists. Not evidenced remains incomplete because testing uncertainty does not displace affirmative evidence of a material coverage failure. The counterfactual adds approved exclusions and a tested compensating control, which changes the decision.

Both scenarios keep Source, Application and Action separate, label their figures and entities as illustrative, and use counterfactuals that change a decision-determining fact.

### Release-blocking defects

None found in the regulatory wording, source status, analytical labelling, scenario grading, ledger mapping, progressive enhancement, accessibility contract, metadata or changed-file scope. Static, browser, ledger, reading-time and diff checks remain the implementation evidence and are not replaced by this review.

### Final verdict

PASS. No unresolved material finding remains from this independent regulatory and grading review. This verdict does not authorise merge, deployment or publication.
