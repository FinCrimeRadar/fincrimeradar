# Guide Standard

**This document is the canonical source for guide structure and presentation. Do not duplicate these requirements in CLAUDE.md or BACKLOG.md.** Sourcing, the verification ledger, and adversarial review requirements are defined in CLAUDE.md; this document references them, it does not restate them. Unfinished work, retrofit queues, and open decisions against this standard live in BACKLOG.md, not here.

---

## Global core

Applies to every guide regardless of which treatment below it uses.

**Claim sourcing.** Every material claim gets a real source or honest epistemic framing; illustrative figures get no citation. Fully governed by CLAUDE.md's Content sourcing standard, not restated here.

**Worked decisions.** At least two worked scenarios, each with a decision point offering graded multiple-choice options and full reasoning revealed after the analyst chooses, plus a structure or relationship diagram where the content has one to show. One scenario plus a formal counterfactual section is an acceptable substitute for a second scenario, not a silent shortfall, when the content genuinely supports one deep scenario better than two shallower ones, state the substitution explicitly when it's used. Scenario verdict and feedback text must follow the reasoning-distinction rule defined in CLAUDE.md: what the source establishes, what the guide's own application of it concludes, and what the guide recommends, kept visibly separate.

**Risk/Signal/Response.** A merged, unified card design, not a table, not two separate card types: icon, memorable metaphor-style name, one short explanatory line, then three compact labelled lines (Risk / Signal / Response). One component, two placements, renders inline in the guide body at the point each pattern is introduced, and the identical set regroups into a grid at the very end as the closing summary.

**Knowledge check.** Multi-question, live scoring. Where a guide includes a real named case study, at least one question must test a genuine detail or lesson from that specific case, not a generic guide concept.

**FAQ.** An accordion as a standard closing section, native `<details>`/`<summary>`, not a custom JS toggle.

**Summary export.** A "Save as image" button stays permanent, exporting the closing Risk/Signal/Response card grid via Canvas 2D, not a table. A downloadable summary snapshot image is standard wherever a guide's content justifies one: externally generated against a fixed template, compressed to keep clear of the working ceiling (roughly 400KB), zoom-checked for compression artifacts before accepting, and its content verified against the live page before wiring in, every time it or the claims it depicts change (see CLAUDE.md's stale-asset synchronisation rule).

**Accessibility.** `aria-live="polite"` on verdict and quiz-feedback containers, from the start, not added after a review catches its absence. Native disclosure (`<details>`/`<summary>`) for the FAQ, from the start. A skip-to-content link at the top of `<body>`, targeting the main content region. Logical heading order, accessible names on interactive elements, full keyboard operability, and respect for `prefers-reduced-motion`.

**Mobile verification.** Real device-width verification is required, not a static CSS read-through and not a browser-window resize (confirmed non-functional in this project's working environment). Use iframe-based device-width emulation at a minimum of 320/375/390/428/768px. Any click-triggered dynamic behaviour (a reparented panel, a revealed verdict, an advancing decision tree) must be verified by actually triggering the interaction and checking the result, structurally and visually, not inferred from how the page looks at rest. A behaviour that cannot be verified in this environment (for example, a `matchMedia` reverse-transition that depends on a genuine browser resize event) gets reported honestly as unverified, not claimed as confirmed and not silently re-patched.

**data-date convention.** Unchanged: every guide's Knowledge Hub card carries a `data-date` attribute.

**Adversarial review.** Fully governed by CLAUDE.md's Review policy, Regulatory-claim adversarial review, and related checklist entries. Not restated here.

**Stale-asset synchronisation.** Fully governed by CLAUDE.md. When a guide's content changes, every derived representation (summary image, metadata, structured data, social copy, stat strip figures, quiz/scenario text, closing cards, Knowledge Hub description) must be checked against the new content before publication.

---

## Default treatment: merged-card Knowledge Hub format

The default for operational playbooks, typologies, investigation handbooks, and straightforward regulatory explainers, which is to say most guides. Reference implementations: kyc-onboarding-dilemma.html for interactivity depth, adverse-media-intelligence-guide.html for the merged Risk/Signal/Response card standard in full.

Structure, beyond the Global core above:
- An animated stat strip near the top, where real numbers exist worth leading with.
- A process-flow diagram where the content has a genuine sequential process.
- A real named case study where one exists and can be accurately cited; a clearly labelled composite/illustrative case is acceptable where no real citable case exists.
- Standard Knowledge Hub card layout and navigation chrome, no experimental shell.

---

## Evidence Essay treatment (optional, per-guide)

An alternative presentation, not a default and not a shell to reach for automatically. Select it per guide, deliberately, against these criteria, not as an upgrade applied by habit:

- The guide advances an original or contested thesis.
- Source limitations materially affect the conclusion.
- Several claims need precise source mapping for a reader to evaluate them.
- Regulatory interpretation requires extended reasoning, not a single citation.
- The expected reader value justifies the additional build and review cost, this treatment costs more to build and more to review than the default.

**Shell.** A three-column adaptive layout: a sticky contents rail (left), the editorial column (centre, the actual article), and a source-record rail (right) that displays contextual detail for whichever citation the reader last clicked. This is a treatment-specific pattern, not a requirement of the guide standard generally.

**Contextual source records are currently an Evidence Essay-only feature, not a global requirement.** They have not been generalised to the default treatment, pending evidence that readers actually use them. Do not add this pattern to a default-treatment guide without first deciding whether it belongs in the Global core instead.

**Mobile behaviour.** The source-record rail collapses out of the three-column layout below the 800px breakpoint. Clicking a citation reparents the single source-panel node (never duplicated) to sit inline immediately after the clicked citation's containing element; confirmed working via live triggered-click testing, structurally and visually, on both guides shipped under this treatment. The panel's resting/default position, before any citation is clicked, is after all article content, this is correct, documented behaviour, not a defect. The reverse transition, a viewport widening back past 800px restoring the panel to its home position, has not been verified live in this environment on either shipped guide; see BACKLOG.md.

**Shipped guides.** gambling-white-label-blind-spot-guide.html (first) and classification-asymmetry-guide.html (second). Both still labelled experimental per methodology.html's own note; this treatment is not yet a standing format decision, and does not become one by virtue of a second guide using it.

**Reuse, don't reinvent.** The proven component family: the three-column shell, the source-record panel with its mobile inline-reveal, the process-flow diagram, native FAQ disclosure, the shared Risk/Signal/Response cloneNode pattern, and the Canvas 2D export. A third Evidence Essay guide should build faster than the second did, because this componentry already exists.
