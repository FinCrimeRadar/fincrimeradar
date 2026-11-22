import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join, basename, dirname } from 'node:path';
import { validateSite, checkAdsTxt, loadManifest, isIsoDate, isNamedReviewer, brokenLinks, parseSitemap, canonicalFor, sharedAssetFiles } from '../scripts/lib/site.mjs';
import { classifyHref } from '../scripts/lib/classify.mjs';
import { buildManifest } from '../scripts/build_manifest.mjs';
import { buildSitemap } from '../scripts/generate_sitemap.mjs';
import { stripIneligibleAds } from '../scripts/strip_ineligible_ads.mjs';
import { verifyAdsTxt, fetchChain } from '../scripts/verify_production.mjs';
import { ADS_TXT_RECORD, ORIGIN, adsenseInfo } from '../scripts/lib/page.mjs';
import { makeSite, articleHtml, codes, failedRules, cleanupFixtures, FIXTURE_PREFIX } from './helpers.mjs';

after(cleanupFixtures);

test('1. valid manifest and site pass with ads retained', () => {
  const s = makeSite();
  const r = validateSite(s.root);
  assert.deepEqual(r.errors, []);
  assert.equal(r.summary.adsense_eligible, 2);
  assert.ok(loadManifest(s.root).pages.every((p) => p.review_state === null));
});

test('2. invalid manifest fields are rejected', () => {
  const s = makeSite();
  s.edit((p) => { p[1].page_type = 'blog'; p[1].indexable = 'yes'; delete p[1].author; p[1].extra = 1; });
  const c = codes(validateSite(s.root));
  for (const k of ['manifest.page_type', 'manifest.boolean', 'manifest.field_missing', 'manifest.field_unknown']) assert.ok(c.includes(k), k);
});

test('3. duplicate canonical URLs are reported', () => {
  const s = makeSite({ a: {}, b: { canonical: `${ORIGIN}/a.html` } });
  const r = validateSite(s.root);
  assert.ok(codes(r).includes('canonical.mismatch'));
  assert.ok(codes(r).includes('canonical.duplicate'));
});

test('3b. missing and multiple canonical tags are reported', () => {
  const s = makeSite({ a: { canonical: null }, b: {} });
  s.write('b.html', s.read('b.html').replace('</head>', '<link rel="canonical" href="https://fincrimeradar.org/b.html"></head>'));
  s.edit((p) => { p.find((x) => x.url === '/b.html').canonical = `${ORIGIN}/b.html`; });
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('canonical.missing'));
  assert.ok(c.includes('canonical.multiple'));
});

test('4. duplicate titles and descriptions are reported', () => {
  const s = makeSite({ a: { title: 'Same', description: 'Same d' }, b: { title: 'Same', description: 'Same d' } });
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('title.duplicate'));
  assert.ok(c.includes('description.duplicate'));
});

test('5. missing H1 is an error on an indexable page', () => {
  const s = makeSite({ a: { h1: false }, b: {} });
  assert.ok(codes(validateSite(s.root)).includes('h1.missing'));
});

test('6. invalid structured data is reported', () => {
  const s = makeSite({ a: { ld: '{ not json' }, b: {} });
  assert.ok(codes(validateSite(s.root)).includes('structured_data.invalid_json'));
});

test('6b. structured data type must match the manifest', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').structured_data_type = 'WebApplication'; });
  assert.ok(codes(validateSite(s.root)).includes('structured_data.type_mismatch'));
});

test('7. incomplete and beta pages cannot enter the sitemap', () => {
  const s = makeSite();
  s.edit((p) => { Object.assign(p.find((x) => x.url === '/a.html'), { status: 'incomplete', page_type: 'incomplete' }); });
  assert.throws(() => buildSitemap(s.root), /sitemap=true requires status published/);
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('sitemap.unpublished'));
  assert.ok(c.includes('status.incomplete_indexable'));
});

test('7b. non indexable pages need a noindex directive and stay out of the sitemap', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').indexable = false; });
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('robots.missing_noindex'));
  assert.ok(c.includes('sitemap.nonindexable'));
});

test('7c. a sitemap page carrying noindex is reported', () => {
  const s = makeSite({ a: { robots: 'noindex, follow' }, b: {} });
  s.edit((p) => { Object.assign(p.find((x) => x.url === '/a.html'), { indexable: true, sitemap: true }); });
  assert.ok(codes(validateSite(s.root)).includes('robots.noindex_on_indexable'));
});

test('8. ineligible pages containing AdSense are reported, and stripping fixes them', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').adsense_eligible = false; });
  assert.ok(codes(validateSite(s.root)).includes('ads.ineligible_has_script'));
  assert.deepEqual(stripIneligibleAds(s.root), { changed: ['a.html'], manual: [] });
  assert.ok(!codes(validateSite(s.root)).includes('ads.ineligible_has_script'));
  assert.ok(s.read('b.html').includes('adsbygoogle.js'), 'eligible page keeps its script');
});

test('8b. an eligible flag on a page that fails the rules is reported', () => {
  const s = makeSite({ a: { sources: 2 }, b: {} });
  s.edit((p) => { p.find((x) => x.url === '/a.html').adsense_eligible = true; });
  assert.ok(codes(validateSite(s.root)).includes('ads.eligibility'));
});

test('8c. automation never grants eligibility or approval', () => {
  const s = makeSite({ a: {}, b: {} }, { approve: false });
  const m = loadManifest(s.root).pages;
  for (const r of m) {
    assert.equal(r.adsense_eligible, false, r.url);
    assert.equal(r.editorial_review_status, null);
    assert.equal(r.regulatory_review_status, null);
    assert.equal(r.approved_by, null);
    assert.equal(r.date_reviewed, null);
    assert.equal(r.review_evidence, null);
  }
  // pages still carry the script, so the validator rejects the unapproved state
  assert.ok(codes(validateSite(s.root)).includes('ads.ineligible_has_script'));
  // a refresh preserves human decisions and never fills approvals
  s.edit((p) => { p[1].approved_by = 'Jane Hartley'; });
  assert.equal(buildManifest(s.root).pages.find((x) => x.url === p1(s)).approved_by, 'Jane Hartley');
  assert.equal(buildManifest(s.root).pages.find((x) => x.url === '/b.html').approved_by, null);
});
const p1 = (s) => loadManifest(s.root).pages[1].url;

test('9. incorrect ads.txt content is reported', () => {
  assert.deepEqual(checkAdsTxt(ADS_TXT_RECORD + '\r\n'), []);
  assert.ok(checkAdsTxt('google.com, pub-9999999999999999, DIRECT, f08c47fec0942fa0\n').length);
  assert.ok(checkAdsTxt('<html></html>').length);
  const s = makeSite();
  s.write('ads.txt', 'google.com, pub-1, DIRECT\n');
  assert.ok(codes(validateSite(s.root)).includes('ads_txt.invalid'));
});

test('9b. the repository ads.txt is exactly the publisher record', () => {
  const txt = readFileSync(join(import.meta.dirname, '..', 'ads.txt'), 'utf8');
  assert.deepEqual(checkAdsTxt(txt), []);
  assert.equal(txt.trim(), ADS_TXT_RECORD);
});

test('10. missing source files are reported and rejected by the sitemap generator', async () => {
  const s = makeSite();
  const { unlinkSync } = await import('node:fs');
  unlinkSync(join(s.root, 'a.html'));
  assert.ok(codes(validateSite(s.root)).includes('source.missing'));
  assert.throws(() => buildSitemap(s.root), /source file a\.html is missing/);
});

test('10b. a public page missing from the manifest is reported', () => {
  const s = makeSite();
  s.write('orphan.html', articleHtml('orphan'));
  assert.ok(codes(validateSite(s.root)).includes('manifest.uncovered_file'));
});

test('11. invalid date ordering and formats are reported', () => {
  const s = makeSite();
  s.edit((p) => { Object.assign(p.find((x) => x.url === '/a.html'), { date_published: '2026-05-01', date_modified: '2026-04-01' }); p.find((x) => x.url === '/b.html').date_modified = '2026-02-30'; });
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('date.order'));
  assert.ok(c.includes('date.invalid'));
  assert.equal(isIsoDate('2026-02-30'), false);
  assert.equal(isIsoDate('2026-02-28'), true);
});

test('12. broken internal links are reported', () => {
  const s = makeSite({ a: { links: ['/b.html', '/missing.html', 'nope.html', 'https://fincrimeradar.org/gone.html', 'https://example.com/x', '#top'] }, b: {} });
  const r = validateSite(s.root);
  const e = r.errors.find((x) => x.code === 'links.broken');
  assert.ok(e);
  assert.match(e.message, /missing\.html/);
  assert.match(e.message, /gone\.html/);
  assert.doesNotMatch(e.message, /example\.com|\/b\.html/);
});

test('13. sitemap generation is stable, location only and never uses the build date', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').date_modified = null; });
  const one = buildSitemap(s.root), two = buildSitemap(s.root);
  assert.equal(one, two);
  assert.ok(!one.includes(String(new Date().getUTCFullYear()) + '-' + String(new Date().getUTCMonth() + 1).padStart(2, '0') + '-' + String(new Date().getUTCDate()).padStart(2, '0')));
  assert.ok(!one.includes('lastmod'), 'a genuine manifest date_modified must not become lastmod either');
  assert.ok(!one.includes('2026-02-01'), 'no page date appears in the sitemap');
});

test('13b. duplicate sitemap URLs are rejected', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/b.html').canonical = `${ORIGIN}/a.html`; });
  assert.throws(() => buildSitemap(s.root), /duplicate sitemap URL/);
});

test('13c. sitemap and manifest disagreement is reported', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').sitemap = false; });
  assert.ok(codes(validateSite(s.root)).includes('sitemap.not_in_manifest'));
});

// ---- production verification (fake fetch, no network) ----
const res = (status, body, headers = {}) => ({ status, headers: new Map(Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v])), text: async () => body });
const fake = (routes) => async (url) => { const r = routes[url]; if (!r) throw new Error('unreachable'); return r; };
const URL_ = `${ORIGIN}/ads.txt`;

test('14. production verification passes on a correct response', async () => {
  const r = await verifyAdsTxt(ORIGIN, fake({ [URL_]: res(200, ADS_TXT_RECORD + '\n', { 'content-type': 'text/plain; charset=utf-8' }) }));
  assert.equal(r.ok, true);
});

test('14b. production verification fails clearly on 404, HTML, wrong type, wrong record', async () => {
  const bad = [
    [res(404, 'Not found', { 'content-type': 'text/plain' }), /status 404/],
    [res(200, '<html>x</html>', { 'content-type': 'text/html' }), /HTML/],
    [res(200, ADS_TXT_RECORD, { 'content-type': 'text/html' }), /text\/plain/],
    [res(200, 'google.com, pub-1, DIRECT, f08c47fec0942fa0', { 'content-type': 'text/plain' }), /publisher record/],
  ];
  for (const [response, re] of bad) {
    const r = await verifyAdsTxt(ORIGIN, fake({ [URL_]: response }));
    assert.equal(r.ok, false);
    assert.match(r.failures.join(' '), re);
  }
});

test('14c. redirects, loops and network failures fail verification', async () => {
  const redirect = (to) => res(301, '', { location: to });
  const moved = await verifyAdsTxt(ORIGIN, fake({ [URL_]: redirect('https://other.example/ads.txt'), 'https://other.example/ads.txt': res(200, ADS_TXT_RECORD, { 'content-type': 'text/plain' }) }));
  assert.equal(moved.ok, false);
  assert.match(moved.failures.join(' '), /final URL/);
  const loop = await fetchChain(URL_, fake({ [URL_]: redirect('https://x.example/'), 'https://x.example/': redirect(URL_) }));
  assert.match(loop.error, /loop/);
  const long = await fetchChain('https://h0.example/', async (u) => redirect(`https://h${Number(u.match(/h(\d+)/)[1]) + 1}.example/`));
  assert.match(long.error, /more than/);
  const down = await verifyAdsTxt(ORIGIN, fake({}));
  assert.equal(down.ok, false);
  assert.match(down.failures[0], /request failed/);
});

// ---- human controlled eligibility ----
test('15. each missing approval element rejects eligibility', () => {
  const cases = [
    ['editorial review not approved', (r) => { r.editorial_review_status = 'in_review'; }, 'editorial_review'],
    ['regulatory review not approved', (r) => { r.regulatory_review_status = 'changes_required'; }, 'regulatory_review'],
    ['no approver', (r) => { r.approved_by = null; }, 'approved_by'],
    ['automation named as approver', (r) => { r.approved_by = 'Claude Code'; }, 'approved_by'],
    ['single token name', (r) => { r.approved_by = 'Jane'; }, 'approved_by'],
    ['no review date', (r) => { r.date_reviewed = null; }, 'date_reviewed'],
    ['review before publication', (r) => { r.date_reviewed = '2025-12-31'; }, 'date_reviewed'],
    ['no evidence', (r) => { r.review_evidence = '  '; }, 'review_evidence'],
    ['claims not assessed', (r) => { r.unverified_claim_count = null; }, 'unverified_claims'],
    ['unresolved claims', (r) => { r.unverified_claim_count = 2; }, 'unverified_claims'],
    ['regulatory blockers', (r) => { r.regulatory_blockers = ['Needs review']; }, 'regulatory_blockers'],
  ];
  for (const [name, mutate, rule] of cases) {
    const s = makeSite();
    assert.deepEqual(validateSite(s.root).errors, [], 'baseline is clean');
    s.edit((p) => mutate(p.find((x) => x.url === '/a.html')));
    const r = validateSite(s.root);
    assert.ok(codes(r).includes('ads.eligibility'), name);
    assert.ok(failedRules(r, '/a.html').includes(rule), `${name}: ${failedRules(r, '/a.html')}`);
  }
  assert.equal(isNamedReviewer('Jane Hartley'), true);
  assert.equal(isNamedReviewer('GitHub Actions'), false);
});

test('16. date_modified is not accepted as a review date', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').date_reviewed = null; });
  const r = validateSite(s.root);
  assert.ok(failedRules(r, '/a.html').includes('date_reviewed'));
  assert.equal(s.rec('/a.html').date_modified, '2026-02-01');
});

// ---- authorship ----
test('17. authorship needs a visible body author that matches structured data', () => {
  const run = (o) => { const s = makeSite({ a: o, b: {} }); return failedRules(validateSite(s.root), '/a.html'); };
  assert.deepEqual(run({}).filter((x) => x === 'author'), [], 'agreeing Person author passes');
  assert.ok(run({ byline: null }).includes('author'), 'metadata alone (meta + schema) is not enough');
  assert.ok(run({ byline: 'By Sam Other' }).includes('author'), 'body and schema must agree');
  assert.ok(run({ ldAuthor: { '@type': 'Organization', name: 'FinCrimeRadar' }, byline: 'By FinCrimeRadar Team' }).includes('author'), 'organisation is not a named person');
  assert.ok(run({ ldAuthor: { '@type': 'Organization', name: 'Pat Author' } }).includes('author'), 'organisation type fails even with a matching name');
  assert.ok(run({ byline: 'Reviewed by the compliance team and published after a long internal process of review work' }).includes('author'), 'prose is not a byline');
});

// ---- sources ----
test('18. internal references do not satisfy the authoritative source threshold', () => {
  const s = makeSite({ a: { sourceBase: '/index.html#', sources: 4 }, b: { sourceBase: 'https://blog.example.com/', sources: 4 } });
  const r = validateSite(s.root);
  assert.ok(failedRules(r, '/a.html').includes('sources'));
  assert.ok(failedRules(r, '/b.html').includes('sources'), 'secondary sources do not count either');
  const a = s.rec('/a.html');
  assert.deepEqual([a.authoritative_source_count, a.secondary_source_count, a.internal_reference_count], [0, 0, 4]);
  assert.equal(classifyHref('https://www.legislation.gov.uk/ukpga/2002/29'), 'authoritative');
  assert.equal(classifyHref('https://fincrimeradar.org/about.html'), 'internal');
  assert.equal(classifyHref('https://medium.com/x'), 'secondary');
});

// ---- CI gates on eligible pages ----
test('19. an eligible page with a warning fails validation', () => {
  const s = makeSite();
  s.edit((p) => { p.find((x) => x.url === '/a.html').regulatory_blockers = ['Open finding']; });
  const r = validateSite(s.root);
  assert.ok(codes(r).includes('ads.eligible_has_warning'));
  assert.deepEqual(r.review_blockers, [{ url: '/a.html', blockers: ['Open finding'] }]);
  assert.ok(r.warnings.some((w) => w.code === 'regulatory.blocker'), 'warning stays visible in the report');
});

test('19b. ineligible pages keep warnings without failing validation', () => {
  const s = makeSite({ a: { ads: false }, b: {} });
  s.edit((p) => { Object.assign(p.find((x) => x.url === '/a.html'), { adsense_eligible: false, regulatory_blockers: ['Open finding'] }); });
  const r = validateSite(s.root);
  assert.deepEqual(r.errors, []);
  assert.ok(r.warnings.some((w) => w.url === '/a.html'));
});

test('20. the repository manifest carries no automated approvals and no eligible pages', () => {
  const m = loadManifest(join(import.meta.dirname, '..'));
  for (const r of m.pages) {
    if (r.adsense_eligible) assert.equal(isNamedReviewer(r.approved_by), true, r.url);
  }
  const rejected = ['/tm-guide.html', '/a7a5-sanctions-evasion-guide.html', '/freezing-a-stablecoin-guide.html', '/annex-1-firms-aml-blind-spot-guide.html', '/why-stablecoins-compliance-priority-guide.html'];
  for (const u of rejected) {
    const r = m.pages.find((x) => x.url === u);
    assert.equal(r.adsense_eligible, false, u);
    assert.ok(r.regulatory_blockers.length > 0, u);
    assert.equal(r.approved_by, null, u);
  }
});

// ---- fixture hygiene ----
test('21. fixture directories are removed by cleanupFixtures', () => {
  cleanupFixtures(); // drop earlier tests' fixtures so the baseline is only pre-existing directories
  const before = readdirSync(tmpdir()).filter((n) => n.startsWith(FIXTURE_PREFIX)).length;
  const s = makeSite();
  assert.ok(existsSync(s.root));
  assert.equal(readdirSync(tmpdir()).filter((n) => n.startsWith(FIXTURE_PREFIX)).length, before + 1);
  cleanupFixtures();
  assert.ok(!existsSync(s.root));
  assert.equal(readdirSync(tmpdir()).filter((n) => n.startsWith(FIXTURE_PREFIX)).length, before);
});

// ---- manifest read failures never throw ----
const validateNoThrow = (root, opts) => { let r; assert.doesNotThrow(() => { r = validateSite(root, opts); }); return r; };

test('22. a missing manifest returns manifest.unreadable', () => {
  const s = makeSite();
  rmSync(s.manifestPath);
  const r = validateNoThrow(s.root);
  assert.equal(r.ok, false);
  assert.deepEqual(codes(r), ['manifest.unreadable']);
  assert.equal(r.summary.pages, 0);
  assert.deepEqual(validateNoThrow(s.root), r, 'deterministic');
});

test('22b. malformed manifest JSON returns manifest.unreadable', () => {
  const s = makeSite();
  writeFileSync(s.manifestPath, '{ "pages": [ ');
  assert.deepEqual(codes(validateNoThrow(s.root)), ['manifest.unreadable']);
});

test('22c. pages that is not an array, or a non object manifest, returns manifest.shape', () => {
  const s = makeSite();
  writeFileSync(s.manifestPath, JSON.stringify({ schema_version: 2, origin: ORIGIN, pages: { a: 1 } }));
  assert.deepEqual(codes(validateNoThrow(s.root)), ['manifest.shape']);
  for (const body of ['null', '[]', '"x"']) {
    writeFileSync(s.manifestPath, body);
    assert.deepEqual(codes(validateNoThrow(s.root)), ['manifest.shape'], body);
  }
});

// ---- schema 2 ----
test('23. schema version, origin, url drift and canonical origin are validated', () => {
  const s = makeSite();
  assert.equal(loadManifest(s.root).schema_version, 2);
  s.edit((p, m) => { m.schema_version = 1; });
  assert.ok(codes(validateSite(s.root)).includes('manifest.schema_version'));
  s.edit((p, m) => { m.schema_version = 2; m.origin = 'https://example.com'; });
  assert.ok(codes(validateSite(s.root)).includes('manifest.origin'));
  s.edit((p, m) => { m.origin = ORIGIN; p.find((x) => x.url === '/a.html').url = '/elsewhere.html'; });
  assert.ok(codes(validateSite(s.root)).includes('manifest.url_drift'));
  s.edit((p) => { p.find((x) => x.source_file === 'a.html').url = '/a.html'; p.find((x) => x.url === '/a.html').canonical = 'https://evil.example/a.html'; });
  assert.ok(codes(validateSite(s.root)).includes('canonical.origin'));
});

test('23b. the repository manifest is schema 2 on the production origin', () => {
  const m = loadManifest(join(import.meta.dirname, '..'));
  assert.equal(m.schema_version, 2);
  assert.equal(m.origin, 'https://fincrimeradar.org');
});

// ---- path containment ----
test('24. a sibling directory sharing the repository name prefix is outside the repository', () => {
  const s = makeSite();
  const sibling = s.root + '-evil';
  mkdirSync(sibling, { recursive: true });
  writeFileSync(join(sibling, 'secret.html'), '<html></html>');
  try {
    const link = `/../${basename(sibling)}/secret.html`;
    assert.deepEqual(brokenLinks(s.root, [link], 'a.html'), [link], 'rejected even though the target exists');
    assert.deepEqual(brokenLinks(s.root, ['../' + basename(sibling) + '/secret.html'], 'a.html').length, 1);
    assert.deepEqual(brokenLinks(s.root, ['/b.html'], 'a.html'), [], 'inside links still resolve');
    assert.deepEqual(brokenLinks(s.root, ['/../../etc/passwd'], 'a.html').length, 1);
  } finally { rmSync(sibling, { recursive: true, force: true }); }
});

// ---- protocol relative URLs ----
test('25. protocol relative URLs are resolved as external URLs', () => {
  assert.equal(classifyHref('//www.fca.org.uk/publication/x.pdf'), 'authoritative');
  assert.equal(classifyHref('//medium.com/x'), 'secondary');
  assert.equal(classifyHref('//fincrimeradar.org/about.html'), 'internal');
  assert.equal(classifyHref('//www.fincrimeradar.org/about.html'), 'internal');
  assert.equal(classifyHref('/about.html'), 'internal');
  assert.equal(classifyHref('about.html'), 'internal');
});

// ---- review dates (injected clock) ----
test('26. a future review date is rejected using an injected date', () => {
  const s = makeSite();
  const ok = validateSite(s.root, { today: '2026-03-01' });
  assert.deepEqual(ok.errors, []);
  const early = validateSite(s.root, { today: '2026-02-10' });
  assert.ok(codes(early).includes('date.future'));
  assert.ok(codes(early).includes('ads.eligibility'));
  assert.ok(failedRules(early, '/a.html').includes('date_reviewed'));
  assert.deepEqual(validateSite(s.root, { today: '2026-02-15' }).errors, [], 'review dated today is allowed');
});

test('26b. a page modified after its review is not eligible', () => {
  const s = makeSite({ a: { modified: '2026-03-01' }, b: {} });
  const r = validateSite(s.root, { today: '2026-06-01' });
  assert.ok(failedRules(r, '/a.html').includes('date_reviewed'));
  assert.match(r.pages.find((p) => p.url === '/a.html').eligibility_failures.find((f) => f.rule === 'date_reviewed').message, /after the 2026-02-15 review/);
  assert.deepEqual(failedRules(r, '/b.html'), []);
  // a new review after the modification restores eligibility
  s.edit((p) => { p.find((x) => x.url === '/a.html').date_reviewed = '2026-03-05'; });
  assert.deepEqual(validateSite(s.root, { today: '2026-06-01' }).errors, []);
});

// ---- every advertising artefact ----
const ARTEFACTS = {
  script: ['script', null],
  ins: ['ins', '<ins class="adsbygoogle" style="display:block"></ins>'],
  push: ['push', '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'],
  ad_client: ['ad_client', '<div data-ad-client="ca-pub-1158691611711023"></div>'],
};
for (const [name, [code, extra]] of Object.entries(ARTEFACTS)) {
  test(`27. an ineligible page with a ${name} advertising artefact fails validation`, () => {
    const s = makeSite({ a: name === 'script' ? {} : { ads: false, extra }, b: { ads: false } });
    s.edit((p) => { p.forEach((x) => { x.adsense_eligible = false; }); });
    const r = validateSite(s.root);
    assert.ok(codes(r).includes(`ads.ineligible_has_${code}`), codes(r).join());
    assert.equal(r.pages.find((p) => p.url === '/a.html').ad_artefacts.includes(code), true);
    assert.equal(r.pages.find((p) => p.url === '/b.html').ad_artefacts.length, 0);
    assert.equal(r.summary.with_ad_artefacts, 1);
  });
}

test('27b. an unexpected publisher identifier fails validation', () => {
  const s = makeSite({ a: { ads: false, extra: '<meta name="x" content="ca-pub-9999999999999999">' }, b: {} });
  assert.ok(codes(validateSite(s.root)).includes('publisher.inconsistent'));
});

test('27c. stripping removes only the external script and reports inline units for manual removal', () => {
  const s = makeSite({ a: { extra: '<ins class="adsbygoogle"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script>' }, b: {} });
  s.edit((p) => { p.forEach((x) => { x.adsense_eligible = false; }); });
  const before = s.read('a.html');
  const res = stripIneligibleAds(s.root);
  assert.deepEqual(res.changed.sort(), ['a.html', 'b.html']);
  assert.deepEqual(res.manual, [{ source_file: 'a.html', artefacts: ['ins', 'push'] }]);
  const after = s.read('a.html');
  assert.ok(!after.includes('adsbygoogle.js'));
  assert.ok(after.includes('class="adsbygoogle"') && after.includes('.push({})'), 'inline units untouched');
  assert.equal(before.replace(/^.*adsbygoogle\.js.*\n/m, ''), after, 'nothing else changed');
});

// ---- stablecoin series contradiction ----
test('28. every stablecoin page that still calls Guide 1 forthcoming carries a blocker', () => {
  const root = join(import.meta.dirname, '..');
  const m = loadManifest(root);
  const affected = ['/a7a5-sanctions-evasion-guide.html', '/freezing-a-stablecoin-guide.html', '/stablecoin-financial-crime-guide.html', '/systemic-stablecoins-guide.html', '/why-stablecoins-compliance-priority-guide.html'];
  for (const u of affected) {
    const r = m.pages.find((x) => x.url === u);
    assert.ok(r.regulatory_blockers.some((b) => /Guide 1/.test(b) && /forthcoming/.test(b)), u);
    assert.equal(r.adsense_eligible, false);
  }
  const report = validateSite(root);
  const named = report.review_blockers.filter((b) => b.blockers.some((x) => /Guide 1/.test(x))).map((b) => b.url).sort();
  assert.deepEqual(named, [...affected].sort());
});

test('29. the real repository has zero eligible pages and zero advertising artefacts', () => {
  const r = validateSite(join(import.meta.dirname, '..'));
  assert.equal(r.summary.adsense_eligible, 0);
  assert.equal(r.summary.with_ad_artefacts, 0);
  assert.deepEqual(r.errors, []);
});

const REPO = join(import.meta.dirname, '..');
const eligibleLocs = (manifest) => manifest.pages.filter((r) => r.sitemap === true && r.status === 'published' && r.indexable === true)
  .map((r) => r.canonical ?? canonicalFor(r.source_file)).sort();

test('30. the sitemap contains exactly the eligible indexable URLs', () => {
  const s = makeSite({ a: {}, b: {}, c: { robots: 'noindex, follow' }, d: {} });
  s.edit((p) => { p.find((x) => x.url === '/d.html').sitemap = false; });
  const manifest = loadManifest(s.root);
  const locs = parseSitemap(buildSitemap(s.root)).map((u) => u.loc).sort();
  assert.deepEqual(locs, eligibleLocs(manifest));
  assert.ok(locs.includes(`${ORIGIN}/a.html`) && locs.includes(`${ORIGIN}/b.html`));
  assert.ok(!locs.includes(`${ORIGIN}/c.html`), 'noindex page excluded');
  assert.ok(!locs.includes(`${ORIGIN}/d.html`), 'page not flagged for the sitemap excluded');
});

test('31. the sitemap emits no lastmod, changefreq, priority or comments', () => {
  const s = makeSite({ a: {}, b: {} });
  assert.ok(loadManifest(s.root).pages.every((r) => r.date_modified), 'fixture pages carry a date_modified that must not leak');
  const xml = buildSitemap(s.root);
  for (const tag of ['lastmod', 'changefreq', 'priority']) assert.ok(!xml.includes(`<${tag}`), `${tag} must not be emitted`);
  assert.ok(!xml.includes('<!--'), 'comments must not be emitted');
  const urls = [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((m) => m[1]);
  assert.ok(urls.length >= 2);
  for (const u of urls) assert.match(u, /^\n    <loc>[^<]+<\/loc>\n  $/, 'each url element holds a loc and nothing else');
  assert.ok(xml.startsWith('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'));
  assert.ok(xml.endsWith('</urlset>\n'));
});

test('32. sitemap generation is byte deterministic', () => {
  const s = makeSite({ a: {}, b: {} });
  const runs = [buildSitemap(s.root), buildSitemap(s.root), buildSitemap(s.root)];
  assert.ok(runs.every((x) => x === runs[0]));
  const hashes = [];
  for (let i = 0; i < 2; i++) {
    const r = spawnSync(process.execPath, [join(REPO, 'scripts', 'generate_sitemap.mjs')], { cwd: s.root, encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
    hashes.push(createHash('sha256').update(readFileSync(join(s.root, 'sitemap.xml'))).digest('hex'));
  }
  assert.equal(hashes[0], hashes[1]);
  assert.equal(hashes[0], createHash('sha256').update(runs[0]).digest('hex'));
  const check = spawnSync(process.execPath, [join(REPO, 'scripts', 'generate_sitemap.mjs'), '--check'], { cwd: s.root, encoding: 'utf8' });
  assert.equal(check.status, 0, check.stderr);
});

test('33. a sitemap carrying lastmod, changefreq, priority or comments is reported', () => {
  const s = makeSite({ a: {}, b: {} });
  const good = buildSitemap(s.root);
  const withLastmod = good.replace('</loc>', '</loc>\n    <lastmod>2026-02-01</lastmod>');
  s.write('sitemap.xml', withLastmod);
  assert.ok(codes(validateSite(s.root)).includes('sitemap.lastmod'));
  s.write('sitemap.xml', good.replace('</loc>', '</loc>\n    <changefreq>weekly</changefreq>'));
  assert.ok(codes(validateSite(s.root)).includes('sitemap.extra_elements'));
  s.write('sitemap.xml', good.replace('</loc>', '</loc>\n    <priority>0.8</priority>'));
  assert.ok(codes(validateSite(s.root)).includes('sitemap.extra_elements'));
  s.write('sitemap.xml', good.replace('<urlset', '<!-- note -->\n<urlset'));
  assert.ok(codes(validateSite(s.root)).includes('sitemap.extra_elements'));
  s.write('sitemap.xml', good);
  assert.ok(!codes(validateSite(s.root)).some((c) => c.startsWith('sitemap.')));
});

test('34. the real sitemap is location only, matches the manifest and excludes KYB Lab and Scenario Lab', () => {
  const xml = readFileSync(join(REPO, 'sitemap.xml'), 'utf8').replace(/\r\n/g, '\n');
  assert.equal(xml, buildSitemap(REPO));
  const manifest = loadManifest(REPO);
  assert.deepEqual(parseSitemap(xml).map((u) => u.loc).sort(), eligibleLocs(manifest));
  for (const tag of ['lastmod', 'changefreq', 'priority']) assert.ok(!xml.includes(`<${tag}`), `${tag} present`);
  assert.ok(!xml.includes('<!--'));
  assert.ok(!/kyb-lab|scenario-lab/.test(xml), 'a lab is in the sitemap');
  for (const f of ['kyb-lab.html', 'scenario-lab.html']) {
    const r = manifest.pages.find((x) => x.source_file === f);
    assert.ok(r && r.indexable === false && r.sitemap === false, `${f} must be non indexable and outside the sitemap`);
    assert.match(readFileSync(join(REPO, f), 'utf8'), /<meta name="robots" content="noindex, follow"/);
  }
});

const AD_SCRIPT = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1158691611711023" crossorigin="anonymous"></script>';
const kinds = (text) => adsenseInfo(text).artefacts;

test('35. every advertising artefact kind is detected, whatever the data-ad-client value', () => {
  assert.deepEqual(kinds(AD_SCRIPT), ['script']);
  assert.deepEqual(kinds('<ins class="adsbygoogle" style="display:block"></ins>'), ['ins']);
  assert.deepEqual(kinds('<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'), ['push']);
  assert.deepEqual(kinds('<div data-ad-client="ca-pub-1158691611711023"></div>'), ['ad_client'], 'expected publisher id');
  assert.deepEqual(kinds('<div data-ad-client="ca-pub-9999999999999999"></div>'), ['ad_client'], 'another publisher id');
  assert.deepEqual(kinds('<div data-ad-client="whatever"></div>'), ['ad_client'], 'arbitrary value');
  assert.deepEqual(kinds('<div data-ad-client=""></div>'), ['ad_client'], 'empty value');
  assert.deepEqual(kinds('<div data-ad-client=unquoted></div>'), ['ad_client'], 'unquoted value');
  assert.deepEqual(kinds('<div\n  class="x"\n  DATA-AD-CLIENT="y"></div>'), ['ad_client'], 'multi line tag, any case');
  assert.deepEqual(kinds('<div data-ad-slot="1234567890"></div>'), ['ad_slot'], 'data-ad-slot has its own code');
  assert.deepEqual(kinds('<div data-ad-slot></div>'), ['ad_slot'], 'valueless attribute');
  assert.deepEqual(kinds('<ins class="adsbygoogle" data-ad-client="x" data-ad-slot="1"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script>' + AD_SCRIPT).sort(),
    ['ad_client', 'ad_slot', 'ins', 'push', 'script']);
});

test('35b. unexpected publisher ids stay a separate signal from the artefact', () => {
  const info = adsenseInfo('<div data-ad-client="ca-pub-9999999999999999"></div>');
  assert.deepEqual(info.artefacts, ['ad_client']);
  assert.deepEqual(info.publisherIds, ['pub-9999999999999999']);
  const s = makeSite({ a: { ads: false, extra: '<div data-ad-client="ca-pub-9999999999999999"></div>' } }, { approve: false });
  const c = codes(validateSite(s.root));
  assert.ok(c.includes('ads.ineligible_has_ad_client'));
  assert.ok(c.includes('publisher.inconsistent'));
});

test('36. clean markup, script and style produce no advertising artefact', () => {
  const clean = '<p>The data-ad-client attribute is documented elsewhere and an ad slot is a placement.</p><div class="data-adventure" data-adjust="1" data-ad="x"></div>'
    + '<script>const adsense = false; adsbygoogle_disabled = 1; fetch("/x");</script><style>.sidebar{display:none}.ad-banner{margin:0}</style>';
  assert.deepEqual(kinds(clean), []);
  assert.deepEqual(kinds('body{color:#000}.insight{display:block}'), []);
  assert.deepEqual(kinds('const el = document.getElementById("ins"); el.dataset.adventure = 1;'), []);
});

test('37. an ineligible page carrying any artefact is reported with a deterministic code and label', () => {
  const cases = {
    script: [AD_SCRIPT, 'adsbygoogle script'],
    ins: ['<ins class="adsbygoogle"></ins>', 'ins.adsbygoogle unit'],
    push: ['<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>', 'inline adsbygoogle push call'],
    ad_client: ['<div data-ad-client="anything"></div>', 'data-ad-client attribute'],
    ad_slot: ['<div data-ad-slot="42"></div>', 'data-ad-slot attribute'],
  };
  for (const [code, [html, label]] of Object.entries(cases)) {
    const s = makeSite({ a: { ads: false, extra: html } }, { approve: false });
    const hit = validateSite(s.root).errors.filter((e) => e.code === `ads.ineligible_has_${code}`);
    assert.equal(hit.length, 1, code);
    assert.match(hit[0].message, new RegExp(label.replace(/[.]/g, '\\.')));
  }
});

test('38. an advertising artefact in a shared JavaScript, CSS or partial file fails validation', () => {
  const cases = [
    ['js/shared.js', '(adsbygoogle = window.adsbygoogle || []).push({});', ['push']],
    ['js/shared.js', 'const s = document.createElement("script"); s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js";', ['script']],
    ['js/shared.js', 'el.setAttribute("data-ad-client", "ca-pub-1");', ['ad_client']],
    ['js/shared.js', 'document.querySelectorAll("[data-ad-slot]");', ['ad_slot']],
    ['brand.js', 'el.dataset.adClient = "x"; el.dataset.adSlot = "1";', ['ad_client', 'ad_slot']],
    ['brand.css', 'ins.adsbygoogle { display: none; }', ['ins']],
    ['brand.css', '[data-ad-client] { margin: 0 }', ['ad_client']],
    ['partials/footer.html', '<ins class="adsbygoogle" data-ad-client="x" data-ad-slot="1"></ins>', ['ad_client', 'ad_slot', 'ins']],
    ['partials/nav.html', AD_SCRIPT, ['script']],
    ['scenario-lab.js', 'window.adsbygoogle = window.adsbygoogle || []; window.adsbygoogle.push({});', ['push']],
  ];
  for (const [file, content, want] of cases) {
    const s = makeSite({ a: {} });
    s.write(file, content);
    const r = validateSite(s.root);
    const got = r.errors.filter((e) => e.code.startsWith('ads.shared_asset_has_') && e.url === '/' + file).map((e) => e.code.replace('ads.shared_asset_has_', '')).sort();
    assert.deepEqual(got, [...want].sort(), `${file}: ${content}`);
    assert.ok(!r.ok);
    assert.equal(r.summary.shared_assets_with_ad_artefacts, 1);
  }
});

test('38b. clean shared files produce no false positive', () => {
  const s = makeSite({ a: {} });
  s.write('js/shared.js', 'export const load = (u) => fetch(u).then((r) => r.json()); const insight = 1;');
  s.write('brand.css', 'body { color: #111 } .ad-note { margin: 0 } .insight { display: block }');
  s.write('brand.js', 'document.documentElement.dataset.theme = "light";');
  s.write('partials/footer.html', '<footer><p>The data-ad-client attribute is not used here.</p></footer>');
  const r = validateSite(s.root);
  assert.deepEqual(r.errors.filter((e) => e.code.startsWith('ads.shared_asset')), []);
  assert.equal(r.summary.shared_assets_with_ad_artefacts, 0);
  assert.ok(sharedAssetFiles(s.root).includes('js/shared.js') && sharedAssetFiles(s.root).includes('partials/footer.html'));
});

test('39. the real repository has zero advertising artefacts in pages and in shared files', () => {
  const root = join(import.meta.dirname, '..');
  const r = validateSite(root);
  assert.equal(r.summary.with_ad_artefacts, 0);
  assert.equal(r.summary.shared_assets_with_ad_artefacts, 0);
  assert.equal(r.summary.adsense_eligible, 0);
  assert.deepEqual(r.errors.filter((e) => e.code.startsWith('ads.')), []);
  const scanned = sharedAssetFiles(root);
  for (const f of ['brand.js', 'brand.css', 'delta.css', 'scenario-lab.js', 'js/site-chrome.js', 'partials/nav.html', 'partials/footer.html', 'api/subscribe.js']) {
    assert.ok(scanned.includes(f), `${f} must be scanned`);
  }
  for (const f of scanned) assert.deepEqual(adsenseInfo(readFileSync(join(root, f), 'utf8')).artefacts, [], f);
});

const MALFORMED = {
  'pages containing null': (m) => { m.pages = [null]; },
  'pages containing an array': (m) => { m.pages = [[]]; },
  'pages containing a string': (m) => { m.pages = ['index.html']; },
  'pages containing a number': (m) => { m.pages = [5]; },
  'missing source_file': (m) => { delete m.pages[0].source_file; },
  'null source_file': (m) => { m.pages[0].source_file = null; },
  'numeric source_file': (m) => { m.pages[0].source_file = 5; },
  'empty source_file': (m) => { m.pages[0].source_file = '  '; },
  'missing url': (m) => { delete m.pages[0].url; },
  'null url': (m) => { m.pages[0].url = null; },
  'numeric url': (m) => { m.pages[0].url = 7; },
};

test('40. malformed manifest records never throw and return deterministic record errors', () => {
  for (const [label, mutate] of Object.entries(MALFORMED)) {
    const s = makeSite();
    s.edit((p, m) => mutate(m));
    let one;
    assert.doesNotThrow(() => { one = validateSite(s.root); }, label);
    const two = validateSite(s.root);
    assert.deepEqual(one.errors, two.errors, `${label}: errors must be deterministic`);
    assert.equal(one.ok, false, label);
    assert.ok(one.errors.length >= 1, label);
    assert.ok(one.errors.every((e) => e.code === 'manifest.record_shape' || e.code === 'manifest.record_field'), `${label}: only record shape errors expected, got ${one.errors.map((e) => e.code)}`);
    assert.equal(one.pages.length, 0, `${label}: no later validation stage may run`);
  }
});

test('40b. record errors name the record and the problem exactly', () => {
  const msgs = (mutate) => { const s = makeSite(); s.edit((p, m) => mutate(m)); return validateSite(s.root).errors.map((e) => `${e.code}|${e.url}|${e.message}`); };
  assert.deepEqual(msgs((m) => { m.pages = [null]; }), ['manifest.record_shape|pages[0]|pages[0] must be a plain object, got null']);
  assert.deepEqual(msgs((m) => { m.pages = [[]]; }), ['manifest.record_shape|pages[0]|pages[0] must be a plain object, got array']);
  assert.deepEqual(msgs((m) => { m.pages = ['x']; }), ['manifest.record_shape|pages[0]|pages[0] must be a plain object, got string']);
  assert.deepEqual(msgs((m) => { delete m.pages[0].source_file; }), ['manifest.record_field|pages[0]|pages[0].source_file must be a non empty string, got undefined']);
  assert.deepEqual(msgs((m) => { m.pages[0].source_file = null; }), ['manifest.record_field|pages[0]|pages[0].source_file must be a non empty string, got null']);
  assert.deepEqual(msgs((m) => { m.pages[0].source_file = 5; }), ['manifest.record_field|pages[0]|pages[0].source_file must be a non empty string, got number']);
  assert.deepEqual(msgs((m) => { delete m.pages[0].url; }), ['manifest.record_field|pages[0]|pages[0].url must be a non empty string, got undefined']);
  assert.deepEqual(msgs((m) => { m.pages[0].url = 7; }), ['manifest.record_field|pages[0]|pages[0].url must be a non empty string, got number']);
  // every bad record is reported, valid records are not validated further, and valid files are still never read
  const mixed = msgs((m) => { m.pages = [m.pages[0], null, { url: 3 }, m.pages[1]]; });
  assert.deepEqual(mixed, ['manifest.record_shape|pages[1]|pages[1] must be a plain object, got null',
    'manifest.record_field|pages[2]|pages[2].url must be a non empty string, got number',
    'manifest.record_field|pages[2]|pages[2].source_file must be a non empty string, got undefined']);
});

test('40c. a well formed manifest still validates through every stage', () => {
  const s = makeSite();
  const r = validateSite(s.root);
  assert.deepEqual(r.errors, []);
  assert.ok(r.pages.length >= 2);
});

const kindsAs = (text, kind) => adsenseInfo(text, kind).artefacts;

test('41. quoted prose and unused quoted strings are not advertising artefacts', () => {
  for (const name of ['data-ad-client', 'data-ad-slot']) {
    for (const q of ['"', "'", '`']) {
      assert.deepEqual(kinds(`<p>The attribute ${q}${name}${q} is documented here.</p>`), [], `html prose ${q}${name}${q}`);
    }
    assert.deepEqual(kinds(`<p>Use <code>"${name}"</code> and <em>'${name}'</em> carefully.</p>`), [], `inline code ${name}`);
    assert.deepEqual(kinds(`<script>const NAME = "${name}";</script>`), [], `unused string in an inline script ${name}`);
    assert.deepEqual(kindsAs(`const NAME = "${name}";`, 'js'), [], `unused constant ${name}`);
    assert.deepEqual(kindsAs(`const s = '${name}'; console.log(s);`, 'js'), [], `logged string ${name}`);
    assert.deepEqual(kindsAs(`const o = { a: \`${name}\`, list: ["${name}"] };`, 'js'), [], `object and array strings ${name}`);
    assert.deepEqual(kindsAs(`/* "${name}" */ // setAttribute is not called here`, 'js'), [], `comment ${name}`);
    assert.deepEqual(kindsAs(`.note::after { content: "${name}"; }`, 'css'), [], `css content string ${name}`);
  }
  assert.deepEqual(kinds('<p>Selectors such as [data-ad-client] are discussed in the guide.</p>'), [], 'bracketed prose in visible text');
  const s = makeSite({ a: {} });
  s.write('js/shared.js', 'export const NAME = "data-ad-client"; export const SLOT = "data-ad-slot";');
  assert.deepEqual(validateSite(s.root).errors.filter((e) => e.code.startsWith('ads.shared_asset')), []);
});

test('41b. real usage in JavaScript still counts', () => {
  const calls = ['setAttribute', 'getAttribute', 'hasAttribute', 'removeAttribute', 'toggleAttribute'];
  for (const [name, code] of [['data-ad-client', 'ad_client'], ['data-ad-slot', 'ad_slot']]) {
    for (const call of calls) {
      for (const q of ['"', "'", '`']) assert.deepEqual(kindsAs(`el.${call}(${q}${name}${q}, "x");`, 'js'), [code], `${call} ${q}${name}${q}`);
    }
    for (const sel of ['querySelector', 'querySelectorAll', 'matches', 'closest']) {
      assert.deepEqual(kindsAs(`el.${sel}("[${name}]");`, 'js'), [code], `${sel} bare selector`);
      assert.deepEqual(kindsAs(`document.${sel}('ins[${name}="1"]');`, 'js'), [code], `${sel} tag selector`);
      assert.deepEqual(kindsAs(`x.${sel}(".unit [ ${name} ]");`, 'js'), [code], `${sel} descendant selector`);
    }
  }
  for (const [text, code] of [['el.dataset.adClient = "x";', 'ad_client'], ['el.dataset.adSlot = "1";', 'ad_slot'], ['el.dataset["adClient"] = "x";', 'ad_client'],
    ["el.dataset['adSlot'] = '1';", 'ad_slot'], ['const v = el.dataset .adClient;', 'ad_client']]) {
    assert.deepEqual(kindsAs(text, 'js'), [code], text);
  }
  // the same calls inside an inline script of an HTML page
  assert.deepEqual(kinds('<script>el.setAttribute("data-ad-client", "x"); document.querySelector("[data-ad-slot]");</script>').sort(), ['ad_client', 'ad_slot']);
  // markup built inside a JavaScript string is real usage
  assert.deepEqual(kindsAs('wrap.innerHTML = \'<ins class="x" data-ad-client="y"></ins>\';', 'js'), ['ad_client']);
});

test('41c. CSS attribute selectors still count', () => {
  for (const [css, code] of [['[data-ad-client] { margin: 0 }', 'ad_client'], ['ins[data-ad-slot="1"] { display: none }', 'ad_slot'], ['div[ data-ad-client ] { x: y }', 'ad_client'],
    ['.a > [data-ad-slot^="x"], .b { x: y }', 'ad_slot']]) {
    assert.deepEqual(kindsAs(css, 'css'), [code], css);
  }
  assert.deepEqual(kinds('<style>[data-ad-client] { margin: 0 } ins[data-ad-slot] { x: y }</style>').sort(), ['ad_client', 'ad_slot']);
  const s = makeSite({ a: {} });
  s.write('brand.css', '[data-ad-slot] { display: none }');
  assert.deepEqual(validateSite(s.root).errors.filter((e) => e.code.startsWith('ads.shared_asset')).map((e) => e.code), ['ads.shared_asset_has_ad_slot']);
});

test('41d. real HTML attributes still count, in a page and in a partial', () => {
  for (const [html, want] of [
    ['<div data-ad-client="ca-pub-1158691611711023"></div>', ['ad_client']],
    ['<div data-ad-client="anything"></div>', ['ad_client']],
    ['<ins class="adsbygoogle" data-ad-client="x" data-ad-slot="1"></ins>', ['ad_client', 'ad_slot', 'ins']],
    ['<div\n  class="x"\n  data-ad-slot="9"></div>', ['ad_slot']],
    ['<div data-ad-client></div>', ['ad_client']],
  ]) {
    assert.deepEqual(kinds(html).sort(), want, html);
  }
  const s = makeSite({ a: {} });
  s.write('partials/footer.html', '<footer><div data-ad-client="x" data-ad-slot="1"></div></footer>');
  assert.deepEqual(validateSite(s.root).errors.filter((e) => e.code.startsWith('ads.shared_asset')).map((e) => e.code).sort(),
    ['ads.shared_asset_has_ad_client', 'ads.shared_asset_has_ad_slot']);
  const page = makeSite({ a: { ads: false, extra: '<p>The attribute "data-ad-client" is documented here.</p>' } }, { approve: false });
  assert.deepEqual(validateSite(page.root).errors.filter((e) => e.code.startsWith('ads.')), [], 'quoted prose on a real page is not reported');
});

test('41e. the real repository still has zero advertising artefacts', () => {
  const root = join(import.meta.dirname, '..');
  const r = validateSite(root);
  assert.equal(r.summary.with_ad_artefacts, 0);
  assert.equal(r.summary.shared_assets_with_ad_artefacts, 0);
  assert.equal(r.summary.adsense_eligible, 0);
  assert.deepEqual(r.errors, []);
  for (const f of sharedAssetFiles(root)) {
    const kind = f.endsWith('.css') ? 'css' : f.endsWith('.js') ? 'js' : 'html';
    assert.deepEqual(adsenseInfo(readFileSync(join(root, f), 'utf8'), kind).artefacts, [], f);
  }
});
