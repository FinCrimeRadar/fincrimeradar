# E-commerce Fraud Part 1: independent review record

Guide: `e-commerce-fraud-system-guide.html`
Review date: 18 October 2026
Reviewer: independent Codex legal and scheme review, run outside Claude Code.
Outcome: **PASS**, after the two source corrections recorded below.

## Sources checked on 18 October 2026

- Financial Conduct Authority, Strong Customer Authentication: https://www.fca.org.uk/firms/strong-customer-authentication
- FCA Handbook technical standards, Chapter -3 Application: https://handbook.fca.org.uk/technical-standards/provision/s140c1221sn0p1814
- FCA Handbook technical standards, Chapter 3 Exemptions from strong customer authentication: https://handbook.fca.org.uk/technical-standards/s140c1226
- Payment Services Regulations 2017, regulations 67, 74, 75 and 76: https://www.legislation.gov.uk/uksi/2017/752/regulation/67 (and /74, /75, /76)
- Consumer Rights Act 2015, section 20: https://www.legislation.gov.uk/ukpga/2015/15/section/20
- Consumer Contracts Regulations 2013, regulations 29 and 34: https://www.legislation.gov.uk/uksi/2013/3134/regulation/29 and /34
- Visa, Dispute Management Guide for Merchants (October 2026)
- Europol, Safe sales, safe revenue
- United States Department of Justice, Artemis Refund Group sentencing release of 29 April 2026

## Review groups (source pack section 7)

| # | Group | Result |
| --- | --- | --- |
| 1 | Strong customer authentication scope, exemptions and merchant versus payment service provider responsibility | PASS after correction 2 |
| 2 | Payer consent, authentication evidence and unauthorised-payment reimbursement under regulations 67, 75 and 76 | PASS after correction 1 |
| 3 | Consumer Rights Act 2015 and Consumer Contracts Regulations 2013 boundaries | PASS |
| 4 | Visa scheme statements, response rights, evidence and deadlines | PASS |
| 5 | Scenario recommendations on delaying fulfilment, restricting accounts, refusing or reducing refunds and alleging fraud | PASS |
| 6 | Cross-jurisdiction comparison and industry-practice claims | PASS |

Both scenario verdicts, both counterfactuals, the FAQs, the refund-delay wording, the Europol framing and the DOJ Artemis framing were confirmed as substantively supported and appropriately qualified. No conclusion was broadened or rewritten.

## Corrections made

1. Regulation 74 added to source record 7, the source pack, editorial draft, implementation contract, static checker pins and `verification-ledger.json` (claim `e-commerce-fraud-system.psr-2017-reg74-notification.014`). The bounded proposition is that redress under regulation 76 is subject to notification without undue delay and, generally, no later than 13 months after the debit date, subject to regulation 74(2). It is not merchant advice.
2. Source record 3 now links the FCA technical standards on application (Chapter -3) and exemptions (Chapter 3). The wording is unchanged.

## Release boundary

This record does not authorise release. No commit, push, pull request, merge, deployment or publication may occur without separate authorisation from the owner.
