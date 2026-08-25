# Guide Standard

**This document is the canonical source for guide structure, presentation, and the treatment-independent Guide Quality Layer.** Do not duplicate these requirements in `CLAUDE.md` or `BACKLOG.md`. Sourcing, the verification ledger, and adversarial review requirements are defined in `CLAUDE.md`; this document references them, it does not restate them. Unfinished work, retrofit queues, and open decisions against this standard live in `BACKLOG.md`, not here.

Every guide follows the same shape: **Global core** (universal, both treatments), then the **Guide Quality Layer** (treatment-independent quality practices), then a choice of **one** presentation treatment, **Default Knowledge Hub** or **Evidence Essay**.

---

## Global core

Applies to every guide regardless of which treatment below it uses. This section defines the minimum FinCrimeRadar quality floor. A presentation treatment may change how a guide delivers this standard, it must never silently lower it; every requirement below is mandatory, not a menu.

**Claim sourcing.** Every material claim gets a real source or honest epistemic framing; illustrative figures get no citation. Fully governed by `CLAUDE.md`'s Published content sourcing section, not restated here.

**Human practitioner writing.** Every guide reads like work written by an experienced human financial crime practitioner, not generated prose. Fully governed by `CLAUDE.md`'s Human writing standard, not restated here.

**Brand, metadata and navigation consistency.** New components use namespaced classes and are checked against `brand.css`'s generic selectors and `brand.js`'s watched selectors before shipping, governed by `CLAUDE.md`'s Component isolation rule. Every guide carries standard `Article` and `BreadcrumbList` structured data and the standard Knowledge Hub navigation chrome, no experimental shell for these elements.

**Worked decisions.** Every new guide requires at least two distinct worked scenarios, each with a decision point offering graded multiple-choice options and full reasoning revealed after the analyst chooses, plus a structure or relationship diagram where the content has one to show. A scenario should be materially distinct in facts, decision context, risk mechanism, or practitioner judgement; cosmetic changes to the same underlying fact pattern do not satisfy the requirement. Counterfactual reasoning may deepen an existing scenario but does not count as a separate scenario and cannot substitute for the two-scenario minimum. Scenario verdict and feedback text must follow the Source, Application, Action distinction defined in the Guide Quality Layer below.

**Risk/Signal/Response.** A merged, unified card design, not a table, not two separate card types: icon, memorable metaphor-style name, one short explanatory line, then three compact labelled lines (Risk / Signal / Response). One component, two placements, renders inline in the guide body at the point each pattern is introduced, and the identical set regroups into a grid at the very end as the closing summary.

**Knowledge check.** Multi-question, live scoring. Where a guide includes a real named case study, at least one question must test a genuine detail or lesson from that specific case, not a generic guide concept.

**FAQ.** An accordion as a standard closing section, native `<details>`/`<summary>`, not a custom JS toggle.

**Summary export.** A "Save as image" button stays permanent, exporting the closing Risk/Signal/Response card grid via Canvas 2D, not a table. A downloadable summary snapshot image is standard wherever a guide's content justifies one: externally generated against a fixed template, compressed to keep clear of the working ceiling (roughly 400KB), zoom-checked for compression artifacts before accepting, and its content verified against the live page before wiring in, every time it or the claims it depicts change (see `CLAUDE.md`'s Derived asset synchronisation rule).

**Accessibility.** `aria-live="polite"` on verdict and quiz-feedback containers, from the start, not added after a review catches its absence. Native disclosure (`<details>`/`<summary>`) for the FAQ, from the start. A skip-to-content link at the top of `<body>`, targeting the main content region. Logical heading order, accessible names on interactive elements, full keyboard operability, and respect for `prefers-reduced-motion`. See the Guide Quality Layer's Accessibility baseline below for the full WCAG 2.2 AA checklist this summarises.

**Mobile verification.** Real device-width verification is required, not a static CSS read-through and not a browser-window resize (confirmed non-functional in this project's working environment). Use iframe-based device-width emulation at a minimum of 320/375/390/428/768px. Any click-triggered dynamic behaviour (a reparented panel, a revealed verdict, an advancing decision tree) must be verified by actually triggering the interaction and checking the result, structurally and visually, not inferred from how the page looks at rest. A behaviour that cannot be verified in this environment gets reported honestly as unverified, not claimed as confirmed and not silently re-patched.

**data-date convention.** Every guide's Knowledge Hub card carries a `data-date` attribute.

**Sitemap.** Mandatory, no exceptions: every new guide's URL is added to `sitemap.xml` before the guide is considered shipped, matching the format and `<priority>` tier of the most recently added comparable guide. Confirm both the file addition and a fresh live-site check (not just the local working tree) before marking a guide's sitemap step complete.

**Adversarial review.** Fully governed by `CLAUDE.md`'s Regulatory claim review section and related checklist entries. Not restated here.

**Stale-asset synchronisation.** Fully governed by `CLAUDE.md`'s Derived asset synchronisation section. When a guide's content changes, every derived representation (summary image, metadata, structured data, social copy, stat strip figures, quiz/scenario text, closing cards, Knowledge Hub description) must be checked against the new content before publication.

---

## Guide Quality Layer

Treatment-independent. Applies whether a guide uses the Default Knowledge Hub treatment or Evidence Essay, and strengthens the Global core above without replacing or weakening it.

**Originality gate.** Before substantive drafting, establish what practitioner value the guide contributes beyond regulator summaries, generic compliance articles, and existing search results. Contribute at least one meaningful differentiator: original practitioner judgement, a decision framework, a structured investigation method, a regulatory comparison, a failure mode analysis, a unique scenario model, an evidence synthesis, or an operational control framework. If the guide cannot articulate a meaningful practitioner gain, the angle needs further development before publication. Rewording existing sources is not originality.

**Regulatory context.** Where relevant, provide compact context identifying jurisdiction, the relevant legal or regulatory regime, the intended practitioner audience, the verification or evidence date, material scope limitations, and whether the subject is particularly change-sensitive. Do not add this where it creates visual clutter for guides where it adds no value.

**Source, Application, Action distinction.** For legally or regulatorily sensitive teaching points, keep three layers visibly separate: **Source**, what the authority expressly establishes; **Application**, how FinCrimeRadar applies that authority to the facts or scenario; **Action**, the operational response or practitioner consideration FinCrimeRadar recommends. Never present FinCrimeRadar's own inference as though it were the precise wording or mandatory conclusion of the cited authority. This is the reader-facing form of the accuracy discipline already defined in `CLAUDE.md`'s Scenario reasoning section; it does not create a second standard, it applies that one to guide prose and scenario copy specifically.

**Counterfactual scenario reasoning.** Where a scenario contains a genuinely decision-determining fact, consider a counterfactual step after the initial reasoning: change one material fact and ask whether the decision changes. Examples: ownership moving from below to above a relevant threshold, a subject changing from a non-qualifying public role to one that satisfies a legal definition, an isolated transaction becoming a repeated behavioural pattern, source-of-funds evidence becoming independently corroborated, control rights changing without a corresponding ownership change. The purpose is to teach which facts actually drive the judgement. Do not add a counterfactual where changing the fact would teach nothing.

**Learner confidence.** Where useful, let the reader record High, Medium, or Low confidence after choosing but before seeing the reasoning. A calibration mechanism, not gamification, distinguishing correct-and-confident from correct-but-uncertain from incorrect-but-uncertain from incorrect-and-confidently-wrong. Not mandatory for every scenario.

**Visual purpose rule.** Every substantive visual must answer a defined reader question: who owns or controls whom, where does the transaction chain change, which fact changes the risk assessment, where should an investigation escalate, how does a process move from signal to decision. Do not ship a decorative diagram that repeats nearby prose without improving comprehension. Complex visuals need an accessible textual equivalent where required.

**Progressive enhancement.** Core guide content, regulatory reasoning, conclusions, citations, and essential practitioner guidance must remain accessible if JavaScript fails. JavaScript may enhance scenario decisions, knowledge checks, scoring, source panels, card exports, and progressive disclosure. It must not become the only route to material guide content.

**Accessibility baseline.** WCAG 2.2 AA is the interaction baseline. Pay particular attention to keyboard navigation, visible focus, focus not being obscured, accessible pointer targets, logical reading order, semantic controls, screen reader labels, colour contrast, reduced-motion preferences, no essential hover-only information, and no unexpected context changes caused only by focus. Where practical, favour comfortable touch targets beyond the strict minimum. Animations must never be required to understand the content.

**Interaction telemetry.** For meaningful new interaction families, support privacy-conscious aggregate analytics so the team can tell whether the interaction provides real reader value: `scenario_complete`, `knowledge_check_complete`, `source_record_open`, `counterfactual_complete`, `card_export`. Telemetry must use the site's existing consent and analytics architecture and must not bypass applicable consent state; do not introduce additional tracking technology or personal data collection merely to satisfy this standard. Do not collect unnecessary personal data. Do not add telemetry merely to increase event volume; it should answer a specific product question, such as whether readers actually use contextual source records or complete scenarios.

**Reader outcome test.** Before publication, every guide should be able to answer: what can the reader now decide, recognise, investigate, explain, or do better because they completed this guide? If the answer is unclear, the guide may be informative but is not yet practitioner grade.

---

## Default treatment: merged-card Knowledge Hub format

The default for operational playbooks, financial crime typologies, investigation handbooks, control frameworks, practitioner decision guides, straightforward regulatory explainers, and procedural guidance, which is to say most guides. Reference implementations: `kyc-onboarding-dilemma.html` for interaction depth, `adverse-media-intelligence-guide.html` for the merged card implementation.

Beyond the Global core's mandatory floor (two worked scenarios with graded decision points, knowledge check, Risk/Signal/Response cards, Save as image export, FAQ, data-date, all still required here, this treatment does not relax them), the following remain content-dependent, included only where content need and practitioner utility justify them, not by default and not because another guide happens to contain them:
- An animated stat strip where real evidence justifies it.
- A process-flow diagram where the content is genuinely sequential.
- A structure or relationship diagram beyond what Worked decisions already requires.
- A real named case study where one exists and can be accurately cited; a clearly labelled composite/illustrative case is acceptable where no real citable case exists.
- A counterfactual interaction, per the Guide Quality Layer.
- Learner confidence capture, per the Guide Quality Layer.

Standard Knowledge Hub card layout and navigation chrome, no experimental shell.

---

## Evidence Essay treatment (optional, per-guide)

A separate, explicitly opt-in presentation, not a default, not a shell to reach for automatically, and not a premium or automatically superior version of a normal guide. Select it only where evaluating the evidence chain is materially part of evaluating the guide's central conclusion, against these criteria, not as an upgrade applied by habit:

- The guide advances an original or contested thesis.
- Source limitations materially affect the conclusion.
- Several important claims need precise evidence mapping for a reader to evaluate them.
- Regulatory interpretation requires sustained reasoning, not a single citation.
- Competing interpretations need to be evaluated.
- Contextual source inspection materially improves the reader's ability to assess the argument.

Selection should normally satisfy at least two of the criteria above, including at least one drawn from evidential complexity, regulatory interpretation, source limitations, competing interpretations, or contested reasoning. A single loosely-fitting criterion is not enough on its own.

**Decision rule: if the sources merely support the guide rather than forming part of the reader's reasoning task, use the Default Knowledge Hub treatment instead.**

**Proportionality: the expected reader value must justify this treatment's additional build, sourcing, interaction, and review cost.** It costs more on all four fronts than the Default treatment; do not select it where that additional cost is not earned.

Reference implementations: `gambling-white-label-blind-spot-guide.html`, `classification-asymmetry-guide.html`.

**Shell.** A three-column adaptive layout: a sticky contents rail (left), the editorial column (centre, the actual article), and a source-record rail (right) that displays contextual detail for whichever citation the reader last clicked.

**Contextual source records remain specific to Evidence Essay, not a Global core requirement,** unless a future explicit standards decision promotes them into the Global core. Do not add this pattern to a Default-treatment guide without first making that decision explicitly.

**Mobile behaviour.** The source-record rail collapses out of the three-column layout below the 800px breakpoint. Clicking a citation reparents the single source-panel node (never duplicated) to sit inline immediately after the clicked citation's containing element. The panel's resting/default position, before any citation is clicked, is after all article content; this is correct, documented behaviour, not a defect. When the viewport returns above the desktop breakpoint, the required behaviour is that the source panel restores to its desktop rail position without duplication, state loss, or layout instability.

---

## Shared component principle

Both treatments may reuse proven FinCrimeRadar components where they improve comprehension: process flows, native FAQ disclosure, Risk/Signal/Response cards, Canvas 2D export, scenario interactions, knowledge checks, structure and relationship diagrams, and existing responsive navigation patterns. Reuse the existing component family instead of building a treatment-specific duplicate.

A component belongs in a guide because it improves understanding, judgement, investigation capability, or practitioner utility. Template completeness alone is not a reason to include it.

---

## Evidence freshness

Where regulatory or evidential freshness matters, distinguish publication date, editorial update date, and regulatory or source verification date. Do not imply an old regulatory proposition is current merely because surrounding prose was recently edited. Use this only where freshness materially affects practitioner trust or interpretation.

---

## Evidence uncertainty

Where evidence is genuinely uncertain, preserve that uncertainty; do not convert ambiguity into artificial certainty for visual simplicity. Where useful, distinguish primary authority confirmed, official guidance, specialist secondary evidence, estimate, and illustrative scenario. Do not turn every paragraph into a badge system, use uncertainty treatments only where they materially help the reader assess evidence quality.

---

## Avoid interaction overload

This standard is not permission to add more interactions to every guide. FinCrimeRadar already has a mature interaction system; the priority is better reasoning interactions, not more interaction volume.

A strong interaction sequence where appropriate: **Scenario → Decision → Confidence → Reasoning → Change one fact → Reconsider.** Do not require this exact sequence where the subject matter does not justify it.
