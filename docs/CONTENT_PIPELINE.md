# Content pipeline: manifest, advertising eligibility, sitemap, validation

All tooling is dependency free Node, pinned to 24.x in `package.json` (`engines`) and in CI, so a platform default upgrade cannot move the project to an untested Node version. Nothing here deploys, edits the AdSense account or requests a review.

## Manifest (`data/content_manifest.json`)

The authoritative inventory of every public HTML page. `schema_version` is 2 and `origin` must be `https://fincrimeradar.org`. Every `url` must equal the URL derived from `source_file` and every `canonical` must sit on the declared origin. A missing, unreadable or malformed manifest produces `manifest.unreadable` or `manifest.shape` in the report rather than an exception. Files that are public but not content (the Search Console verification token) are listed under `excluded_files` with a reason. `partials/`, `docs/`, `drafts/` and similar folders are not public pages.

| Field | Meaning | Source |
| --- | --- | --- |
| `url`, `source_file` | Path and file. `index.html` is `/`. | derived |
| `page_type` | `article`, `tool`, `navigation`, `legal`, `archive`, `incomplete` | decision |
| `status` | `published`, `beta`, `incomplete`, `archived` | decision |
| `title`, `description`, `canonical` | As written in the page head | read from page |
| `indexable` | Whether the page may be indexed. `false` requires a `noindex` robots meta. | decision |
| `sitemap` | Whether the page is listed in `sitemap.xml` | decision |
| `adsense_eligible` | Explicit advertising decision, `false` by default | decision |
| `author` | Author only when visibly printed on the page, else `null` | read from page |
| `date_published`, `date_modified` | From the page's Article structured data, else `null` | read from page |
| `authoritative_source_count`, `secondary_source_count`, `internal_reference_count` | Sources entries classified by link host. Government, regulator, legislature and intergovernmental hosts are authoritative, other external links are secondary, FinCrimeRadar links are internal references and never authoritative. An unlinked entry counts as secondary. | read from page |
| `unverified_claim_count` | Material claims a human has found unresolved. `null` means not assessed. | decision |
| `structured_data_type` | Primary schema.org type, else `null` | read from page |
| `review_state` | `null`, `draft`, `ready_for_review`, `in_review`, `approved` | decision |
| `editorial_review_status`, `regulatory_review_status` | `null`, `not_started`, `in_review`, `changes_required`, `approved` | decision |
| `date_reviewed` | Date of a substantive factual and regulatory review. Distinct from `date_modified`, which is schema or page modification and is never evidence of review. It may not be in the future. | decision |
| `review_evidence`, `approved_by` | Where the review is recorded, and the named human reviewer | decision |
| `regulatory_blockers` | Open findings from review, each a sentence. Shown in the report, and any entry blocks eligibility. | decision |

Facts read from the page are refreshed by `npm run manifest:refresh`. Decisions are never overwritten by a refresh. New pages get conservative defaults: not in the sitemap, not advertising eligible.

## Advertising eligibility

Advertising eligibility is human controlled. Automation may reject eligibility but never grants it: every new record starts at `adsense_eligible: false` with empty review fields, a refresh never fills them, and nothing in the repository sets them.

`adsense_eligible: true` requires `editorial_review_status` and `regulatory_review_status` both `approved`, an `approved_by` naming a real person (at least two name parts, not a tool or placeholder), a valid `date_reviewed` not before publication, non empty `review_evidence`, `unverified_claim_count` assessed and equal to 0, no `regulatory_blockers`, and every rule below. Legal, navigation, archive, beta and incomplete pages are never eligible.

Articles need: published status, indexable, in the sitemap, exactly one H1, one canonical, unique title and description, a visible body byline naming a person that agrees with a `Person` author in the Article structured data (an Organization author, metadata alone, or a mismatch fails), a valid publication date, a valid modified date not earlier than publication, Article structured data with headline, author and datePublished, a Sources section with at least three authoritative external sources, no Beta label, no broken internal links.

Tools need: published status, indexable, one H1, one canonical, headings covering purpose, instructions, methodology or data, limitations and privacy, appropriate structured data, no Beta label, no broken internal links.

These are mechanical checks. They cannot judge whether sources are relevant, whether a date is a genuine review date, or whether the content is original and useful. Word count is never a criterion. A human still owns those judgements.

Any substantive modification invalidates an older review. An eligible page whose `date_modified` is later than its `date_reviewed` fails validation until a human reviews it again and records a new `date_reviewed`.

Advertising artefacts are detected broadly: the `adsbygoogle.js` script, an `ins` element with the `adsbygoogle` class, inline `adsbygoogle` push calls, `data-ad-client` attributes carrying the publisher id, and any unexpected publisher id. An ineligible page containing any of them fails validation.

`npm run ads:strip-ineligible` removes only the known external `adsbygoogle.js` tag from ineligible pages. Inline units are reported as `MANUAL REMOVAL NEEDED` (exit code 1) and must be removed by hand. The Funding Choices consent snippet is a separate script and is not touched.

## Sitemap

`npm run sitemap:generate` writes `sitemap.xml` from the manifest. It includes only `sitemap: true` records and refuses anything that is not published and indexable, has a missing source file, or duplicates a URL. The sitemap is location only: `lastmod`, `changefreq`, `priority` and comments are not emitted. `lastmod` must represent a genuine significant update of the page, and the existing `date_modified` values have not all received human verification for that purpose. `lastmod` may be introduced later only through an explicit human verified significant modification field. It must never be inferred from schema metadata, `date_modified` or file timestamps. Output is sorted and byte deterministic. `npm run sitemap:check` fails if the file is stale.

## Indexing controls

The validator fails on: a sitemap page carrying `noindex`, a non indexable page in the sitemap, a non indexable page without `noindex`, missing or multiple canonicals, a canonical that is not the page's own URL, and duplicate titles, descriptions or canonicals among indexable pages. `reports/url_inventory.csv` lists every URL with its indexing and advertising state for reconciliation against a Search Console export.

## Commands

| Command | Purpose |
| --- | --- |
| `npm test` | Unit tests against temporary fixture sites |
| `npm run validate:content` | Full validation, writes `reports/content_quality_report.json` and `reports/url_inventory.csv`. Add `-- --strict` to fail on warnings. |
| `npm run sitemap:generate` / `sitemap:check` | Write or verify the sitemap |
| `npm run manifest:refresh` | Re-read page facts into the manifest |
| `npm run ads:strip-ineligible` | Remove the AdSense script from ineligible pages |
| `npm run verify:production` | Read only live check of `ads.txt` and `sitemap.xml` |
| `npm run ci` | tests, sitemap check, validation |

Errors are integrity failures (contradictions, broken structure). Warnings are editorial gaps such as a missing modification date or sources section. Gaps are reported, never repaired by the tooling.

## Continuous integration

`.github/workflows/content-quality.yml` runs tests, the sitemap check and full validation on pushes to `main` and on pull requests. Any error fails the job. This is a quality check, not an inherent deployment gate: it blocks a merge or deployment only if it is configured as a required status check in branch protection and in the Vercel deployment settings, which this repository does not configure. An eligible page fails the build for any warning, missing approval, missing review date or evidence, unresolved claims or blockers, author mismatch, or too few authoritative sources. Warnings on ineligible pages stay in the report without failing the build. It has read only permissions and contains no deployment step. It does not call production.

## Production verification

`npm run verify:production` follows redirects manually and checks `ads.txt` for status 200, final URL, a `text/plain` content type, no HTML body, no more than three redirects and the exact record. It also compares the live sitemap URL set with the repository copy, which fails until a deployment lands. A correct repository file is not evidence that production is correct, so run this after each deploy. It is not part of CI.

## Workflows

Ready for editorial review: set the record's `review_state` to `ready_for_review` once the page has a Sources section, a visible author and real dates. Set `editorial_review_status` and `regulatory_review_status` to `in_review` while a human works through it. Run `npm run validate:content` and read the warnings for that page.

Advertising eligible: only after a human has completed the review. Record the approvals, `date_reviewed`, `review_evidence` and `approved_by`, set `unverified_claim_count` to 0 and clear `regulatory_blockers`, then set `adsense_eligible` to `true`, add the AdSense script to the page, run `npm run validate:content`. If the validator reports `ads.eligibility`, the page is not ready. Never enable advertising on a new page to make a count look better.

## Why editorial facts are never fabricated

Authors, publication dates, modification dates, source lists and review states are claims about the work. A modification date that nobody earned, a source that was not consulted or a review that did not happen is a factual error and a trust failure, and it is exactly what a quality review looks for. The tooling reads these facts from the page and reports `null` or a warning when they are absent. Fix the page, not the manifest.

## Deployment surface

`npm run validate:deploy` (`scripts/validate_deploy_surface.mjs`, part of `npm run ci`) applies the real `.vercelignore` rules to the working tree and fails if the calculated upload inventory contains anything outside the permitted public surface: public HTML, CSS, browser JavaScript, referenced images, `api/subscribe.js`, `ads.txt`, `robots.txt`, `sitemap.xml`, `vercel.json`, `package.json` and exactly one data file, `scenario-lab/data/cases.json`. It reports every retained data file with the deployed files that reference it.

- The root `data/` directory is excluded as a whole by one anchored rule (`/data/`). It is anchored on purpose: a bare `data/` would also match `scenario-lab/data/`. That covers the weekly FinCrime Week JSON, the content manifest, snapshots and inventories, so a new file there needs no `.vercelignore` edit. They are generator and tooling input, not runtime files.
- The permitted data surface is exactly `scenario-lab/data/cases.json`, which sits outside root `data/`. Any other JSON, CSV or compressed data file that would be uploaded fails validation, even if a deployed file contains its name as text.
- A data file needs a concrete runtime reference: a `fetch`, `import`, `Request`, `URL`, `Worker`, XHR `open` or `sendBeacon` call (directly, through a string constant passed to such a call or to a function that makes one), a tag attribute such as `href` or `src`, or a CSS `url()`. A reference inside an HTML, JavaScript or CSS comment, in visible prose, or in an unused string constant does not count.
- Internal Markdown, the verification ledger, the content manifest, reports, drafts, caches, workflows and source scripts must never be uploaded.
- Public page text must not tell readers to see an excluded operational file. Comments, scripts and styles are ignored by this check.
- Vercel uses .vercelignore to exclude matching paths from deployments, including deployments sourced from Git. The resulting deployment surface must still be verified on a Vercel preview before production.
