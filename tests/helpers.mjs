// Fixture sites are built in a throwaway temp directory. Nothing here reads
// or writes the real repository files. Every directory created is tracked
// and removed by cleanupFixtures(), which runs from a test framework after
// hook and again on process exit.
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { buildManifest } from '../scripts/build_manifest.mjs';
import { buildSitemap } from '../scripts/generate_sitemap.mjs';
import { saveManifest, loadManifest, MANIFEST_PATH } from '../scripts/lib/site.mjs';
import { ADS_TXT_RECORD, ORIGIN } from '../scripts/lib/page.mjs';

export const FIXTURE_PREFIX = 'fcr-site-';
const AD = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1158691611711023" crossorigin="anonymous"></script>';

const created = new Set();
export function cleanupFixtures() {
  for (const dir of created) {
    try { rmSync(dir, { recursive: true, force: true }); } catch { /* best effort, retried on exit */ }
    created.delete(dir);
  }
}
process.on('exit', cleanupFixtures);

export function articleHtml(slug, o = {}) {
  const title = o.title ?? `Guide ${slug}`;
  const author = o.ldAuthor ?? { '@type': 'Person', name: 'Pat Author' };
  const ld = o.ld ?? JSON.stringify({ '@context': 'https://schema.org', '@type': 'Article', headline: title,
    author, datePublished: o.published ?? '2026-01-10', dateModified: o.modified ?? '2026-02-01' });
  const sources = o.sources ?? 3;
  const base = o.sourceBase ?? 'https://example.gov/';
  const byline = o.byline === undefined ? 'By Pat Author' : o.byline;
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>${title}</title>
<meta name="description" content="${o.description ?? `Description of ${slug}`}">
<meta name="author" content="Pat Author">
${o.robots ? `<meta name="robots" content="${o.robots}">` : ''}
${o.canonical === null ? '' : `<link rel="canonical" href="${o.canonical ?? `${ORIGIN}/${slug}.html`}">`}
<script type="application/ld+json">${ld}</script>
${o.ads === false ? '' : AD}
</head><body>
${o.h1 === false ? '' : `<h1>${title}</h1>`}
${byline ? `<p>${byline}</p>` : ''}
<p>${(o.links ?? []).map((l) => `<a href="${l}">link</a>`).join(' ')}</p>
${sources === 0 ? '' : `<h2>Sources</h2><ol>${Array.from({ length: sources }, (_, i) => `<li><a href="${base}${i}">Source ${i}</a></li>`).join('')}</ol>`}
${o.extra ?? ''}
</body></html>`;
}

// approve:true fills the human review fields the way a reviewer would, so that
// fixtures can exercise eligible pages. Real manifests are never filled by code.
export function makeSite(pages = { a: {}, b: {} }, { approve = true } = {}) {
  const root = mkdtempSync(join(tmpdir(), FIXTURE_PREFIX));
  created.add(root);
  const write = (f, s) => { mkdirSync(dirname(join(root, f)), { recursive: true }); writeFileSync(join(root, f), s); };
  write('index.html', articleHtml('index', { canonical: `${ORIGIN}/`, ads: false, title: 'Home' }));
  for (const [slug, o] of Object.entries(pages)) write(`${slug}.html`, articleHtml(slug, o));
  write('ads.txt', ADS_TXT_RECORD + '\n');
  const all = ['index', ...Object.keys(pages)];
  write('sitemap.xml', `<urlset>${all.map((s) => `<url><loc>${ORIGIN}/${s === 'index' ? '' : s + '.html'}</loc></url>`).join('')}</urlset>`);
  saveManifest(root, buildManifest(root));
  const m = loadManifest(root);
  m.pages.find((r) => r.source_file === 'index.html').page_type = 'navigation';
  if (approve) {
    for (const r of m.pages.filter((x) => x.page_type === 'article')) {
      Object.assign(r, { adsense_eligible: true, editorial_review_status: 'approved', regulatory_review_status: 'approved',
        approved_by: 'Jane Hartley', date_reviewed: '2026-02-15', review_evidence: 'review-log/2026-02-15', unverified_claim_count: 0 });
    }
  }
  saveManifest(root, m);
  try { writeFileSync(join(root, 'sitemap.xml'), buildSitemap(root)); } catch { /* invalid fixtures keep the seed sitemap */ }
  return { root, write, read: (f) => readFileSync(join(root, f), 'utf8'),
    edit(fn) { const mm = loadManifest(root); fn(mm.pages, mm); saveManifest(root, mm); return mm; },
    rec: (url) => loadManifest(root).pages.find((x) => x.url === url),
    manifestPath: join(root, MANIFEST_PATH) };
}
export const codes = (r) => r.errors.map((e) => e.code);
export const failedRules = (r, url) => (r.pages.find((p) => p.url === url)?.eligibility_failures ?? []).map((f) => f.rule);
