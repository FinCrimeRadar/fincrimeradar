// Generates sitemap.xml from data/content_manifest.json.
//   node scripts/generate_sitemap.mjs          write sitemap.xml
//   node scripts/generate_sitemap.mjs --check  fail if sitemap.xml is not current
// The sitemap is location only: lastmod, changefreq, priority and comments are intentionally
// not emitted. lastmod may be introduced later only through an explicit human verified
// significant modification field. It must never be inferred from schema metadata, date_modified
// or file timestamps.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { ORIGIN } from './lib/page.mjs';
import { loadManifest, canonicalFor } from './lib/site.mjs';

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function buildSitemap(root) {
  const { pages } = loadManifest(root);
  const seen = new Set();
  const urls = [];
  for (const r of pages.filter((x) => x.sitemap === true)) {
    if (r.status !== 'published' || r.indexable !== true) throw new Error(`${r.url}: sitemap=true requires status published and indexable true (got ${r.status}, indexable ${r.indexable})`);
    if (!existsSync(join(root, r.source_file))) throw new Error(`${r.url}: source file ${r.source_file} is missing`);
    const loc = r.canonical ?? canonicalFor(r.source_file);
    if (!loc.startsWith(ORIGIN + '/')) throw new Error(`${r.url}: canonical ${loc} is not on ${ORIGIN}`);
    if (seen.has(loc)) throw new Error(`duplicate sitemap URL ${loc}`);
    seen.add(loc);
    urls.push({ loc });
  }
  urls.sort((a, b) => (a.loc < b.loc ? -1 : 1));
  const body = urls.map((u) => `  <url>\n    <loc>${esc(u.loc)}</loc>\n  </url>`).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = process.cwd();
  try {
    const xml = buildSitemap(root);
    const file = join(root, 'sitemap.xml');
    if (process.argv.includes('--check')) {
      const cur = existsSync(file) ? readFileSync(file, 'utf8').replace(/\r\n/g, '\n') : null;
      if (cur !== xml) { console.error('sitemap.xml is out of date. Run: npm run sitemap:generate'); process.exit(1); }
      console.log('sitemap.xml is current.');
    } else {
      writeFileSync(file, xml);
      console.log(`Wrote sitemap.xml (${(xml.match(/<url>/g) || []).length} URLs).`);
    }
  } catch (e) { console.error(`sitemap generation failed: ${e.message}`); process.exit(1); }
}
