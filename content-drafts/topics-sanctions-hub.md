<!--
STATUS: Unpublished pilot content. Reference material for the eventual
/topics/ hub scoping session only. NOT a live guide, NOT routed under any
URL, NOT linked from any live page. The /topics/ hub build itself remains
on hold pending that scoping session (conflicts with the Domains rail
already shipped in the Knowledge Hub redesign; no /topics/ subdirectory
or URL infrastructure exists on this static site yet). See BACKLOG.md,
Polish Loop, "Eight /topics/ hub pages" for the open decision this
belongs to.

Sourcing pass completed 2026-08-12: the two [NEEDS SOURCING] gaps in the
original draft are now filled with primary-sourced material, logged in
verification-ledger.json (claimIds prefixed topics-sanctions-hub.*). The
"Sanctions Ownership and Control" cross-link was removed, that guide
does not exist yet and should not be referenced as if it does.
-->

# Sanctions Compliance: The FinCrimeRadar Topic Hub

## What sanctions screening actually is

Sanctions screening is the process of checking a customer, counterparty,
or transaction against government-maintained lists of designated
individuals, entities, vessels, and jurisdictions, to prevent a firm from
knowingly or unknowingly dealing with a sanctioned party. It sits
alongside PEP screening and adverse media monitoring as one of the three
pillars of a modern screening programme, but carries the highest
consequence of the three, sanctions breaches can mean strict liability
regardless of intent, unlike most AML obligations.

## OFAC versus OFSI: two regimes, two different postures

The US Treasury's Office of Foreign Assets Control (OFAC) and the UK's
Office of Financial Sanctions Implementation (OFSI) both administer
sanctions regimes, but a firm operating across both jurisdictions needs
to understand they aren't interchangeable, particularly on the question
of what a firm has to prove, or disprove, once a breach has happened.

OFAC has applied a strict liability standard to civil penalties for many
years: a person subject to US jurisdiction can be held civilly liable
even if they did not know, or have no reason to know, that a transaction
was prohibited [1]. Knowledge and intent affect how OFAC weighs
aggravating and mitigating factors when it sets the size of a penalty,
but they are not a defence to liability itself.

OFSI's position converged toward the same standard more recently. For
breaches on or after 15 June 2022, the Economic Crime (Transparency and
Enforcement) Act 2022 amended section 146 of the Policing and Crime Act
2017 so that OFSI no longer has to prove a person knew, suspected, or had
reasonable cause to believe they were in breach, establishing strict
civil liability on the UK side too [2]. Knowledge doesn't disappear from
the analysis, it's still weighed as a case factor when OFSI assesses how
severe a breach was and whether the person's conduct was mitigating,
neutral, or aggravating. OFSI's most recent guidance update (9 February
2026) also introduced a four-level seriousness model for classifying
breaches, from Level 1 (least serious) to Level 4, where a case can
warrant a criminal referral or a penalty set at 75 to 100% of the
statutory maximum [2].

The practical difference for a firm operating across both regimes isn't
whether strict liability applies, it now does on both sides, it's that
OFAC and OFSI arrive at a penalty figure through different assessment
frameworks, and disclosure behaves differently under each (see the
enforcement examples below, both UK cases here received a 50% penalty
reduction for voluntary disclosure).

## Sanctions evasion typologies

Sanctioned parties don't stop transacting, they restructure how they
transact. The common patterns worth understanding at a glance: ownership
layering through shell entities and nominee directors (see the UBO
Investigation Handbook for the investigative technique), trade-based
value transfer through over- or under-invoicing, and, increasingly,
crypto-asset movement through unhosted wallets and cross-chain hopping
(see Crypto Guide Part 4 on how wallets actually end up sanctioned).

## Name matching and the false positive problem

A sanctions match starts with a name comparison, but name comparison
alone produces an unacceptable false positive rate at scale, common
names, transliteration variance, and deliberate obfuscation all defeat
naive string matching. The Tuning Screening Algorithms guide covers the
actual mechanics, Jaro-Winkler, phonetic matching, the production
threshold tradeoffs, with a real documented case of two different people
scoring 0.98 on the same list.

## Ownership and control: the 50% rule isn't the whole analysis

Direct ownership above a stated threshold is the easy case. Real evasion
usually runs through indirect ownership, control without ownership,
family members, trusts, or layered corporate structures, none of which a
simple percentage threshold catches.

## Screening in practice: from alert to decision

A name hit is the start of an investigation, not the end of one. The
Screening Alert Survival Guide covers the operational reality, alert
fatigue, documentation burden, what actually helps an analyst work
through volume without missing a genuine match.

## Enforcement, why this isn't theoretical

Three recent, dated cases across both regimes, chosen to show what
strict liability actually looks like in practice, not as an exhaustive
list.

OFAC assessed a $215,988,868 civil monetary penalty, the statutory
maximum, against GVA Capital Ltd., a San Francisco venture capital firm,
after it knowingly managed investments on behalf of sanctioned Russian
oligarch Suleiman Kerimov between April 2018 and May 2021, routing the
relationship through Kerimov's nephew as a known proxy, and then failed
to comply with an OFAC subpoena during the investigation [3].

OFSI imposed a £160,000 penalty on Bank of Scotland Plc (published 26
January 2026, penalty imposed 10 November 2025) after the bank processed
payments to and from a personal account held by a person designated
under the Russia sanctions regime, a 50% voluntary disclosure discount
brought the figure down from £320,000 [4].

OFSI imposed a £465,000 penalty on Herbert Smith Freehills CIS LLP's
Moscow office (published 20 March 2025) over six payments totalling
£3,932,392.10 made to designated persons, via Alfa-Bank, Sovcombank, and
Sberbank, during the hasty closure of the firm's Russian office in May
2022, again reduced by 50% for voluntary disclosure from an initial
£930,000 [5].

## Guides in this cluster

- FATF Grey List, Black List & Country Risk (Parts 1 and 2)
- The Sanctions Compliance Guide
- Tuning Screening Algorithms
- The Screening Alert Survival Guide
- The Crypto Travel Rule Sunrise Guide
- Crypto Guide Part 4: How Wallets Actually End Up Sanctioned

## Sources

1. Office of Foreign Assets Control, U.S. Department of the Treasury, *FAQ 65* (strict liability for civil penalties), last substantively amended 13 November 2024. [ofac.treasury.gov/faqs/65](https://ofac.treasury.gov/faqs/65)
2. Office of Financial Sanctions Implementation (OFSI), HM Treasury, *Financial sanctions enforcement and monetary penalties guidance*, updated 9 February 2026 (strict civil liability for breaches on or after 15 June 2022; four-level seriousness model). [gov.uk/government/publications/financial-sanctions-enforcement-and-monetary-penalties-guidance](https://www.gov.uk/government/publications/financial-sanctions-enforcement-and-monetary-penalties-guidance/financial-sanctions-enforcement-and-monetary-penalties-guidance)
3. Office of Foreign Assets Control, U.S. Department of the Treasury, *Civil Monetary Penalty against GVA Capital, Ltd.*, 12 June 2025. [ofac.treasury.gov/recent-actions/20250612](https://ofac.treasury.gov/recent-actions/20250612)
4. Office of Financial Sanctions Implementation (OFSI), HM Treasury, *Imposition of a monetary penalty: Bank of Scotland Plc*, published 26 January 2026. [gov.uk/government/publications/imposition-of-monetary-penalty-bank-of-scotland-plc](https://www.gov.uk/government/publications/imposition-of-monetary-penalty-bank-of-scotland-plc)
5. Office of Financial Sanctions Implementation (OFSI), HM Treasury, *Herbert Smith Freehills CIS LLP monetary penalty notice*, published 20 March 2025. [assets.publishing.service.gov.uk/.../200325_HSF_PENALTY_NOTICE.pdf](https://assets.publishing.service.gov.uk/media/67dae19a1a60f79643028472/200325_HSF_PENALTY_NOTICE.pdf)
