// Creates or refreshes data/content_manifest.json.
//
// Page facts (title, description, canonical, author, dates, source count,
// structured data type) are always re-read from the HTML. Editorial and
// advertising decisions (page_type, status, indexable, sitemap,
// adsense_eligible, review_state and every review/approval field) are only set
// here for a page seen for the first time, and never overwritten afterwards.
//
// Automation never grants advertising eligibility or approval. Every new
// record starts with adsense_eligible=false and empty review fields; a human
// edits them. First run (no manifest) seeds sitemap membership from the
// current sitemap.xml; later runs default new pages to sitemap=false.
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { readPage, ORIGIN } from './lib/page.mjs';
import { listPublicHtml, loadManifest, saveManifest, sortPages, parseSitemap, canonicalFor, urlFor,
  structuredDataType, MANIFEST_PATH, SCHEMA_VERSION } from './lib/site.mjs';

const EXCLUDED = [
  { source_file: 'googlea1b6df2e32a52673.html', reason: 'Google Search Console ownership verification token, not a content page' },
];
const NAVIGATION = new Set(['index.html', 'knowledge.html', 'about.html', 'contact.html', 'supporters.html', 'editorial-standards.html', 'methodology.html']);
const LEGAL = new Set(['privacy.html', 'terms.html']);
const TOOLS = new Set(['screen.html']);
// Pages that must stay out of the index until their content is complete.
const HELD = {
  'kyb-lab.html': { page_type: 'tool', status: 'beta' },
  'scenario-lab.html': { page_type: 'incomplete', status: 'incomplete' },
};

function defaults(file, page) {
  const held = HELD[file];
  if (held) return { ...held, indexable: false };
  if (file.startsWith('delta/')) return { page_type: 'archive', status: 'archived', indexable: false };
  const page_type = LEGAL.has(file) ? 'legal' : TOOLS.has(file) ? 'tool' : NAVIGATION.has(file) ? 'navigation'
    : page.articleNode ? 'article' : 'navigation';
  return { page_type, status: 'published', indexable: !page.robots.includes('noindex') };
}

export function buildManifest(root) {
  const existing = existsSync(join(root, MANIFEST_PATH)) ? loadManifest(root) : null;
  const prior = new Map((existing?.pages ?? []).map((r) => [r.source_file, r]));
  const smPath = join(root, 'sitemap.xml');
  const seedSitemap = !existing && existsSync(smPath)
    ? new Set(parseSitemap(readFileSync(smPath, 'utf8')).map((s) => s.loc)) : new Set();
  const excluded = new Set(EXCLUDED.map((e) => e.source_file));

  const pages = new Map();
  const records = [];
  for (const file of listPublicHtml(root).filter((f) => !excluded.has(f))) {
    const p = readPage(join(root, file));
    pages.set(file, p);
    const old = prior.get(file);
    const d = old ?? defaults(file, p);
    const keep = (k, fallback = null) => (old && k in old ? old[k] : fallback);
    records.push({
      url: urlFor(file),
      source_file: file,
      page_type: d.page_type,
      status: d.status,
      title: p.title,
      description: p.description,
      canonical: p.canonicals[0] ?? null,
      indexable: d.indexable,
      sitemap: old ? old.sitemap : (d.indexable && d.status === 'published' && seedSitemap.has(canonicalFor(file))),
      adsense_eligible: old ? old.adsense_eligible : false,
      author: p.visibleAuthor,
      date_published: p.datePublished,
      date_modified: p.dateModified,
      authoritative_source_count: p.sources.authoritative,
      secondary_source_count: p.sources.secondary,
      internal_reference_count: p.sources.internal,
      unverified_claim_count: keep('unverified_claim_count'),
      structured_data_type: structuredDataType(p),
      review_state: keep('review_state'),
      editorial_review_status: keep('editorial_review_status'),
      regulatory_review_status: keep('regulatory_review_status'),
      date_reviewed: keep('date_reviewed'),
      review_evidence: keep('review_evidence'),
      approved_by: keep('approved_by'),
      regulatory_blockers: keep('regulatory_blockers', []),
    });
  }

  return { schema_version: SCHEMA_VERSION, origin: ORIGIN, excluded_files: existing?.excluded_files ?? EXCLUDED, pages: sortPages(records) };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = process.cwd();
  const m = buildManifest(root);
  saveManifest(root, m);
  console.log(`Wrote ${MANIFEST_PATH}: ${m.pages.length} pages, ${m.pages.filter((r) => r.adsense_eligible).length} adsense_eligible, ${m.pages.filter((r) => r.sitemap).length} in sitemap.`);
}
