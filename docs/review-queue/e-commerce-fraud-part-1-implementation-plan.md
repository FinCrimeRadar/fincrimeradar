# The E-commerce Fraud System: Part 1 atomic implementation plan

This plan completes Content Loop steps 07 and 08 for Part 1. Every Requirement Coverage Matrix ID in `e-commerce-fraud-part-1-implementation-contract.md` is assigned to exactly one sequential task. Tasks 1 to 10 are local implementation. Task 11 holds the review and release gates that Claude Code does not perform: they are recorded as outstanding human or Codex actions.

| Task | Scope | Assigned requirements | Targeted proof |
|---|---|---|---|
| 1 | Page shell, locked identity, evidence status, how-to-use block, 18 section skeleton, unique `ecf` IDs and classes, Article and BreadcrumbList JSON-LD, metadata, internal-terminology hygiene. | E01 to E03, H01 to H03, H07 to H09, H11, D07, D09, D10 | HTML parse, section order, heading outline, ID uniqueness, JSON-LD parse, metadata parity. |
| 2 | Lifecycle, decision levels, Fraud Evidence Relay, backtrace, outcome boundary, FinCrimeRadar attribution, credential-stuffing limit, lifecycle visual with textual equivalent. | E04 to E10, E13, H04, H12, H13, A02 | Label extraction and order checks, visual plus textual equivalent check. |
| 3 | Source records, citations and evidence boundaries. | E11, E12, E14 to E17, E24 to E28, H10 | Citation resolution, pinned figures and caveats, source-type labels, forbidden-pattern scan. |
| 4 | Two scenarios, graded options, Source, Application, Action reasoning, counterfactuals, five duplicated control patterns, native disclosures and fieldsets. | E18 to E21, E30, S01 to S08, S13, S14, H05, H06 | Scenario fact pins, grade-order pins, three-layer labels, pattern text-identity. |
| 5 | Control-owner checklist, assessment-change triggers, knowledge check and FAQ with pinned qualifications. | E22, E23, E29, K01, K02, K04 to K08 | Option, answer-key and FAQ pins, answer-leak scan. |
| 6 | Page CSS (namespaced), accessibility and responsive presentation. | A01, A03 to A10 | Computed-style and brand.css collision check, then width, zoom, text-expansion, reduced-motion, keyboard and JavaScript-disabled checks. |
| 7 | Page JavaScript: confidence, reveal, counterfactual, knowledge scoring, PNG export, consent-gated aggregate telemetry. | S09 to S12, S15, K03, J01 to J14 | `node --check`, static script scan, interaction and payload checks. |
| 8 | Discovery surfaces and derived assets: Knowledge Hub card and counts, sitemap, reciprocal relationships, Related Topics, social card, reading time, `methodology.html` untouched. | D01 to D06, D08, D11, D12 | Hub count parser, XML and JSON assertions, backlink render, image dimensions, reading-time checker, diff-scope check. |
| 9 | Claim-level ledger records, with the ledger base check run first. | L01 to L06 | `check_ledger_base.py` before and after, ledger scan, overdue and validate, source-set comparison. |
| 10 | Permanent static checker and headless-browser regression, then full integration regression and regression of other suites sharing changed files. | V01 to V07 | New checkers plus shared and affected suites, recorded outputs. |
| 11 | Review and release gates: independent claim review, correction propagation, Codex release review, remediation, exact-scope staging, release boundary. Not performed by this local pass. | L07 to L10, V08 to V12 | Written review records and explicit release authority, none of which this local pass supplies. |

Tasks are sequential. Task 9 prepares ledger records for review but publication stays blocked until Task 11 passes. Nothing in Tasks 1 to 10 authorises a commit, push, pull request, merge or publication.
