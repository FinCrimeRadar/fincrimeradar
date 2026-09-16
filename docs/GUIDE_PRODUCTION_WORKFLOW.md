# Guide Production Workflow

This document defines the operational workflow for producing new FinCrimeRadar publications. It complements `GUIDE_STANDARD.md`, which remains authoritative for guide structure, presentation treatments and the Guide Quality Layer. Sourcing, regulatory accuracy and release verification remain governed by `CLAUDE.md`.

## 1. Purpose

This workflow applies to new publications using these public formats:

- Guide
- Framework
- Case File
- Intelligence Brief
- Evidence Essay

The APP Scam Decision Framework established the first experimental workflow. Experiment 01 took approximately two days from concept to verified production. That was acceptable for the first format experiment, but it is too slow for the normal publishing cadence.

The normal target is approximately 2.5 to 4 hours of active workflow, subject to legal, regulatory and research complexity.

## 2. Core responsibility split

### GPT or Codex

GPT or Codex owns:

- Topic selection and scoping
- Primary source research and source verification
- Regulatory interpretation
- Differentiation thesis
- Product design and editorial formulation
- Information architecture
- Scenario and interaction design
- Acceptance criteria and test specification
- A Requirement Coverage Matrix covering every requirement the publication must satisfy
- Implementation specification
- Release review planning

The goal is to provide one complete implementation contract before repository work begins.

### Claude Code

Claude Code owns:

- Repository inspection
- Dividing the implementation contract into small atomic tasks and assigning every requirement to exactly one task
- HTML and page-specific CSS and JavaScript
- Metadata
- Knowledge Hub integration
- Sitemap and content relations
- Verification ledger integration
- Social assets
- Automated tests
- Targeted deterministic checks during each atomic task, and full integration regression once implementation is complete
- Browser, accessibility and responsive checks
- Diff inspection
- Implementation reporting

Claude Code should implement the approved concept, not redesign it during the build. If the specification creates a genuine architectural, regulatory or accessibility problem, Claude Code should stop and report it rather than silently changing the product direction.

### Fresh GPT or Codex context

A fresh GPT or Codex context owns one independent adversarial release review covering:

- Regulatory and factual accuracy
- Source freshness
- Source label, version and target consistency
- Originality and analytical integrity
- Architecture containment
- Accessibility and responsive behaviour
- JavaScript-disabled comprehension
- Test quality
- Metadata and discovery
- Verification ledger precision
- Diff scope
- Public terminology and internal terminology leakage

### Claude Code remediation

Claude Code then performs one consolidated remediation pass. Avoid repeated micro-review loops unless remediation introduces a genuine new defect.

## 3. Standard production sequence

This sequence is proven by Experiments 01 to 03, most fully by Experiments 02 and 03. GPT or Codex owns steps 1 to 6; Claude Code owns steps 7 to 11 and 14 to 16; a fresh GPT or Codex context owns step 12; Claude Code owns the remediation in step 13.

### 01. Select

Choose the topic and public format.

### 02. Research

Refresh primary sources and verify them directly before drafting any claim.

### 03. Establish originality thesis

Identify the original FinCrimeRadar angle and confirm it clears the Guide Quality Layer's originality gate.

### 04. Lock analytical model

Fix the analytical model, scenarios, interaction pattern and information architecture before drafting. Reopening the model after drafting begins is a specification failure, not a normal editing step.

### 05. Draft

Complete the substantive editorial draft before repository implementation begins.

### 06. Create Requirement Coverage Matrix

Produce one Claude Code implementation contract listing every requirement the publication must satisfy. This is the "one complete implementation contract" referenced in section 2.

### 07. Divide into atomic tasks

Claude Code divides implementation into small atomic tasks, each independently verifiable.

### 08. Assign requirements to tasks

Assign every requirement in the Requirement Coverage Matrix to exactly one task. No requirement is left unassigned, and no requirement is assigned to more than one task.

### 09. Implement sequentially

Implement the atomic tasks in order, one at a time.

### 10. Run targeted checks per task

Run targeted, deterministic checks during each individual task: the smallest checks that actually prove that task's requirements. See the regression discipline lesson in section 5.

### 11. Run full integration regression

Once implementation is complete, run the full regression suite: this publication's own checks, the shared checks it touches (ledger, sitemap, Knowledge Hub counts, reading time), and the other live experiment suites where a shared file changed.

### 12. Independent adversarial release review

A fresh GPT or Codex context performs one independent adversarial release review.

### 13. Consolidated remediation

Claude Code applies one consolidated remediation pass addressing the review's findings.

### 14. Final release verification

Re-run the full regression suite against the exact revision about to be committed.

### 15. Commit and release

Inspect the diff, commit, and push according to the repository's current workflow and authorisation requirements.

### 16. Verify production

Verify the production URL, metadata, sources, mobile rendering, consent behaviour and discovery against the live site, not just the local working tree.

## 4. Target production time

| Stage | Active time target |
| --- | --- |
| GPT or Codex research, design and specification | 60 to 120 minutes |
| Claude Code implementation and testing | 30 to 90 minutes |
| Independent adversarial review | 20 to 45 minutes |
| Remediation and release | 20 to 45 minutes |

Normal target: approximately 2.5 to 4 hours of active workflow.

Longer cycles are acceptable for:

- Evidence Essays
- New experimental formats
- Complex legal interpretation
- Major regulatory change
- New interactive architecture
- Deep source verification

## 5. Lessons from Experiments 01 to 03

### Regression discipline (confirmed by Experiments 02 and 03)

Do not run the full repository regression suite after every small task. Use targeted, deterministic checks during individual implementation tasks, the smallest checks that actually prove that task's requirements. Run the full integration regression once implementation is complete, and again at the final release-verification gate. Run the full regression suite mid-implementation only where a task changes shared architecture (shared CSS, shared JavaScript, the Knowledge Hub shell, the verification ledger schema) or otherwise creates a credible cross-site regression risk.

### Public taxonomy and rendering architecture are separate

Framework can exist as a public format without requiring a new shell. Public taxonomy tells the reader what kind of publication they are using. Rendering architecture determines how the content is presented.

### Originality comes from reasoning structure

Experiment 01 differentiated the publication through:

- The Four Verdict Problem
- Six sequential decision gates
- Decision Records
- Nominal Performance Trap
- Vulnerability before blame
- Scheme outcome versus defensibility outcome
- Five reasoning traps
- Red Team Questions
- What Would Change My Decision

These created product differentiation through practitioner reasoning, not decorative styling.

### Static first remains the default

All material reasoning should exist in the initial HTML. JavaScript may enhance interaction, scoring, export and consent-gated telemetry. It must not contain the only copy of material reasoning or conclusions.

### Scenario symmetry matters

Where scenarios use the same analytical structure, equivalent reasoning structures should normally exist. Any asymmetry should be deliberate and justified by the subject.

### Internal terminology stays internal

Terms such as Experiment 01 are project terminology. Public pages should use finished product labels such as Framework.

### Source freshness is a release requirement

The Pay.UK Schedule 4 version mismatch demonstrated that HTTP 200 is not sufficient. Release verification must confirm:

- Source title
- Source version
- Source target
- Effective date
- Exact proposition supported
- Current authoritative version

### Do not abstract too early

Experiment 01 did not require a generic Framework renderer, branching engine, scoring engine, component library, shared CSS change or shared JavaScript change. Extract reusable implementation only after repetition proves a stable contract.

## 6. Reusable patterns proven by Experiment 01

The following are candidates for reuse:

- Decision Record
- What Would Change My Decision
- Red Team Questions
- Practitioner Lens
- One Screen Operational Summary
- Static-first progressive enhancement
- Framework public label treatment
- Source, Application and Action reasoning

They should not be copied automatically into every publication. The subject should determine whether each pattern improves understanding, judgement or action.

## 7. APP Scam specific patterns

The following are analytical content specific to APP scams, not universal Framework components:

- The Four Verdict Problem
- Six APP scam gates
- Nominal Performance Trap
- Consumer Standard of Caution logic
- Vulnerability-before-blame structure
- Scheme outcome versus defensibility distinction

## 8. Standard quality gates

Every release should apply the relevant recurring checks:

- Primary source freshness
- Source title and target consistency
- Source version consistency
- Verification ledger coverage
- Material claim support
- Static and JavaScript content parity
- JavaScript-disabled comprehension
- Keyboard operation
- Visible focus
- 320 pixel viewport
- 200 percent zoom
- Reduced motion
- Long text expansion
- No page-level horizontal overflow
- Metadata parity
- Canonical parity
- Sitemap parity
- Knowledge Hub discovery
- Public guide count consistency
- Social asset validity
- Internal terminology leakage
- Consent-gated telemetry
- No sensitive telemetry
- No unrelated diff contamination
- Production URL verification
- Regression scope discipline: targeted checks during tasks, full regression at integration and release gates

Use the smallest deterministic checks that prove the requirement. A successful HTTP response does not prove source accuracy, browser behaviour or production parity.

## 9. Release philosophy

One design gate. One implementation gate. One independent release gate. One consolidated remediation pass. Then release.

Quality should come from strong specifications, automation and independent review rather than repeated sequential review loops. Do not reopen completed editorial or architectural decisions without new evidence.

## 10. Experiment 02 and 03 outcomes

Experiment 02 shipped as **Money Mule or Victim?** (`money-mule-or-victim-case-file.html`), proving the Case File public format. It tested a genuinely different investigative composition from the APP Scam Framework, as intended. Its accepted recurring contract is defined in `GUIDE_STANDARD.md`'s Case File contract; the twelve-stage disclosure, five-hypothesis board, and specific state machine built for that subject are Subject Specific Composition, not standardised beyond it.

Experiment 03 shipped as **FATF Recommendation 16: The Payment Transparency Reset** (`fatf-recommendation-16-intelligence-brief.html`), proving the Intelligence Brief public format. Its accepted recurring contract is defined in `GUIDE_STANDARD.md`'s Intelligence Brief contract; Recommendation 16 specific content and component layout are Subject Specific Composition, not standardised beyond it.

Both compositions are accepted following the completed cross-experiment review, without requiring a second instance of either. Framework remains the exception: Experiment 01 (`app-scam-decision-framework.html`) is still its only implementation, and a second Framework publication remains required future work to test recurrence.

## 11. Current status

| Publication | Status | Public format | Production verified | Outstanding blockers |
| --- | --- | --- | --- | --- |
| APP Scam Decision Framework | Live | Framework | Yes | A second Framework implementation is required to test recurrence |
| Money Mule or Victim? | Live | Case File | Yes | None; Case File is an accepted composition |
| FATF Recommendation 16: The Payment Transparency Reset | Live | Intelligence Brief | Yes | None; Intelligence Brief is an accepted composition |

Framework remains experimental pending a second Framework implementation to test recurrence. Case File and Intelligence Brief are accepted compositions and do not require a second instance.

## 12. Shared helper maturity

Following the cross-experiment review, two categories of repeated implementation are approved for future extraction, but not extracted during this review.

**Browser regression harness.** The CDP-based server-and-browser test harness (a threaded local HTTP server, a tracked-PID Chrome launch, a CDP client, and device-width emulation) now repeats near-identically across multiple experiment suites. Approved for extraction into a shared test helper the next time it is touched.

**Consent-aware aggregate telemetry helper.** Approved for extraction only as a small, strict helper with an explicit event allow-list. It must never transmit free text, case decisions, hypothesis selections, Decision Record contents, or unnecessary personal data.

Not approved, and not to be created without separate evidence: a generic Framework renderer, a generic Case File renderer, a generic Intelligence Brief renderer, a generic decision engine, a generic hypothesis engine, a shared publication component library, or a `KnowledgeCountParser` extraction. The principle remains: abstract stable infrastructure, not immature editorial architecture.
