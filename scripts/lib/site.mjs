// Shared site model: manifest IO, public page discovery, advertising
// eligibility rules and whole-site validation. Every function takes a
// `root` directory so tests can run against throwaway fixture sites.
import { readdirSync, readFileSync, writeFileSync, existsSync, statSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve, relative, isAbsolute, sep } from 'node:path';
import { readPage, adsenseInfo, ORIGIN, PUBLISHER_ID, ADS_TXT_RECORD } from './page.mjs';

export const SCHEMA_VERSION = 2;
export const MANIFEST_PATH = 'data/content_manifest.json';
export const REPORT_PATH = 'reports/content_quality_report.json';
export const PAGE_TYPES = ['article', 'tool', 'navigation', 'legal', 'archive', 'incomplete'];
export const STATUSES = ['published', 'beta', 'incomplete', 'archived'];
export const REVIEW_STATES = [null, 'draft', 'ready_for_review', 'in_review', 'approved'];
export const REVIEW_STATUSES = [null, 'not_started', 'in_review', 'changes_required', 'approved'];
// Names that cannot be a real human reviewer.
const NOT_A_PERSON = /\b(auto|automat\w*|bot|claude|codex|chatgpt|gpt|openai|anthropic|ai|llm|ci|github|actions?|system|script|tbd|todo|na|none|unknown|admin|reviewer|test|placeholder)\b/i;
export function isNamedReviewer(v) {
  return typeof v === 'string' && /^[\p{L}][\p{L}.'-]+(\s+[\p{L}][\p{L}.'-]+)+$/u.test(v.trim()) && !NOT_A_PERSON.test(v);
}
export const FIELDS = ['url', 'source_file', 'page_type', 'status', 'title', 'description', 'canonical',
  'indexable', 'sitemap', 'adsense_eligible', 'author', 'date_published', 'date_modified',
  'authoritative_source_count', 'secondary_source_count', 'internal_reference_count', 'unverified_claim_count',
  'structured_data_type', 'review_state', 'editorial_review_status', 'regulatory_review_status', 'date_reviewed',
  'review_evidence', 'approved_by', 'regulatory_blockers'];
const SKIP_DIRS = new Set(['.git', '.github', '.claude', '.codex', 'node_modules', 'docs', 'drafts',
  'content-drafts', 'partials', 'scripts', 'reports', 'tests', 'api', 'js', 'data']);
const MIN_SOURCES = 3;
const AD_LABELS = { script: 'adsbygoogle script', ins: 'ins.adsbygoogle unit', push: 'inline adsbygoogle push call', ad_client: 'data-ad-client attribute', ad_slot: 'data-ad-slot attribute' };

const read = (root, f) => readFileSync(join(root, f), 'utf8');
export const urlFor = (file) => (file === 'index.html' ? '/' : '/' + file);
export const canonicalFor = (file) => ORIGIN + urlFor(file);

export function listPublicHtml(root, dir = '') {
  const out = [];
  for (const e of readdirSync(join(root, dir), { withFileTypes: true })) {
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name) && !e.name.startsWith('.')) out.push(...listPublicHtml(root, dir ? `${dir}/${e.name}` : e.name));
    } else if (e.name.endsWith('.html')) out.push(dir ? `${dir}/${e.name}` : e.name);
  }
  return out.sort();
}

export function loadManifest(root) {
  return JSON.parse(read(root, MANIFEST_PATH));
}
export function saveManifest(root, manifest) {
  const p = join(root, MANIFEST_PATH);
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, JSON.stringify(manifest, null, 2) + '\n');
}
export const sortPages = (pages) => [...pages].sort((a, b) =>
  (a.url === '/' ? -1 : b.url === '/' ? 1 : a.url < b.url ? -1 : a.url > b.url ? 1 : 0));

// ---------- date helpers ----------
export function isIsoDate(s) {
  if (typeof s !== 'string') return false;
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?$/);
  if (!m) return false;
  const d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  return d.getUTCFullYear() === +m[1] && d.getUTCMonth() === +m[2] - 1 && d.getUTCDate() === +m[3];
}
const day = (s) => s.slice(0, 10);

// ---------- internal links ----------
// Containment by path.relative, not string prefix: a sibling directory whose
// name starts with the root's name must not count as inside the root.
export function isInside(root, target) {
  const rel = relative(resolve(root), resolve(target));
  return !(rel === '..' || rel.startsWith('..' + sep) || rel.startsWith('../') || isAbsolute(rel));
}

export function brokenLinks(root, links, fromFile) {
  const broken = [];
  for (const raw of new Set(links)) {
    if (/^(mailto:|tel:|javascript:|data:|#|\/\/)/i.test(raw)) continue;
    let path;
    if (/^https?:/i.test(raw)) {
      if (!raw.startsWith(ORIGIN + '/') && raw !== ORIGIN) continue;
      path = raw.slice(ORIGIN.length);
    } else path = raw;
    path = path.split('#')[0].split('?')[0];
    if (path === '') continue;
    let abs = path.startsWith('/') ? join(root, path) : join(root, dirname(fromFile), path);
    if (!isInside(root, abs)) { broken.push(raw); continue; }
    if (path.endsWith('/') || (existsSync(abs) && statSync(abs).isDirectory())) abs = join(abs, 'index.html');
    if (!existsSync(abs) || !statSync(abs).isFile()) broken.push(raw);
  }
  return broken;
}

// ---------- structured data ----------
export function structuredDataType(page) {
  if (page.articleNode) return [].concat(page.articleNode['@type']).find((t) => /Article|BlogPosting/.test(t));
  return page.ldTypes.find((t) => t !== 'BreadcrumbList') ?? null;
}

// ---------- eligibility ----------
const has = (page, re) => page.headings.some((h) => re.test(h));
export function evaluateEligibility(rec, page, ctx) {
  const f = [];
  const fail = (rule, message) => f.push({ rule, message });
  const robotsNoindex = page.robots.includes('noindex');
  if (!['article', 'tool'].includes(rec.page_type)) {
    return [{ rule: 'page_type', message: `${rec.page_type} pages are never advertising eligible` }];
  }
  if (rec.status !== 'published') fail('status', `status is ${rec.status}, must be published`);
  if (rec.page_type === 'incomplete') fail('page_type', 'incomplete page');
  if (!rec.indexable || robotsNoindex) fail('indexable', 'page is not indexable');
  if (page.h1Count !== 1) fail('h1', `${page.h1Count} H1 elements, need exactly 1`);
  if (page.canonicals.length !== 1) fail('canonical', `${page.canonicals.length} canonical tags, need exactly 1`);
  if (page.hasBetaLabel) fail('beta_label', 'page carries a Beta label');
  const sd = page.jsonLd;
  if (sd.some((b) => !b.ok)) fail('structured_data', 'structured data contains invalid JSON');
  // Human control: automation may reject eligibility but never grants it.
  if (rec.editorial_review_status !== 'approved') fail('editorial_review', 'editorial review is not approved');
  if (rec.regulatory_review_status !== 'approved') fail('regulatory_review', 'regulatory review is not approved');
  if (!isNamedReviewer(rec.approved_by)) fail('approved_by', 'approved_by must name a real human reviewer');
  if (!isIsoDate(rec.date_reviewed)) fail('date_reviewed', 'no substantive review date');
  else {
    if (day(rec.date_reviewed) > ctx.today) fail('date_reviewed', `review date ${rec.date_reviewed} is in the future`);
    if (isIsoDate(rec.date_published) && day(rec.date_reviewed) < day(rec.date_published)) fail('date_reviewed', 'review date precedes publication date');
    // Any substantive modification after the review invalidates that review.
    if (isIsoDate(rec.date_modified) && day(rec.date_reviewed) < day(rec.date_modified)) fail('date_reviewed', `page modified ${rec.date_modified} after the ${rec.date_reviewed} review, a new review is required`);
  }
  if (typeof rec.review_evidence !== 'string' || !rec.review_evidence.trim()) fail('review_evidence', 'no review evidence recorded');
  if (rec.unverified_claim_count !== 0) fail('unverified_claims', `unverified_claim_count is ${rec.unverified_claim_count}, must be assessed and equal 0`);
  if (Array.isArray(rec.regulatory_blockers) && rec.regulatory_blockers.length) fail('regulatory_blockers', `${rec.regulatory_blockers.length} unresolved regulatory blocker(s)`);
  if (rec.page_type === 'article') {
    if (!rec.sitemap) fail('sitemap', 'not included in the sitemap');
    if (!page.title || ctx.titleCounts.get(page.title) !== 1) fail('title', 'title missing or not unique');
    if (!page.description || ctx.descCounts.get(page.description) !== 1) fail('description', 'description missing or not unique');
    if (!page.visibleAuthor) fail('author', page.authorProblem ?? 'no visible author');
    if (!isIsoDate(page.datePublished)) fail('date_published', 'no valid publication date');
    if (!isIsoDate(page.dateModified)) fail('date_modified', 'no valid review or modification date');
    else if (isIsoDate(page.datePublished) && day(page.dateModified) < day(page.datePublished)) fail('date_order', 'modified date precedes publication date');
    const a = page.articleNode;
    if (!a || !a.headline || !a.author || !a.datePublished) fail('article_schema', 'missing valid Article structured data (headline, author, datePublished)');
    if (!page.sources.found) fail('sources', 'no sources section');
    else if (page.sources.authoritative < MIN_SOURCES) fail('sources', `${page.sources.authoritative} authoritative external sources (${page.sources.internal} internal, ${page.sources.secondary} secondary), need at least ${MIN_SOURCES}`);
    if (ctx.broken(rec.source_file).length) fail('broken_links', `broken internal links: ${ctx.broken(rec.source_file).join(', ')}`);
  } else {
    // tool
    if (!has(page, /\b(what (is|this)|purpose|overview|about (this|the))\b/i)) fail('purpose', 'no purpose explanation heading');
    if (!has(page, /\b(how to|instructions|getting started|how it works|how to use)\b/i)) fail('instructions', 'no user instructions heading');
    if (!has(page, /\b(methodology|data sources?|how (scores?|results?|matches?) .*(work|calculated))\b/i)) fail('methodology', 'no methodology or data explanation heading');
    if (!has(page, /\b(limitations?|caveats?|not (a )?(substitute|legal))\b/i)) fail('limitations', 'no limitations heading');
    if (!has(page, /\b(privacy|your data|data (handling|protection))\b/i)) fail('privacy', 'no privacy information heading');
    if (!page.ldTypes.some((t) => /Application|WebApplication|SoftwareApplication|HowTo|WebPage/.test(t))) fail('structured_data', 'no appropriate structured data');
    if (ctx.broken(rec.source_file).length) fail('broken_links', `broken internal links: ${ctx.broken(rec.source_file).join(', ')}`);
  }
  return f;
}

export const todayIso = () => new Date().toISOString().slice(0, 10);

export function makeContext(root, records, pages, today = todayIso()) {
  const titleCounts = new Map(), descCounts = new Map(), cache = new Map();
  for (const r of records) {
    const p = pages.get(r.source_file);
    if (!p?.exists || !r.indexable) continue;
    if (p.title) titleCounts.set(p.title, (titleCounts.get(p.title) || 0) + 1);
    if (p.description) descCounts.set(p.description, (descCounts.get(p.description) || 0) + 1);
  }
  return {
    titleCounts, descCounts, today,
    broken: (file) => {
      if (!cache.has(file)) cache.set(file, brokenLinks(root, pages.get(file)?.links ?? [], file));
      return cache.get(file);
    },
  };
}

export function loadPages(root, records) {
  const pages = new Map();
  for (const r of records) pages.set(r.source_file, readPage(join(root, r.source_file)));
  return pages;
}

// ---------- sitemap parsing (for agreement checks) ----------
export function parseSitemap(xml) {
  return [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((m) => ({
    loc: m[1].match(/<loc>([^<]*)<\/loc>/)?.[1] ?? null,
    lastmod: m[1].match(/<lastmod>([^<]*)<\/lastmod>/)?.[1] ?? null,
  }));
}

// ---------- ads.txt ----------
export function checkAdsTxt(text) {
  const issues = [];
  if (text.includes('<')) issues.push('ads.txt contains markup');
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
  if (lines.length !== 1 || lines[0] !== ADS_TXT_RECORD) issues.push(`ads.txt must contain exactly the record "${ADS_TXT_RECORD}"`);
  return issues;
}

// ---------- whole-site validation ----------
export function validateSite(root, { today = todayIso() } = {}) {
  const issues = [];
  const report = [];
  const add = (severity, code, url, message) => issues.push({ severity, code, url: url ?? null, message });
  const err = (c, u, m) => add('error', c, u, m);
  const warnings = [];
  const warn = (c, u, m) => { add('warning', c, u, m); warnings.push(issues[issues.length - 1]); };

  let manifest;
  try { manifest = loadManifest(root); }
  catch (e) { err('manifest.unreadable', null, `cannot read ${MANIFEST_PATH}: ${e.message}`); return finish(); }
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) { err('manifest.shape', null, 'manifest must be a JSON object'); return finish(); }
  if (!Array.isArray(manifest.pages)) { err('manifest.shape', null, 'manifest.pages must be an array'); return finish(); }
  if (manifest.schema_version !== SCHEMA_VERSION) err('manifest.schema_version', null, `schema_version is ${JSON.stringify(manifest.schema_version)}, expected ${SCHEMA_VERSION}`);
  if (manifest.origin !== ORIGIN) err('manifest.origin', null, `origin is ${JSON.stringify(manifest.origin)}, expected ${ORIGIN}`);
  const records = manifest.pages;

  // Record shape. Every later stage reads fields, builds paths and parses files from each record, so a
  // record that is not a plain object with string url and source_file stops validation here without throwing.
  const kindOf = (x) => (x === null ? 'null' : Array.isArray(x) ? 'array' : typeof x);
  let shapeOk = true;
  records.forEach((r, i) => {
    if (r === null || typeof r !== 'object' || Array.isArray(r)) {
      err('manifest.record_shape', `pages[${i}]`, `pages[${i}] must be a plain object, got ${kindOf(r)}`);
      shapeOk = false;
      return;
    }
    for (const k of ['url', 'source_file']) {
      if (typeof r[k] !== 'string' || !r[k].trim()) {
        err('manifest.record_field', `pages[${i}]`, `pages[${i}].${k} must be a non empty string, got ${kindOf(r[k])}`);
        shapeOk = false;
      }
    }
  });
  if (!shapeOk) return finish();

  // shape
  for (const r of records) {
    const u = r?.url ?? '(no url)';
    for (const k of FIELDS) if (!(k in r)) err('manifest.field_missing', u, `missing field ${k}`);
    for (const k of Object.keys(r)) if (!FIELDS.includes(k)) err('manifest.field_unknown', u, `unknown field ${k}`);
    if (!PAGE_TYPES.includes(r.page_type)) err('manifest.page_type', u, `invalid page_type ${r.page_type}`);
    if (!STATUSES.includes(r.status)) err('manifest.status', u, `invalid status ${r.status}`);
    if (!REVIEW_STATES.includes(r.review_state)) err('manifest.review_state', u, `invalid review_state ${r.review_state}`);
    for (const k of ['indexable', 'sitemap', 'adsense_eligible']) if (typeof r[k] !== 'boolean') err('manifest.boolean', u, `${k} must be a boolean`);
    for (const k of ['authoritative_source_count', 'secondary_source_count', 'internal_reference_count', 'unverified_claim_count']) {
      if (r[k] !== null && !(Number.isInteger(r[k]) && r[k] >= 0)) err('manifest.count', u, `${k} must be a non negative integer or null`);
    }
    for (const k of ['editorial_review_status', 'regulatory_review_status']) if (!REVIEW_STATUSES.includes(r[k])) err('manifest.review_status', u, `invalid ${k} ${r[k]}`);
    if (r.date_reviewed !== null && !isIsoDate(r.date_reviewed)) err('date.invalid', u, `date_reviewed "${r.date_reviewed}" is not a valid ISO date`);
    else if (r.date_reviewed && day(r.date_reviewed) > today) err('date.future', u, `date_reviewed ${r.date_reviewed} is in the future`);
    if (typeof r.source_file === 'string' && r.url !== urlFor(r.source_file)) err('manifest.url_drift', u, `url ${r.url} does not match ${urlFor(r.source_file)} derived from ${r.source_file}`);
    if (r.canonical && manifest.origin && !r.canonical.startsWith(manifest.origin + '/')) err('canonical.origin', u, `canonical ${r.canonical} is not on the declared origin ${manifest.origin}`);
    for (const k of ['review_evidence', 'approved_by']) if (r[k] !== null && typeof r[k] !== 'string') err('manifest.string', u, `${k} must be a string or null`);
    if (!Array.isArray(r.regulatory_blockers) || r.regulatory_blockers.some((x) => typeof x !== 'string')) err('manifest.blockers', u, 'regulatory_blockers must be an array of strings');
    for (const k of ['date_published', 'date_modified']) {
      if (r[k] !== null && !isIsoDate(r[k])) err('date.invalid', u, `${k} "${r[k]}" is not a valid ISO date`);
    }
    if (isIsoDate(r.date_published) && isIsoDate(r.date_modified) && day(r.date_modified) < day(r.date_published)) {
      err('date.order', u, 'date_modified precedes date_published');
    }
  }
  const dupes = (key) => {
    const seen = new Map();
    for (const r of records) if (r[key]) seen.set(r[key], [...(seen.get(r[key]) || []), r.url]);
    return [...seen.entries()].filter(([, v]) => v.length > 1);
  };
  for (const [v, us] of dupes('url')) err('manifest.duplicate_url', v, `duplicate url in manifest: ${us.join(', ')}`);
  for (const [v, us] of dupes('source_file')) err('manifest.duplicate_source', v, `duplicate source_file ${v}`);

  // coverage
  const excluded = new Set((manifest.excluded_files || []).map((e) => e.source_file));
  const known = new Set(records.map((r) => r.source_file));
  for (const f of listPublicHtml(root)) if (!known.has(f) && !excluded.has(f)) err('manifest.uncovered_file', '/' + f, `${f} is not in the manifest or excluded_files`);
  const live = records.filter((r) => r.source_file && existsSync(join(root, r.source_file)));
  for (const r of records) if (!live.includes(r)) err('source.missing', r.url, `source file ${r.source_file} does not exist`);

  const pages = loadPages(root, live);
  const ctx = makeContext(root, live, pages, today);

  for (const r of live) {
    const p = pages.get(r.source_file);
    const u = r.url;
    const noindex = p.robots.includes('noindex');
    const indexable = r.indexable === true;
    const lvl = indexable ? err : warn;
    const expected = canonicalFor(r.source_file);

    if (indexable && !p.h1Count) err('h1.missing', u, 'no H1');
    else if (p.h1Count > 1) err('h1.multiple', u, `${p.h1Count} H1 elements`);
    else if (!p.h1Count) warn('h1.missing', u, 'no H1');
    if (!p.title) lvl('title.missing', u, 'no title');
    if (!p.description) lvl('description.missing', u, 'no meta description');

    if (p.canonicals.length > 1) err('canonical.multiple', u, `${p.canonicals.length} canonical tags`);
    else if (p.canonicals.length === 0) lvl('canonical.missing', u, 'no canonical tag');
    else if (p.canonicals[0] !== expected) err('canonical.mismatch', u, `canonical ${p.canonicals[0]} does not match ${expected}`);

    if (indexable && noindex) err('robots.noindex_on_indexable', u, 'page is marked indexable but carries noindex');
    if (!indexable && !noindex) err('robots.missing_noindex', u, 'page is marked non indexable but has no noindex robots directive');
    if (r.sitemap && !indexable) err('sitemap.nonindexable', u, 'non indexable page is flagged for the sitemap');
    if (r.sitemap && r.status !== 'published') err('sitemap.unpublished', u, `${r.status} page is flagged for the sitemap`);
    if (r.status !== 'published' && indexable) err('status.indexable', u, `${r.status} pages must not be indexable`);
    if (r.page_type === 'incomplete' && indexable) err('status.incomplete_indexable', u, 'incomplete pages must not be indexable');

    // structured data
    p.jsonLd.forEach((b, i) => { if (!b.ok) err('structured_data.invalid_json', u, `block ${i + 1}: ${b.error}`); });
    const sdType = structuredDataType(p);
    if (r.structured_data_type !== sdType) err('structured_data.type_mismatch', u, `manifest says ${r.structured_data_type}, page has ${sdType}`);

    // links
    const bl = ctx.broken(r.source_file);
    if (bl.length) lvl('links.broken', u, `broken internal links: ${bl.join(', ')}`);

    // manifest drift against the page
    const facts = { title: p.title, description: p.description, canonical: p.canonicals[0] ?? null,
      author: p.visibleAuthor, date_published: p.datePublished, date_modified: p.dateModified,
      authoritative_source_count: p.sources.authoritative, secondary_source_count: p.sources.secondary, internal_reference_count: p.sources.internal };
    for (const [k, v] of Object.entries(facts)) {
      const mv = r[k];
      if (mv !== v) err('manifest.stale', u, `${k}: manifest ${JSON.stringify(r[k])} but page has ${JSON.stringify(v)} (run npm run manifest:refresh)`);
    }

    // advertising
    const failures = evaluateEligibility(r, p, ctx);
    if (r.adsense_eligible && failures.length) err('ads.eligibility', u, `marked adsense_eligible but fails: ${failures.map((x) => x.rule).join(', ')}`);
    if (!r.adsense_eligible) {
      for (const a of p.ads.artefacts) err(`ads.ineligible_has_${a}`, u, `advertising artefact (${AD_LABELS[a]}) present on a page that is not adsense_eligible`);
    }
    if (r.adsense_eligible && !['article', 'tool'].includes(r.page_type)) err('ads.page_type', u, `${r.page_type} pages cannot be adsense_eligible`);
    for (const id of p.ads.publisherIds) if (id !== PUBLISHER_ID) err('publisher.inconsistent', u, `unexpected publisher id ${id}`);
    if (p.ads.scriptCount > 1) err('ads.duplicate_script', u, 'AdSense script included more than once');

    // editorial gaps are reported, not repaired
    if (r.page_type === 'article' && indexable) {
      if (!r.author) warn('editorial.author', u, p.authorProblem ?? 'no visible author');
      if (!r.date_reviewed) warn('editorial.date_reviewed', u, 'no substantive review date recorded');
      for (const b of r.regulatory_blockers ?? []) warn('regulatory.blocker', u, b);
      if (!r.date_published) warn('editorial.date_published', u, 'no publication date');
      if (!r.date_modified) warn('editorial.date_modified', u, 'no modification date');
      if (!p.sources.found) warn('editorial.sources', u, 'no sources section');
      else if (p.sources.authoritative < MIN_SOURCES) warn('editorial.sources', u, `${p.sources.authoritative} authoritative sources (${p.sources.internal} internal, ${p.sources.secondary} secondary), ${MIN_SOURCES} needed`);
    }
    report.push({ url: u, source_file: r.source_file, status: r.status, page_type: r.page_type, indexable, sitemap: r.sitemap,
      adsense_eligible: r.adsense_eligible, has_adsense_script: p.ads.hasScript, ad_artefacts: p.ads.artefacts, word_count: p.wordCount,
      eligibility_failures: failures, regulatory_blockers: r.regulatory_blockers ?? [] });
  }

  // an advertising eligible page must be clean: no warnings at all
  for (const r of live.filter((x) => x.adsense_eligible)) {
    for (const w of warnings.filter((x) => x.url === r.url)) err('ads.eligible_has_warning', r.url, `eligible page has warning ${w.code}: ${w.message}`);
  }

  // uniqueness across indexable pages
  const uniq = (key, getter, code) => {
    const seen = new Map();
    for (const r of live.filter((x) => x.indexable)) {
      const v = getter(pages.get(r.source_file));
      if (v) seen.set(v, [...(seen.get(v) || []), r.url]);
    }
    for (const [v, us] of seen) if (us.length > 1) err(code, us.join(', '), `${key} shared by ${us.length} indexable pages: "${String(v).slice(0, 80)}"`);
  };
  uniq('title', (p) => p.title, 'title.duplicate');
  uniq('description', (p) => p.description, 'description.duplicate');
  uniq('canonical', (p) => p.canonicals[0], 'canonical.duplicate');

  // sitemap agreement
  const smPath = join(root, 'sitemap.xml');
  if (!existsSync(smPath)) err('sitemap.missing', null, 'sitemap.xml does not exist');
  else {
    const smRaw = readFileSync(smPath, 'utf8');
    const sm = parseSitemap(smRaw);
    if (/<(changefreq|priority)>/.test(smRaw) || /<!--/.test(smRaw)) err('sitemap.extra_elements', null, 'sitemap.xml must contain locations only: changefreq, priority and comments are not emitted');
    const locs = sm.map((s) => s.loc);
    if (new Set(locs).size !== locs.length) err('sitemap.duplicate', null, 'sitemap.xml contains duplicate URLs');
    const want = new Map(live.filter((r) => r.sitemap).map((r) => [canonicalFor(r.source_file), r]));
    for (const s of sm) {
      const r = want.get(s.loc);
      if (!r) err('sitemap.not_in_manifest', s.loc, 'URL is in sitemap.xml but not flagged for the sitemap in the manifest');
      else if (s.lastmod !== null) err('sitemap.lastmod', s.loc, 'sitemap.xml is location only: lastmod must not be emitted until a human verified significant modification field exists');
    }
    for (const loc of want.keys()) if (!locs.includes(loc)) err('sitemap.missing_url', loc, 'flagged for the sitemap but absent from sitemap.xml (run npm run sitemap:generate)');
  }

  // ads.txt and publisher id everywhere
  if (!existsSync(join(root, 'ads.txt'))) err('ads_txt.missing', null, 'ads.txt does not exist');
  else for (const m of checkAdsTxt(read(root, 'ads.txt'))) err('ads_txt.invalid', null, m);
  for (const f of ['partials/nav.html', 'partials/footer.html']) {
    if (!existsSync(join(root, f))) continue;
    const links = [...read(root, f).matchAll(/<a\b[^>]*\bhref\s*=\s*"([^"]*)"/gi)].map((m) => m[1]);
    const broken = brokenLinks(root, links, 'x.html');
    if (broken.length) err('links.broken', '/' + f, `broken internal links: ${broken.join(', ')}`);
  }
  for (const f of publisherScanFiles(root)) {
    for (const id of new Set(read(root, f).match(/pub-\d{10,}/g) || [])) {
      if (id !== PUBLISHER_ID) err('publisher.inconsistent', '/' + f, `unexpected publisher id ${id}`);
    }
  }
  // Shared JavaScript, CSS and partials cannot be tied to one eligible page, so any advertising artefact fails.
  for (const f of sharedAssetFiles(root)) {
    const kind = f.endsWith('.css') ? 'css' : f.endsWith('.js') ? 'js' : 'html';
    for (const a of adsenseInfo(read(root, f), kind).artefacts) {
      err(`ads.shared_asset_has_${a}`, '/' + f, `advertising artefact (${AD_LABELS[a]}) in a shared file that cannot be associated with a single eligible page`);
    }
  }

  return finish();

  function finish() {
    const errors = issues.filter((i) => i.severity === 'error');
    const pagesOut = report.sort((a, b) => (a.url < b.url ? -1 : 1));
    const eligible = pagesOut.filter((p) => p.adsense_eligible);
    return {
      ok: errors.length === 0,
      summary: {
        pages: pagesOut.length, errors: errors.length, warnings: warnings.length,
        adsense_eligible: eligible.length, with_adsense_script: pagesOut.filter((p) => p.has_adsense_script).length,
        with_ad_artefacts: pagesOut.filter((p) => p.ad_artefacts.length).length,
        shared_assets_with_ad_artefacts: new Set(issues.filter((i) => i.code.startsWith('ads.shared_asset_has_')).map((i) => i.url)).size,
        sitemap_urls: pagesOut.filter((p) => p.sitemap).length, non_indexable: pagesOut.filter((p) => !p.indexable).length,
      },
      review_blockers: pagesOut.filter((p) => p.regulatory_blockers.length).map((p) => ({ url: p.url, blockers: p.regulatory_blockers })),
      errors, warnings, pages: pagesOut,
    };
  }
}

// Deployable JavaScript and CSS (root, js/, api/ and any other non tooling directory) plus the partials.
const SHARED_SKIP = new Set([...SKIP_DIRS].filter((d) => !['partials', 'js', 'api'].includes(d)));
export function sharedAssetFiles(root, dir = '') {
  const out = [];
  for (const e of readdirSync(join(root, dir), { withFileTypes: true })) {
    const rel = dir ? `${dir}/${e.name}` : e.name;
    if (e.isDirectory()) {
      if (!SHARED_SKIP.has(e.name) && !e.name.startsWith('.')) out.push(...sharedAssetFiles(root, rel));
    } else if (/\.(js|css)$/.test(e.name) || (dir === 'partials' && e.name.endsWith('.html'))) out.push(rel);
  }
  return out.sort();
}

function publisherScanFiles(root) {
  const out = [...listPublicHtml(root), 'ads.txt'];
  for (const d of ['partials', 'js', '']) {
    if (!existsSync(join(root, d))) continue;
    for (const e of readdirSync(join(root, d), { withFileTypes: true })) {
      if (e.isFile() && /\.(js|html)$/.test(e.name)) out.push(d ? `${d}/${e.name}` : e.name);
    }
  }
  return [...new Set(out)].filter((f) => existsSync(join(root, f)));
}
