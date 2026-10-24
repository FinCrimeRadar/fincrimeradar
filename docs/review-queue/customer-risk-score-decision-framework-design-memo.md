# Customer Risk Scores: What the Number Cannot Decide, design memo

Status: specified and built in one Claude Code session on 24 October 2026. Loop: Content, `/ponytail full`. Public format: Framework (Default Knowledge Hub treatment, accepted composition). Source basis: `customer-risk-score-decision-framework-source-pack.md`. The page cites sources only through the proposition IDs recorded there.

## 1. Intelligence Core

| Element | Statement |
| --- | --- |
| Intelligence question | How can a firm design and govern a customer risk scoring method so the number informs judgement without replacing it? |
| Evidence state | Established: the Regulations require risk assessment and risk-sensitive CDD and prescribe no model. Guidance: FCA good and poor practice examples and one case study. FinCrimeRadar assessment: the seven control points, the override and change-control designs, the scenario grading. Unknown: validation standards, double counting treatment, acceptable override rates. |
| Decision object | One judgement about a scoring method: accept it, challenge it, or require a controlled change. Not a decision about any single customer's rating. |
| Uncertainty | No source read sets a validation standard, a sensitivity test, an override tolerance or a band count. FCA findings on customer scoring are thin and several items use the generic words "risk assessment". The Case Study 17 sample is wholesale brokers. |
| Change condition | A regulator or the courts stating a model standard; an FCA finding that addresses overrides or thresholds directly; a change to reg 28 or reg 33; evidence from the firm's own testing that contradicts a control point. |
| Practitioner outcome | The reader can challenge a scoring methodology against seven control points, document an override so it survives review, and recognise when a model change needs impact assessment, testing and approval. |

## 2. Originality gate

The practitioner value beyond the regulator text is a score-to-decision control framework: seven control points that turn "the FCA expects a robust method" into questions a reviewer can put to a model owner, together with the two ways such a method most often fails in operation (model applicability after a change, and override patterns as unreported model feedback).

Differentiators, each FinCrimeRadar assessment resting on the sources:

1. The distinction between what a score can inform and what it cannot decide alone, with each statement tied to a source or labelled as assessment.
2. The "inside the number" decomposition: nine hidden design decisions behind one displayed score.
3. The controlled override versus silent manipulation test.
4. Treating repeated overrides as management information and a model-remediation trigger, which no source states and the guide says so.
5. A change-control cycle sized to model change rather than to a calendar.

## 3. Non-overlap

### Scenario Lab Risk Scoring module (`docs/risk-scoring-module-spec.md`)

That module teaches an analyst, case by case, to weigh signals on one customer file, separate material factors from noise, choose a graded response (standard monitoring, EDD, escalate, block or SAR), challenge a mechanically high result (Case 4, the over-scored customer) and record an override rationale. Its unit is a customer file.

This guide does not reuse any of the eight cases, does not present a points model, does not ask the reader to rate a customer, and does not include a calculator. Its unit is the scoring method and the governance around it. The two overlapping ideas are handled by link rather than repetition:

| Scenario Lab idea | This guide's position |
| --- | --- |
| A score is an input, not a verdict (Case 4) | Taken as given. The guide asks what must be true of the method for the number to deserve that role. |
| Override with documented rationale (Case 4) | The analyst's side is not repeated. The guide covers the firm's side: reason codes, approval, audit trail, aggregate MI and what a concentration means. |
| Event-Driven CDD Review (queued Scenario Lab candidate) | Not built. This guide treats triggers only as a model-governance control (what causes re-scoring and model change). |

### Existing guides

| Guide | Overlap | Boundary |
| --- | --- | --- |
| The De-Risking Judgement Call | Relationship exit decisions, reg 31 | This guide never decides exit. It states that a score does not mandate exit and links there. |
| KYC / KYB / CDD / EDD: The Onboarding Dilemma | CDD and EDD levels | That guide teaches the due diligence choices. This one governs the number that feeds them. |
| Perpetual KYC: Why Periodic and Event-Driven Review Are Not the Same Control | Triggered review | That guide is the operating model for review. This one covers how triggers connect to re-scoring and when the model itself must change. |
| Tuning Screening Algorithms, The False Positive Playbook | Threshold language | Those concern name-matching and alert thresholds. This guide concerns customer risk bands. The word "threshold" is used for risk bands only, and the guide says so. |

## 4. Format decision

Framework, because the reader's job is to reach and defend a difficult judgement through structured analysis. Primitives used, as the GUIDE_STANDARD Framework contract allows: sequential decision stages (the score-to-decision chain), a Decision Record in each scenario, Source, Application and Action reasoning, Red Team Questions, static What Would Change My Decision, a one-screen operational summary. A Practitioner Lens is not used because the subject has no optional depth layer that earns it. No generic Framework renderer is built. All CSS is page-scoped under the `crs-` prefix and all behaviour is in `js/customer-risk-score-decision-framework.js`.

The public label is "Framework". No internal experiment numbering appears on the page.

## 5. Visual spine

Each visual answers one reader question, per the Visual purpose rule. All are semantic HTML and CSS, with inline SVG only for small connectors, so the text is the content and no separate alternative text can drift from it.

| Visual | Reader question | Construction | Text equivalent |
| --- | --- | --- | --- |
| 1. Score-to-decision chain | Where does the arithmetic stop and what sits outside it? | Ordered list of seven stages, numbered badges, arrows that turn from horizontal to vertical, a labelled "outside the arithmetic" band | The ordered list is the content. The band is a labelled section, not a colour. |
| 2. Inside the number | What decisions are hidden inside one displayed score? | Stack of nine numbered layers, each with the hidden decision and the question to ask | Definition list |
| 3. What the number can and cannot decide | What may a firm let the score do, and what must it not? | Two panels with words "Can inform" and "Cannot decide alone", each item tagged with its evidence state and citation | Plain lists |
| 4. Override governance loop | What separates a controlled override from silent manipulation? | Six-step loop plus a two column contrast | Ordered list and a definition list |
| 5. Change-control cycle | When must the model itself be changed, and by what route? | Seven-step cycle plus a list of triggers | Ordered list |

Nothing depends on colour, hover or animation. Stages carry numbers and words, the contrast panels carry text labels, and the evidence-state tags carry words. There is no animation, so reduced-motion needs only the standard guard.

## 6. Scenarios

Both are composites. All figures are fictional and labelled on the page.

### Scenario 1, new product, old model

Decision: is the existing model still valid for a new customer population, and what controlled route restores reliance? Not a customer rating.

| Option | Grade | Why |
| --- | --- | --- |
| Treat the old model as unvalidated for the new population: document an impact assessment, apply interim controls, test affected factors, thresholds and consequences, and get approval before extending reliance | best | The conclusion follows from P27, P28, P29 as application and from P07. |
| Keep scoring because the engine produced a result without error, and review at the next annual model review | unsupported | Technical availability is not evidence of suitability. |
| Stop onboarding the segment until a new model is built and approved, with no interim controls | incomplete | It avoids the risk but does not answer the question and ignores proportionate interim controls. |
| Keep using the score and add manual review of every high rated customer in the segment | incomplete | It misses wrongly low ratings, which is where missing data defaults hide. |

Counterfactual: the new product is a re-branded variant of an existing product with the same customer type and data sources. The impact assessment can be short, but the documented applicability conclusion remains.

### Scenario 2, the override pattern

Decision: what is the right response to a sustained concentration of downward overrides with one reason code?

| Option | Grade | Why |
| --- | --- | --- |
| Preserve the files, sample affected cases, examine approval quality, outcomes and conflicts, and report the pattern as management information and a possible model remediation trigger | best | P44, P47, P63 as application. |
| Prohibit downward overrides | unsupported | The FCA's good practice example is a clear audit trail of overrides and rationale, so overrides are contemplated. |
| Accept the pattern because each file has some supporting evidence and an approval | unsupported | Individual adequacy does not answer why the pattern exists. |
| Re-review each overridden file and reverse the unsupported ones | incomplete | It fixes files and leaves the cause unexamined. |

Counterfactual: the same number of overrides, spread over five units with five different reasons and approvers. The pattern points less to one design gap, but sampling still applies.

Both scenarios carry the Source, Application and Recommendation triad for every option. The page uses the word "Recommendation" in line with CLAUDE.md section 10. The static analysis of every option is in the HTML and is hidden by script only when script is available and until a decision is recorded.

## 7. Interaction contract

| Interaction | Implementation | No-JavaScript behaviour |
| --- | --- | --- |
| Two graded scenario decisions | Native radio group in a form with `method="dialog"`; submit reveals the analysis and focuses a link to the chosen option's analysis; feedback in a polite live region | Every option analysis is visible; submit buttons are hidden because they do nothing |
| Knowledge check | Five questions, live score on submit | Questions visible and the answer notes are a native `details` |
| FAQ | Native `details` and `summary` | Same |
| Save as image | Canvas 2D export of the closing Risk, Signal and Response grid, read from the DOM | Button hidden |
| Telemetry | The existing consent gated `gtag` events `scenario_complete`, `knowledge_check_complete`, `card_export`, once per page load, aggregate only (guide id, scenario id, grade, score). No free text. | None |

The knowledge check includes one question testing a specific detail of Case Study 17.

## 8. Requirement Coverage Matrix

Each requirement is assigned to exactly one task.

| # | Requirement | Task |
| --- | --- | --- |
| R1 | Source pack, design memo, external review brief | T1 |
| R2 | Page shell, metadata, JSON-LD, skip link, nav chrome, scope strip, Intelligence Core | T2 |
| R3 | Evidence labelling, source-led sections for the seven control points | T3 |
| R4 | Visuals 1 to 5 with text equivalents, mobile reflow | T4 |
| R5 | Two scenarios, graded options, Source/Application/Recommendation, change analysis, counterfactuals, Decision Records | T5 |
| R6 | Six Risk, Signal and Response cards inline and closing grid, Save as image | T6 |
| R7 | Operational summary, Red Team Questions, knowledge check, FAQ, sources, related links | T7 |
| R8 | Page script: decisions, quiz, export, telemetry, js class | T8 |
| R9 | Knowledge Hub card and counts, sitemap, content relations, social card | T9 |
| R10 | Ledger entries and reconciliation | T10 |
| R11 | Static checker | T11 |
| R12 | Real-browser test | T12 |
| R13 | Full regression, diff scope, dash scan | T13 |
| R14 | Pull request, `/code-review`, delivery report | T14 |

## 9. Review classification

Two items trigger CLAUDE.md review rules.

1. Regulatory claim review (section 7), because the page makes statements about regulatory scope and statutory triggers (reg 18, 28, 33) and what the FCA examples do and do not establish. Listed in the external review brief.
2. Scoring and grading logic (section 15). The page contains no scoring engine and no calculator. It does contain graded scenario options and a scored knowledge check, which are grading logic. They are small and deterministic and are covered by the same manual review.

No new API endpoint, authentication, financial data or money movement is involved.
