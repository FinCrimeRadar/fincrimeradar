# Digital Identity Is Not the Whole of CDD: atomic implementation plan

This plan completes Content Loop steps 07 and 08. Every Requirement Coverage Matrix ID is assigned once to one sequential task.

| Task | Scope | Assigned requirements | Targeted proof |
|---|---|---|---|
| 1 | Build the public Intelligence Brief shell, metadata, semantic structure and locked editorial content. | E01 to E20, H01 to H10 | HTML parse, source-link resolution, heading and section checks. |
| 2 | Implement the two worked decisions and the five duplicated control patterns. | S01 to S08 | Scenario, grading, reasoning and text-identity checks. |
| 3 | Implement the knowledge check and FAQ. | K01 to K05 | Static option and answer-key checks. |
| 4 | Implement accessibility and responsive presentation. | A01 to A07 | Keyboard, viewport, zoom, text-expansion, reduced-motion and no-JavaScript checks. |
| 5 | Implement page JavaScript, aggregate telemetry and PNG export. | J01 to J10 | Static script scan and interaction regression. |
| 6 | Add discovery surfaces, metadata, social card and reciprocal relationships. | D01 to D07 | Knowledge Hub count, XML, JSON, backlink, metadata and image checks. |
| 7 | Add claim-level ledger records and complete the regulatory review gate. | L01 to L07 | Ledger baseline and validation, source-set comparison and written independent review. |
| 8 | Add permanent static and browser release contracts and run integration regression. | V01 to V04 | New page checks plus every affected shared and experiment suite. |
| 9 | Independent release review, remediation, exact-revision verification and release staging. | V05 to V08 | Fresh review record, rerun logs, cached diff and explicit release authority. |

Tasks are sequential. Task 7 may prepare ledger records before independent review, but publication remains blocked until the review passes. Task 9 does not authorise commit, push, merge or production claims.
