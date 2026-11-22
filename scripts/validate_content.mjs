// Whole-site content, indexing and advertising validation.
//   node scripts/validate_content.mjs [--strict]   (--strict also fails on warnings)
// Writes reports/content_quality_report.json and reports/url_inventory.csv,
// both deterministic (no timestamps). Exit code 1 on any error.
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { validateSite, REPORT_PATH } from './lib/site.mjs';

export function writeReports(root, result) {
  mkdirSync(join(root, 'reports'), { recursive: true });
  writeFileSync(join(root, REPORT_PATH), JSON.stringify(result, null, 2) + '\n');
  const cols = ['url', 'source_file', 'page_type', 'status', 'indexable', 'sitemap', 'adsense_eligible', 'has_adsense_script', 'word_count'];
  const csv = [cols.join(',')].concat(result.pages.map((p) => cols.map((c) => p[c]).join(','))).join('\n') + '\n';
  writeFileSync(join(root, 'reports/url_inventory.csv'), csv);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = process.cwd();
  const strict = process.argv.includes('--strict');
  const r = validateSite(root);
  writeReports(root, r);
  const s = r.summary;
  console.log(`Content quality: ${s.pages} pages, ${s.sitemap_urls} in sitemap, ${s.non_indexable} non indexable, ${s.adsense_eligible} adsense eligible, ${s.with_adsense_script} carrying the AdSense script`);
  const group = (list) => list.reduce((m, i) => ((m[i.code] ||= []).push(i), m), {});
  for (const [label, list] of [['ERRORS', r.errors], ['WARNINGS (editorial gaps, not repaired)', r.warnings]]) {
    if (!list.length) continue;
    console.log(`\n${label}: ${list.length}`);
    for (const [code, items] of Object.entries(group(list))) {
      console.log(`  ${code} (${items.length})`);
      for (const i of items.slice(0, label === 'ERRORS' ? 50 : 4)) console.log(`    ${i.url ?? '-'}: ${i.message}`);
      if (label !== 'ERRORS' && items.length > 4) console.log(`    ... ${items.length - 4} more in ${REPORT_PATH}`);
    }
  }
  const retained = r.pages.filter((p) => p.adsense_eligible).map((p) => p.url);
  console.log(`\nAdvertising eligible: ${retained.length}`);
  console.log(`Report: ${REPORT_PATH}`);
  process.exit(r.errors.length || (strict && r.warnings.length) ? 1 : 0);
}
