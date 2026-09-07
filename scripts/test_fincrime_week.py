#!/usr/bin/env python3
"""
Tests for the FinCrime Week module: fincrime_week_lib, generate_fincrime_week,
and the send_weekly_digest integration. stdlib unittest, no new dependency.

Fixture weekly-issue JSON files live under a temp directory per test, never
under data/fincrime-week/ itself, so the real (empty, .gitkeep-only)
directory is never touched by the test suite.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fincrime_week_lib as lib
import generate_fincrime_week as gen
import send_weekly_digest as digest


def write_issue(dir_path, filename, **overrides):
    issue = {
        "week": "2026-W37",
        "period_start": "2026-09-07",
        "period_end": "2026-09-13",
        "published_at": "2026-09-14",
        "author": "Test Author",
        "items": [],
    }
    issue.update(overrides)
    with open(os.path.join(dir_path, filename), "w", encoding="utf-8") as f:
        json.dump(issue, f)
    return issue


class EscTests(unittest.TestCase):
    def test_escapes_markup_characters(self):
        self.assertEqual(
            lib.esc('<b>"quoted" & \'single\'</b>'),
            "&lt;b&gt;&quot;quoted&quot; &amp; &#x27;single&#x27;&lt;/b&gt;",
        )

    def test_none_becomes_empty_string(self):
        self.assertEqual(lib.esc(None), "")

    def test_plain_string_passes_through(self):
        self.assertEqual(lib.esc("FCA"), "FCA")


class LoadLatestPublishedFincrimeWeekTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_none_when_directory_empty(self):
        result = lib.load_latest_published_fincrime_week(
            reference_date=date(2026, 9, 8), data_dir=self.tmpdir
        )
        self.assertIsNone(result)

    def test_monday_rollover_selects_prior_weeks_issue(self):
        # Editor publishes Friday 2026-09-04 for week 2026-W36 (Aug 31-Sep 6).
        # Digest sends Monday 2026-09-07, the start of ISO week 2026-W37,
        # with no 2026-W37.json yet. The function must not derive the
        # filename from the reference date's own ISO week, it must fall
        # back to the latest already-published issue.
        write_issue(self.tmpdir, "2026-W36.json", week="2026-W36", published_at="2026-09-04")
        result = lib.load_latest_published_fincrime_week(
            reference_date=date(2026, 9, 7), data_dir=self.tmpdir
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["week"], "2026-W36")

    def test_future_dated_published_at_excluded(self):
        write_issue(self.tmpdir, "2026-W38.json", week="2026-W38", published_at="2026-09-18")
        result = lib.load_latest_published_fincrime_week(
            reference_date=date(2026, 9, 7), data_dir=self.tmpdir
        )
        self.assertIsNone(result)

    def test_selects_latest_among_several_eligible_files(self):
        write_issue(self.tmpdir, "2026-W35.json", week="2026-W35", published_at="2026-08-31")
        write_issue(self.tmpdir, "2026-W36.json", week="2026-W36", published_at="2026-09-04")
        write_issue(self.tmpdir, "2026-W37.json", week="2026-W37", published_at="2026-09-11")
        result = lib.load_latest_published_fincrime_week(
            reference_date=date(2026, 9, 8), data_dir=self.tmpdir
        )
        self.assertEqual(result["week"], "2026-W36")

    def test_defaults_to_today_when_reference_date_omitted(self):
        write_issue(
            self.tmpdir,
            "past.json",
            week="2020-W01",
            published_at="2020-01-01",
        )
        result = lib.load_latest_published_fincrime_week(data_dir=self.tmpdir)
        self.assertIsNotNone(result)
        self.assertEqual(result["week"], "2020-W01")

    def test_malformed_json_file_is_skipped_not_fatal(self):
        with open(os.path.join(self.tmpdir, "broken.json"), "w", encoding="utf-8") as f:
            f.write("{not valid json")
        write_issue(self.tmpdir, "2026-W36.json", week="2026-W36", published_at="2026-09-04")
        result = lib.load_latest_published_fincrime_week(
            reference_date=date(2026, 9, 7), data_dir=self.tmpdir
        )
        self.assertEqual(result["week"], "2026-W36")


# ---------------- generate_fincrime_week.py: validation ----------------

def make_item(**overrides):
    item = {
        "id": "item-1",
        "headline": "FCA fines firm X £2m for AML failings",
        "source_name": "FCA",
        "source_url": "https://www.fca.org.uk/news/press-releases/example",
        "published_date": "2026-09-10",
        "jurisdiction": "UK",
        "category": "AML_CTF",
        "signal": "ENFORCEMENT",
        "what_happened": "The FCA fined firm X for AML control failings identified during a supervisory review.",
        "why_it_matters": "Signals heightened enforcement focus on transaction monitoring gaps.",
        "radar_implication": "Review your own transaction monitoring coverage against these findings.",
        "primary_source": True,
        "reviewed": True,
    }
    item.update(overrides)
    return item


def make_issue(items=None, **overrides):
    issue = {
        "week": "2026-W37",
        "period_start": "2026-09-07",
        "period_end": "2026-09-13",
        "published_at": "2026-09-13",
        "author": "Pratik Zanke",
        "items": [make_item()] if items is None else items,
    }
    issue.update(overrides)
    return issue


def write_issue_file(dir_path, filename, issue):
    path = os.path.join(dir_path, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(issue, f)
    return path


class ValidateFileTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_file_passes(self):
        path = write_issue_file(self.tmpdir, "2026-W37.json", make_issue())
        data = gen.validate_file(path)
        self.assertEqual(data["week"], "2026-W37")

    def test_malformed_json_raises(self):
        path = os.path.join(self.tmpdir, "2026-W37.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        with self.assertRaises(ValueError):
            gen.validate_file(path)

    def test_duplicate_id_within_file(self):
        items = [make_item(id="dup"), make_item(id="dup", source_url="https://example.org/other")]
        path = write_issue_file(self.tmpdir, "2026-W37.json", make_issue(items=items))
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "id")

    def test_duplicate_source_url_within_file(self):
        items = [make_item(id="a"), make_item(id="b")]
        path = write_issue_file(self.tmpdir, "2026-W37.json", make_issue(items=items))
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "source_url")

    def test_missing_required_field(self):
        item = make_item()
        del item["headline"]
        path = write_issue_file(self.tmpdir, "2026-W37.json", make_issue(items=[item]))
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "headline")

    def test_invalid_signal_value(self):
        path = write_issue_file(
            self.tmpdir, "2026-W37.json", make_issue(items=[make_item(signal="URGENT")])
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "signal")

    def test_invalid_category_value(self):
        path = write_issue_file(
            self.tmpdir, "2026-W37.json", make_issue(items=[make_item(category="TAX")])
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "category")

    def test_reviewed_false_rejected(self):
        path = write_issue_file(
            self.tmpdir, "2026-W37.json", make_issue(items=[make_item(reviewed=False)])
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "reviewed")

    def test_filename_week_mismatch(self):
        path = write_issue_file(self.tmpdir, "2026-W38.json", make_issue(week="2026-W37"))
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "week")

    def test_period_start_outside_declared_iso_week(self):
        # 2026-W37 runs 2026-09-07 to 2026-09-13; 2026-09-14 is week 38.
        path = write_issue_file(
            self.tmpdir,
            "2026-W37.json",
            make_issue(period_start="2026-09-14", period_end="2026-09-20", published_at="2026-09-20"),
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "period_start")

    def test_period_end_not_exactly_six_days_after_period_start(self):
        path = write_issue_file(
            self.tmpdir,
            "2026-W37.json",
            make_issue(period_end="2026-09-14", published_at="2026-09-14"),
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "period_end")

    def test_published_at_earlier_than_period_end(self):
        path = write_issue_file(
            self.tmpdir, "2026-W37.json", make_issue(published_at="2026-09-12")
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "published_at")

    def test_non_https_source_url_rejected(self):
        path = write_issue_file(
            self.tmpdir,
            "2026-W37.json",
            make_issue(items=[make_item(source_url="http://www.fca.org.uk/news/example")]),
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "source_url")

    def test_hostname_less_source_url_rejected(self):
        path = write_issue_file(
            self.tmpdir, "2026-W37.json", make_issue(items=[make_item(source_url="https:///path")])
        )
        with self.assertRaises(gen.ValidationError) as ctx:
            gen.validate_file(path)
        self.assertEqual(ctx.exception.field, "source_url")

    def test_published_date_outside_period_is_allowed(self):
        # published_date is explicitly an editorial judgement call, not
        # required to fall inside the weekly period.
        path = write_issue_file(
            self.tmpdir,
            "2026-W37.json",
            make_issue(items=[make_item(published_date="2026-01-01")]),
        )
        data = gen.validate_file(path)
        self.assertEqual(data["items"][0]["published_date"], "2026-01-01")


# ---------------- generate_fincrime_week.py: rendering ----------------

class RenderingTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_homepage_fragment_escapes_markup(self):
        item = make_item(headline='<script>alert(1)</script>')
        write_issue_file(self.tmpdir, "2026-W37.json", make_issue(items=[item]))
        fragment = gen.render_homepage_fragment(
            reference_date=date(2026, 9, 14), data_dir=self.tmpdir
        )
        self.assertNotIn("<script>alert(1)</script>", fragment)
        self.assertIn("&lt;script&gt;", fragment)

    def test_homepage_fragment_empty_when_no_eligible_issue(self):
        fragment = gen.render_homepage_fragment(
            reference_date=date(2026, 9, 1), data_dir=self.tmpdir
        )
        self.assertEqual(fragment, "")

    def test_homepage_marker_replacement(self):
        html = f"<html><body>before{gen.MARKER_START}old content{gen.MARKER_END}after</body></html>"
        result = gen.inject_homepage_section(html, "NEW FRAGMENT")
        self.assertIn("NEW FRAGMENT", result)
        self.assertNotIn("old content", result)
        self.assertIn("before", result)
        self.assertIn("after", result)

    def test_archive_page_reverse_chronological_ordering(self):
        older = make_issue(week="2026-W35", period_start="2026-08-24", period_end="2026-08-30", published_at="2026-08-30")
        newer = make_issue(week="2026-W37", published_at="2026-09-13")
        write_issue_file(self.tmpdir, "2026-W35.json", older)
        write_issue_file(self.tmpdir, "2026-W37.json", newer)

        issues = gen.load_all_valid_issues(data_dir=self.tmpdir)
        issues_desc = sorted(issues, key=lambda pair: pair[1]["published_at"], reverse=True)
        page = gen.render_archive_page(issues_desc)

        newer_pos = page.index('id="2026-W37"')
        older_pos = page.index('id="2026-W35"')
        self.assertLess(newer_pos, older_pos)

    def test_archive_page_escapes_item_fields(self):
        item = make_item(what_happened='Regulator said "<b>bad</b>" & worse')
        write_issue_file(self.tmpdir, "2026-W37.json", make_issue(items=[item]))
        issues = gen.load_all_valid_issues(data_dir=self.tmpdir)
        page = gen.render_archive_page(issues)
        self.assertNotIn("<b>bad</b>", page)
        self.assertIn("&lt;b&gt;bad&lt;/b&gt;", page)


# ---------------- send_weekly_digest.py integration ----------------

class DigestFincrimeWeekTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._real_data_dir = lib.DATA_DIR
        lib.DATA_DIR = Path(self.tmpdir)

    def tearDown(self):
        lib.DATA_DIR = self._real_data_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_section_when_no_eligible_issue(self):
        html = digest.build_digest_html()
        self.assertNotIn("FinCrime Week", html)
        self.assertNotIn("Read the full briefing", html)

    def test_section_rendered_when_eligible_issue_exists(self):
        item = make_item(headline="Regulator fines firm for AML gaps")
        period_end = date.today()
        period_start = period_end - timedelta(days=6)
        iso_year, iso_week, _ = period_start.isocalendar()
        week_str = f"{iso_year}-W{iso_week:02d}"
        issue = make_issue(
            items=[item],
            week=week_str,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            published_at=period_end.isoformat(),
        )
        write_issue_file(self.tmpdir, f"{week_str}.json", issue)

        html = digest.build_digest_html()
        self.assertIn("FinCrime Week", html)
        self.assertIn("Regulator fines firm for AML gaps", html)
        self.assertIn(f"{digest.SITE}/fincrime-week.html", html)

    def test_section_escapes_headline(self):
        item = make_item(headline="<script>alert(1)</script>")
        period_end = date.today()
        period_start = period_end - timedelta(days=6)
        iso_year, iso_week, _ = period_start.isocalendar()
        week_str = f"{iso_year}-W{iso_week:02d}"
        issue = make_issue(
            items=[item],
            week=week_str,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            published_at=period_end.isoformat(),
        )
        write_issue_file(self.tmpdir, f"{week_str}.json", issue)

        html = digest.build_digest_html()
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)


# ---------------- Archive navigator ----------------

class NavigatorTests(unittest.TestCase):
    def setUp(self):
        # Three issues spanning a month boundary (Aug/Sep) and, separately,
        # a pair spanning a year boundary (Dec 2026 / Jan 2027), built as
        # plain dicts: these render functions consume already-validated
        # data, they don't re-run validate_file, so the fixture dates only
        # need to be internally consistent for grouping/ordering purposes.
        self.w36 = make_issue(week="2026-W36", period_start="2026-08-31", period_end="2026-09-06", published_at="2026-09-06")
        self.w37 = make_issue(week="2026-W37", period_start="2026-09-07", period_end="2026-09-13", published_at="2026-09-13")
        self.w52 = make_issue(week="2026-W52", period_start="2026-12-21", period_end="2026-12-27", published_at="2026-12-27")
        self.w01 = make_issue(week="2027-W01", period_start="2027-01-04", period_end="2027-01-10", published_at="2027-01-10")

    def desc(self, *issues):
        # (path, data) pairs in reverse-chronological order, as main()
        # would build them; path is never used by these render functions.
        return [(None, issue) for issue in issues]

    def test_reverse_chronological_week_navigation(self):
        issues_desc = self.desc(self.w37, self.w36)
        nav_html = gen.render_navigator(issues_desc)
        self.assertLess(nav_html.index("2026-W37"), nav_html.index("2026-W36"))

    def test_month_grouping(self):
        # w36 (31 Aug-06 Sep) and w37 (07-13 Sep) both end in September,
        # so they must share one group even though w36 starts in August.
        groups = gen.build_navigator_groups(self.desc(self.w37, self.w36))
        self.assertEqual(len(groups), 1)
        label, items = groups[0]
        self.assertEqual(label, "September 2026")
        self.assertEqual([i["week"] for i in items], ["2026-W37", "2026-W36"])

    def test_week_spanning_month_boundary_groups_by_period_end(self):
        # The exact case that motivated this correction: a week starting
        # in August and ending in September must be grouped under
        # September, not August.
        groups = gen.build_navigator_groups(self.desc(self.w36))
        self.assertEqual(groups, [("September 2026", [self.w36])])

    def test_week_spanning_year_boundary_groups_by_period_end(self):
        crossing = make_issue(
            week="2026-W53", period_start="2026-12-28", period_end="2027-01-03", published_at="2027-01-03"
        )
        groups = gen.build_navigator_groups(self.desc(crossing))
        self.assertEqual(groups, [("January 2027", [crossing])])

    def test_year_grouping(self):
        groups = gen.build_navigator_groups(self.desc(self.w01, self.w52))
        self.assertEqual([label for label, _ in groups], ["January 2027", "December 2026"])
        self.assertEqual(groups[0][1][0]["week"], "2027-W01")
        self.assertEqual(groups[1][1][0]["week"], "2026-W52")

    def test_group_order_is_reverse_chronological(self):
        groups = gen.build_navigator_groups(self.desc(self.w01, self.w52, self.w37, self.w36))
        self.assertEqual(
            [label for label, _ in groups],
            ["January 2027", "December 2026", "September 2026"],
        )
        # September 2026 group holds both w37 and w36, newest first.
        self.assertEqual([d["week"] for d in groups[2][1]], ["2026-W37", "2026-W36"])

    def test_latest_issue_selected_by_default(self):
        issues_desc = self.desc(self.w37, self.w36)
        page = gen.render_archive_page(issues_desc)
        # The default week in ARCHIVE_SCRIPT is issues[0].id, the first
        # .fcw-issue rendered, so the latest issue's article must come
        # first in document order.
        self.assertLess(
            page.index('id="2026-W37"'),
            page.index('id="2026-W36"'),
        )
        self.assertIn("var defaultWeek = issues[0].id;", page)

    def test_direct_hash_targeting(self):
        issues_desc = self.desc(self.w37, self.w36)
        page = gen.render_archive_page(issues_desc)
        self.assertIn('id="2026-W37"', page)
        self.assertIn('id="2026-W36"', page)
        self.assertIn('href="#2026-W37"', page)
        self.assertIn("location.hash", page)
        self.assertIn("currentHashWeek", page)

    def test_previous_and_next_issue_links(self):
        issues_desc = self.desc(self.w37, self.w36)  # newest first: index 0 = W37, index 1 = W36

        newest_pager = gen.render_issue_pager(issues_desc, 0)
        self.assertIn("fcw-pager-prev", newest_pager)
        self.assertIn("2026-W36", newest_pager)
        self.assertNotIn("fcw-pager-next", newest_pager)

        oldest_pager = gen.render_issue_pager(issues_desc, 1)
        self.assertIn("fcw-pager-next", oldest_pager)
        self.assertIn("2026-W37", oldest_pager)
        self.assertNotIn("fcw-pager-prev", oldest_pager)

    def test_previous_and_next_with_middle_issue(self):
        issues_desc = self.desc(self.w37, self.w36, make_issue(week="2026-W35", period_start="2026-08-24", period_end="2026-08-30", published_at="2026-08-30"))
        middle_pager = gen.render_issue_pager(issues_desc, 1)
        self.assertIn("fcw-pager-prev", middle_pager)
        self.assertIn("fcw-pager-next", middle_pager)
        self.assertIn("2026-W35", middle_pager)
        self.assertIn("2026-W37", middle_pager)

    def test_mobile_selector_generation(self):
        issues_desc = self.desc(self.w37, self.w36)
        select_html = gen.render_mobile_select(issues_desc)
        self.assertEqual(select_html.count("<option"), 2)
        self.assertIn('value="2026-W37"', select_html)
        self.assertIn('value="2026-W36"', select_html)
        self.assertLess(select_html.index("2026-W37"), select_html.index("2026-W36"))
        self.assertIn('id="fcwMobileSelect"', select_html)
        self.assertIn("aria-label=", select_html)

    def test_empty_archive_behaviour(self):
        page = gen.render_archive_page([])
        self.assertIn("No FinCrime Week issues published yet", page)
        self.assertNotIn('class="fcw-nav-link"', page)
        self.assertNotIn("fcwMobileSelect", page)
        self.assertEqual(gen.build_navigator_groups([]), [])
        self.assertEqual(gen.render_navigator([]), "")
        self.assertEqual(gen.render_mobile_select([]), "")

    def test_latest_issue_not_hidden(self):
        latest_article = gen.render_issue_article(self.w37, is_latest=True)
        # No bare "hidden" token anywhere in the latest issue's own tag.
        opening_tag = latest_article.split(">", 1)[0]
        self.assertNotIn("hidden", opening_tag)

    def test_historical_issues_initially_hidden(self):
        older_article = gen.render_issue_article(self.w36, is_latest=False)
        opening_tag = older_article.split(">", 1)[0]
        self.assertIn("hidden", opening_tag)

    def test_only_latest_issue_lacks_hidden_in_full_page(self):
        issues_desc = self.desc(self.w37, self.w36, self.w52)
        page = gen.render_archive_page(issues_desc)
        self.assertIn(f'id="{self.w37["week"]}" data-week="{self.w37["week"]}">', page)
        self.assertIn(f'id="{self.w36["week"]}" data-week="{self.w36["week"]}" hidden>', page)
        self.assertIn(f'id="{self.w52["week"]}" data-week="{self.w52["week"]}" hidden>', page)

    def test_noscript_fallback_present(self):
        page = gen.render_archive_page(self.desc(self.w37, self.w36))
        self.assertIn("<noscript>", page)
        self.assertIn(".fcw-issue[hidden]", page)
        self.assertIn("display: block !important;", page)

    def test_switching_logic_maintains_one_visible_issue(self):
        # ARCHIVE_SCRIPT's core invariant: every issue's hidden state is
        # recomputed as a strict equality check against exactly one target
        # week, which guarantees exactly one issue is ever unhidden at a
        # time. This can't be executed here without a browser/JS engine
        # (no new test dependency), so it's verified structurally and
        # exercised for real in the manual browser smoke test.
        self.assertIn("el.hidden = el.id !== week;", gen.ARCHIVE_SCRIPT)

    def test_invalid_hash_falls_back_to_latest_issue(self):
        self.assertIn("var defaultWeek = issues[0].id;", gen.ARCHIVE_SCRIPT)
        self.assertIn("if (!isKnownWeek(week)) { week = defaultWeek; }", gen.ARCHIVE_SCRIPT)


if __name__ == "__main__":
    unittest.main()
