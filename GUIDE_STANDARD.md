# Guide Standard

**This document is the canonical source for guide structure, presentation, and the treatment-independent Guide Quality Layer.** Do not duplicate these requirements in `CLAUDE.md` or `BACKLOG.md`. Sourcing, the verification ledger, and adversarial review requirements are defined in `CLAUDE.md`; this document references them, it does not restate them. Unfinished work, retrofit queues, and open decisions against this standard live in `BACKLOG.md`, not here.

FinCrimeRadar separates two concepts: a **public format** and a **rendering treatment**. Public format tells the reader what kind of work they are using. Rendering treatment tells the implementation how that work is presented. The same Knowledge Hub shell can support multiple public formats without creating separate page systems.

## Publication architecture

FinCrimeRadar publications are governed through four conceptual layers. These are layers of governance, not four (or five) separate rendering systems or code paths.

1. **Universal Evidence Core.** The non-negotiable quality floor every substantial publication meets, regardless of public format or rendering treatment. Defined below.
2. **Intelligence Core.** The analytical spine every substantial publication states explicitly: the practitioner question it resolves, the evidence state behind its conclusion, the decision it supports, its material uncertainty, what would change the assessment, and what the reader can now do. Defined below.
3. **Public Format Contract.** The recurring analytical primitives a chosen public format (Guide, Framework, Case File, Intelligence Brief, Evidence Essay) carries once selected. A primitive earns a place in a format's contract by proving it recurs, not by appearing once in a single reference implementation.
4. **Subject Specific Composition.** The implementation choices one specific publication makes to serve its own subject: scenario facts, a named case study, an exact component layout, a specific interaction sequence. These stay specific to that publication and are never promoted into a format contract merely because they exist in one reference implementation.

A publication's rendering treatment presents its Public Format Contract, which sits on top of its Intelligence Core, which sits on top of the Universal Evidence Core. Subject Specific Composition is what makes each publication distinct within that structure. The layering is conceptual, and exists to keep decisions at the right altitude, not to create a fifth template.

| Public format | Rendering treatment | Current maturity |
| --- | --- | --- |
| Guide | Default Knowledge Hub | Standing |
| Framework | Default Knowledge Hub with decision or control compositions | Experimental pending a second Framework implementation |
| Case File | Default Knowledge Hub with investigative compositions | Accepted composition |
| Intelligence Brief | Default Knowledge Hub with temporal and comparison compositions | Accepted composition |
| Evidence Essay | Evidence Essay | Standing opt-in treatment |

This is not a five-template system. Framework, Case File, and Intelligence Brief are candidate compositions within the Default Knowledge Hub treatment, not separate rendering systems. Following the completed cross-experiment review of Experiments 01 to 03, Case File and Intelligence Brief are accepted compositions: each proved its analytical contract through a real publication, and neither requires a second instance before acceptance. Framework remains experimental because Experiment 01, the APP Scam Decision Framework, is still its only implementation; a second Framework publication is required to test whether its contract genuinely recurs rather than reflecting one subject's specific reasoning. The table records the current approved architecture, not a promise that every future publication in an accepted composition will look identical to its first instance. Every publication still follows the **Universal Evidence Core** and the **Intelligence Core** below. Existing publications are not retrofitted merely to adopt these labels.

---

## Universal Evidence Core

This is the Global core referred to elsewhere in this standard. It applies to every substantial publication regardless of public format or rendering treatment and defines the minimum FinCrimeRadar quality floor. A format or treatment may change how a publication delivers this standard, it must never silently lower it; every requirement below is mandatory, not a menu.

**Claim sourcing.** Every material claim gets a real source or honest epistemic framing; illustrative figures get no citation. Fully governed by `CLAUDE.md`'s Published content sourcing section, not restated here.

**Human practitioner writing.** Every guide reads like work written by an experienced human financial crime practitioner, not generated prose. Fully governed by `CLAUDE.md`'s Human writing standard, not restated here.

**Brand, metadata and navigation consistency.** New components use namespaced classes and are checked against `brand.css`'s generic selectors and `brand.js`'s watched selectors before shipping, governed by `CLAUDE.md`'s Component isolation rule. Every guide carries standard `Article` and `BreadcrumbList` structured data and the standard Knowledge Hub navigation chrome, no experimental shell for these elements.

**Worked decisions.** Every new guide requires at least two distinct worked scenarios, each with a decision point offering graded multiple-choice options and full reasoning revealed after the analyst chooses, plus a structure or relationship diagram where the content has one to show. A scenario should be materially distinct in facts, decision context, risk mechanism, or practitioner judgement; cosmetic changes to the same underlying fact pattern do not satisfy the requirement. Counterfactual reasoning may deepen an existing scenario but does not count as a separate scenario and cannot substitute for the two-scenario minimum. Scenario verdict and feedback text must follow the Source, Application, Action distinction defined in the Guide Quality Layer below.

**Risk/Signal/Response.** A merged, unified card design, not a table, not two separate card types: icon, memorable metaphor-style name, one short explanatory line, then three compact labelled lines (Risk / Signal / Response). One component, two placements, renders inline in the guide body at the point each pattern is introduced, and the identical set regroups into a grid at the very end as the closing summary.

**Knowledge check.** Multi-question, live scoring. Where a guide includes a real named case study, at least one question must test a genuine detail or lesson from that specific case, not a generic guide concept.

**FAQ.** An accordion as a standard closing section, native `<details>`/`<summary>`, not a custom JS toggle.

**Summary export.** A "Save as image" button stays permanent, exporting the closing Risk/Signal/Response card grid via Canvas 2D, not a table. This is a separate, already-standing feature, unaffected by what follows.

**Social card.** The standard requirement for every published guide is a programmatically generated Open Graph / social card, built from a reusable template rather than bespoke per guide: sitewide branding, the guide's series label where it has one, guide number where applicable, guide title, one short analytical subtitle, `fincrimeradar.org`, standard OG dimensions, accessible contrast, and no embedded statistic or claim that would need its own separate verification. Regenerate it whenever the guide's title or subtitle changes materially (see `CLAUDE.md`'s Derived asset synchronisation rule, which this card falls under). A bespoke infographic remains an optional enhancement where a guide's subject genuinely benefits from one (architecture, transaction flow, intervention points), never a publication blocker; where a guide does carry one, it still needs external generation against a fixed template, compression to keep clear of the working ceiling (roughly 400KB), a zoom check for compression artifacts before accepting, and its content verified against the live page before wiring in, every time it or the claims it depicts change.

**Accessibility.** `aria-live="polite"` on verdict and quiz-feedback containers, from the start, not added after a review catches its absence. Native disclosure (`<details>`/`<summary>`) for the FAQ, from the start. A skip-to-content link at the top of `<body>`, targeting the main content region. Logical heading order, accessible names on interactive elements, full keyboard operability, and respect for `prefers-reduced-motion`. See the Guide Quality Layer's Accessibility baseline below for the full WCAG 2.2 AA checklist this summarises.

**Mobile verification.** Real device-width verification is required, not a static CSS read-through and not a browser-window resize (confirmed non-functional in this project's working environment). Use iframe-based device-width emulation at a minimum of 320/375/390/428/768px. Any click-triggered dynamic behaviour (a reparented panel, a revealed verdict, an advancing decision tree) must be verified by actually triggering the interaction and checking the result, structurally and visually, not inferred from how the page looks at rest. A behaviour that cannot be verified in this environment gets reported honestly as unverified, not claimed as confirmed and not silently re-patched.

**data-date convention.** Every guide's Knowledge Hub card carries a `data-date` attribute.

**Sitemap.** Mandatory, no exceptions: every new guide's URL is added to `sitemap.xml` before the guide is considered shipped, matching the format and `<priority>` tier of the most recently added comparable guide. Confirm both the file addition and a fresh live-site check (not just the local working tree) before marking a guide's sitemap step complete.

**Adversarial review.** Fully governed by `CLAUDE.md`'s Regulatory claim review section and related checklist entries. Not restated here.

**Stale-asset synchronisation.** Fully governed by `CLAUDE.md`'s Derived asset synchronisation section. When a guide's content changes, every derived representation (summary image, metadata, structured data, social copy, stat strip figures, quiz/scenario text, closing cards, Knowledge Hub description) must be checked against the new content before publication.

---

## Intelligence Core

Every substantial publication states its Intelligence Core explicitly, in addition to meeting the Universal Evidence Core above. This is the publication's analytical spine, not a new mandatory section a reader must find; the elements below can live in the argument, an explicit context strip, an evidence-limitation note, or wherever the format naturally puts them, but each one must actually be answerable from the published page, not merely implied.

**Intelligence question.** The precise practitioner question the publication exists to resolve. Not a topic label ("failure to prevent fraud"); a question a reader could restate in one sentence ("was this control environment reasonable for the fraud risk that existed at the time").

**Evidence state.** What is established, provisional, an industry position, a FinCrimeRadar assessment, or unknown, where those distinctions materially affect how much weight a reader should give the conclusion. See Evidence vocabulary below for the standard labels. Do not force a label onto a claim where the distinction adds no practitioner value.

**Decision object.** The judgement, investigation, control response, or implementation decision the reader is being helped to make. This is what the Universal Evidence Core's Worked decisions requirement and the Guide Quality Layer's Reader outcome test already require a publication to serve; the Intelligence Core names it explicitly rather than leaving it implicit.

**Uncertainty.** The material unresolved facts, limitations, or missing evidence that constrain the conclusion. Governed alongside Evidence uncertainty below; state it honestly rather than converting it into false certainty for visual simplicity.

**Change condition.** The fact, evidence, or event that would materially change the conclusion or require reassessment. This is the shared analytical spine behind Red Team Questions, What Would Change My Decision, What Would Change Our Assessment, and an Evidence Essay's competing-interpretations and assessment-change analysis: one requirement, expressed through whichever challenge mechanism (see Challenge requirement below) actually fits the format and subject.

**Practitioner outcome.** What the reader should now be better able to decide, investigate, recognise, explain, implement, or monitor. This is the Guide Quality Layer's Reader outcome test, restated here as a required Intelligence Core element rather than a pre-publication check performed once and forgotten.

Do not build a dedicated visual component to display these six elements. Most publications already answer them somewhere in existing prose, the thesis, an evidence-limitation note, or a what-would-change-this section; the requirement is that the answer exists and is findable, not that it takes a new fixed shape.

### Evidence vocabulary

Where the distinction materially affects how a reader should weigh a claim, use these five epistemic states consistently.

**Established.** Directly supported by current authoritative evidence: the statute, an in-force regulation, a reported judgment, official guidance currently in effect.

**Provisional.** Published or proposed material whose final form, implementation, or consequence remains unresolved: a consultation, a draft, a de facto standard awaiting formal adoption, guidance expected but not yet issued.

**Industry position.** A documented interpretation, proposal, or operational position from an industry participant or representative body, not from a regulator or legislature.

**FinCrimeRadar assessment.** An analytical conclusion FinCrimeRadar produced from the available evidence: a practitioner framework, a synthesis, a judgement about how facts likely apply. FinCrimeRadar analysis must never be presented as though it were the authoritative source's own wording or a mandatory conclusion the authority itself established; this is the Guide Quality Layer's Source, Application, Action distinction applied at the evidence-state level, not a second standard.

**Unknown.** A material fact needed for a stronger judgement is unavailable or cannot currently be verified. State this honestly rather than filling the gap with a plausible-sounding assumption.

Do not force these five labels into a publication where the distinctions add no practitioner value; a straightforward procedural guide with no contested or time-sensitive claims does not need an evidence-state badge on every paragraph. Use them where a reader's confidence in a conclusion should genuinely vary claim by claim.

---

## Guide Quality Layer

Treatment-independent. Applies whether a guide uses the Default Knowledge Hub treatment or Evidence Essay, and strengthens the Global core above without replacing or weakening it.

**Originality gate.** Before substantive drafting, establish what practitioner value the guide contributes beyond regulator summaries, generic compliance articles, and existing search results. Contribute at least one meaningful differentiator: original practitioner judgement, a decision framework, a structured investigation method, a regulatory comparison, a failure mode analysis, a unique scenario model, an evidence synthesis, or an operational control framework. If the guide cannot articulate a meaningful practitioner gain, the angle needs further development before publication. Rewording existing sources is not originality.

**Regulatory context.** Where relevant, provide compact context identifying jurisdiction, the relevant legal or regulatory regime, the intended practitioner audience, the verification or evidence date, material scope limitations, and whether the subject is particularly change-sensitive. Do not add this where it creates visual clutter for guides where it adds no value.

**Source, Application, Action distinction.** For legally or regulatorily sensitive teaching points, keep three layers visibly separate: **Source**, what the authority expressly establishes; **Application**, how FinCrimeRadar applies that authority to the facts or scenario; **Action**, the operational response or practitioner consideration FinCrimeRadar recommends. Never present FinCrimeRadar's own inference as though it were the precise wording or mandatory conclusion of the cited authority. This is the reader-facing form of the accuracy discipline already defined in `CLAUDE.md`'s Scenario reasoning section; it does not create a second standard, it applies that one to guide prose and scenario copy specifically.

**Counterfactual scenario reasoning.** Where a scenario contains a genuinely decision-determining fact, consider a counterfactual step after the initial reasoning: change one material fact and ask whether the decision changes. Examples: ownership moving from below to above a relevant threshold, a subject changing from a non-qualifying public role to one that satisfies a legal definition, an isolated transaction becoming a repeated behavioural pattern, source-of-funds evidence becoming independently corroborated, control rights changing without a corresponding ownership change. The purpose is to teach which facts actually drive the judgement. Do not add a counterfactual where changing the fact would teach nothing.

**Challenge requirement.** A substantial analytical publication exposes its important reasoning to challenge through at least one suitable mechanism where applicable: Red Team Questions, Competing Hypotheses, Competing Interpretations, Counterfactual reasoning (above), What Would Change My Decision, or What Would Change Our Assessment. These are the format-specific instances of the Intelligence Core's Change condition element; picking one is the requirement, not building all of them. Do not manufacture artificial disagreement merely to satisfy this rule; a publication with no genuinely contested reasoning to challenge does not need one invented.

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

### Framework contract

Framework is used when the primary reader job is to reach and defend a difficult judgement through structured analysis. The publication uses the Default Knowledge Hub shell and adds only the decision compositions the subject actually justifies. It is not a separate template or rendering system.

Framework remains experimental: Experiment 01, the APP Scam Decision Framework, is still its only implementation. `app-scam-decision-framework.html` remains a reference implementation, not a fixed template. A second Framework publication is required to test whether the contract below genuinely recurs, rather than reflecting one subject's specific reasoning.

Retain these as candidate recurring Framework primitives where the subject justifies them:

- Sequential decision stages.
- A structured Decision Record separating facts, assumptions, indicators, mitigants, decision, and rationale.
- Full Source, Application, and Action reasoning.
- Red Team Questions that test the defensibility of the judgement.
- A static What Would Change My Decision analysis.
- A Practitioner Lens or other limited, optional progressive disclosure.
- A compact operational summary suitable for practitioner reference.

Do not treat APP scam specific analytical constructs (for example the Four Verdict Problem, the Nominal Performance Trap, or the Consumer Standard of Caution logic) as universal Framework requirements; they are Subject Specific Composition for that publication. Material reasoning and conclusions must remain present in the initial HTML and must not depend on completing an interaction. Do not build a generic Framework renderer.

### Case File contract

Case File is an accepted composition, used when the reader must investigate incomplete, changing, or conflicting facts and determine which explanation best fits the evidence. The publication uses the Default Knowledge Hub shell and adds only the investigative compositions the subject justifies. It is not a separate template or rendering system.

`money-mule-or-victim-case-file.html` remains a reference implementation, not a fixed template. A second Case File is not required for the format to remain accepted.

The recurring analytical contract should normally cover:

- An initial investigative question.
- Progressive evidence disclosure.
- A chronology where sequence matters.
- Competing hypotheses.
- An evidence-status model distinct from hypothesis status.
- Decision points requiring practitioner judgement.
- A final evidence position.
- A final Decision Record.
- A challenge to the preferred conclusion.
- Practitioner actions and their consequences.

Do not standardise Experiment 02's exact twelve stages, exact five hypotheses, or its specific state machine; those are Subject Specific Composition for that publication, not universal Case File requirements. Do not build a generic Case File renderer or a generic hypothesis engine.

### Intelligence Brief contract

Intelligence Brief is an accepted composition, used when a subject is evolving and practitioners need to understand what changed, what is settled, what remains unresolved, and when action is appropriate. The publication uses the Default Knowledge Hub shell and adds only the temporal and comparison compositions the subject justifies. It is not a separate template or rendering system.

`fatf-recommendation-16-intelligence-brief.html` remains a reference implementation, not a fixed template. A second Intelligence Brief is not required for the format to remain accepted.

The recurring analytical contract should normally include:

- A dated intelligence assessment.
- An evidence checked date.
- A current assessment status.
- A clear distinction between settled and unresolved material.
- An intelligence timeline where the subject's chronology matters.
- Operational or control implications.
- A decision horizon.
- The next material trigger that would prompt reassessment.
- A static What Would Change Our Assessment analysis.
- Worked practitioner decisions where actual judgement is materially relevant to the subject.

Do not treat Recommendation 16 specific content or its exact component layout as universal Intelligence Brief requirements; they are Subject Specific Composition for that publication. Do not build a generic Intelligence Brief renderer.

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

## Temporal intelligence

For a materially change-sensitive subject, publication date alone is not sufficient temporal intelligence. Applicable subjects include regulatory change, sanctions, enforcement, emerging typologies, technology, and policy or implementation guidance. Where a subject is materially change-sensitive, identify:

- **Evidence checked date.** When the underlying evidence was last verified, distinct from when the surrounding prose was last edited.
- **Current assessment.** What the publication concludes given the evidence as it stood on that date.
- **Material unresolved issue.** What remains genuinely open and could change the conclusion.
- **Next known trigger.** A specific, named event or publication expected to resolve or move the issue, where one is known.
- **Reassessment condition.** What would require the publication to be revisited, whether or not a trigger date is known.

This is the Intelligence Core's Evidence state, Uncertainty, and Change condition elements, applied specifically to time-sensitive subjects; it does not create a second, separate temporal framework. Do not imply an old regulatory proposition is current merely because surrounding prose was recently edited. Use this only where freshness materially affects practitioner trust or interpretation, not on every publication regardless of subject.

---

## Evidence uncertainty

Where evidence is genuinely uncertain, preserve that uncertainty; do not convert ambiguity into artificial certainty for visual simplicity. Where distinguishing claims by confidence helps the reader, use the Evidence vocabulary above rather than inventing a second labelling scheme. Do not turn every paragraph into a badge system, use uncertainty treatments only where they materially help the reader assess evidence quality.

---

## Avoid interaction overload

This standard is not permission to add more interactions to every guide. FinCrimeRadar already has a mature interaction system; the priority is better reasoning interactions, not more interaction volume. Do not add interactive state or a component merely because another publication already has it; each publication's interaction choices are Subject Specific Composition, introduced only where they materially improve the reader's intelligence task, not a template every publication fills in.

A strong interaction sequence where appropriate: **Scenario → Decision → Confidence → Reasoning → Change one fact → Reconsider.** Do not require this exact sequence where the subject matter does not justify it.
