# Annex 1 Firms and the AML Blind Spot: external adversarial review pack (v2)

Compiled 2026-08-27. No v1 draft existed anywhere in this repo (git history, working
tree, or `docs/review-queue/`) to supersede; the prior review attempt terminated on
its own usage limit before producing any findings or writing any file. This is a
first-and-only pack, not a revision.

**Purpose.** CLAUDE.md section 7 requires external adversarial review, run manually
outside Claude Code (ChatGPT or Codex), for any claim about which regulation applies
to which entity or activity, statutory applicability, registration conditions, or
what an authority legally established. `annex-1-firms-aml-blind-spot-guide.html`
carries exactly that class of claim and has not yet had this review completed. This
document assembles the guide's regulatory claims against primary-source text so a
human-run external review session can work from it directly.

**This document does not contain a review.** Nothing below has been assessed for
correctness by this session beyond the source-pairing and structural cross-checks
noted explicitly as such. Where a genuine discrepancy surfaced while compiling this
pack, it is flagged for the reviewer, not corrected. **Flag 1 below, on regulation
56, is the one substantive discrepancy this compilation surfaced** and should be the
reviewer's first port of call.

**Guide state covered.** Current live `annex-1-firms-aml-blind-spot-guide.html` on
`main`, i.e. after all three commits: `d5b399c` (original publish), `2163014` (first
correction pass, corrected the regulation 55/58/59 wording and added a new
regulation 56/57 ledger entry), `423f3d3` (pattern synchronisation, no regulatory
wording changed). All guide text quoted below was re-pulled from the working tree at
compile time, not carried over from memory of the original build.

---

## Correction history, so the reviewer knows what already survived one pass

| Commit | What changed | Regulatory wording affected? |
|---|---|---|
| `d5b399c` (original publish) | Guide shipped with 8 ledger entries. Regulation 55 was described as itself requiring registration ("Regulation 55 defines Annex I financial institution... and requires an in-scope Annex I financial institution to be registered"); regulations 58/59 were described only as "fit and proper assessment and refusal grounds" with no reference to regulation 55/56/57's relationship. | Original, unreviewed text. |
| `2163014` ("correct Annex 1 guide review findings") | Rewrote the regulation 55 ledger entry and body text to separate the register-power/definition function (55) from the operative prohibition (56) and applications (57); added a **new** ledger entry `mlr-reg56-57-registration.001` that hadn't existed before; rewrote the regulation 58/59 entry to state 58 applies "where the FCA has decided to maintain the regulation 55 register" rather than asserting it as a blanket rule. Also inlined the four risk-pattern mini-cards into their contextual sections (trap/concerns/workflow/spv-scenario), which introduced wording that briefly drifted from the canonical `#patterns` section and the save-as-image script's own hardcoded copy. | **Corrected once.** This is the passage this pack scrutinises most closely (Flag 1). |
| `423f3d3` ("synchronise Annex 1 risk patterns") | Re-synchronised the four inline pattern cards to match the canonical `#patterns` section wording exactly, and rewrote the save-as-image script to read pattern text from the DOM at click time instead of a second hardcoded copy, removing the drift source structurally rather than patching the string once. No regulatory wording touched. | N/A, pattern-copy only. |

Everything **not** listed as touched in `2163014` (the authorised-vs-registered
distinction, the SPV/Annex 1 registration test, the MFS case framing, the NRA
bridging-finance context, the FCA August/March statistics, regulation 10/Schedule 2)
is **original text from `d5b399c`, never revised, never externally reviewed.**

---

## Flag 1 (the substantive one): regulation 56's actual scope

**Guide's live claim** (`#meaning` section, `a1-callout a1-law`, and ledger entry
`annex-1-firms-aml-blind-spot-guide.mlr-reg56-57-registration.001`):

> "Regulation 56 contains the operative requirement that a person covered by a
> register required under regulations 54 or 55 must not act in the relevant business
> unless included in the appropriate register, subject to the regulation's
> application exception."

**Primary source, regulation 56, pulled directly from legislation.gov.uk's XML on
2026-08-27** (not a summarised fetch; this is the statute's own paragraph structure):

- **56(1)**: "Unless a person in respect of whom the registering authorities are
  required to maintain a register under **regulation 54** is included in the
  appropriate register, or paragraph (2) or regulation 56A... applies, that person
  must not act as—(a) high value dealer; (b) money service business; (c) trust or
  company service provider; (d) bill payment service provider; (e)
  telecommunication, digital and IT payment service provider; (f) cryptoasset
  exchange provider; or (g) custodian wallet provider."
  **Regulation 54 only. "Annex I financial institution" is not one of the (a)–(g)
  categories, and regulation 55 is not named in 56(1).**
- **56(5)**: "Where a registering authority decides to maintain a register under
  regulation 55(1) or (3)... and establishes a register for that purpose... a
  relevant person of that description must not carry on the business or profession
  in question for a period of more than 12 months beginning with the date on which
  the registering authority establishes the register... unless (a) that person is
  included in the register, (b) that person has applied for registration... but that
  application has not yet been determined, or (c) that person is an art market
  participant or a letting agent."
  **This is the paragraph that actually reaches regulation-55 (Annex I) registrants
  — via a different mechanism (a rolling 12-month grace window tied to when the
  register was established) than 56(1)'s more direct prohibition for regulation-54
  categories.**

**What this means for the reviewer to assess:** the guide's sentence collapses two
structurally different provisions, 56(1) (regulation 54 categories, direct
prohibition) and 56(5) (regulation 55 categories, 12-month-from-establishment
prohibition), into one undifferentiated "regulation 56 contains the operative
requirement... covered by a register required under regulations 54 or 55." That is
directionally defensible (56 as a whole does eventually reach Annex I firms), but it
does not name paragraph (5) specifically, and a reader could come away thinking
56(1)'s prohibition text itself lists Annex I institutions, which it does not. Is
this level of abstraction acceptable for a practitioner guide's summary sentence, or
does it need "regulation 56(5)" precision given CLAUDE.md section 6's rule that
subsection-level precision is required "where the distinction itself affects the
legal or practical conclusion"? This session did not correct it; that judgement call
belongs to the external review per the task's own instruction not to correct
findings made while compiling the pack.

---

## Flag 2 (minor, sourcing hygiene, not regulatory accuracy)

Source 9 in the guide's own Sources list, "FCA, Financial Services Register, scope
and use of the official record" (`https://www.fca.org.uk/firms/financial-services-register`),
has **zero inline `[9]` citations anywhere in the guide body** (confirmed via
`grep -c 'href="#source-9"'`, hit count 0, versus every other source having 1 or 2
inline citations). Either this source was meant to back a claim that never got a
citation link added, or it is deliberately general background reading with no
specific claim attached. Worth a decision, not a regulatory risk either way.

---

## Claims paired with primary-source text

For each claim: the guide's current live wording, its location, its ledger entry
(if any), and the primary source text pulled directly from the source on
2026-08-27.

### A. Authorised vs registered distinction

**Guide** (`#opening` decision, best-response feedback and static reasoning; `#trap`
section; `#faq` first item; consistent across all three):
> "The screenshot does not identify the precise legal entity, the activity
> recorded, any permissions, or the source and purpose of the financing... the FCA
> distinguishes firms authorised to perform regulated activities from firms
> registered for a defined purpose."

**Ledger**: `annex-1-firms-aml-blind-spot-guide.fca-status-distinction.001` —
"FCA consumer guidance distinguishes an authorised firm, which has permission for
specified regulated activities and must meet relevant standards, from a registered
firm, which meets requirements for a registration regime but does not thereby have
permission to provide wider regulated products or services."

**Primary source** (`fca.org.uk/consumers/how-check-firm-individual-authorised`,
fetched 2026-08-27): "Being **authorised** means that firms must meet certain
standards and have our permission to provide certain products and services...
Being **registered** means that firms must meet certain requirements, but they
don't need to have our permission to provide products and services." The page also
states that using an unauthorised firm forfeits access to the Financial Ombudsman
Service and FSCS.

**Assessment for reviewer**: matches. No structural gap found. Internal consistency:
this distinction is restated in the opening scenario, the trap section, and FAQ
item 1, all three phrased consistently with no drift between them.

---

### B. Regulation 55–59 chain

**Guide** (`#meaning` section, corrected in `2163014`):
> "Regulation 55 gives the FCA power to maintain an Annex 1 register and defines an
> Annex 1 financial institution for that register... Where the FCA establishes the
> register, regulation 56 contains the operative requirement not to act unless the
> relevant person is included in the appropriate register, subject to its
> conditions. Regulation 57 governs applications, regulation 58 applies the fit and
> proper test to Annex 1 institutions, and regulation 59 sets out other refusal
> grounds."

**Ledger**: `mlr-reg55-framework.001`, `mlr-reg56-57-registration.001`,
`mlr-reg58-59-assessment.001` (full text in the correction-history table above and
the live `verification-ledger.json`).

**Primary source, regulation 55** (legislation.gov.uk, fetched 2026-08-27):
- 55(1): "The FCA may maintain a register of Annex 1 financial institutions."
- 55(2): defines "Annex 1 financial institution" as a financial institution which
  falls within regulation 10(2)(a) and is not a money service business, authorised
  person, bill payment service provider, or telecommunication/digital/IT payment
  service provider.
Confirms the guide's "power to maintain... and defines" framing precisely; 55 itself
carries no prohibition.

**Primary source, regulation 56**: see Flag 1 above — accurate that 56 is where the
operative prohibition lives, imprecise on which paragraph.

**Primary source, regulation 57** (fetched 2026-08-27): 57(1), applicants for
registration "under regulation 54 or 55" must apply in the manner the registering
authority specifies; 57(2)–(6) cover required information, follow-up information
requests (21 days), and duty to notify material changes (30 days). Matches "governs
applications."

**Primary source, regulation 58** (fetched 2026-08-27): 58(1) is the fit-and-proper
refusal test for regulation-54 registrants (MSB, TCSP); **58(2)** is the specific
extension clause: "Where the FCA has decided to maintain a register of Annex I
financial institutions under regulation 55, paragraph (1) applies in relation to
those institutions as it applies to a money service business and a trust or company
service provider." The guide's "applies... where the FCA has decided to maintain the
regulation 55 register" tracks 58(2) precisely, better than the original `d5b399c`
wording did (that version stated it as an unconditional rule). **This is the one
regulation-chain claim in this guide that is now more precise than a plain read of
the regulation number alone would suggest, and it withstands direct textual
comparison.**

**Primary source, regulation 59** (fetched 2026-08-27): 59(1) lists the grounds on
which the registering authority "may refuse to register an applicant... in a
register maintained under regulation 54 or 55," including non-compliance with
regulation 57, false or misleading information, unpaid penalties, supervisory
authority objection, or reasonable suspicion of future non-compliance. Matches
"other refusal grounds."

**Assessment for reviewer**: apart from Flag 1's paragraph-level imprecision on
regulation 56, the reg 55/57/58/59 claims hold up against the statute's actual text,
including the subtlety (58(2)) that the corrected wording captures and the original
`d5b399c` wording did not.

---

### C. SPV / Annex 1 registration test (worked scenario 2, with counterfactual)

**Guide** (`#spv-scenario`, unchanged since `d5b399c`):
> "Source: current FCA guidance says only the original lender needs Annex 1
> registration where an SPV only receives the legal or beneficial interest in
> loans. Application: the facts do not yet show whether the SPV originated credit
> or only took an assignment. Action: map roles and payments. **Counterfactual: if
> evidence shows the SPV itself originates lending, reassess the perimeter and
> obtain specialist advice.**"
> Option B (SPV must register in every case) is graded "weak": "SPV registration is
> not automatic. Current FCA guidance focuses on whether it originates loans or
> merely receives an interest."

**Ledger**: `fca-current-registration-guidance.001` — "Current FCA guidance, updated
26 August 2026... says only the original lender needs Annex 1 registration where an
SPV only receives the legal or beneficial interest in loans."

**Primary source** (`fca.org.uk/firms/financial-crime/money-laundering-terrorist-financing/registration`,
fetched 2026-08-27): "If your firm is a special purpose vehicle involved in
lending, you only need to register with us as an Annex 1 financial institution if
you are the original lender... If only the legal or beneficial interest in loans is
transferred to your firm, you do not need to register with us." The same page:
"If you are authorised under the Financial Services and Markets Act 2000, you do
not need to register with us as an Annex 1 financial institution."

**Assessment for reviewer**: matches the primary source precisely, including the
scenario's own counterfactual branch (the guide does not assert the SPV never needs
registration, only that this specific fact pattern doesn't trigger it, and names the
condition that would flip the answer). This claim was **never revised** across all
three commits, so it has had no correction-cycle scrutiny at all, worth the
reviewer's full attention for that reason alone.

---

### D. MFS case framing

**Guide** (`#case-study`, unchanged since `d5b399c`):
> "The FCA announced that it had opened an enforcement investigation into Market
> Financial Solutions Limited. It said the firm was registered under Annex 1 for
> money laundering supervision but was not authorised under the wider financial
> services regime, and that it entered administration on 25 February 2026... An
> investigation is not a finding of misconduct. No later FCA outcome was identified
> in the primary-source review completed on 26 August 2026."

**Ledger**: `fca-mfs-investigation.001`.

**Primary source** (`fca.org.uk/news/statements/investigation-market-financial-solutions-limited`,
fetched 2026-08-27): "MFS is an Annex 1 business, which is solely registered with
and supervised by us for its compliance with the [MLRs 2017]"; the FCA "opened an
enforcement investigation into Market Financial Solutions Limited (MFS)"; "MFS
entered administration on 25 February 2026."

**Assessment for reviewer**: matches. The "investigation is not a finding of
misconduct" framing and "do not generalise... to Annex 1 firms as a class" caveat
are FinCrimeRadar's own analytical framing, correctly labelled as such rather than
attributed to the FCA (consistent with CLAUDE.md section 10's source/application/
recommendation separation). Reviewer should independently confirm no FCA outcome
has since been published, since "no later outcome was identified" is a
point-in-time claim (as of 26 August 2026) that could go stale.

---

### E. NRA bridging-finance context (worked scenario 2 callout)

**Guide** (`#spv-scenario`, "Narrow 2025 National Risk Assessment context",
unchanged since `d5b399c`):
> "The assessment reports criminal use of bridging loans and bridging-loan
> companies, and says speed and flexibility can create susceptibility to money
> laundering. It notes that many bridging lenders are Annex 1 supervised while some
> are FSMA regulated. This supports transaction-specific scrutiny, not a
> presumption against bridging lenders."

**Ledger**: `nra-bridging-finance.001`.

**Primary source**, National Risk Assessment of Money Laundering and Terrorist
Financing 2025, **paragraph 3.97**, extracted directly from the PDF at
`assets.publishing.service.gov.uk` on 2026-08-27 (verbatim, not summarised):
> "The exact scale of money laundering through high-end commercial real estate is
> unknown. Identified examples have included the use of professional services and
> criminals financing property purchases with bridging loans, which are then
> replaced by mortgages from UK financial institutions (bridging finance is a
> short-term loan used to bridge the gap between money going out and money coming
> in). Criminals have set up bridging loan companies to launder their funds, issuing
> their criminal capital as bridging loans which are then repaid as legitimate
> investments. Bridging finance is characterised by speed and flexibility, making it
> a popular choice for property transactions. However, the rapid nature of these
> transactions also makes bridging finance susceptible to money laundering risks.
> **Bridging finance firms are supervised by the FCA, many as annex 1 activity under
> the MLRs. Some bridging finance is regulated under FSMA.**"

**Assessment for reviewer**: matches precisely, including the "many... some" framing
(not "most" or "all"). Also unrevised since `d5b399c`; no correction-cycle scrutiny
yet.

---

### F. FCA scrutiny and due-diligence statistics

**Guide** (`#concerns`, unchanged since `d5b399c`):
> "The FCA said it was applying increased scrutiny to Annex 1 firms because it was
> concerned some may facilitate financial crime. It sent information requests to
> around 900 firms after contacting 300 firms in late 2025, meaning all registered
> Annex 1 firms had been contacted."
> "The FCA told regulated firms dealing with Annex 1 entities to conduct appropriate
> due diligence. Its March statement highlighted direct confirmation with
> customers, independent checks and understanding the risks presented."

**Ledger**: `fca-august-scrutiny.001`, `fca-march-due-diligence.001`.

**Primary source, 7 August 2026 statement** (fetched 2026-08-27): FCA "sent an
information request to around 900 Annex 1 firms" following prior contact with "300
Annex 1 firms in late 2025." Concerns: firms "rely too heavily on the financial
crime controls of their parent company"; cannot use "off-the-shelf procedures
designed for a different company"; FCA "concerned about the risks... from
unregulated lending often conducted through complex structures, including special
purpose vehicles"; regulated firms must "do their due diligence... including
seeking direct confirmation of their registration status."

**Primary source, 20 March 2026 statement** (fetched 2026-08-27): "There are around
1,200 of these firms registered with us for solely anti-money laundering purposes."
"Our wider conduct rules do not apply to these firms, nor are customers of Annex 1
firms able to access the Financial Ombudsman Service." Regulated firms should "seek
direct confirmation from the firm of their registration status, conduct independent
checks of the information they provide, and understand and manage any risks."

**Assessment for reviewer**: matches on both statements, including the 900/300/1,200
figures and the specific due-diligence actions named. The guide's "meaning all
registered Annex 1 firms had been contacted" is FinCrimeRadar's own arithmetic
(900 + 300 ≈ the ~1,200 figure from the separate March statement), not a sentence
the FCA itself states in the August release, worth the reviewer confirming that
inference is sound and not overstated as an FCA claim.

---

### G. Regulation 10 and Schedule 2 scope

**Guide** (`#meaning`, unchanged since `d5b399c`):
> "Regulation 10 and Schedule 2 describe relevant financial activity... Broad
> activities can include lending, financial leasing, guarantees and commitments,
> certain payment or investment-related services, and safe custody. Scope depends on
> the precise activity, exclusions and surrounding facts."

**Ledger**: `mlr-reg10-schedule2-scope.001`.

**Primary source** (legislation.gov.uk, fetched 2026-08-27): regulation 10(2)(a)
defines "financial institution" (subject to 10(3) exclusions) as an undertaking
that carries out one or more "listed activity," and 10(4)(a) defines "listed
activity" as an activity listed in points 2–12, 14 and 15 of Schedule 2.

**Assessment for reviewer**: matches; the guide correctly frames this as broad,
condition-dependent categories rather than a fixed list, consistent with the
regulation's own conditional structure.

---

## Internal consistency sweep (CLAUDE.md section 8)

Every representation of each proposition above was located and checked for drift:

- **Reg 55–59 chain**: appears once in body prose (`#meaning`) and once in a
  restating callout box in the same section, plus the Sources list citations.
  Identical wording both places, no stray or stale restatement in the matrix, FAQ,
  workflow list, or quiz.
- **Authorised vs registered**: appears in the opening scenario, the trap section's
  three status cards, and FAQ item 1. All consistent; no version asserts something
  the others don't.
- **SPV registration test**: appears in worked scenario 2, the matrix table's "SPV
  provides or receives unexplained finance" row ("The SPV needs Annex 1
  registration merely because loan interests were transferred" listed correctly
  under "What it does not mean"), and the SPV fog pattern card. Consistent.
- **Four risk-pattern cards** (Registry halo, Borrowed controls, Entity drift, SPV
  fog): now byte-identical between the canonical `#patterns` section and the four
  inline contextual cards, confirmed directly against the live HTML on 2026-08-27
  (this is the drift `423f3d3` fixed; re-confirmed still fixed, not re-drifted).

No claim in this guide was found stated one way in one place and a different way
elsewhere.

---

## What the external reviewer should do with this pack

1. Adjudicate Flag 1 (regulation 56 paragraph precision): acceptable abstraction or
   needs a subsection-level correction citing 56(5) specifically.
2. Decide Flag 2 (orphaned source 9): add a citation, or leave as background
   reading, reviewer's call.
3. Independently re-verify every "Primary source" quote above against the live URL
   given, rather than trusting this document's transcription, per CLAUDE.md section
   18's caution against treating a single fetch as unquestionable ground truth.
4. Give particular scrutiny to claim clusters C (SPV test) and E (NRA context),
   since both are original `d5b399c` text that has never been through any
   correction cycle and has had zero external review to date.
5. Report findings (or a clean pass) back through the normal channel; this guide's
   BACKLOG.md item stays open until that happens, not merely because this pack now
   exists.
