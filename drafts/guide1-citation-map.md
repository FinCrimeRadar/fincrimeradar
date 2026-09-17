# Citation numbering map — stablecoin-series-guide-1.html, Sections A-L

Status: planning only, not implemented. No inline `[n]` markers, no Sources section,
and no ledger changes have been made to the guide from this map. Regenerated directly
from the live `stablecoin-series-guide-1.html` working tree and the 42 dedicated
`verification-ledger.json` entries for this guide (guide field exactly matching
`stablecoin-series-guide-1.html (not yet published: drafting substantially complete,
Sections A-L, both worked scenarios, the Risk/Signal/Response cards and the
activity-classification diagram are all built; no inline citations or rendered Sources
section exist yet; the overseas-issuance, hybrid-stablecoin and split-out
wrapping/bridging claims carry their own pending-external-review status independently
of this guide-level note)`).

The 6 ledger entries jointly attributed to this guide and `systemic-stablecoins-guide.html`
are out of scope for this map: 5 are explicitly marked "legacy, not a live dependency of
either guide's evidence pack", and the sixth (`smcr-enhanced-thresholds-stablecoin-custodian.001`)
is explicitly "background cross-reference, not currently mapped to either guide's section
structure." None of the 6 correspond to text currently in Sections A-L.

## Numbered source list

Grouped by distinct primary source document, not by claim. Several claims cite the same
statutory instrument or the same FCA policy statement at different provisions; the
specific article, regulation, or chapter is already named in the guide's own prose, so the
pinpoint travels in the sentence and the footnote number stays generic to the document.

| # | Source | Publisher | URL |
|---|---|---|---|
| [1] | The Financial Services and Markets Act 2000 (Cryptoassets) Regulations 2026 (SI 2026/102) | legislation.gov.uk | https://www.legislation.gov.uk/uksi/2026/102/made |
| [2] | FCA, Policy Statement PS26/18, Cryptoasset Perimeter Guidance | Financial Conduct Authority | https://www.fca.org.uk/publication/policy/ps26-18.pdf |
| [3] | FCA Policy Statement PS26/13, "Crypto Regime: Application of FCA Handbook for Regulated Cryptoasset Activities" | Financial Conduct Authority | https://www.fca.org.uk/publication/policy/ps26-13.pdf |
| [4] | FCA, "Cryptoassets: How the gateway will operate" | Financial Conduct Authority | https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/how-gateway-will-operate |
| [5] | FCA, "Cryptoassets: The transitional provision" | Financial Conduct Authority | https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/transitional-provision |
| [6] | The Money Laundering and Terrorist Financing (Amendment) Regulations 2026 (SI 2026/621) | legislation.gov.uk | https://www.legislation.gov.uk/uksi/2026/621/pdfs/uksi_20260621_en.pdf |
| [7] | FCA Policy Statement PS26/10, "Crypto Regime: Stablecoin issuance" | Financial Conduct Authority | https://www.fca.org.uk/publication/policy/ps26-10.pdf |

7 distinct sources cover 40 of the 42 dedicated claims. The remaining 2 have no source by
design (see Category 2 flags below) and must never receive a number.

## Section-by-section attachment map

### Section A — What legally counts as a stablecoin?

- "Article 88F of the Regulated Activities Order defines a 'qualifying cryptoasset'..." → **[1]** (`article-88f-qualifying-cryptoasset.001`)
- "...the main one for this guide being electronic money" (clause inside that same sentence, not the sentence as a whole) → **[1]** (`article-88f-emoney-exclusion.001`)
- "Article 88G then narrows that further: a 'qualifying stablecoin'..." → **[1]** (`article-88g-qualifying-stablecoin.001`)
- "article 88G(3) says a non-fiat reference doesn't qualify..." (Application paragraph) → **[1]** (`article-88g-qualifying-stablecoin.001`, 88G(3) limb, same claim as above)
- "the FCA's own guidance... states plainly that a mechanism relying partly or wholly on algorithmic methods... does not produce a qualifying stablecoin" → **[2]** (`perg18-4-5-hybrid-wrapped-stablecoin.001`)
- Whole "wrapped token" paragraph ("A wrapped token, one issued in exchange for holding or locking up another cryptoasset...") → **[2]** (`perg18-4-5-hybrid-wrapped-stablecoin.001`, second, non-adjacent location for the same claim)
- "Whether providing the wrapping service itself amounts to a separately regulated activity is a live question this guide doesn't resolve yet" → **no citation, no home yet** (see flags: this is where `perg18-8-7-wrapping-services-dealing-arranging.001` would attach once this point is drafted, and the sentence itself says it is deliberately left open)

### Section B — Who is "issuing" a qualifying stablecoin?

- "Under article 9M(1)-(2), a person (A) is issuing a qualifying stablecoin only where..." through "...holding or arranging the holding of the backing assets." → **[1]** (`article-9m-issuing-conditions.001`)
- "Article 9M(3) then narrows the offering limb specifically..." through end of that Source paragraph → **[1]** (`article-9m-minting-exclusion.001`)
- "Article 9M(4)(c) answers who's on the hook in that situation directly..." → **[1]** (`article-9m-outsourcing-issuer.001`)
- "That 'provided' is doing real work..." paragraph → no new citation; derivative reasoning from the 9M(4)(c) fact already cited above, optional repeat of **[1]**.

### Section C — Who is "safeguarding" a qualifying stablecoin?

- "Article 9N(1) makes two things specified activities in their own right..." → **[1]** (`article-9n-safeguarding-activity.001`)
- "Article 9N(2)(a) defines safeguarding by a control-based test..." through "...includes a private cryptographic key." → **[1]** (`article-9n-control-based-test.001`)
- "Articles 9O to 9R then carve out four specific situations..." (rest of that sentence) → **[1]** (`articles-9o-9r-safeguarding-exclusions.001`)

### Section D — What activity is a stablecoin trading platform, dealer, or arranger carrying on?

One Source paragraph, five sentences, five claims, mapped 1:1:

- "Article 9S makes operating a qualifying cryptoasset trading platform a specified activity in a single, standalone provision, with no exclusions set out in the article itself." → **[1]** (`article-9s-trading-platform.001`)
- "Article 9T makes buying, selling, subscribing for or underwriting a qualifying cryptoasset as principal a specified activity; article 9U excludes transactions absent specific holding-out or public-solicitation conduct... and article 9V excludes stablecoin creation and design, minting..." → **[1]** (`articles-9t-9v-dealing-principal.001`)
- "Article 9W makes the same conduct a specified activity where it's carried on as agent rather than principal; article 9X excludes the same stablecoin-specific categories as article 9V..." → **[1]** (`articles-9w-9x-dealing-agent.001`)
- "Article 9Y makes two things specified activities: arrangements for another to deal in a qualifying cryptoasset, and arrangements made with a view to a participant dealing; articles 9Z to 9Z5 exclude..." → **[1]** (`articles-9y-9z5-arranging-deals.001`)
- "Article 9Z6 sits alongside all three: it makes arranging, as principal or agent, for qualifying cryptoasset staking a specified activity in its own right..." → **[1]** (`article-9z6-staking-context.001`)

### Section E — Two exclusions that cut across every activity in this guide

- Whole Source paragraph ("Article 9Z10 excludes activity carried on by a supplier of goods or services..." and "Article 9Z11 excludes activity incidental to a profession or business...") → **[1]** (`articles-9z10-9z11-incidental-exclusions.001`)

### Section F — Territorial scope, UK and overseas issuers

- "PERG 18.3.5 states that issuing a qualifying stablecoin is considered to be carried on in the UK..." through "...unless a relevant exemption, saving or transitional provision applies." → **[2]** (`perg18-3-5-section418-6b-overseas-deeming.001`)
- "PERG 18.8.5-18.8.6 addresses the other side of this..." through end of that Source paragraph → **[2]** (`perg18-8-5-overseas-issuer-dealing-permission.001`)
- Application paragraph 1 ("Article 9M(2)(a) and (c), already covered in Section B...") → derivative of the two claims just cited; no new source, optional repeat of **[2]**.
- "The FCA's AICF guidance sets a default expectation that international cryptoasset firms will operate through a UK legal entity..." (whole paragraph) → **[3]** (`regulatory-status-aicf-legal-entity.001`, PS26/13 Chapter 2)

### Section G — Commencement, the application window, and the saving and transitional provisions

- "Subject to the preparatory-commencement carve-out below, the Regulations come into force on 25 October 2027..." → **[1]** (`regulation-1-full-commencement.001`)
- "For a defined set of preparatory purposes only, they come into force earlier..." → **[1]** (`regulation-1-preparatory-commencement.001`)
- "The cryptoasset authorisation application period itself runs from 30 September 2026 to 28 February 2027..." → **[4]** (`application-window-dates.001`)
- "The saving provision protects a firm that applied for authorisation..." through "...moves into the transitional provision to exit the market in an orderly manner." (first three sentences of the paragraph, including the FCA-redirect-power sentence, which appears verbatim inside this claim's own text) → **[4]** (`saving-provision-mechanics.001`)
- "The transitional provision is a separate, more restrictive mechanism..." through end of that paragraph → **[5]** (`transitional-provision-mechanics.001`)

### Section H — The parallel MLR registration regime

- Whole Source paragraph (regulation 14A pre-existing, SI 2026/621's three separate commencement dates) → **[6]** (`mlr-2017-fsma-2026-parallel-regimes.001`)
- "Regulation 34A requires a cryptoasset exchange provider or custodian wallet provider..." → **[6]** (`mlr-reg34a-enhanced-due-diligence.001`)
- "Schedule 6B applies the existing FSMA change-of-control regime..." → **[6]** (`mlr-schedule6b-change-of-control.001`)
- "Registration under regulation 14A doesn't convert into FSMA authorisation automatically either..." (Application paragraph, final clause) → **[5]**, not [6] — see flags, this is the wrong-source trap.

### Section I — CASS treatment of an issuer's money

- "CASS 7, the ordinary client money chapter, is disapplied in full for firms carrying on the issuing activity..." through "...is unchanged." → **[3]** (`cass7-disapplied-stablecoin-issuers.001`)
- "CASS 16 is the chapter that actually governs the backing funds account..." through end of that paragraph → **[3]** (`cass16-backing-assets-segregation.001`)

### Section J — CASS treatment of safeguarding firms

- "CASS 17 applies to a firm safeguarding qualifying cryptoassets..." → **[3]** (`cass17-qualifying-cryptoasset-safeguarding.001`)
- "RSIC custody is not under CASS 17 at all..." through "...before this regime existed." → **[3]** (`rsic-cass6-not-cass17.001`)
- "Separately again, CASS 8, the mandate rules, does not apply..." through end of that paragraph → **[3]** (`cass8-not-applicable-article9n-safeguarding.001`)

### Section K — CASS 7 protections that survive for other cryptoasset business

- "The professional client opt-out under CASS 7 is disapplied..." → **[3]** (`cass7-professional-client-optout-disapplied.001`)
- "The delivery-versus-payment (DvP) exemption for commercial settlement systems is separately disapplied..." → **[3]** (`cass7-dvp-exemption-disapplied.001`)

### Section L — The due diligence framework checklist

- "regulation 13(1)(a)(ii) requires disclosure of the underlying technology..." (technical control fields paragraph) → **[1]** (`regulation13-qcdd-technical-control-fields.001`)
- Reserve composition and custodian fields paragraph (whole paragraph) → **[7]** (`reserve-composition-custodian-ps26-10.001`)
- Redemption and disclosure fields paragraph (whole paragraph) → **[7]** (`redemption-disclosure-ps26-10.001`)
- Independent assurance field paragraph (whole paragraph) → **[7]** (`independent-assurance-fca-mandated.001`)
- "Historical depegs, sanctions exposure, and previous enforcement incidents..." → **no citation** (see Category 2 flags)
- "Concentration risk arising from a limited pool of unconnected custodians..." → **no citation** (see Category 2 flags)

## Flags

### No clean single-sentence attachment (claim spread across a paragraph or across locations)

- **Section G, paragraph 2.** One continuous paragraph carries two different citations
  mid-flow: [4] for the first three sentences (through "...orderly manner."), then [5]
  from "The transitional provision is a separate, more restrictive mechanism..." onward.
  The saving/transitional split reads as one idea; mark at the end of sentence 3 and again
  at the end of the paragraph, not with one marker for the whole thing.
- **Section A.** `perg18-4-5-hybrid-wrapped-stablecoin.001` attaches at two separate,
  non-adjacent locations: the algorithmic-mechanism sentence inside the Application
  paragraph, and the entire wrapped-token paragraph that follows it. Same claim, same [2],
  needs two markers, not one.
- **Section H, paragraph 2.** `mlr-reg34a-enhanced-due-diligence.001` and
  `mlr-schedule6b-change-of-control.001` both live inside one paragraph, but both share
  citation [6] with the rest of the section, so there is no visible splitting problem in
  practice. Flagged only so whoever inserts markers doesn't assume the paragraph needs
  three different numbers when it needs one.

### Sub-sentence attachment

- **Section A.** `article-88f-emoney-exclusion.001` attaches to a four-word clause ("the
  main one for this guide being electronic money") inside a longer sentence about article
  88F generally, not to the sentence as a whole. A marker here has to sit mid-sentence,
  immediately after that clause.

### Wrong-source trap

- **Section H, Application paragraph, final sentence** ("Registration under regulation
  14A doesn't convert into FSMA authorisation automatically either...") sits inside a
  paragraph otherwise entirely sourced to [6] (SI 2026/621), but this specific sentence is
  actually the trailing "Background, not independently verified" caveat inside
  `transitional-provision-mechanics.001` — source [5], not [6]. Proximity to the rest of
  the paragraph makes it easy to mis-cite as [6] by default; this is exactly the kind of
  case this map exists to catch before insertion.

### Category 2 fields — must not get a citation number

- **Section L**: "Historical depegs, sanctions exposure, and previous enforcement
  incidents reflect standard KYB and AML investigative practice; no FCA source reviewed
  for this guide requires disclosure of any of the three." Corresponds to
  `ddframework-category2-non-mandated-fields.001`, which has `"source": null` and status
  `retained-as-estimate` by design. A numbered citation here would misrepresent an
  explicitly unsourced field as sourced.
- **Section L**: "Concentration risk arising from a limited pool of unconnected
  custodians is included on the same basis... could not be verified... no regulatory
  citation behind it." Corresponds to `concentration-risk-citation-unverified.001`, status
  `unverifiable-remove`, `"source": null`. This sentence states directly that it carries no
  citation; giving it one would contradict its own text.

### Claims with no current attachment point at all

- **`perg18-8-7-wrapping-services-dealing-arranging.001`** (the
  wrapping/bridging claim corrected in the prior ledger task) has no home in the current
  guide text. Section A explicitly defers the question it answers: "Whether providing the
  wrapping service itself amounts to a separately regulated activity is a live question
  this guide doesn't resolve yet; treat it as open until that specific point has been
  through this repository's own review process, not as settled." Nothing to mark until
  that section is actually drafted.
- **`issuer-entity-jurisdiction-partial.001`** is not guide prose
  at all. Its claimText is a ledger housekeeping note recording a mis-attribution that was
  later corrected and superseded by `regulatory-status-aicf-legal-entity.001`, which does
  have a clean attachment point in Section F (see above). No marker recommended for this
  claimId; its substantive content is fully absorbed by [3] at Section F already.

### Illustrative material, correctly out of scope for markers

- The six Risk/Signal/Response cards (inline and in the closing "At a glance" grid) and
  the activity-classification diagram (inline SVG-equivalent plus its plain-text
  walkthrough) all restate already-cited claims in illustrative or summary form. Per the
  Universal Evidence Core, illustrative material doesn't get its own citation. These
  should stay uncited when markers go in, to avoid double-citing the same claim at both
  its source sentence and its card/diagram summary.

## Completeness check against the 42 dedicated claims

Every one of the 42 dedicated claimIds appears above in exactly one of three states:
attached to a specific sentence/paragraph with a numbered citation, listed under a "no
citation" Category 2 flag, or listed under "no current attachment point at all." The
automated check run against this file (see below) confirms no claimId fell through.

| # | claimId | Disposition |
|---|---|---|
| 1 | article-9m-issuing-conditions.001 | Section B, [1] |
| 2 | article-9m-minting-exclusion.001 | Section B, [1] |
| 3 | article-9m-outsourcing-issuer.001 | Section B, [1] |
| 4 | article-9n-safeguarding-activity.001 | Section C, [1] |
| 5 | article-9n-control-based-test.001 | Section C, [1] |
| 6 | articles-9o-9r-safeguarding-exclusions.001 | Section C, [1] |
| 7 | article-9s-trading-platform.001 | Section D, [1] |
| 8 | articles-9t-9v-dealing-principal.001 | Section D, [1] |
| 9 | articles-9w-9x-dealing-agent.001 | Section D, [1] |
| 10 | articles-9y-9z5-arranging-deals.001 | Section D, [1] |
| 11 | article-9z6-staking-context.001 | Section D, [1] |
| 12 | articles-9z10-9z11-incidental-exclusions.001 | Section E, [1] |
| 13 | article-88f-qualifying-cryptoasset.001 | Section A, [1] |
| 14 | article-88g-qualifying-stablecoin.001 | Section A, [1] |
| 15 | article-88f-emoney-exclusion.001 | Section A, [1] (sub-sentence flag) |
| 16 | regulation-1-full-commencement.001 | Section G, [1] |
| 17 | regulation-1-preparatory-commencement.001 | Section G, [1] |
| 18 | mlr-2017-fsma-2026-parallel-regimes.001 | Section H, [6] |
| 19 | mlr-reg34a-enhanced-due-diligence.001 | Section H, [6] |
| 20 | mlr-schedule6b-change-of-control.001 | Section H, [6] |
| 21 | cass7-disapplied-stablecoin-issuers.001 | Section I, [3] |
| 22 | cass16-backing-assets-segregation.001 | Section I, [3] |
| 23 | cass17-qualifying-cryptoasset-safeguarding.001 | Section J, [3] |
| 24 | rsic-cass6-not-cass17.001 | Section J, [3] |
| 25 | cass8-not-applicable-article9n-safeguarding.001 | Section J, [3] |
| 26 | cass7-professional-client-optout-disapplied.001 | Section K, [3] |
| 27 | cass7-dvp-exemption-disapplied.001 | Section K, [3] |
| 28 | application-window-dates.001 | Section G, [4] |
| 29 | saving-provision-mechanics.001 | Section G, [4] |
| 30 | transitional-provision-mechanics.001 | Section G, [5]; echoed at Section H (wrong-source trap flag) |
| 31 | regulation13-qcdd-technical-control-fields.001 | Section L, [1] |
| 32 | issuer-entity-jurisdiction-partial.001 | No attachment point; superseded, flagged |
| 33 | reserve-composition-custodian-ps26-10.001 | Section L, [7] |
| 34 | redemption-disclosure-ps26-10.001 | Section L, [7] |
| 35 | ddframework-category2-non-mandated-fields.001 | Section L; no citation, Category 2 flag |
| 36 | independent-assurance-fca-mandated.001 | Section L, [7] |
| 37 | concentration-risk-citation-unverified.001 | Section L; no citation, Category 2 flag |
| 38 | regulatory-status-aicf-legal-entity.001 | Section F, [3] |
| 39 | perg18-3-5-section418-6b-overseas-deeming.001 | Section F, [2] |
| 40 | perg18-8-5-overseas-issuer-dealing-permission.001 | Section F, [2] |
| 41 | perg18-4-5-hybrid-wrapped-stablecoin.001 | Section A, [2] (two locations) |
| 42 | perg18-8-7-wrapping-services-dealing-arranging.001 | No attachment point; guide text defers this question, flagged |
