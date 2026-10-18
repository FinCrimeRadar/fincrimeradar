# Claude Code handoff: E-commerce Fraud Part 1

Implement Part 1 from the locked specification chain. Local implementation and verification are authorised. Commit, push, pull request, merge and publication are not authorised.

## 1. Read before changing anything

Read these files completely in this order:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `GUIDE_STANDARD.md`
4. `docs/GUIDE_PRODUCTION_WORKFLOW.md`
5. `docs/review-queue/e-commerce-fraud-series-non-overlap-review.md`
6. `docs/review-queue/e-commerce-fraud-part-1-charter.md`
7. `docs/review-queue/e-commerce-fraud-part-1-source-pack.md`
8. `docs/review-queue/e-commerce-fraud-part-1-design-memo.md`
9. `docs/review-queue/e-commerce-fraud-part-1-editorial-draft.md`
10. `docs/review-queue/e-commerce-fraud-part-1-implementation-contract.md`

Inspect the current working tree before editing. Preserve all unrelated tracked and untracked work.

## 2. Required first deliverable

Before changing publication files:

1. Divide the implementation contract into small sequential tasks.
2. Assign every Requirement Coverage Matrix ID to exactly one task.
3. Prove that all 124 IDs are assigned once, with no omissions or duplicates.
4. Save the plan as `docs/review-queue/e-commerce-fraud-part-1-implementation-plan.md`.

Do not begin implementation until this requirement map passes its own completeness check.

## 3. Implementation authority

Implement the exact file set and behaviour defined by the contract, including:

- the public guide and page-specific JavaScript;
- the social card;
- static and browser verification scripts;
- Knowledge Hub, sitemap and reciprocal related-content changes;
- verification-ledger records;
- all required deterministic and browser checks.

Use the existing FinCrimeRadar architecture and accepted components. Inspect relevant live guide implementations before copying any pattern. Keep all material reasoning in the HTML and preserve JavaScript-disabled comprehension.

## 4. Hard boundaries

- Do not create a backend, API, database, account integration, authentication feature, free-text collection, shared renderer or generic fraud engine.
- Do not redesign the Fraud Evidence Relay, backtrace test, scenarios, outcome boundaries or control patterns.
- Do not use Nisbets information or employer-specific examples.
- Do not invent legal, scheme, prevalence or effectiveness claims.
- Do not weaken tests or remove required coverage to obtain a pass.
- Do not alter unrelated work.
- Do not commit, push, open a pull request, merge or publish.

If a current source, repository constraint, legal boundary or architecture makes the specification unsafe or incoherent, stop and report the exact conflict. Do not silently change the model.

## 5. Verification discipline

Run the ledger baseline before ledger edits. Use targeted checks after each atomic task. Run the complete relevant integration regression only after implementation, then inspect the entire diff and working-tree scope.

Report:

1. files changed;
2. requirement-to-task coverage result;
3. targeted checks run per task;
4. full regression results, including every failure;
5. unresolved legal, scheme, browser, accessibility or release risk;
6. confirmation that no backend or external release action occurred.

Passing local checks does not authorise commit or publication. Stop after the local implementation report so Codex can perform the independent review.
