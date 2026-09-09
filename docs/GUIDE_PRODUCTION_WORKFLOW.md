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
- Implementation specification
- Release review planning

The goal is to provide one complete implementation contract before repository work begins.

### Claude Code

Claude Code owns:

- Repository inspection
- HTML and page-specific CSS and JavaScript
- Metadata
- Knowledge Hub integration
- Sitemap and content relations
- Verification ledger integration
- Social assets
- Automated tests
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

### 01. Select

Choose the topic and public format.

### 02. Research

Refresh primary sources and identify the original FinCrimeRadar angle.

### 03. Design

Define the analytical model, scenarios, interaction pattern and information architecture.

### 04. Draft

Complete the substantive publication before repository implementation.

### 05. Specify

Create one complete Claude Code implementation contract.

### 06. Build

Claude Code implements the publication and automated tests.

### 07. Review

A fresh GPT or Codex context performs one independent adversarial release review.

### 08. Remediate

Claude Code applies one consolidated remediation pass.

### 09. Release

Run final tests, inspect the diff, commit and push.

### 10. Verify

Verify the production URL, metadata, sources, mobile rendering, consent behaviour and discovery.

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

## 5. Experiment 01 lessons

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

Use the smallest deterministic checks that prove the requirement. A successful HTTP response does not prove source accuracy, browser behaviour or production parity.

## 9. Release philosophy

One design gate. One implementation gate. One independent release gate. One consolidated remediation pass. Then release.

Quality should come from strong specifications, automation and independent review rather than repeated sequential review loops. Do not reopen completed editorial or architectural decisions without new evidence.

## 10. Experiment 02

The current preferred candidate is **Money Mule as Victim**, proposed as a **Case File** public format.

Potential experimental elements:

- Initial alert
- Customer profile
- Transaction chronology
- Evidence sequence
- Competing hypotheses
- Vulnerability indicators
- Scenario Inject
- Decision Record
- SAR implications
- Customer treatment

Experiment 02 should test a genuinely different investigative composition rather than reproduce the APP Scam Framework structure.

## 11. Current status

| Publication | Status | Public format | Production verified | Outstanding Experiment 01 blockers |
| --- | --- | --- | --- | --- |
| APP Scam Decision Framework | Live | Framework | Yes | None |

Framework remains experimental pending further evaluation, preferably including Experiment 02.
