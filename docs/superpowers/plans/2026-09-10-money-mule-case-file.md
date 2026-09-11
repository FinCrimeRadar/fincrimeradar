# Money Mule or Victim? Case File Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Content source of truth:** The full frozen specification (all 43 sections, verbatim) lives at `docs/superpowers/plans/2026-09-10-money-mule-case-file-spec.md`. Every task below tells you exactly which spec section(s) supply the literal editorial copy for that task. Read the cited section(s) from that file before writing the corresponding data object. Do not paraphrase, summarise, shorten or improve the wording; transcribe it into the data structures described below.

**Goal:** Build "Money Mule or Victim?", FinCrimeRadar's first **Case File** (a new content archetype distinct from Guide and Framework): a 12-stage, gated, stateful investigative experience where a practitioner classifies a synthetic money-mule case against five persistent hypotheses as evidence is progressively disclosed.

**Architecture:** One static HTML shell (`money-mule-or-victim-case-file.html`) carrying only Stage 1's orientation essay and site chrome in the initial DOM. A pure-data JS module (`js/money-mule-case-file-data.js`) holds every stage's evidence, hypothesis text and narrative content as structured objects, never as HTML strings. A stateful engine (`js/money-mule-case-file.js`) owns a versioned `localStorage`-backed state machine, renders the current stage into `#caseFileApp` via DOM-builder functions (never `innerHTML`), and gates progression behind structured practitioner input. No backend, no query-parameter state, no free-text transmission.

**Tech Stack:** Vanilla ES5-style IIFE JavaScript (matches `js/site-chrome.js` and `js/app-scam-decision-framework.js`), native HTML controls (radio/checkbox/details), `localStorage`, existing `brand.css`/`brand.js`, existing consent-gated `gtag` telemetry pattern. Python static-contract checker (`scripts/check_money_mule_case_file.py`, mirrors `scripts/check_app_scam_framework.py`) plus a headless-Chrome CDP regression script (`scripts/test_money_mule_case_file_browser.py`, mirrors `scripts/test_app_scam_framework_browser.py`).

## Global Constraints

- British English throughout. No em dash (`—`, U+2014) or en dash (`–`, U+2013) anywhere in new HTML, JS, or JSON content (spec §39).
- Public format label is **Case File**. Never "Guide". Never "Framework" (spec §36, §1).
- No arbitrary score, percentage confidence, pass mark, or leaderboard anywhere (spec §39, §2).
- No hypothesis or Decision Record selection, and no free text, is ever transmitted via telemetry. Only stage-completion events and the single final reasoning-shift aggregate answer may be sent, gated on `fcr_cookie_consent_v2 === 'accepted'` (spec §23).
- No backend dependency, no new analytics package, no query parameters that alter case evidence, no admin/evidence-editing mechanism (spec §27).
- Future-stage evidence content must not exist anywhere in the initial `.html` document; it must live only in the JS data module and be rendered into the DOM only once its stage unlocks (spec §29).
- Reuse existing site chrome, tokens, and components; namespace all new CSS classes (prefix `mmc-`) and check them against `brand.css` bare-element/generic-class selectors and `brand.js` watched selectors before shipping (CLAUDE.md Component isolation rule; spec §30).
- WCAG 2.2 AA baseline: visible focus, no colour-only state signalling, native controls with programmatic state, keyboard operability, `prefers-reduced-motion` respected (spec §31).
- Every material regulatory/factual claim traceable to SRC01-09 (spec §34) via the existing `verification-ledger.json` mechanism; synthetic case facts are never cited to a real source (spec §35).
- Do not push, merge, or deploy. Do not modify `CLAUDE.md`, `AGENTS.md`, or `BACKLOG.md`'s historical entries beyond appending a new status entry at the end of the build (per repository convention; see Task 16).

---

## Repository-level decision flagged up front (read before starting)

`GUIDE_STANDARD.md` (lines 10-15 and the "Experiment 01 Framework contract" section starting at line 95) currently states that Framework remains "Experimental pending evaluation of Experiment 01 and, preferably, Experiment 02 as a second Framework implementation," and lists "Case File" as merely "**Proposed**" (not yet built). `methodology.html:177` makes the same claim publicly. The frozen spec for this experiment explicitly requires a **Case File**, architecturally incompatible with Framework's flowing-article contract (this is a gated, stateful, 12-stage investigation, not a second decision-gates article). Building this as instructed means:

1. Framework's own evaluation plan (a second Framework data point) remains unmet by this build, it is not silently resolved.
2. Case File graduates from "Proposed" to "Experimental pending evaluation," and needs its own contract section in `GUIDE_STANDARD.md`, mirroring the existing Experiment 01 Framework contract section.

Task 13 below makes both of these facts explicit in the repository (updates the maturity table, adds an "Experiment 02 Case File contract" section, and corrects `methodology.html`'s paragraph so it does not misstate which format was actually evaluated second). This is called out here, and again in the final completion report, so the user can correct course if this was not the intended sequencing.

---

## File structure

| File | Responsibility |
| --- | --- |
| `money-mule-or-victim-case-file.html` | New page. Head metadata (consent/gtag/FC block, JSON-LD, OG/Twitter, canonical), nav/breadcrumb/footer chrome, static Stage 1 orientation essay (spec §4, §5, §9), synthetic-case disclosure banner, empty `#caseFileApp` mount point, static Sources/Methodology and Related Intelligence sections. |
| `js/money-mule-case-file-data.js` | Pure data: `window.MMC_DATA = { stages: {...}, hypotheses: {...}, sources: {...} }`. No HTML strings. Holds every stage's copy (spec §10-§25). |
| `js/money-mule-case-file.js` | State machine, persistence, DOM-builder renderers, gating, telemetry, reset. IIFE, `'use strict'`. |
| `scripts/check_money_mule_case_file.py` | Static contract checker (Task 14). |
| `scripts/test_money_mule_case_file_browser.py` | Headless-Chrome CDP regression test (Task 15). |
| `knowledge.html` | New Knowledge Hub card + updated counts (Task 13). |
| `sitemap.xml` | New `<url>` entry (Task 13). |
| `content-relations.json` | Reciprocal related-content entries (Task 13). |
| `verification-ledger.json` | New claims for SRC01-09 (Task 12). |
| `GUIDE_STANDARD.md` | Maturity table + new Case File contract section (Task 13). |
| `methodology.html` | Corrected Framework/Case File evaluation paragraph (Task 13). |
| `BACKLOG.md` | New status entry documenting the build (Task 16). |

## Data schema (owned by `js/money-mule-case-file.js`)

```js
var STORAGE_KEY = 'fcr_case_money_mule_v1';
var CASE_VERSION = 1;

var DEFAULT_STATE = {
  caseVersion: CASE_VERSION,
  currentStage: 1,
  highestUnlockedStage: 1,
  hypothesisState: { A: 'Unresolved', B: 'Unresolved', C: 'Unresolved', D: 'Unresolved', E: 'Unresolved' },
  hypothesisSnapshots: { initial: null, final: null },
  knowledgeTimeline: { entryState: null, prePaymentThreeState: null, changePoint: null },
  controlDecision: null,
  voluntarinessDecision: null,
  decisionRecord: { activity: null, control: null, knowledge: null, exploitation: null, evidence: null },
  redTeamCompleted: {
    transactionBias: false, authenticationBias: false, outcomeBias: false,
    vulnerabilityBias: false, culpabilityBias: false, narrativeBias: false,
    suspicionThreshold: false, corroboration: false, counterfactual: false, proportionality: false
  },
  decisionChangeSelections: {
    item1: false, item2: false, item3: false, item4: false,
    item5: false, item6: false, item7: false, item8: false, item9: false
  },
  reasoningShift: null,
  caseCompleted: false
};
```

Hypothesis states are one of `['Leading', 'Plausible', 'Unresolved', 'Weak']`. Timeline values are one of `['Unaware', 'ConcernEmerging', 'Suspicious', 'LikelyAware', 'CannotDetermine']`. `controlDecision`/`voluntarinessDecision` are one of `['Yes', 'No', 'CannotDetermine']`. `reasoningShift` is one of `['Substantially', 'Somewhat', 'NoMaterialChange']`.

**Validation on load:** `loadState()` reads `localStorage.getItem(STORAGE_KEY)`, `JSON.parse`s inside `try/catch`, and calls `isValidState(parsed)` which checks: `parsed.caseVersion === CASE_VERSION`, every top-level key in `DEFAULT_STATE` is present with the right JS `typeof`, `hypothesisState` has exactly keys A-E each one of the four allowed strings, and every nested boolean map has exactly its expected keys as booleans. Any failure (parse error, version mismatch, shape mismatch) returns a **fresh deep copy** of `DEFAULT_STATE` and does not throw.

**Timeline point reveal map** (implementation decision, not explicit in the spec, documented here so it does not need re-deriving): the nine timeline points from spec §14 unlock as follows:
- Stage 6 unlock: `Initial Recruitment`, `Payment One`, `Payment Two`, `Concern Emerges`, `Payment Three`.
- Stage 7 unlock (added): `Attempted Exit`, `Threats`, `Payment Four`, `Intervention`.

**Decision Record option sets** (implementation decision, spec leaves the exact control open): five single-select `<fieldset>`/radio groups, neutral labels, no option pre-marked as correct:
- Activity: `Confirmed`, `Partially confirmed`, `Not established`, `Cannot determine`.
- Control: `Strongly established`, `Partially established`, `Not established`, `Cannot determine`.
- Knowledge: `Established from entry`, `Developed during the timeline`, `Not established`, `Cannot determine`.
- Exploitation: `Materially supported`, `Some indicators, not conclusive`, `Not supported`, `Cannot determine`.
- Evidence: `Strong across all dimensions`, `Strong for some, incomplete for others`, `Weak overall`, `Cannot determine`.

After the practitioner records all five, reveal FinCrimeRadar's own analysis (spec §19 verbatim text) per dimension immediately beneath the practitioner's own choice, for comparison, never as a "correct answer" marker.

## Telemetry contract (exhaustive allow-list)

Only two event names may ever be passed to `gtag('event', ...)`, both gated behind `consentGranted()` (copy the exact function from `js/app-scam-decision-framework.js`):
- `case_file_stage_complete` with params `{ case_id: 'money_mule_or_victim', stage: <1-12> }`, fired once per stage advance.
- `case_file_reasoning_shift` with params `{ case_id: 'money_mule_or_victim', shift: <'Substantially'|'Somewhat'|'NoMaterialChange'> }`, fired once when the Stage 11 final question is answered.

No other `gtag('event', ...)` call may exist in `js/money-mule-case-file.js`. No hypothesis, Decision Record, timeline, or red-team value is ever passed to `gtag`.

---

### Task 1: Page shell, head metadata, and Stage 1 Orientation (static, no JS engine yet)

**Files:**
- Create: `money-mule-or-victim-case-file.html`
- Reference: `docs/superpowers/plans/2026-09-10-money-mule-case-file-spec.md` §4, §5, §9 (literal copy)
- Reference pattern: `app-scam-decision-framework.html` (head block, nav, breadcrumb, footer wiring, CSS token reuse)

**Interfaces:**
- Produces: the DOM contract every later task's JS depends on: `<div id="caseFileApp"></div>` mount point, `<button id="openCaseFile">Open Case File</button>`, `<div id="mmcDisclosure">` (spec §5 text), `<nav>`/breadcrumb identical structure to `app-scam-decision-framework.html` but with breadcrumb label "Money Mule or Victim?" and `kh-format-label`-equivalent text "Case File".

- [ ] **Step 1: Copy the head block, nav, breadcrumb, and footer wiring verbatim in structure from `app-scam-decision-framework.html`**, updating: `<title>`, meta description, canonical/og:url to `https://fincrimeradar.org/money-mule-or-victim-case-file.html`, `og:image` to a not-yet-created `money-mule-or-victim-case-file-social-card.png` (flag as a follow-up asset, do not block on generating it), JSON-LD `Article.headline`/`description`/`articleSection` (use `"Case File"` for `articleSection`, not `"Framework"`), and `BreadcrumbList` third item to this page.

- [ ] **Step 2: Write the page-local `<style>` block**, namespaced `mmc-` (mirror `fcr-` conventions from `app-scam-decision-framework.html`'s CSS almost line for line: same tokens, same `:focus-visible` rule, same `@media (prefers-reduced-motion: reduce)` block, same print block). Add: `.mmc-disclosure` (persistent banner style, high-contrast border, not colour-only), `.mmc-progress` (stage stepper, flex-wrap for mobile), `.mmc-stage` (stage content container), `.mmc-hypothesis-board`, `.mmc-evidence-card`, `.mmc-evidence-status` (icon glyph, e.g. `◆ Corroborated`, `○ Unknown`, `● Observed`, `◐ Self Reported`, `◇ Inferred`, each a distinct Unicode glyph plus text label, never colour alone), `.mmc-timeline` (as an `<ol>`, no absolute positioning requiring drag), `.mmc-decision-record`, `.mmc-radar`.

- [ ] **Step 3: Write the full Stage 1 orientation content as static HTML** inside `<section id="mmcOrientation">`, transcribing spec §4 verbatim (every heading and paragraph from "Money Mule or Victim?" through "The investigative principle"), then spec §5's synthetic disclosure in `<div id="mmcDisclosure" role="note">`, then the Stage 1 framing line from spec §9 ("The alert looks straightforward. The investigation will not be.") and the `<button id="openCaseFile" class="mmc-action" type="button">Open Case File</button>`.

- [ ] **Step 4: Add the JS-required notice and mount point.** After the orientation section: `<noscript><div class="mmc-noscript">This investigation requires JavaScript to progress beyond orientation. All reasoning above remains fully readable without it.</div></noscript>`, then `<div id="caseFileApp" data-stage-root hidden></div>` (starts `hidden`; Task 2's engine un-hides it once the shell mounts).

- [ ] **Step 5: Add empty Sources/Methodology and Related Intelligence static sections** (`<section id="sources">`, `<section id="related">`) as placeholders with correct `id`s and heading structure only; Task 12 fills in the source list, Task 13's related-content task fills the related links. This keeps heading order and anchor structure stable from the start.

- [ ] **Step 6: Wire script tags** at the end of `<body>`: `<script src="/js/money-mule-case-file-data.js"></script>` then `<script defer src="/js/money-mule-case-file.js"></script>` then the existing `<script defer src="/js/site-chrome.js"></script>` and `<script defer src="/brand.js"></script>`, matching `app-scam-decision-framework.html`'s ordering (data file is not `defer` since the engine script depends on `window.MMC_DATA` existing synchronously before it runs; keep the data file as a plain non-deferred `<script>` immediately before the deferred engine script, or make the engine wait for `DOMContentLoaded` and load both as `defer` in document order, since `defer` scripts execute in order relative to each other; either works, pick the latter for consistency with the rest of the page's `defer` scripts).

- [ ] **Step 7: Create a stub `js/money-mule-case-file-data.js`** with `window.MMC_DATA = { stages: {}, hypotheses: {}, sources: {} };` and a stub `js/money-mule-case-file.js` with just `(function () { 'use strict'; document.getElementById('caseFileApp').hidden = false; }());` so the page loads end to end for a manual smoke check.

- [ ] **Step 8: Manual check.** Open the file locally (or via the project's existing local static-server convention used by `scripts/test_app_scam_framework_browser.py`, a `ThreadingHTTPServer` over the repo root) and confirm: page loads, one `<h1>`, skip link present and functional, orientation essay fully readable, "Open Case File" button visible, no console errors.

- [ ] **Step 9: Commit.**

```bash
git add money-mule-or-victim-case-file.html js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add Money Mule or Victim Case File page shell and orientation"
```

---

### Task 2: CaseFileShell engine — state, persistence, gating skeleton, CaseReset

**Files:**
- Modify: `js/money-mule-case-file.js`
- Modify: `money-mule-or-victim-case-file.html` (add a minimal Stage 2 stub target if needed for the manual check)

**Interfaces:**
- Consumes: `window.MMC_DATA.stages[n]` (may be empty stub objects for now; only stage 1's already-static content and a stage-2 placeholder are needed to prove the engine).
- Produces (for every later task to call): `CaseFileShell.getState()`, `CaseFileShell.advanceStage(stageCompleteData)`, `CaseFileShell.updateState(mutatorFn)` (applies `mutatorFn(state)`, persists, re-renders), `CaseFileShell.renderCurrentStage()`, `CaseFileShell.goToStage(n)` (only for `n <= highestUnlockedStage`, does not change `highestUnlockedStage`), `CaseFileShell.resetCase()`.

- [ ] **Step 1: Write `loadState()`, `saveState(state)`, `isValidState(candidate)`, `defaultState()`** exactly per the Data schema section above. `defaultState()` returns a fresh deep copy (`JSON.parse(JSON.stringify(DEFAULT_STATE))`) so mutation never corrupts the template.

- [ ] **Step 2: Manual malformed-state check before writing more code.** In a browser console on the loaded page: `localStorage.setItem('fcr_case_money_mule_v1', 'not json')`, reload, confirm no thrown error and state resets to stage 1. Then `localStorage.setItem('fcr_case_money_mule_v1', JSON.stringify({caseVersion: 0}))`, reload, confirm the same safe fallback. This is the manual equivalent of a failing test; do not proceed until both fall back safely.

- [ ] **Step 3: Implement `advanceStage()`**: increments `state.currentStage` by 1 (capped at 12), sets `state.highestUnlockedStage = Math.max(state.highestUnlockedStage, state.currentStage)`, persists, calls `emitAggregateEvent('case_file_stage_complete', { case_id: 'money_mule_or_victim', stage: state.currentStage })`, then `renderCurrentStage()`.

- [ ] **Step 4: Implement `goToStage(n)`**: no-ops if `n > state.highestUnlockedStage`; otherwise sets `state.currentStage = n` (does not touch `highestUnlockedStage`), persists, re-renders. This is what `CaseProgress` (Task 3+) will call for reviewing completed stages.

- [ ] **Step 5: Implement the `CaseReset` control.** A permanent `<button id="mmcResetCase">Reset Case</button>` plus an initially-`hidden` inline confirm row (`<span id="mmcResetConfirm" hidden>Discard all progress? <button id="mmcResetYes">Yes, reset</button> <button id="mmcResetNo">Cancel</button></span>`), added to the page in Task 1's footer area of `#caseFileApp`'s wrapper (add the markup now in `money-mule-or-victim-case-file.html`, right after the mount point, so it's always present regardless of stage). Clicking Reset Case reveals the confirm row and hides the button; Cancel reverses that; "Yes, reset" calls `localStorage.removeItem(STORAGE_KEY)`, resets in-memory state to `defaultState()`, hides the confirm row, and re-renders at stage 1.

- [ ] **Step 6: Implement a minimal `renderCurrentStage()` dispatch** that clears `#caseFileApp`'s content (`while (root.firstChild) root.removeChild(root.firstChild);`, never `innerHTML = ''`) and calls a per-stage render function looked up from a `STAGE_RENDERERS` object keyed `1..12`. For this task, only wire a stub `STAGE_RENDERERS[2]` that renders a placeholder heading "Stage 2 placeholder" and a "Continue" button calling `advanceStage()`, just enough to prove the engine end to end. Stages 3-12 render "Not yet implemented" placeholders for now (later tasks replace each one).

- [ ] **Step 7: Wire `#openCaseFile`'s click handler** to un-hide `#caseFileApp`, hide/disable the orientation "Open Case File" button (so it is not re-clickable), and call `renderCurrentStage()` for the restored (or default) `currentStage`. On page load (before any click), if `loadState().currentStage > 1`, skip the button entirely and render directly, so reload resumes where the practitioner left off.

- [ ] **Step 8: Manual check.** Click Open Case File, confirm Stage 2 placeholder renders; click Continue, confirm Stage 3 placeholder renders and reload restores Stage 3; click Reset Case, confirm the two-step confirm flow, confirm-yes returns to Stage 1 orientation.

- [ ] **Step 9: Commit.**

```bash
git add js/money-mule-case-file.js money-mule-or-victim-case-file.html
git commit -m "feat: add Case File state engine, persistence, and reset control"
```

---

### Task 3: HypothesisBoard component + Stage 02 (Case Intake and Initial Assessment)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (add `MMC_DATA.hypotheses` and `MMC_DATA.stages[2]`)
- Modify: `js/money-mule-case-file.js` (add `HypothesisBoard` renderer, `STAGE_RENDERERS[2]`)
- Reference: spec §6 (five hypotheses, four states), §10 (all Stage 2 content, verbatim)

**Interfaces:**
- Produces: `renderHypothesisBoard(container, currentSelections, options)` — a reusable DOM builder used by every later stage that shows the board (Stages 2, 4, 5, 7, 9). `options.readOnly` (boolean, for Stage 5/9 comparison views that show snapshots rather than editable controls) and `options.suggested` (optional object of FinCrimeRadar's suggested starting positions, Stage 2 only, rendered as a distinct labelled row above the practitioner's own controls, never merged into them).
- Consumes: `CaseFileShell.updateState`, `CaseFileShell.advanceStage`.

- [ ] **Step 1: Populate `MMC_DATA.hypotheses`** as `{ A: {name:'Knowing Participation', description:'...'}, B: {...}, C: {...}, D: {...}, E: {...} }` transcribing spec §6's five definitions verbatim into `description`.

- [ ] **Step 2: Populate `MMC_DATA.stages[2]`** as a structured object (no HTML strings): `{ alert: {...fields from spec §10 "The Alert"...}, profile: {...fields from "Customer profile"...}, chronology: [ {day:1, incoming:{sender:'Sender A', amount:2850}, outgoing:{type:'transfer', beneficiary:'new', amount:2500}, timeToMove:'26 minutes'}, ... four entries ...], totals: {received:11420, moved:10200, difference:1220}, suggestedHypotheses: {A:'Plausible', B:'Unresolved', C:'Plausible', D:'Unresolved', E:'Plausible'}, practitionerLensCanEstablish: [...four bullet strings from spec §10...], practitionerLensCannotEstablish: [...five bullet strings...], practitionerLensClosing: 'Do not let the transaction pattern answer a customer intent question that has not yet been investigated.' }`.

- [ ] **Step 3: Implement `renderHypothesisBoard(container, state, options)`** in `js/money-mule-case-file.js`: for each of A-E, build a `<fieldset class="mmc-hypothesis">` with `<legend>` = name + description, and (unless `options.readOnly`) four native `<input type="radio" name="hyp-<id>" value="<state>">` labelled Leading/Plausible/Unresolved/Weak, checked to match `state.hypothesisState[id]`. On change, call `CaseFileShell.updateState(function(s){ s.hypothesisState[id] = value; })` (does not itself advance the stage). If `options.suggested` is present, render it as a separate, visually distinct, clearly-labelled `<div class="mmc-suggested-board">FinCrimeRadar's suggested starting position</div>` above the practitioner's own fieldsets, never pre-filling the radios.

- [ ] **Step 4: Implement `STAGE_RENDERERS[2]`**: render the Alert, Customer profile (including the "absence of a previously recorded vulnerability" callout), the transaction chronology as an accessible responsive table (`<table>` with `<caption>`, scoped `<th>`), the totals line, then `renderHypothesisBoard` with `options.suggested` set, then the Practitioner Lens block (can/cannot establish lists + closing line), then a `<button>Record initial assessment and continue</button>`.

- [ ] **Step 5: Gate the continue button** (`DecisionGate` behaviour): disabled until all five hypotheses have been explicitly set to something other than the initial default in state (track a separate `touched` flag per hypothesis in memory, since `'Unresolved'` is both a valid deliberate choice and the untouched default; simplest correct approach: require the practitioner to click each radio at least once, tracked via a local `Set` of touched hypothesis ids in the stage's closure, reset each time the stage is (re)rendered fresh vs restored from a state where snapshot already exists). On click: `CaseFileShell.updateState(function(s){ s.hypothesisSnapshots.initial = shallowCopy(s.hypothesisState); }); CaseFileShell.advanceStage();`.

- [ ] **Step 6: Manual check.** Reach Stage 2, confirm the suggested board is visually distinct from the practitioner's own controls, confirm the continue button stays disabled until all five are touched, confirm reload mid-stage-2 restores partial selections, confirm advancing freezes `hypothesisSnapshots.initial` correctly (inspect via `localStorage.getItem('fcr_case_money_mule_v1')`).

- [ ] **Step 7: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add HypothesisBoard and Stage 02 Case Intake"
```

---

### Task 4: EvidenceCard/EvidenceStatus components + Stages 03-04 (Evidence Inject 01-02)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[3]`, `MMC_DATA.stages[4]`)
- Modify: `js/money-mule-case-file.js` (`renderEvidenceCard`, `STAGE_RENDERERS[3]`, `STAGE_RENDERERS[4]`)
- Reference: spec §11 (Stage 3, verbatim), §12 (Stage 4, verbatim)

**Interfaces:**
- Produces: `renderEvidenceCard(container, { title, body, status })` where `status` is one of `['Observed','SelfReported','Corroborated','Inferred','Unknown']`, rendering the glyph+label pairing defined in Task 1's CSS, never colour-only.
- Consumes: `renderHypothesisBoard` (read-only mode not needed here; Stage 4 requires the board again with "Require Hypothesis Board confirmation before progression").

- [ ] **Step 1: Populate `MMC_DATA.stages[3]`**: `{ customerExplanation: {...paragraphs...}, provided: ['A screenshot of the original job advertisement.', ...], retainedFundsExplanation: '...', framingLine: 'At this point these documents establish what Customer R claims happened. They do not establish that the employment was genuine.', evidenceItems: [ {title:'Customer account of recruitment', status:'SelfReported'}, {title:'Job advertisement screenshot', status:'SelfReported', note:'authenticity not yet established'}, ... all six from spec §11 "Evidence classification" ...], hypothesisImpactNotes: {A:'Weakened slightly', B:'Still unresolved', C:'Strengthened', D:'Still uncertain', E:'Weakened if the customer's explanation is accurate'}, practitionerLens: {...verbatim...}, investigationActions: ['Verify company registration and trading history.', ... all seven from spec §11 ...] }`.

- [ ] **Step 2: Populate `MMC_DATA.stages[4]`** similarly from spec §12: digital-evidence paragraphs, the six evidence items with statuses (five `Observed`, one `Corroborated`), the core message callout, and the Practitioner Lens text.

- [ ] **Step 3: Implement `renderEvidenceCard`** as a small `<article class="mmc-evidence-card">` with `<h3>`, body paragraphs, and a `<span class="mmc-evidence-status" data-status="...">` containing the glyph and text label from Task 1's CSS map.

- [ ] **Step 4: Implement `STAGE_RENDERERS[3]`**: customer explanation prose, the "provided" list, the framing callout, a grid of `renderEvidenceCard` calls for each `evidenceItems` entry, a hypothesis-impact note block (plain text per hypothesis, not editable controls, just the "impact" narration), Practitioner Lens text, then the seven `investigationActions` rendered as plain **non-scored** checkboxes (local component state only, not persisted, not gated, purely reflective, per spec §11 "No selection should be marked correct or incorrect"), then a `<button>Continue</button>` with no gate requirement (this stage has no structured decision to complete beyond reading, matching the spec which requires no explicit gate here).

- [ ] **Step 5: Implement `STAGE_RENDERERS[4]`**: digital-evidence prose, evidence cards, the "Control has become clearer. Intent has not." callout (visually prominent, e.g. a `.mmc-callout`), Practitioner Lens text, then `renderHypothesisBoard` again (editable, no `suggested` this time), gated: continue button disabled until every hypothesis has been touched at least once during this stage's visit (same touched-tracking approach as Task 3 Step 5), calling `advanceStage()` on confirm.

- [ ] **Step 6: Manual check.** Confirm Stage 3's investigation-action checkboxes are inert (no grading UI, no persistence needed), confirm Stage 4's hypothesis board re-confirmation gate behaves like Stage 2's.

- [ ] **Step 7: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add EvidenceCard component and Stages 03-04"
```

---

### Task 5: DecisionGate comparison view + Stage 05 (Decision Point 01)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[5]` — mostly static framing copy, the comparison itself is computed, not authored data)
- Modify: `js/money-mule-case-file.js` (`renderHypothesisDiff`, `STAGE_RENDERERS[5]`)
- Reference: spec §13 (verbatim framing and banned-word list)

**Interfaces:**
- Produces: `renderHypothesisDiff(container, snapshotA, snapshotB, labelA, labelB)`, a reusable diff renderer used again in Stage 9.

- [ ] **Step 1: Implement `renderHypothesisDiff`**: for each of A-E, if `snapshotA[id] !== snapshotB[id]`, render a neutral sentence built from a template: `"Your assessment of " + MMC_DATA.hypotheses[id].name + " moved from " + snapshotA[id] + " to " + snapshotB[id] + "."` (matching spec §13's exact example phrasing pattern). If nothing changed for a given hypothesis, render nothing for it (not a "no change" filler line, to avoid five lines of noise when little changed) unless **no** hypothesis changed at all, in which case render one line: `"Your assessment did not change across any of the five hypotheses at this point."`

- [ ] **Step 2: Add a banned-word guard as a code comment and a matching assertion in Task 14's checker** (not runtime logic, since the renderer never emits these words by construction): never emit "Correct", "Incorrect", "Right", "Wrong", "Pass", "Fail", or "Score" anywhere in this renderer's output strings (spec §13).

- [ ] **Step 3: Implement `STAGE_RENDERERS[5]`**: heading "What changed?", `renderHypothesisDiff(container, state.hypothesisSnapshots.initial, state.hypothesisState, 'Initial assessment', 'Current assessment')`, then a `<button>Confirm and continue</button>` calling `advanceStage()` (no further gate condition; the practitioner has already made all required selections in Stages 2 and 4).

- [ ] **Step 4: Manual check.** Manipulate hypothesis state in Stages 2 and 4 to produce zero, one, and multiple changes; confirm Stage 5 renders each case correctly and never uses a banned word.

- [ ] **Step 5: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add hypothesis diff view and Stage 05 Decision Point 01"
```

---

### Task 6: CaseTimeline component + Stage 06 (Evidence Inject 03 and Timeline Assessment)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[6]`, `MMC_DATA.timelinePoints`)
- Modify: `js/money-mule-case-file.js` (`renderCaseTimeline`, `STAGE_RENDERERS[6]`)
- Reference: spec §14 (verbatim)

**Interfaces:**
- Produces: `renderCaseTimeline(container, revealedPointIds)` — renders `MMC_DATA.timelinePoints` (the full ordered list of nine, each `{id, label}`) as an `<ol class="mmc-timeline">`, but only points whose `id` is in `revealedPointIds` get their label text; unrevealed points render as an empty, disabled `<li aria-hidden="true"></li>` placeholder so the list length/order context exists without exposing what happens next (do not print "locked" or any partial title for these, since the spec is silent on whether a placeholder tick mark is acceptable and a blank marker is the safer reading of "do not expose future evidence content").

- [ ] **Step 1: Populate `MMC_DATA.timelinePoints`** as the ordered array of nine `{id, label}` pairs from spec §14: `initialRecruitment`, `paymentOne`, `paymentTwo`, `concernEmerges`, `paymentThree`, `attemptedExit`, `threats`, `paymentFour`, `intervention`.

- [ ] **Step 2: Populate `MMC_DATA.stages[6]`**: the full message-history narrative paragraphs (spec §14 "The messages change the picture"), the evidence-status list (seven items), the "Timeline Problem" callout, and the two timeline-assessment question labels plus their five allowed values (`Unaware`, `ConcernEmerging`, `Suspicious`, `LikelyAware`, `CannotDetermine`), plus the "At what point did Customer R's understanding materially change?" question (its answer options are the timeline point ids revealed so far: `initialRecruitment`, `paymentOne`, `paymentTwo`, `concernEmerges`, `paymentThree`).

- [ ] **Step 3: Implement `STAGE_RENDERERS[6]`**: narrative, evidence cards (reuse `renderEvidenceCard`), the Timeline Problem callout, `renderCaseTimeline(container, ['initialRecruitment','paymentOne','paymentTwo','concernEmerges','paymentThree'])` (the Task-plan-documented reveal map), then two `<fieldset>` radio groups for `knowledgeTimeline.entryState` and `knowledgeTimeline.prePaymentThreeState`, then a `<select>` (or radio group) for `knowledgeTimeline.changePoint`. Gate: continue button disabled until all three are set; on confirm, persist via `updateState` then `advanceStage()`.

- [ ] **Step 4: Manual check.** Confirm the `<ol>` renders nine list items with exactly five populated and four present-but-empty, confirm keyboard `Tab`/`Shift+Tab` moves through the populated items' focusable content (if any) without needing drag, confirm all three assessments persist and gate correctly.

- [ ] **Step 5: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add CaseTimeline component and Stage 06 timeline assessment"
```

---

### Task 7: Stage 07 (Evidence Inject 04 and Coercion Assessment)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[7]`)
- Modify: `js/money-mule-case-file.js` (`STAGE_RENDERERS[7]`)
- Reference: spec §15 (verbatim)

- [ ] **Step 1: Populate `MMC_DATA.stages[7]`**: the attempted-disengagement narrative, the eight-item evidence-status list, the "Did Customer R control Payment Four?" / "Does the available evidence establish that Payment Four was freely voluntary?" question pair (each answered `Yes`/`No`/`CannotDetermine`, rendered as two **separate** fieldsets per spec "Do not merge these questions"), the "Control and voluntariness are not the same thing" callout, and the five hypothesis-impact narration strings.

- [ ] **Step 2: Implement `STAGE_RENDERERS[7]`**: narrative, evidence cards, the two separate control/voluntariness fieldsets (bound to `state.controlDecision` / `state.voluntarinessDecision`), the callout, the hypothesis-impact narration, then `renderHypothesisBoard` again (editable, gated on all five touched, per spec "Require Hypothesis Board confirmation"). On confirm: persist `controlDecision`/`voluntarinessDecision` (must both be set, in addition to the hypothesis-touched gate) then `advanceStage()`. `advanceStage()`'s stage-6-to-7 transition is where the CaseTimeline's reveal set grows; no separate code path needed since `renderCaseTimeline` is called with the wider array directly inside `STAGE_RENDERERS[7]` and any later stage that re-shows the timeline for review.

- [ ] **Step 3: Manual check.** Confirm both questions are genuinely separate controls (cannot answer one and have it fill the other), confirm the combined gate (2 questions + 5 hypotheses touched) blocks continue correctly.

- [ ] **Step 4: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add Stage 07 coercion assessment"
```

---

### Task 8: Stages 08-09 (final evidence inject, freeze, and Final Hypothesis Assessment)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[8]`, `MMC_DATA.stages[9]`)
- Modify: `js/money-mule-case-file.js` (`STAGE_RENDERERS[8]`, `STAGE_RENDERERS[9]`)
- Reference: spec §16 (verbatim), §17 (verbatim)

- [ ] **Step 1: Populate `MMC_DATA.stages[8]`**: the external-corroboration narrative and the ten-item evidence-status list from spec §16, plus a closing note reproducing "After this point, freeze evidence disclosure" as visible practitioner-facing copy (e.g. "No further evidence will be introduced after this stage.") so the practitioner understands why Stage 9 asks for a final view.

- [ ] **Step 2: Implement `STAGE_RENDERERS[8]`**: narrative + evidence cards + the freeze notice + plain "Continue" button (no gate; nothing further to record here).

- [ ] **Step 3: Populate `MMC_DATA.stages[9]`**: just the instruction copy ("classify all five hypotheses again", comparison framing) — the comparison view itself reuses Task 5's `renderHypothesisDiff`.

- [ ] **Step 4: Implement `STAGE_RENDERERS[9]`**: `renderHypothesisBoard` (editable, gated on all five touched again for this final round), then on confirm: `updateState(function(s){ s.hypothesisSnapshots.final = shallowCopy(s.hypothesisState); })`, render `renderHypothesisDiff(container, state.hypothesisSnapshots.initial, state.hypothesisSnapshots.final, 'Initial assessment', 'Final assessment')` **below** the board once the practitioner confirms (so the sequence within the stage is: classify, confirm, then see the diff, then a second "Continue" advances to Stage 10) — implement this as a two-phase render within the same stage (`phase: 'classify' | 'review'`, tracked in a local closure variable, not persisted state, since revisiting the stage via `goToStage` should show the review phase again if `hypothesisSnapshots.final` is already set).

- [ ] **Step 5: Manual check.** Confirm the two-phase flow (classify → confirm → diff view → continue) works and that reloading mid-Stage-9 (before final confirm) does not lose the in-progress classification.

- [ ] **Step 6: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add Stage 08 evidence freeze and Stage 09 final hypothesis assessment"
```

---

### Task 9: DecisionRecord component + Stage 10 (Decision Record and Operational Decisions)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[10]`)
- Modify: `js/money-mule-case-file.js` (`renderDecisionRecord`, `STAGE_RENDERERS[10]`)
- Reference: spec §19 (verbatim FinCrimeRadar analysis text per dimension), §20 (verbatim operational-decisions copy)

**Interfaces:**
- Produces: `renderDecisionRecord(container, state, dimensionDefs)` where `dimensionDefs` is the five `{id, question, options, fincrimeradarAnalysis}` objects from the Data-schema section's "Decision Record option sets" above.

- [ ] **Step 1: Populate `MMC_DATA.stages[10]`**: the five dimension question/options/analysis objects (options are the plan's own neutral option sets documented above; `fincrimeradarAnalysis` text is spec §19's verbatim text per dimension), plus the five operational-decision blocks from spec §20 (Immediate account intervention, Recovery and network investigation, SAR consideration, Safeguarding assessment, National Fraud Database assessment) as static reference copy, plus the closing line "Account restriction, customer exit, SAR consideration, safeguarding and fraud database filing are separate decisions with different purposes and evidential questions."

- [ ] **Step 2: Implement `renderDecisionRecord`**: for each dimension, a `<fieldset>` with the question as `<legend>`, radio options bound to `state.decisionRecord[id]`; once a dimension has a selection, immediately reveal that dimension's `fincrimeradarAnalysis` text directly beneath it (per-dimension reveal, not all-or-nothing), never marking the practitioner's choice as right or wrong.

- [ ] **Step 3: Implement `STAGE_RENDERERS[10]`**: `renderDecisionRecord`, then (always visible, not gated separately) the five static operational-decision blocks and the closing line, then a `<button>Continue</button>` gated on all five `decisionRecord` fields being set.

- [ ] **Step 4: Manual check.** Confirm each dimension's analysis only appears after that dimension's own selection (not all five at once from the first pick), confirm the gate requires all five.

- [ ] **Step 5: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add DecisionRecord component and Stage 10"
```

---

### Task 10: RedTeamReview + DecisionChange components + Stage 11

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[11]`)
- Modify: `js/money-mule-case-file.js` (`renderRedTeamReview`, `renderDecisionChange`, `STAGE_RENDERERS[11]`)
- Reference: spec §21 (verbatim 10 questions), §22 (verbatim 9 items), §23 (verbatim final question, telemetry rule)

- [ ] **Step 1: Populate `MMC_DATA.stages[11]`**: the ten red-team questions keyed to the `redTeamCompleted` boolean keys from the Data schema (in the same order as spec §21), the nine "what would change my decision" items keyed `item1..item9` (in spec §22's order), and the three `reasoningShift` option labels/values.

- [ ] **Step 2: Implement `renderRedTeamReview`**: ten `<label class="mmc-redteam-item"><input type="checkbox">I have considered this.</label>` rows, each preceded by its question text, bound to `state.redTeamCompleted[key]`.

- [ ] **Step 3: Implement `renderDecisionChange`**: nine plain checkboxes (no correct/incorrect framing) bound to `state.decisionChangeSelections[itemN]`, preceded by the spec §22 explanatory line.

- [ ] **Step 4: Implement `STAGE_RENDERERS[11]`**: `renderRedTeamReview`, `renderDecisionChange`, then the final reasoning-shift `<fieldset>` (three radio options, spec §23), then a `<button>Continue</button>` gated on: all ten `redTeamCompleted` booleans true, AND `reasoningShift` set (the nine `decisionChangeSelections` are explicitly reflective/non-scored per spec, so they are **not** part of the gate, only tracked). On confirm: `updateState` sets `reasoningShift`, calls `emitAggregateEvent('case_file_reasoning_shift', { case_id: 'money_mule_or_victim', shift: state.reasoningShift })`, then `advanceStage()`.

- [ ] **Step 5: Manual check.** Confirm the continue button stays disabled until all ten red-team boxes are checked and a reasoning-shift option is chosen; confirm the nine decision-change checkboxes do **not** gate progression; confirm the `case_file_reasoning_shift` event only fires once, with only the allowed two fields, when consent is granted (toggle `fcr_cookie_consent_v2` in localStorage and watch the Network tab for the `gtag`/GA4 collect request, or intercept `window.gtag` calls via console).

- [ ] **Step 6: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add RedTeamReview, DecisionChange components and Stage 11"
```

---

### Task 11: RadarView component + Stage 12 (final reveal)

**Files:**
- Modify: `js/money-mule-case-file-data.js` (`MMC_DATA.stages[12]`)
- Modify: `js/money-mule-case-file.js` (`renderRadarView`, `STAGE_RENDERERS[12]`)
- Reference: spec §24 (verbatim), §25 (verbatim)

- [ ] **Step 1: Populate `MMC_DATA.stages[12]`**: the five radar dimension summaries (spec §24), the central conclusion arrow-sequence line, and the full "Final FinCrimeRadar analysis" text from spec §25 (Case Conclusion, FinCrimeRadar Principle, closing question, closing line).

- [ ] **Step 2: Implement `renderRadarView`**: a `<div class="mmc-radar">` grid of five `<div>` blocks (Activity/Control/Knowledge/Exploitation/Evidence), each with its heading and one-line summary text.

- [ ] **Step 3: Implement `STAGE_RENDERERS[12]`**: gate check first — if `!state.reasoningShift` (i.e. Stage 11 was never actually completed, defensive check even though normal navigation cannot reach here otherwise), render nothing but a message directing back to Stage 11; otherwise render `renderRadarView`, the central conclusion line, the full Final FinCrimeRadar analysis text, and set `state.caseCompleted = true` via `updateState` on first render of this stage (idempotent, only fires the state write once).

- [ ] **Step 4: Manual check.** Confirm Stage 12 is unreachable via `goToStage(12)` unless Stage 11 was genuinely completed (test by trying to call `CaseFileShell.goToStage(12)` from the console at Stage 6 and confirming it no-ops per Task 2's `highestUnlockedStage` guard), confirm the full analysis text renders correctly, confirm `caseCompleted` persists.

- [ ] **Step 5: Commit.**

```bash
git add js/money-mule-case-file-data.js js/money-mule-case-file.js
git commit -m "feat: add RadarView component and Stage 12 final reveal"
```

---

### Task 12: SourcePanel, static Sources/Methodology section, Related Intelligence, verification ledger

**Files:**
- Modify: `money-mule-or-victim-case-file.html` (fill in the `#sources` and `#related` placeholder sections from Task 1)
- Modify: `js/money-mule-case-file-data.js` (add `MMC_DATA.sources`, wire `data-src="N"` citation markers into stage narrative fields wherever a material claim from SRC01-09 is used)
- Modify: `verification-ledger.json`
- Reference: spec §34 (nine sources, verbatim titles/dates/uses), §35 (sourcing rules), CLAUDE.md §4-5 (sourcing workflow), existing `verification-ledger.json` claim shape (see `app-scam-decision-framework.*` claims for the exact JSON shape to match: `claimId`, `guide`, `claimText`, `claimType`, `source`, `status`)

- [ ] **Step 1: Retrieve and verify each of SRC01-09 directly** (per CLAUDE.md's source-pack-first workflow) before writing any citation: fetch each source, confirm the exact proposition it's being used to support, record the real URL and publication/update date. Do not cite a source for a proposition it does not actually establish.

- [ ] **Step 2: For every material factual/regulatory proposition drawn from SRC01-09 anywhere in `MMC_DATA.stages`** (the money-mule definition variants in Stage 1's orientation essay, the FCA/Cifas/Ombudsman National Fraud Database rules in Stage 10's operational decisions, the Home Office research findings referenced across Stages 1, 3, 6, 7), add one `verification-ledger.json` entry with `guide: "money-mule-or-victim-case-file.html"`, a unique `claimId` (pattern: `money-mule-or-victim-case-file.<short-slug>.001`), `claimText` matching the live wording, `claimType` (`"regulatory-definition"`, `"statute"`, `"guidance"`, etc. as appropriate, matching existing `claimType` values used elsewhere in the ledger), the real `source` object, and `status: "verified"`.

- [ ] **Step 3: Write the static `#sources` section** in `money-mule-or-victim-case-file.html` (not gated, always visible, matching `app-scam-decision-framework.html`'s "Sources and methodology" section pattern): a `<p><strong>Scope:</strong>...` / `<p><strong>Method:</strong>...` pair explicitly stating this is a synthetic educational case informed by the nine listed sources (not a real investigation), then an `<ol>` of nine `<li id="source-N">` entries linking to each source's real URL, matching the numbering used in any inline `<a href="#source-N">` citations inside the rendered stage content.

- [ ] **Step 4: Wire inline citations.** Wherever a stage's data object states a real regulatory/factual proposition (not the synthetic case facts, which are never cited), add a `sourceRefs: [n, ...]` array field to that data entry; have the relevant renderer append `<a href="#source-n">[n]</a>` markers after the corresponding sentence, mirroring `app-scam-decision-framework.html`'s inline citation style.

- [ ] **Step 5: Fill in `#related`** with reciprocal links to `/money-mule-financial-crime-networks-handbook.html` (existing guide on the same topic, must be distinguished, not duplicated) and `/false-positive-playbook.html` or `/fraud-red-flags-guide.html` (whichever better complements the "activity is not intent" theme; read both and pick one at implementation time, do not add both without confirming neither is a stronger fit).

- [ ] **Step 6: Manual check.** Every `<a href="#source-N">` resolves to a real `<li id="source-N">`; every listed source's URL is live and matches the cited proposition; the ledger's new entries' `claimText` matches the exact final rendered wording (not an earlier draft).

- [ ] **Step 7: Commit.**

```bash
git add money-mule-or-victim-case-file.html js/money-mule-case-file-data.js verification-ledger.json
git commit -m "feat: add sourced citations, sources section, and ledger entries for the Case File"
```

---

### Task 13: Repository metadata integration

**Files:**
- Modify: `knowledge.html`
- Modify: `sitemap.xml`
- Modify: `content-relations.json`
- Modify: `GUIDE_STANDARD.md`
- Modify: `methodology.html`

- [ ] **Step 1: `knowledge.html`.** Add a new `<a class="kh-article-card" data-cats="fraud-detection" ...>` card immediately before or after the existing `app-scam-decision-framework` card (newest-first ordering, check the surrounding cards' `data-date` values to place it correctly), with `data-date` set to today's build date, `<span class="kh-format-label">Case File</span>` (not "Framework"), an accurate `kh-item-desc` describing the 12-stage investigative format, and `data-title` carrying relevant search keywords (money mule, victim, exploitation, coercion, hypothesis, deception). Increment both `khHeroCount` and `khStatGuides` by exactly 1 (verify the current values first, do not guess).

- [ ] **Step 2: `sitemap.xml`.** Add a new `<url>` entry for `https://fincrimeradar.org/money-mule-or-victim-case-file.html`, `changefreq monthly`, `priority 0.7` (matching the existing "Framework experiments" entry, the most recently added comparable interactive page per GUIDE_STANDARD.md's Sitemap rule), under a new `<!-- Case File experiments -->` comment.

- [ ] **Step 3: `content-relations.json`.** Add `"money-mule-or-victim-case-file": ["money-mule-financial-crime-networks-handbook", "<second related slug from Task 12 Step 5>"]`, and add `"money-mule-or-victim-case-file"` into the target slugs' own arrays so the relation is reciprocal both ways (matching the existing reciprocity convention).

- [ ] **Step 4: `GUIDE_STANDARD.md`.** Update the maturity table row: `| Case File | Default Knowledge Hub with investigative compositions | Experimental pending Experiment 02 evaluation |` (was "Proposed"). Update the Framework row/paragraph (lines 10 and 15) to state plainly that Framework's own second-implementation evaluation remains open (Experiment 02 was built as a Case File instead), so the table does not read as though that evaluation happened. Add a new subsection after the existing "Experiment 01 Framework contract" section, titled "Experiment 02 Case File contract", written in the same style as the Experiment 01 section (states what the Case File label is used for, that it is not a separate template system, and that any later Case File experiment should reuse this contract's requirements only where evaluation shows they genuinely recur), listing: 12-stage gated progressive disclosure, a persistent five-hypothesis board with snapshot comparison, an evidence-status model distinct from hypothesis status, a keyboard-operable timeline, a five-dimension Decision Record, a Red-Team gate, and a Radar View, as the current experimental Case File contract.

- [ ] **Step 5: `methodology.html`.** Rewrite the paragraph at line 177 so it no longer states only that a second Framework implementation is the expected next evaluation step; add that Experiment 02 ("Money Mule or Victim?", linked) piloted the separate, previously-Proposed Case File format instead, and that Framework's own second-instance evaluation remains open. Keep the existing sentence inviting reader feedback.

- [ ] **Step 6: Manual check.** Re-run the `KnowledgeCountParser`-style logic mentally (or write a one-off check) to confirm `khHeroCount === khStatGuides === (standalone cards + series step cards)` still holds after the new card is added; confirm the sitemap XML is still well-formed; confirm `content-relations.json` still parses and every entry's reciprocity holds repo-wide (not just the new one).

- [ ] **Step 7: Commit.**

```bash
git add knowledge.html sitemap.xml content-relations.json GUIDE_STANDARD.md methodology.html
git commit -m "docs: integrate Money Mule or Victim Case File into site metadata and update Case File maturity status"
```

---

### Task 14: Static contract checker (`scripts/check_money_mule_case_file.py`)

**Files:**
- Create: `scripts/check_money_mule_case_file.py`
- Reference pattern: `scripts/check_app_scam_framework.py` (copy its overall structure: `fail()`/`require()` helpers, `HTMLParser` subclass for Knowledge Hub counts, `if __name__ == "__main__":` guard with the same exception handling)

- [ ] **Step 1: Write the script**, asserting (each as a `require(...)` call with a clear failure message):
  - `money-mule-or-victim-case-file.html` exists; exactly one `<h1>`; skip link + `id="main-content"` (or the page's actual main-content id from Task 1) both present; no duplicate `id` attributes.
  - Heading levels never skip (same `zip(levels, levels[1:])` check as the reference script).
  - Exactly one `Article` and one `BreadcrumbList` JSON-LD block, both complete (same required-property list as the reference script), `Article.articleSection == "Case File"`.
  - `canonical` `href` equals `og:url` `content`; that URL string appears in `sitemap.xml`.
  - `knowledge.html` contains the new card's `href`, and contains `kh-format-label">Case File<` for it (not `Framework` or a missing label).
  - Knowledge Hub `khHeroCount`/`khStatGuides` still equal the parsed card+step count (reuse the `KnowledgeCountParser` class verbatim from the reference script).
  - `content-relations.json` has the new slug with reciprocal entries in both directions.
  - Every `verification-ledger.json` entry with `guide == "money-mule-or-victim-case-file.html"` has `status == "verified"`.
  - No em dash (`"—"`) or en dash (`"–"`) character anywhere in `money-mule-or-victim-case-file.html`, `js/money-mule-case-file-data.js`, or `js/money-mule-case-file.js`.
  - **Progressive-disclosure check:** a curated list of strings that only exist from Stage 3 onward (e.g. `"Client Settlement Assistant"`, `"seventeen attempted calls"`, `"seventeen months"`, `"Frontier"`-style late-stage phrases — enumerate at least six, one per stage from 3 through 8) must appear in `js/money-mule-case-file-data.js` but must **not** appear anywhere in `money-mule-or-victim-case-file.html`.
  - `"innerHTML"` does not appear in `js/money-mule-case-file.js`.
  - Only the two allowed event-name string literals (`"case_file_stage_complete"`, `"case_file_reasoning_shift"`) appear as the first argument in any `gtag('event', ...)` call in `js/money-mule-case-file.js`; `"fcr_cookie_consent_v2"` and a `consentGranted()`-style gate are present.
  - None of `"hypothesisState"`, `"decisionRecord"`, `"knowledgeTimeline"`, `"redTeamCompleted"`, `"decisionChangeSelections"` appear as a substring inside any `gtag(` call's argument list (a simple regex scanning the text between each `gtag(` and its matching close paren is sufficient).
  - `GUIDE_STANDARD.md` contains `Case File | Default Knowledge Hub with investigative compositions | Experimental pending Experiment 02 evaluation` and a `### Experiment 02 Case File contract` heading.
  - Print a final `OK: ...` summary line on success, matching the reference script's convention.

- [ ] **Step 2: Run it against the finished build** (after Tasks 1-13 are complete): `python scripts/check_money_mule_case_file.py`. Fix any failure by correcting the build, not by weakening the check.

- [ ] **Step 3: Commit.**

```bash
git add scripts/check_money_mule_case_file.py
git commit -m "test: add static contract checker for the Money Mule Case File"
```

---

### Task 15: Headless-Chrome regression test (`scripts/test_money_mule_case_file_browser.py`)

**Files:**
- Create: `scripts/test_money_mule_case_file_browser.py`
- Reference pattern: `scripts/test_app_scam_framework_browser.py` (copy the `QuietHandler`/`QuietServer`/`CDP` harness verbatim; reuse `WIDTHS = (320, 375, 390, 428, 768, 1440)`)

- [ ] **Step 1: Write the script**, using the same local-server + headless-Chrome-via-CDP harness as the reference script, driving `money-mule-or-victim-case-file.html`:
  - At each width in `WIDTHS`: load the page, assert `document.documentElement.scrollWidth <= window.innerWidth + 1` (no horizontal overflow).
  - Enable `Runtime.enable` and `Log.enable`, collect console errors across the entire flow below; assert zero at the end.
  - Click `#openCaseFile`. Assert Stage 2 content is present in `document.body.innerText` and that Stage 3-12 marker strings (the same curated list from Task 14) are **absent** from `document.body.innerText` at this point.
  - Programmatically set all five hypothesis radios at Stage 2 (via `Runtime.evaluate` dispatching real `click()` calls on the actual radio elements, not by mutating state directly, so the gating logic is genuinely exercised), click continue; repeat the same pattern through Stage 4, confirm Stage 5's diff view text appears, click through Stage 6 (set both timeline selects + the change-point selection), Stage 7 (set control + voluntariness + hypotheses), Stage 8 (plain continue), Stage 9 (re-classify all five, confirm, confirm diff view, continue), Stage 10 (set all five Decision Record fields, confirm each dimension's analysis appears only after its own selection), Stage 11 (check all ten red-team boxes, set a reasoning-shift value, continue), Stage 12 (assert the Radar View and final analysis text are now present).
  - At each stage transition, assert the **next** stage's marker string is absent from the DOM until that stage's continue button is actually clicked (no unrevealed stage progression through ordinary controls).
  - Reload the page after reaching, say, Stage 6; assert the restored `currentStage` matches (read via `Runtime.evaluate` calling an exposed `CaseFileShell.getState().currentStage`, or by checking the rendered stage heading text).
  - Via `Runtime.evaluate`, set `localStorage.setItem('fcr_case_money_mule_v1', 'not json')`, reload, assert the page falls back to Stage 1 orientation with zero console errors.
  - Set a stale `caseVersion` (e.g. `0`) in a validly-shaped otherwise-current state object, reload, assert fresh-state fallback.
  - Click Reset Case, assert the confirm row appears, click Cancel, assert state is unchanged; click Reset Case again, click "Yes, reset", assert the page returns to Stage 1 and `localStorage.getItem('fcr_case_money_mule_v1')` is `null`.
  - Dispatch `Tab` key events (`Input.dispatchKeyEvent`) across the Stage 2 hypothesis board and the Stage 6 timeline list; assert `document.activeElement` lands on real interactive elements in a sensible order (no keyboard trap).
  - Attempt `Runtime.evaluate` calling `CaseFileShell.goToStage(12)` while state is still at an early stage; assert it does not navigate past `highestUnlockedStage`.

- [ ] **Step 2: Run it.** `python scripts/test_money_mule_case_file_browser.py`. Fix any failure in the build; do not comment out or loosen an assertion to make it pass.

- [ ] **Step 3: Run the full existing relevant checks too**, to confirm nothing regressed: `python scripts/check_app_scam_framework.py`, `python scripts/check_ledger.py scan`, `python scripts/check_ledger_base.py`, and any other repository check scripts that touch files this plan modifies (`knowledge.html`, `sitemap.xml`, `content-relations.json`, `verification-ledger.json`).

- [ ] **Step 4: Commit.**

```bash
git add scripts/test_money_mule_case_file_browser.py
git commit -m "test: add headless-Chrome regression test for the Money Mule Case File"
```

---

### Task 16: Manual verification pass and BACKLOG.md entry

**Files:**
- Modify: `BACKLOG.md` (append only)

- [ ] **Step 1: Work through spec §38's manual verification checklist** exactly as listed (desktop layout, mobile layout, keyboard navigation, visible focus, reduced motion, reload restoration, reset behaviour, stage gating, hypothesis comparison, timeline usability, Decision Record completion, Red Team gate, final analysis reveal, source links, navigation, footer, Knowledge Hub entry, sitemap integration, no layout shift, no horizontal overflow), noting the actual result of each, not an assumption.

- [ ] **Step 2: Re-read the full spec** (`docs/superpowers/plans/2026-09-10-money-mule-case-file-spec.md`) section 41's completion gate line by line against the finished build; list anything not satisfied honestly rather than marking it complete.

- [ ] **Step 3: Append one BACKLOG.md entry** in the file's existing narrative convention (see the 2026-09-08 consent-architecture entries for the expected level of detail and honesty about what was and was not verified), covering: what was built, the Case File maturity/GUIDE_STANDARD.md decision from the "Repository-level decision flagged up front" section above, the test commands actually run and their actual output, and any item from Steps 1-2 that could not be fully verified in this environment.

- [ ] **Step 4: Commit.**

```bash
git add BACKLOG.md
git commit -m "docs: log Money Mule or Victim Case File build in BACKLOG"
```

---

## Self-review notes

**Spec coverage:** §1-§9 → Task 1 (identity/hero copy folded into head metadata + orientation). §10 → Task 3. §11-12 → Task 4. §13 → Task 5. §14 → Task 6. §15 → Task 7. §16-17 → Task 8. §18-20 → Task 9. §21-23 → Task 10. §24-25 → Task 11. §26 → components are distributed across Tasks 2-11 (one component per task that introduces it; no single "Task 26"). §27-28 → Task 2's Data schema. §29 → Task 1 (data/HTML split) + Task 14's progressive-disclosure check. §30-32 → styling/accessibility woven into every task's steps, spot-checked in Task 16. §33 → Data schema (no innerHTML, no free text) + Task 14 checks. §34-35 → Task 12. §36 → Task 13. §37-38 → Tasks 14-16. §39 → Global Constraints + spot-checked per task and in Task 14's dash scan. §40 → Task 11. §41 → Task 16 Step 2. §42 → delivered as this plan's completion report once all tasks finish (not a separate task; it is the final message to the user, not a repository artifact). §43 → Global Constraints (no push/merge/deploy) and Task 16.

**Type/naming consistency check:** `CaseFileShell.getState/advanceStage/updateState/renderCurrentStage/goToStage/resetCase` are the only shell methods referenced across Tasks 3-11, all defined once in Task 2 and never renamed later. `STAGE_RENDERERS[n]` keys 1-12 are each defined exactly once (Task 1 stub for 2, replaced in Task 3; Tasks 4/5/6/7/8/9/10/11 for 4/5/6/7/8-9/10/11/12 respectively; Task 1 itself has no `STAGE_RENDERERS[1]` since Stage 1 is static HTML, not JS-rendered, which is intentional per the no-JS-required orientation requirement). `renderHypothesisBoard`, `renderEvidenceCard`, `renderCaseTimeline`, `renderHypothesisDiff`, `renderDecisionRecord`, `renderRedTeamReview`, `renderDecisionChange`, `renderRadarView` are each defined exactly once (in the task that first needs them) and reused by id in every later task that calls them, with no renamed duplicates.

**No-placeholder scan:** every task cites the exact spec section(s) supplying its literal copy rather than saying "TBD"; every data-shape example is a concrete object literal, not a description; every gating condition names the exact fields it checks; the two components with genuinely unspecified UI (Decision Record's option sets, and the timeline's per-stage reveal map) have concrete, documented answers in the Data schema section rather than being left open.

---

Plan complete and saved to `docs/superpowers/plans/2026-09-10-money-mule-case-file.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
