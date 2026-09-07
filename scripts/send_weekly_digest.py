#!/usr/bin/env python3
"""
FinCrimeRadar weekly compliance digest.

Scans the delta tracker's own output for the past 7 days, builds a
short HTML summary, and sends it as a real campaign through Brevo to
the list the newsletter signup form actually feeds now that
api/subscribe.js exists.

Required environment variables, set as GitHub Actions secrets:
  BREVO_API_KEY    same key used by the subscribe endpoint
  BREVO_LIST_ID    same list id used by the subscribe endpoint
  BREVO_SENDER_EMAIL   a verified sender address in your Brevo account
  BREVO_SENDER_NAME    display name for the sender, for example FinCrimeRadar

Design choices, and why:
  - Reads the delta pages already committed by the tracker rather than
    recomputing anything, this script has zero opinion on sanctions
    data, it only summarises what the tracker already published.
  - Sends via the Email Campaigns API, not the transactional SMTP
    endpoint, because this is a genuine one to many newsletter send to
    a list, not a per user transactional email.
  - Fails loudly and exits non zero on any Brevo error, this runs
    unattended on a schedule and a silent failure here would mean
    subscribers simply never receive anything with nobody noticing,
    exactly the failure mode that broke the signup form for months.
  - Reads a hidden metadata comment the tracker embeds in every page it
    writes, recording whether that day's run was a manual override.
    A subscriber seeing an unusually large amendment count with no
    explanation has no way to distinguish a deliberate one time
    correction from a data anomaly or a bug, this closes that gap by
    naming the exact day and threshold used, directly in the email.
"""

import glob
import html as html_escape
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fincrime_week_lib import esc, load_latest_published_fincrime_week

DELTA_DIR = "delta"
SITE = "https://fincrimeradar.org"
WINDOW_DAYS = 7

META_PATTERN = re.compile(
    r"<!--\s*fincrimeradar-meta:\s*trigger=(\S+)\s+override_active=(yes|no)\s+threshold=(\d+)\s*-->"
)

# Append new guides to the end of this list when they ship. get_this_weeks_guides()
# deterministically rotates through the library by ISO week, so which guides
# appear changes automatically once the library grows past `count` entries.
GUIDE_LIBRARY = [
    {
        "title": "Synthetic Identity and Device-Network Fraud: Two Different Problems People Treat as One",
        "hook": "The industry teaches the detection technology. Nobody teaches the judgement once the alert is already in your queue. Four patterns, three decision scenarios, and a comparative matrix on stolen versus synthetic identity, with a knowledge check.",
        "url": "https://www.fincrimeradar.org/synthetic-identity-device-network-guide.html",
    },
    {
        "title": "Money Mule Networks: The Account Was Never Fraudulent, Until It Was",
        "hook": "Most mule accounts aren't opened for fraud anymore, they're real accounts taken over mid-life. Four decision scenarios on account handovers, instant-payment velocity, business-account fronts, and fraud-AML convergence, with a real £53m case and a knowledge check.",
        "url": "https://www.fincrimeradar.org/money-mule-financial-crime-networks-handbook.html",
    },
    {
        "title": "The Crypto Travel Rule: Making the Call When the Data Doesn't Arrive",
        "hook": "The sunrise problem isn't a policy debate, it's a decision on incomplete data. An interactive decision tree for sending and receiving crypto transfers, the EU's two different thresholds, and what to do when a counterparty's data never arrives.",
        "url": "https://www.fincrimeradar.org/crypto-travel-rule-sunrise-guide.html",
    },
    {
        "title": "Perpetual KYC: Why Periodic and Event-Driven Review Are Not the Same Control",
        "hook": "The FCA's 8 April 2026 review found firms collapse periodic and event-driven review into one control, or define neither well enough to evidence. Four decision scenarios, the Nationwide £44m case, and a knowledge check.",
        "url": "https://www.fincrimeradar.org/perpetual-kyc-framework-guide.html",
    },
    {
        "title": "Transaction Monitoring: From Rules to AI, The Practitioner's Deep Dive",
        "hook": "How TM systems really work, why 95% of alerts are false positives, how AI is changing the game, and what analysts actually do when the queue hits 400. Includes typology cards, alert triage simulator, and knowledge check.",
        "url": "https://www.fincrimeradar.org/tm-guide.html",
    },
    {
        "title": "The Screening Alert Survival Guide: 7 Challenges Every Analyst Faces",
        "hook": "800 alerts. 95% false positives. No DOB on file. The honest, unfiltered guide to what screening alert clearance actually involves, and what genuinely helps.",
        "url": "https://www.fincrimeradar.org/screening-alerts-guide.html",
    },
    {
        "title": "What is Financial Crime Screening? The Complete Guide",
        "hook": "A comprehensive, interactive introduction to sanctions screening, PEP checks, and adverse media monitoring, with quizzes, real examples, and live tool access.",
        "url": "https://www.fincrimeradar.org/learn.html",
    },
    {
        "title": "KYC / KYB / CDD / EDD: The Onboarding Dilemma",
        "hook": "Six archetypes from lone individual to sovereign wealth fund. Six real dilemmas. Make the call yourself, then see the correct answer and the regulation behind it. The only guide that covers every customer type in one place.",
        "url": "https://www.fincrimeradar.org/kyc-onboarding-dilemma.html",
    },
    {
        "title": "Fraud Red Flags: Reading the Patterns, Not Just the Rules",
        "hook": "Four live cases from Scenario Lab's Fraud Detection module, worked through properly. Account takeover, APP scams, transaction laundering, and structuring, decision scenarios with full reasoning and a knowledge check.",
        "url": "https://www.fincrimeradar.org/fraud-red-flags-guide.html",
    },
    {
        "title": "The False Positive Playbook: Disposing Alerts Without Getting It Wrong",
        "hook": "The guide the vendors don't write. Three decision scenarios on disposing sanctions, PEP, and adverse media alerts correctly, name matching, DOB mismatches, transliteration, and adverse media false hits, with full reasoning and a knowledge check.",
        "url": "https://www.fincrimeradar.org/false-positive-playbook.html",
    },
    {
        "title": "The UBO Investigation Handbook: Finding the Real Owner",
        "hook": "Checking a register isn't investigating an ownership structure, it's the starting point. Three decision scenarios on nominee directors, unreliable PSC register data, the 2022 CJEU ruling on EU register access, and trust beneficiaries, with full reasoning and a knowledge check.",
        "url": "https://www.fincrimeradar.org/ubo-investigation-handbook.html",
    },
    {
        "title": "The Source of Wealth Investigation Handbook: Telling a Plausible Story from Verified Evidence",
        "hook": "A well-told explanation is not the same as a verified one. Three decision scenarios on verifying source of wealth and source of funds, a two-step gift case study, and a knowledge check, for compliance analysts who need to distinguish a plausible story from actual verification.",
        "url": "https://www.fincrimeradar.org/source-of-wealth-investigation-handbook.html",
    },
    {
        "title": "The Adverse Media Intelligence Guide: Reading the Story Behind the Headline",
        "hook": "Confirming identity is the easy half. Three decision scenarios on weighing legal stage, source credibility, recency, and role in adverse media hits, with a source credibility hierarchy and a knowledge check.",
        "url": "https://www.fincrimeradar.org/adverse-media-intelligence-guide.html",
    },
    {
        "title": "Vessel Sanctions Fundamentals: What the Shadow Fleet Actually Is",
        "hook": "Designated vs specified, the six routes a party can be caught by a vessel sanction, and why IMO number beats name-based screening. Part 1 of 2, with two decision scenarios and a real SMYRTOS case study.",
        "url": "https://www.fincrimeradar.org/shadow-fleet-guide-part1.html",
    },
    {
        "title": "The Shadow Fleet Investigation Playbook",
        "hook": "Why insurance, not AIS tracking, is where fraud actually hides. The Seaguard P&amp;I fake-insurer case, the IG Clubs verification step, and two more decision scenarios. Part 2 of 2.",
        "url": "https://www.fincrimeradar.org/shadow-fleet-guide-part2.html",
    },
    {
        "title": "Inside the Scam Compound Money Laundering Machine",
        "hook": "A scam compound generates victims. A separate machine launders the proceeds. Nine payment-chain nodes from receiving account to stablecoin off-ramp, two worked scenarios on network reconstruction, and a verified FinCEN Section 311 case study.",
        "url": "https://www.fincrimeradar.org/scam-compound-money-laundering-guide.html",
    },
    {
        "title": "Annex 1 Firms and the AML Blind Spot",
        "hook": "What \"FCA registered\" establishes, what it does not, and the entity, activity, ownership, SPV and financing checks an investigator should perform next.",
        "url": "https://www.fincrimeradar.org/annex-1-firms-aml-blind-spot-guide.html",
    },
    {
        "title": "The Fraud Investigation Playbook: Building a File That Survives Review",
        "hook": "Most investigation guides teach corporate fraud. This one teaches the queue. Three decision scenarios on testing theories, the POCA disclosure boundary, and file documentation, with the full reporting chain from detection to DAML.",
        "url": "https://www.fincrimeradar.org/fraud-investigation-playbook.html",
    },
    {
        "title": "Tuning Screening Algorithms: Why Fuzzy Matching Isn't Magic",
        "hook": "The default threshold, the algorithms actually in production, and the real case where two different people scored 0.98 on the same sanctions list. An interactive pipeline visualizer walks four name pairs through retrieval and scoring.",
        "url": "https://www.fincrimeradar.org/screening-algorithm-tuning-guide.html",
    },
    {
        "title": "Sanctions Compliance: OFAC, OFSI and Beyond",
        "hook": "Sanctions explained in plain English, a real OFAC case that generates false positives against ordinary people, flip flashcards, and a live comparison against a globally known designation.",
        "url": "https://www.fincrimeradar.org/sanctions-compliance-guide.html",
    },
    {
        "title": "The Certifications Dilemma: AML &amp; Compliance Credentials Compared",
        "hook": "Twelve credentials, cost, eligibility, and recertification burden checked directly against each issuing body's own site, not ranked against each other, matched to the career stage each one actually fits.",
        "url": "https://www.fincrimeradar.org/certifications-dilemma.html",
    },
    {
        "title": "What Actually Happens After You Suspect a Deepfake at Onboarding",
        "hook": "The detection tool gives you a confidence score, not a verdict. Four worked scenarios on the judgement that comes next, a real 47-account ABN AMRO case, and a knowledge check.",
        "url": "https://www.fincrimeradar.org/deepfake-onboarding-guide.html",
    },
    {
        "title": "The AI Agent Transaction Nobody Can Screen",
        "hook": "No settled UK answer exists for who is liable when an AI agent makes the purchase. Four composite scenarios grounded in real FCA, CMA, and IMF sources, not a technology explainer.",
        "url": "https://www.fincrimeradar.org/ai-agent-transaction-guide.html",
    },
    {
        "title": "Gambling's White-Label Blind Spot",
        "hook": "A licensed operator supplies the licence, a separate brand supplies the front end. UKGC's own case material and enforcement pattern show exactly where accountability gets lost.",
        "url": "https://www.fincrimeradar.org/gambling-white-label-blind-spot-guide.html",
    },
    {
        "title": "Where Does the Money Actually Stop? Investigating Financial Crime Risk in Private Markets",
        "hook": "Given a real fund ownership chain, LP to fund to GP to SPV to portfolio company, where does the CDD obligation actually start, and where does it genuinely have to stop. Two worked scenarios on upstream beneficial ownership and PEP exposure in a fund-of-funds structure, plus ten Risk/Signal/Response investigation patterns.",
        "url": "https://www.fincrimeradar.org/private-markets-financial-crime-investigation-handbook.html",
    },
    {
        "title": "Classification Asymmetry: The Fraud vs AML Divide",
        "hook": "A fraudster steals from one bank. The money lands at another as an unremarkable deposit. One granted patent argues that fraud-style behavioural scoring can produce money laundering false positives while missing laundering that doesn't deviate from normal behaviour.",
        "url": "https://www.fincrimeradar.org/classification-asymmetry-guide.html",
    },
    {
        "title": "The MLRO Handbook",
        "hook": "Who can become SMF16/17, the FCA's real approval bar, and where personal MLRO liability has actually been tested.",
        "url": "https://www.fincrimeradar.org/mlro-handbook-part1.html",
    },
    {
        "title": "The Crypto Guide",
        "hook": "What actually changes under the incoming FSMA cryptoasset regime, and what to do before the October 2027 deadline.",
        "url": "https://www.fincrimeradar.org/crypto-guide-part1.html",
    },
    {
        "title": "UK AML Compliance",
        "hook": "UK AML law, MLR 2017, POCA 2002, the Terrorism Act 2000 and SAMLA 2018, plus the FCA framework, updated for 2026's FG25/3 and HM Treasury reforms.",
        "url": "https://www.fincrimeradar.org/aml-guide-part1.html",
    },
    {
        "title": "SAR Complete Guide",
        "hook": "The UK SAR legal regime: POCA 2002 offences, who must file, the MLRO role, DAML, tipping off, and the UKFIU.",
        "url": "https://www.fincrimeradar.org/sar-guide-part1.html",
    },
    {
        "title": "PEP Screening Handbook",
        "hook": "PEP identification: FATF definitions, domestic vs foreign PEPs, Relatives and Close Associates, PEP duration, and the FCA's July 2025 FG25/3 guidance.",
        "url": "https://www.fincrimeradar.org/pep-guide-part1.html",
    },
    {
        "title": "FATF 40 Recommendations",
        "hook": "Seven critical FATF Recommendations decoded, with visual memory cards, real-world scenarios, and the compliance decisions they drive daily.",
        "url": "https://www.fincrimeradar.org/fatf-guide-part1.html",
    },
]


def get_this_weeks_guides(guide_library, count=3, reference_date=None):
    """
    Deterministically rotate through guide_library based on ISO week number.
    Same week always yields the same selection (reproducible, auditable).
    Advances every week, never repeats until the full library has cycled.
    """
    if not guide_library:
        raise ValueError("guide_library is empty, cannot select guides for digest")
    if count > len(guide_library):
        raise ValueError(
            f"count ({count}) exceeds guide_library size ({len(guide_library)}), "
            "cannot select without repeating a guide in the same digest"
        )

    reference_date = reference_date or date.today()
    iso_year, iso_week, _ = reference_date.isocalendar()

    # Stable seed independent of dict/list ordering quirks
    start_index = (iso_year * 52 + iso_week) % len(guide_library)

    selected = []
    for offset in range(count):
        idx = (start_index + offset) % len(guide_library)
        selected.append(guide_library[idx])

    return selected


def recent_delta_files():
    """Every delta/YYYY-MM-DD.html file dated within the trailing window."""
    cutoff = date.today() - timedelta(days=WINDOW_DAYS)
    found = []
    for path in sorted(glob.glob(f"{DELTA_DIR}/*.html")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})\.html$", path)
        if not m:
            continue
        try:
            file_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if file_date >= cutoff:
            found.append((file_date, path))
    return sorted(found)


def extract_counts(page_html):
    """Pulls the four category counts straight out of a rendered delta
    page's own headings, rather than re-parsing raw data a second time.
    Returns a dict, missing categories default to zero."""
    counts = {"ADDED": 0, "DELISTED": 0, "AMENDED": 0, "RENAMED": 0}
    patterns = {
        "ADDED": r"New designations \((\d+)\)",
        "DELISTED": r"Delistings \((\d+)\)",
        "AMENDED": r"Amendments \((\d+)\)",
        "RENAMED": r"Identifier changes \((\d+)\)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, page_html)
        if m:
            counts[key] = int(m.group(1))
    return counts


def extract_meta(page_html):
    """Reads the tracker's own trigger and override metadata comment.
    Older pages written before this comment existed simply won't match,
    defaulting to unknown trigger and no override, which is the correct
    safe assumption for historical pages rather than a false flag."""
    m = META_PATTERN.search(page_html)
    if not m:
        return {"trigger": "unknown", "override_active": False, "threshold": None}
    trigger, override_flag, threshold = m.groups()
    return {
        "trigger": trigger,
        "override_active": override_flag == "yes",
        "threshold": int(threshold),
    }


def build_digest_html(entries=None):
    # entries (delta-page data) is no longer required to build a digest.
    # The sanctions snapshot section that consumed it was removed 2026-07-20
    # because OpenSanctions cuts off the unauthenticated bulk endpoint the
    # delta tracker depends on, generate_delta_pages.py, on 2026-08-01, and
    # the workflow that produces delta pages is disabled ahead of that date.
    # Gating the whole digest on recent_delta_files() being non-empty (the
    # old behaviour) would silently stop the guides/Scenario Lab content
    # from sending too, once no delta page exists within the trailing
    # window, not just the sanctions section, which defeats the point of
    # decoupling this email from sanctions data. main() no longer applies
    # that gate. The parameter is kept, unused for now, in case a future
    # migration of generate_delta_pages.py to the authenticated OpenSanctions
    # API brings delta content back and this section is reinstated.
    period_end_date = date.today()
    period_start_date = period_end_date - timedelta(days=WINDOW_DAYS)
    period_start = period_start_date.strftime("%d %b")
    period_end = period_end_date.strftime("%d %b %Y")

    guides_html = ""
    for g in get_this_weeks_guides(GUIDE_LIBRARY):
        guides_html += f"""
        <div style="border:1px solid #E3E8E3;border-radius:8px;padding:16px 18px;margin-top:12px;">
          <div style="font-size:15px;font-weight:700;color:#0B7A57;">{g['title']}</div>
          <p style="font-size:13px;line-height:1.6;color:#3D4E5C;margin:6px 0 10px 0;">{g['hook']}</p>
          <a href="{g['url']}" style="color:#0B7A57;text-decoration:none;font-weight:600;font-size:13px;">Read the guide &rarr;</a>
        </div>"""

    # FinCrime Week: manually curated, primary-sourced weekly briefing, see
    # data/fincrime-week/. None (no eligible published issue, same
    # Monday-rollover selection the homepage and archive page use) renders
    # nothing at all, no header, no placeholder, matching the safe-empty
    # behaviour the old NEWS_ROUNDUP_LIBRARY had while it was still empty.
    fincrime_week_issue = load_latest_published_fincrime_week()
    fincrime_week_html = ""
    if fincrime_week_issue and fincrime_week_issue.get("items"):
        items = fincrime_week_issue["items"]
        lead = items[0]
        supporting = items[1:5]

        stories_html = f"""
        <div style="border:1px solid #E3E8E3;border-radius:8px;padding:16px 18px;margin-top:12px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:0.6px;text-transform:uppercase;color:#66757F;">{esc(lead['signal'])} &middot; {esc(lead['category'].replace('_', ' '))}</div>
          <div style="font-size:15px;font-weight:700;color:#0B7A57;margin-top:4px;">{esc(lead['headline'])}</div>
          <p style="font-size:13px;line-height:1.6;color:#3D4E5C;margin:6px 0 4px 0;">{esc(lead['why_it_matters'])}</p>
          <div style="font-size:11px;color:#66757F;">{esc(lead['source_name'])} &middot; {esc(lead['jurisdiction'])}</div>
        </div>"""
        for item in supporting:
            stories_html += f"""
        <div style="border:1px solid #E3E8E3;border-radius:8px;padding:12px 16px;margin-top:10px;">
          <div style="font-size:13px;font-weight:600;color:#0C1B2A;">{esc(item['headline'])}</div>
          <div style="font-size:11px;color:#66757F;margin-top:2px;">{esc(item['signal'])} &middot; {esc(item['source_name'])}</div>
        </div>"""

        fincrime_week_html = f"""
      <div style="margin-top:28px;">
        <div style="color:#0B7A57;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">FinCrime Week</div>
        {stories_html}
        <a href="{SITE}/fincrime-week.html" style="color:#0B7A57;text-decoration:none;font-weight:600;font-size:13px;display:inline-block;margin-top:10px;">Read the full briefing &rarr;</a>
      </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#F4F6F3;padding:24px;color:#0C1B2A;">
  <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;">
    <div style="background:#071912;padding:28px 32px;">
      <div style="color:#5DCAA5;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Weekly compliance digest</div>
      <div style="color:#ffffff;font-size:22px;font-weight:700;margin-top:8px;">{period_start} to {period_end}</div>
    </div>
    <div style="padding:28px 32px;">
      <div>
        <div style="color:#0B7A57;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">This week's guides</div>
        {guides_html}
      </div>
      {fincrime_week_html}
      <div style="margin-top:28px;">
        <div style="color:#0B7A57;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">This week's tools</div>
        <div style="border:1px solid #E3E8E3;border-radius:8px;padding:16px 18px;margin-top:12px;">
          <div style="font-size:15px;font-weight:700;color:#0B7A57;">Scenario Lab</div>
          <p style="font-size:13px;line-height:1.6;color:#3D4E5C;margin:6px 0 10px 0;">Build the ownership tree, screen every entity, then make the call, approve, reject, or escalate. Two modules live now, KYC/KYB and Fraud Detection, 11 cases combined. Free, no signup.</p>
          <a href="{SITE}/scenario-lab.html" style="color:#0B7A57;text-decoration:none;font-weight:600;font-size:13px;">Try Scenario Lab &rarr;</a>
        </div>
        <div style="border:1px solid #E3E8E3;border-radius:8px;padding:16px 18px;margin-top:12px;">
          <div style="font-size:15px;font-weight:700;color:#0B7A57;">Sanctions &amp; PEP Screening</div>
          <p style="font-size:13px;line-height:1.6;color:#3D4E5C;margin:6px 0 10px 0;">Free real-time sanctions screening against OFAC, UN, EU, OFSI and 40+ global lists. PEP screening and adverse media search. No sign-up required.</p>
          <a href="https://www.fincrimeradar.org/screen.html" style="color:#0B7A57;text-decoration:none;font-weight:600;font-size:13px;">Try the screening tool &rarr;</a>
        </div>
      </div>
      <p style="font-size:12px;color:#66757F;margin-top:28px;">
        You are receiving this because you subscribed at fincrimeradar.org.
        Decision support, not legal advice.
      </p>
    </div>
  </div>
</body>
</html>"""


def send_campaign(subject, html_content):
    api_key = os.environ.get("BREVO_API_KEY")
    list_id = os.environ.get("BREVO_LIST_ID")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name = os.environ.get("BREVO_SENDER_NAME", "FinCrimeRadar")

    missing = [name for name, val in [
        ("BREVO_API_KEY", api_key),
        ("BREVO_LIST_ID", list_id),
        ("BREVO_SENDER_EMAIL", sender_email),
    ] if not val]
    if missing:
        sys.exit(f"ABORT: missing required environment variables: {', '.join(missing)}")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    create_payload = {
        "name": f"Weekly digest {date.today().isoformat()}",
        "subject": subject,
        "sender": {"name": sender_name, "email": sender_email},
        "type": "classic",
        "htmlContent": html_content,
        "recipients": {"listIds": [int(list_id)]},
    }

    r = requests.post(
        "https://api.brevo.com/v3/emailCampaigns",
        headers=headers,
        json=create_payload,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        sys.exit(f"ABORT: Brevo campaign creation failed, status {r.status_code}: {r.text[:300]}")

    campaign_id = r.json().get("id")
    if not campaign_id:
        sys.exit(f"ABORT: Brevo did not return a campaign id: {r.text[:300]}")

    send_r = requests.post(
        f"https://api.brevo.com/v3/emailCampaigns/{campaign_id}/sendNow",
        headers=headers,
        timeout=30,
    )
    if send_r.status_code not in (200, 201, 204):
        sys.exit(
            f"ABORT: campaign {campaign_id} created but send failed, status "
            f"{send_r.status_code}: {send_r.text[:300]}"
        )

    print(f"Sent weekly digest, campaign id {campaign_id}.")


def main():
    # No longer gated on recent_delta_files() being non-empty. The digest's
    # content (guides, Scenario Lab) doesn't depend on delta pages since the
    # 2026-07-20 removal of the sanctions snapshot section, see the comment
    # in build_digest_html(). Sends every run regardless of sanctions
    # activity.
    digest_html = build_digest_html()

    period_end = date.today().strftime("%d %b %Y")
    subject = f"FinCrimeRadar weekly digest, week ending {period_end}"

    send_campaign(subject, digest_html)


if __name__ == "__main__":
    main()
