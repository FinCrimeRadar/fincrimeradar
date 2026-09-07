#!/usr/bin/env python3
"""
Tests for the FinCrime Week module: fincrime_week_lib, generate_fincrime_week,
and the send_weekly_digest integration. stdlib unittest, no new dependency.

Fixture weekly-issue JSON files live under a temp directory per test, never
under data/fincrime-week/ itself, so the real (empty, .gitkeep-only)
directory is never touched by the test suite.
"""

import copy
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fincrime_week_lib as lib
import generate_fincrime_week as gen


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


if __name__ == "__main__":
    unittest.main()
