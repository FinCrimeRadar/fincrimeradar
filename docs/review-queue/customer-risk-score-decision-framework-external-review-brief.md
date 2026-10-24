# Customer Risk Scores: What the Number Cannot Decide, external review brief

For Pratik's manual ChatGPT or Codex adversarial review, outside Claude Code, before merge. This is a CLAUDE.md section 7 review (regulatory scope, statutory triggers, what an authority legally established) and a section 15 review (graded scenario options and a scored knowledge check are grading logic). `/code-review` does not replace it.

Page: `customer-risk-score-decision-framework.html`. Evidence date: 24 October 2026. Source pack: `customer-risk-score-decision-framework-source-pack.md`. Proposition IDs below (P01 and so on) refer to that pack. Ledger claim IDs begin `customer-risk-score-decision-framework.`.

## 1. How to review

Open each primary source yourself and do not rely on the retrieval notes in the source pack. The statutory and FCA web pages were retrieved in the drafting session through a web-fetch helper, not read in a browser, so a direct read is the independent check. For FCG 3.2.3, the good practice and poor practice columns could not be recovered from plain text. They were attributed by parsing the page's table markup, so please confirm the attribution by eye on the Handbook page.

Primary sources:

1. https://www.legislation.gov.uk/uksi/2017/692/regulation/18
2. https://www.legislation.gov.uk/uksi/2017/692/regulation/28
3. https://www.legislation.gov.uk/uksi/2017/692/regulation/33 (added to the six named sources, see the source pack section 6)
4. https://www.fca.org.uk/publications/good-and-poor-practice/risk-assessment-processes-and-controls-firms-our-findings
5. https://www.fca.org.uk/publication/corporate/money-laundering-through-markets-review-january-2025.pdf (Chapter 8 pages 26 to 28, Case Study 17 page 28, paras 6.2 to 6.3 page 22, para 9.9 page 30)
6. https://handbook.fca.org.uk/handbook/fcg2/fcg2s2 (FCG 2.2.4)
7. https://handbook.fca.org.uk/handbook/fcg3/fcg3s2 (FCG 3.2.3)
8. https://handbook.fca.org.uk/handbook/fcg1/fcg1s1 (FCG 1.1, status)

## 2. Claims requiring review, by risk

### A. Statutory scope and trigger claims (highest risk)

| # | Claim as made on the page | Location | Source | What to check |
| --- | --- | --- | --- | --- |
| A1 | None of regulations 18, 28 or 33, as read, prescribes a scoring method, a weighting scheme or a number of rating bands. | `#law`, FAQ 1 | P05, P10, P15 | A statement about the text. Confirm nothing in these regulations (including unapplied amendments by SI 2026/621 reg 20 and reg 36(b), shown as "yet to be applied") alters that. |
| A2 | Regulation 18 is the business-wide risk assessment; the customer risk assessment enters through regulation 28(12) and (13). | `#question`, `#law` | P01, P07, P08 | Is it accurate to say reg 28(12)(a)(ii) and (13) are the customer-level assessment, and that reg 18 is business-level only? Is that how the FCA uses the terms in S4 and S5 para 8.1? |
| A3 | Reg 28(12): the ways of complying with CDD, and the extent of the measures, must reflect the reg 18(1) assessment and the firm's assessment of the level of risk in the particular case, and may differ from case to case. | `#law`, Scenarios, Q5 | P07 | Wording and structure (limb (a)(i), (a)(ii), (b)). |
| A4 | Reg 28(13): case-level factors include the three listed, and the list is open ("among other things"). | `#law`, `#inside-number` | P08 | Confirm the three factors and the open wording. |
| A5 | Reg 28(16): the firm must be able to demonstrate to its supervisory authority that the extent of its measures is appropriate in view of the risks, including those identified by the reg 18(1) assessment and by the supervisory authority. Reg 28(17) disapplies (16) for the National Savings Bank and the Director of Savings. | `#law`, Scenario 1 record | P09 | Structure and the exclusion. The guide's inference (that "the model rated this customer medium" is not a demonstration) is FinCrimeRadar assessment, not statutory text. |
| A6 | Reg 28(11): ongoing monitoring includes scrutiny of transactions consistent with the firm's knowledge of the customer, business and risk profile, and reviews of existing records keeping CDD information up to date. No frequency is stated. | Figure 3, `#change` | P06 | Confirm no frequency anywhere in reg 28 or reg 18. |
| A7 | Reg 18(4): an up-to-date written record of the steps taken, unless the supervisory authority notifies in writing that none is required. | `#change` | P04 | Wording. The guide deliberately avoids the phrase "if the supervisory authority so requires", which is not in reg 18. |
| A8 | Reg 33(1)(a) and (g) depend on the firm's assessment. Reg 33(1)(b), (c), (d), (e) and (f) turn on facts, not on a rating. The page lists the fact-based cases as the rest of reg 33(1), now including (c) correspondent relationships. | `#outside`, Figure 3 | P11 to P13 | This is the guide's central statutory-trigger claim. Is "turn on facts, not on a rating" a fair reading of each limb? In particular (d) is "determined ... in accordance with regulation 35": does that make it a determination-based, not score-based, trigger? |
| A9 | Reg 33(1)(b) applies to a business relationship with a person established in a "FATF call for action country", or a relevant transaction where either party is so established, defined in 33(3)(a) by reference to the FATF Call for Action list "as such list has effect from time to time", subject to the narrow exception in reg 33(2). | `#outside`, Q2, answer note | P12 | Confirm the wording and that (2) is the only exception that should be named. The page names but does not analyse its three conditions. |
| A10 | The wording of reg 33(1)(b) changed with effect from 30 June 2026 (SI 2026/621 reg 19). | `#outside` | P12, P16 | Confirm the effective date and the instrument. The page does not state what the earlier wording said and refers to The De-Risking Judgement Call. |
| A11 | Reg 33(7): the presence of one or more risk factors may not always indicate a high risk. | `#outside`, FAQ 5 | P14 | Wording and context. The page now describes reg 33(7) as a narrow caution about risk factors, in making the reg 33(6) assessment, and does not offer it as authority on suspicion or exit. |
| A12 | A low model rating does not displace the reg 33(1)(b) requirement. (Q2 of the knowledge check is graded on this.) | `#outside`, Q2 | FinCrimeRadar application of P12 | Is the option graded correct, "Regulation 33(1)(b) still requires enhanced due diligence, subject to its narrow exception, whatever the score says", defensible as written, including the reg 33(2) exception and the word "whatever"? Is any distractor arguably correct? |

### B. What the FCA material establishes (second highest risk)

| # | Claim | Location | Source | What to check |
| --- | --- | --- | --- | --- |
| B1 | The FCA findings (11 November 2025) state their purpose as helping firms reflect on how they meet existing risk assessment requirements, and that good practice often goes beyond the minimum regulatory requirements. They do not state that examples create new rules. | `#law` | P20 | Confirm wording and the absence of any contrary statement. |
| B2 | FCG is general guidance under s139B FSMA, not binding; the FCA will not presume a departure indicates a breach; firms can comply in other ways. | `#law`, FAQ 1 | P64 (S8) | FCG 1.1.7, 1.1.8. The pages read do not state the meaning of the "G" suffix. The page does not claim to. |
| B3 | Case Study 17: six categories, weights 10, 20, 10, 30, 5, 25 percent, rating determines the level of due diligence, MLRO escalation alert, manual override section with rationale, prompt for other factors; introduced by the FCA as illustrating "a reasonable approach to calculating risk ratings". | `#inside-number`, Q1, FAQ 2 | P45, P46 | The page reports the six category names and the properties, and deliberately does not reproduce the percentages. Check that nothing on the page presents the weights as recommended or typical. |
| B4 | The FCA lists as good practice: CRAs that directly affect CDD, transaction monitoring and other controls; CRA MI to senior management committees; documenting methodologies and formally logging, discussing and approving changes; reviewing risk assessment models and processes; quarterly or triggered updates; reflecting BWRA risks in the CRA through weightings or sub-factors. | various | P23 to P26, P31 | Each is an FCA example. Confirm none is described as a requirement, and note that P25 and P26 use the generic words "risk assessment". |
| B5 | The FCA lists as poor practice: limited or no testing and review of risk assessment processes when firms make enhancements, upgrades or automation; CRAs not developed in line with business growth; rapid expansion without considering that controls remain appropriate beforehand; risk assessments not sufficiently dynamic. | `#change`, Scenario 1 | P27 to P30 | The "rapid expansion" item uses no BWRA, CRA or "risk assessment" wording. The page says it "describes risk assessment processes generally" and that reading it across to a scoring model is the guide's application. Is that careful enough? |
| B6 | Quarterly or triggered updates are an FCA example of good practice, not a legal minimum, and the statutory text read names no review frequency. (Q3 is graded on this.) | `#change`, Q3, FAQ 3 | P26, P06, P04 | Confirm no statutory frequency exists in reg 18, 28 or any provision this guide relies on. This is a negative claim about the text read, not about all of UK law. |
| B7 | FCG 3.2.3 poor practice includes: a classification system making high "almost impossible"; higher risk countries scored low to avoid EDD; relationship managers able to override customer risk scores without sufficient evidence; assessments unduly influenced by profitability; inability to evidence why customers are rated as they are; relying on group assessments without assessing UK compliance. (Q4 is graded on the override item.) | `#inside-number`, `#overrides`, Scenarios | P63 | Confirm each bullet sits under "Examples of poor practice" on the live page. |
| B8 | FCG 3.2.3 says firms must regularly review their risk assessment; FCG 2.2.4 says firms should regularly review both business-wide and individual risk assessments. "Regularly" is FCG wording and is not in reg 18. | `#change` | P60, P61 | Confirm the "must" and "should" wording and that the page attributes both to FCG, not to the Regulations. |
| B9 | Markets review observations: most firms considered a variety of factors and several weighted; most did not document the CRA methodology; some firms auto-assigned low risk regardless of other factors; one set the rating after due diligence; some used jurisdiction alone; few documented a rationale where overrides occurred; some only reconsidered geography at periodic review; periodic cycles often 1, 3 or 5 years. | `#inside-number`, `#thresholds`, `#overrides`, `#change`, Figure 3 | P41 to P44, P47, P48 | Confirm each is described as an observation in a sample of wholesale brokers. The page labels them Guidance and states the sample limit in `#sources`. |
| B10 | The page states that the FCA findings page covers customer risk assessment briefly, uses generic "risk assessment" wording in most items, and does not mention overrides, thresholds, risk bands, data quality, validation, scoring calibration or double counting. | `#law`, `#sources` | P32 | A negative claim about a page. Please search the page for those terms. Methodology statements are CLAUDE.md section 11 claims, so an error here is a correction. |

### C. FinCrimeRadar assessments that must not read as source statements

These are labelled on the page as FinCrimeRadar assessment. Check that the label is present each time and that the wording cannot be read as the authority's.

1. A high score does not by itself establish suspicion, require exit or show the customer is outside appetite (`#outside`). This is labelled FinCrimeRadar assessment; its basis is the absence in the texts read. Reg 33(7) is described separately and is not offered as authority for it.
2. Repeated overrides can indicate a model or data problem, or pressure (`#overrides`, Scenario 2). The page says no source states this.
3. Fact-based triggers should be built as a floor or a flag beside the score, and the model output and applied treatment should both be recorded (`#outside`).
4. The seven control points, the nine layers, the override loop and the change-control cycle, and every test suggested in `#change`.
5. The scenario recommendations. Each option's Source block should be checkable against a source, each Application block is our reasoning, and each Recommendation block is ours.
6. Double counting of correlated factors (`#inside-number`): no source addresses it. The page says so.

### D. Scoring and grading logic (CLAUDE.md section 15)

The page has no scoring engine or calculator. It has:

1. Two graded scenario decisions. Grades are fixed per option in the HTML and checked by `scripts/check_customer_risk_score_framework.py` (`EXPECTED_OPTION_GRADES`). Please test whether each "best" is genuinely best and whether any "unsupported" option is in fact defensible. In particular:
   - Scenario 1 "stop onboarding until a replacement model is approved" is graded incomplete, not unsupported. Is "incomplete" fair?
   - Scenario 2 "accept the pattern" and "stop all overrides" are both graded unsupported.
2. A five question knowledge check scored in `js/customer-risk-score-decision-framework.js` (one point per correct answer, `data-correct`). The correct option is the longest in only one of five questions.
3. Telemetry sends only guide id, scenario id, grade and score through the existing consent gated `gtag`, once per page load. No free text and no customer data.

### E. Figures and facts that are illustrative

All scenario figures (620 and 240 and 71 customers, 92%, 6% and 14%, twelve files) are fictional and labelled so on the page. They are not cited. The scan in `scripts/check_ledger.py scan` flags them as percentage candidates and they are classified as illustrative.

## 3. Known limits and choices to challenge

1. Regulation 33 and FCG 1.1 were added to the six named sources (source pack section 6). If you would rather keep the named six only, the statutory trigger section would need another statutory home.
2. The page names but does not analyse reg 33(2), reg 35 and reg 31. If the review finds the reg 33(2) wording too thin, the response is to add the three conditions or to soften the sentence.
3. The 8 and 21 per cent sample coverage figures in the markets review (para 6.3) are in the source pack and not on the page.
4. The reading time (55 minutes) follows the Knowledge Hub convention used for comparable Frameworks and is approximate.
5. Observed outside this task's scope: `de-risking-judgement-call.html` contains a literal backslash-n sequence in its page CSS (between the print rule and `.fcr-optfb-head`), which stops the `.fcr-optfb-head` and `.fcr-grade` rules applying. It was not changed. This guide's stylesheet removes the sequence, and the checker asserts it is absent.

## 4. Requested output

For each row in sections A and B: confirmed, confirmed with edit (give the edit), or rejected. For section C: any sentence that reads as a source statement. For section D: any grade you would change and why.
