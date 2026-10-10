# FinCrimeRadar Operating Plan

**Effective date:** Monday, 28 September 2026  
**Last reviewed:** 10 October 2026<br>
**Planning horizon:** 90 days  
**Purpose:** Keep FinCrimeRadar active, credible and improving while Pratik starts a full-time role at Nisbets.

## 1. Operating decision

FinCrimeRadar should run as a controlled publishing system, not as a collection of ad hoc tasks.

The sustainable base commitment is:

- One FinCrime Week issue, published on Monday.
- One substantive Knowledge Hub publication no more often than fortnightly, and only when an item has passed every queue and release gate.
- One scoped Polish, Build or Content batch each week. A batch may advance work without creating a public release.
- No more than two Scenario Lab cases per month, with each case separately gated by distinct value and current repository-to-API synchronisation evidence.
- Up to three LinkedIn posts per week, each built from work already produced for the website and separately approved.
- One small website improvement or maintenance batch per fortnight.

Publication volume is an output, not a quota. Missing a nominal date is preferable to compressing sourcing, originality, review or production verification. Increase cadence only after four consecutive review cycles show that quality, the release-ready bank, employment boundaries and personal workload remain healthy.

## 2. Non-negotiable boundaries

### Nisbets separation

- Perform all FinCrimeRadar work outside Nisbets working time and on personal equipment and accounts.
- Do not use Nisbets data, systems, internal examples, customer information, policies, incidents or confidential knowledge.
- Review the employment contract and handbook provisions covering outside activities, intellectual-property assignment, confidential information and social media before starting any FinCrimeRadar research that materially overlaps Nisbets' business.
- Do not copy the contract, handbook or other employer documents into the FinCrimeRadar repository or research materials.
- Record FinCrimeRadar as an independent pre-existing project if the policy requires disclosure.
- State personal views where relevant. Do not imply that Nisbets sponsors or endorses FinCrimeRadar.
- If an applicable clause is unclear, obtain written clearance before investing in the research or charter. If clearance is doubtful, park the topic rather than narrowing it informally.
- For the proposed e-commerce fraud series, record in the series charter that every scenario, taxonomy and example is derived only from identified public sources. Complete this employer-conflict gate before any subject-matter research starts.

### Editorial and publication controls

- Primary-source verification, regulatory interpretation and final editorial judgement remain human-owned.
- No regulatory guide, FinCrime Week issue, public website change or LinkedIn item is published without a final approval gate.
- AI may research, draft, build, test, prepare a pull request and recommend release. It may not convert uncertainty into fact.
- LinkedIn comments, replies, messages, reactions and profile changes remain separately approved actions.
- Synthetic data only in Scenario Lab. No employer, client or real customer data.

## 3. Weekly operating rhythm

| Day | Automated preparation | Human decision or action | Planned output |
| --- | --- | --- | --- |
| Saturday | Collect primary-source candidates, score backlog readiness, prepare research packs, run stale-source and broken-link checks | Select the coming week's topics and reject weak or overlapping ideas | Approved weekly release slate |
| Sunday | Prepare FinCrime Week candidate file, guide specifications, social drafts and test plans | Verify the selected sources and approve the final FinCrime Week stories | FinCrime Week ready for release, guide work queued |
| Monday | Run FinCrime Week validation, generator, tests and production checklist | Final claim review and release approval by 20:30 | FinCrime Week issue and LinkedIn briefing post |
| Tuesday | Existing weekly digest sends at 08:00 UTC; advance the selected queue item | Review metrics and confirm that the item remains within scope | Content, Build or Polish work advances |
| Wednesday | Prepare Scenario Lab work or a website polish batch; produce LinkedIn Engagement Radar shortlist | Approve the case or maintenance scope; choose at most one engagement action | Scenario or maintenance work advances |
| Thursday | Run the applicable checks and prepare a release pack only when an item is release-ready | Approve or defer without penalty | Fortnightly guide release when every gate passes |
| Friday | Monitoring only: uptime, failed workflows, broken links, ledger expiry and production drift | Intervene only for a real incident | Protected no-build evening |
| Saturday | Refresh source packs, resolve review findings or prepare the next bounded batch | Approve the next scope only when capacity remains healthy | Release bank and evidence improve |

The schedule is deliberately weekend-heavy. Weekday human attention should normally be limited to 20 to 45 minute approval windows.

## 4. Single content conveyor

Every proposed publication moves through one queue:

1. **Idea:** title, audience problem and proposed format.
2. **Research:** current primary sources collected and applicability checked.
3. **Qualified:** originality and non-overlap confirmed.
4. **Specified:** analytical model, scenarios, acceptance criteria and requirement coverage matrix locked.
5. **Built:** page, metadata, discovery surfaces, ledger records and social asset prepared.
6. **Reviewed:** independent adversarial review completed and findings resolved.
7. **Release-ready:** exact revision passes all required checks.
8. **Published:** production URL, metadata, mobile rendering, links and discovery verified.
9. **Distributed:** LinkedIn and digest assets approved and released.
10. **Measured:** seven-day and 28-day performance recorded.

Use the existing `BACKLOG.md` as the source of truth. Do not introduce another planning database. Keep work-in-progress limits of:

- Maximum one item in Build.
- Maximum two items across Review and Release-ready.
- No cadence increase unless at least three items remain in the combined Qualified and Specified bank after the next planned release.

An item enters the release queue only when it has a verification owner, checked evidence, review date and recorded outcome.

## 5. Automation architecture

Build on the current static-site, repository and GitHub Actions model. Do not add a CMS, new database or orchestration service.

### A. Weekly planning automation

**Schedule:** Saturday morning.

The automation should:

- Read `BACKLOG.md` and the recent publication inventory.
- Flag overlap with existing guides.
- Identify ledger items approaching review dates.
- Prepare a ranked candidate slate across AML, fraud, sanctions, KYC/KYB, crypto and investigations.
- Produce a source pack containing direct primary-source links and the exact propositions each source may support.
- Estimate complexity and recommend a format.
- Produce a one-page approval brief.

It must not promote an item to release-ready or publish anything.

### B. Guide production automation

Once a topic is approved, the pipeline should prepare:

- Research notes and claim-source mapping.
- Originality and overlap check.
- Editorial draft.
- Two materially distinct worked scenarios as the default minimum.
- Requirement Coverage Matrix.
- Implementation branch or isolated worktree.
- HTML, page-specific behaviour, metadata, schema, sitemap, Knowledge Hub entry and content relations.
- Verification-ledger records.
- Social card and LinkedIn draft.
- Targeted tests, then full integration regression.
- Independent review pack and consolidated remediation list.
- Pull request with an exact release checklist.

The final merge, production release and LinkedIn action remain approval-gated.

### C. FinCrime Week automation

Keep FinCrime Week manually curated and primary-sourced. Automate preparation, not editorial judgement.

The system should:

- Scan a controlled allow-list of regulators, courts and government publishers for candidate developments.
- Deduplicate links and carry forward unresolved candidates.
- Draft `WHAT HAPPENED`, `WHAT CHANGES` and `WHAT TO REVIEW` fields with sentence-level source references.
- Flag allegation, provisional decision, consultation, effective-date and jurisdiction issues.
- Generate the weekly JSON only after story approval.
- Run the existing generator and dedicated tests.
- Prepare the homepage, archive, digest and LinkedIn release pack.
- Verify the production issue after publication.

Do not allow automated headline selection or unattended publication. A machine cannot safely decide whether a source changes regulatory applicability.

### D. Scenario Lab automation

The case pipeline should:

- Start from an approved case template and synthetic data.
- Check that the lesson is distinct from existing cases.
- Validate the case schema, answer logic, cross-references and regulatory propositions.
- Run module-specific browser and accessibility checks.
- Update the static case file and trigger the existing API synchronisation workflow.
- Poll the live API and compare its case count and identifiers with the repository source.
- Fail the release if the API is stale, unless the documented local fallback is explicitly accepted for that release.

Repository-to-API synchronisation is proven. Do not increase the Scenario Lab cadence until the remaining dispatch and API case-loading hardening is complete and usage supports expansion.

### E. LinkedIn automation

Use the personal profile as the principal distribution channel. The company page can receive secondary reposts only when there is a clear reason.

For every website release, prepare one post with:

- One substantive practitioner idea.
- One primary objective: authority, discussion, reach, traffic, conversion or registration.
- Verified claims and British English.
- Two or three relevant hashtags.
- Exact first-comment copy and verified URL when the objective favours first-comment placement.
- A visual already generated from the publication where useful.

Suggested weekly mix:

1. Monday: FinCrime Week operational implication.
2. Tuesday or Wednesday: guide A, focused on one judgement or control failure.
3. Thursday or Saturday: guide B or a Scenario Lab decision challenge.

Automation may draft, humanise, quality-check and place approved posts in a schedule. Publishing, comments and replies require explicit approval.

Run the Engagement Radar once each Wednesday. Return at most five high-value opportunities. Avoid automatic comments, generic engagement and promotional replies.

### F. Website quality automation

Run the following checks on every publication change:

- Relevant guide-specific checks.
- Verification-ledger validation, scan and overdue checks.
- Sitemap, metadata, schema and content-relation checks.
- Broken internal and external links.
- HTML validity and JavaScript syntax.
- Mobile viewport and keyboard checks.
- Reduced-motion and JavaScript-disabled comprehension where applicable.
- Screenshot comparison for shared-layout changes.
- Production URL, canonical URL and HTTP status verification after release.

Run weekly:

- Full-site broken-link scan.
- Accessibility smoke test across key templates.
- Core Web Vitals or Lighthouse trend, treated as directional rather than absolute.
- Production versus repository inventory comparison.
- Scenario Lab static versus API case comparison.
- Newsletter workflow health and delivery failure review.

Run monthly:

- Content freshness and ledger review.
- Search and analytics review.
- Highest-exit and no-traffic page analysis.
- Internal-link opportunities in small reviewed batches.
- Dependency and security review.
- Backup and recovery check for repository, deployment and email configuration.

## 6. Publishing gates

A release is allowed only when all applicable gates are green:

| Gate | Required evidence |
| --- | --- |
| Scope | Approved topic, audience, format and non-overlap decision |
| Sources | Current primary sources opened and the load-bearing claims mapped |
| Originality | Clear FinCrimeRadar practitioner value beyond a summary |
| Editorial | Scenarios, uncertainty, jurisdiction and operational implications checked |
| Build | Exact planned files changed, no unrelated work included |
| Automated checks | Relevant tests and repository checks pass |
| Independent review | Adversarial review completed and material findings resolved |
| Release | Exact revision approved for publication |
| Production | Live page, metadata, mobile behaviour, links and discovery checked |
| Distribution | Exact post and exact first comment approved |

If a load-bearing claim cannot be verified, qualify it, remove it or stop the release. Missing a weekly volume target is preferable to publishing a weak or incorrect guide.

## 7. Website enhancement programme

Do not redesign the site while starting a new job. Use a controlled polish lane.

### Priority 1: reliability and accessibility

- Harden Scenario Lab module dispatch so unknown modules fail explicitly.
- Replace unvalidated Scenario Lab case loading in the API with bounded schema validation.
- Complete the confirmed quiz-title heading repair across the affected guides.
- Scope and repair the skip-link focus-target issue.
- Preserve direct repository-to-API inventory comparison as the release proof for Scenario Lab changes.

### Priority 2: discovery and retention

- Add only useful contextual internal links, in reviewed batches.
- Improve related-content journeys between guides, Scenario Lab and FinCrime Week.
- Measure newsletter conversion by landing page.
- Add consistent seven-day and 28-day content performance reporting.

### Priority 3: selective product growth

- Expand Scenario Lab only when the sync path is proven and usage supports it.
- Advance the Companies House KYB Investigation Lab only after a scoped architecture and terms review.
- Keep SAR Writing Sandbox expansion separate from normal guide delivery.
- Do not start the guide chatbot until ranking, attribution, refusal, prompt-injection, freshness and cost controls are resolved.

## 8. Current content research queue

`BACKLOG.md` remains the queue authority. The list below records the current order and planning constraints only. Every candidate remains RESEARCH until its owner, checked evidence, review date and verification outcome are recorded.

### Prioritised guide queue

1. **Customer Risk Scores: What the Number Cannot Decide.** Prove distinct value beyond the Scenario Lab Risk Scoring module and re-check the FCA evidence before promotion.
2. **Financial Crime Control Testing: A Control Exists, But Does It Work?** Separate design, implementation and operating effectiveness using current primary sources.
3. **SAR Escalation Under Commercial Pressure.** Develop as a UK-first judgement guide. Do not convert US material into a UK legal standard.
4. **Synthetic Data for AML Model Testing.** Verify the FCA and Alan Turing Institute programme and any published 2026 Solution Sprint outcome before drawing effectiveness conclusions.
5. **Nested VASP Exposure: The Counterparty You Cannot See.** Prove a distinct decision model beyond the Crypto series, Travel Rule guide and Scam Compound guide.
6. **E-commerce Fraud: From Account Creation to Chargeback.** Do not begin subject-matter research until the employer-conflict gate in section 2 passes. The first authorised scope is limited to the series-level non-overlap review and the Part 1 charter. Do not build the master taxonomy, five-guide coverage matrix or scenario inventory in that first scope. The charter must record public-source provenance and prohibit Nisbets information, systems, policies, incidents and examples.

Do not assign dated release pairings while no candidate is READY.

### Removed or moved out of the active guide queue

- **Scam or Civil Dispute?** Remove. The shipped APP Scam Decision Framework already covers the civil-dispute boundary, partial or nominal performance, the GBP 85,000 cap and the PSR decision factors.
- **Victim, Mule or Fraudster?** Park. It overlaps materially with the Money Mule Case File, Fraud Detection scenarios and Scam Compound guide. Reconsider only if research identifies a genuinely distinct first-party-fraud decision model.
- **Repeat AML Failure as a Risk Signal.** Move to reserve research. It currently depends on a US case and an unverified UK comparator and risks blending jurisdictions into a standard neither regulator states.
- **Companies House verified does not mean KYC complete.** Keep within the planned Companies House KYB Investigation Lab rather than creating a separate overlapping guide.

### Scenario Lab candidates

1. Event-Driven CDD Review.
2. Failure to Prevent Fraud, reusing the verified evidence pack from the shipped Evidence Essay.
3. Proliferation Financing Investigation, only after a defensive scope and UK regulatory basis are established.

Domestic PEP Proportionality is not a new candidate because Scenario Lab already contains **The PEP Who Should Not Be Declined**, grounded in MLR 2017 and FCA FG25/3.

### Deliberate holds

- Sanctions Ownership and Control remains on hold pending the UK consultation outcome.
- No new public-data integration until terms, limits, provenance and failure behaviour are checked.
- No automated FinCrime Week publication.
- No site-wide redesign or CMS migration.

## 9. 30, 60 and 90-day rollout

### Current reset, 10 October 2026

1. Treat the refreshed `BACKLOG.md` as the queue authority. No content item is READY.
2. Prepare FinCrime Week W41 through the normal manual sourcing and release gates.
3. Scope the quiz-title heading repair as the next Polish batch.
4. Treat Scenario Lab synchronisation as closed. Scope dispatch hardening and bounded API case validation as the remaining reliability work.
5. Complete the employer-conflict gate before any e-commerce series research.
6. Keep unrelated redesign work frozen.

### Days 1 to 30

- Publish FinCrime Week weekly and no more than one fully gated guide per fortnight.
- Add no more than two separately gated Scenario Lab cases during the month.
- Advance one bounded Polish, Build or Content batch each week without treating progress as a publication obligation.
- Keep one protected evening with no planned work.
- Measure human approval time and automation failure rate.
- Build a three-item Qualified or Specified bank before considering any cadence increase.

### Days 31 to 60

- Add automated seven-day and 28-day performance reports.
- Complete the highest-priority accessibility debt.
- Review the fortnightly guide cadence against quality, traffic and human workload.
- Increase output only if the bank, review quality, employment boundaries and personal workload remain healthy.

### Days 61 to 90

- Set the permanent cadence from evidence.
- Retire low-value content formats and double down on topics that produce qualified practitioner engagement, returning visitors and Scenario Lab use.
- Decide whether a second distribution channel, such as Reddit or a company-page repost, earns its maintenance cost.
- Review sponsorship, newsletter conversion and product opportunities without weakening free access or editorial independence.

## 10. Scorecard

Review this dashboard each Sunday. Keep it to one page.

### Reliability

- FinCrime Week published by Monday 20:30.
- Tuesday digest workflow successful.
- Production checks completed for every release.
- Scenario Lab repository and API inventories match.
- Zero overdue verification-ledger records.

### Quality

- Zero known unverified load-bearing claims at release.
- Corrections or material post-release defects.
- Independent-review findings by severity and recurrence.
- Accessibility and broken-link failures.
- Percentage of releases that pass on the first final-gate run.

### Throughput

- Guides published.
- FinCrime Week issues published.
- Scenario Lab cases added.
- Qualified, Specified and Release-ready bank size.
- Median human approval time per release.

### Audience value

- Organic entrances and seven-day returning visitors.
- Newsletter sign-ups and delivery failures.
- LinkedIn impressions, saves, substantive comments and verified clicks.
- Scenario Lab starts, case completions and return use where privacy-safe measurement exists.
- Top five pages by useful engagement, not raw page views alone.

## 11. Stop rules

Reduce the cadence immediately when any of these occurs:

- The release-ready bank falls below three items.
- A material regulatory or factual correction is required.
- Independent review is skipped or compressed to meet a date.
- The same automated check fails in two consecutive releases.
- FinCrimeRadar work regularly exceeds the agreed weekly time budget.
- Nisbets responsibilities, rest or family time are being affected.

When reduced, preserve FinCrime Week and essential reliability work. Publish a guide only when it is already release-ready and capacity remains healthy. Pause new product work and low-value distribution first.

## 12. Recommended automation tasks

Create these recurring tasks after the plan is approved:

1. **Saturday Content Planner:** prepare the next week's ranked queue and research packs, with no writes to production.
2. **Sunday FinCrime Week Desk:** prepare candidate stories and claim-source mapping, then wait for approval.
3. **Monday Release Gate:** run FinCrime Week checks and return an approval pack.
4. **Wednesday Engagement Radar:** return at most five high-value LinkedIn opportunities, with no external action.
5. **Friday Reliability Monitor:** report only failures or material changes in production, workflows, links, ledger status or Scenario Lab synchronisation.
6. **Monthly Performance Review:** produce the scorecard and recommend one cadence or backlog adjustment.

Notifications should be exception-based. Routine successful checks should remain quiet unless an approval is required.

## 13. Current planning baseline

Repository and named production evidence inspected on 10 October 2026 shows:

- 59 Knowledge Hub publications: 25 series parts and 34 standalone publications.
- 19 Scenario Lab cases, with the live API matching the repository's entity identifiers and module counts on the first comparison attempt.
- FinCrime Week W36 to W40 present, with W40 current.
- The weekly digest scheduled for Tuesday at 08:00 UTC.
- Scenario Lab repository-to-API synchronisation proven. The local fallback remains a resilience path, not release evidence.
- 695 verification-ledger entries validated, with no overdue entries.

This is a planning baseline, not a complete site-wide production audit. Recheck every material dependency as part of its own release gate.
