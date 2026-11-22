// Removes the known external AdSense script (adsbygoogle.js) from every page
// whose manifest record is not adsense_eligible. Nothing else is edited.
// Inline units (ins.adsbygoogle, adsbygoogle.push calls, data-ad-client
// attributes) are NOT removed automatically: they are reported for manual removal.
//   node scripts/strip_ineligible_ads.mjs [--dry-run]
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadManifest } from './lib/site.mjs';
import { readPage } from './lib/page.mjs';

const TAG = /^[ \t]*<script\b[^>]*adsbygoogle\.js[^>]*><\/script>[ \t]*\r?\n?/gim;

export function stripIneligibleAds(root, dryRun = false) {
  const changed = [];
  const manual = [];
  for (const r of loadManifest(root).pages.filter((x) => !x.adsense_eligible)) {
    const file = join(root, r.source_file);
    const html = readFileSync(file, 'utf8');
    const out = html.replace(TAG, '');
    if (out !== html) { changed.push(r.source_file); if (!dryRun) writeFileSync(file, out); }
    const remaining = readPage(file).ads.artefacts.filter((a) => a !== 'script');
    if (remaining.length) manual.push({ source_file: r.source_file, artefacts: remaining });
  }
  return { changed, manual };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const dry = process.argv.includes('--dry-run');
  const { changed, manual } = stripIneligibleAds(process.cwd(), dry);
  console.log(`${dry ? 'Would remove' : 'Removed'} the AdSense script from ${changed.length} page(s).`);
  for (const m of manual) console.log(`MANUAL REMOVAL NEEDED: ${m.source_file} still contains ${m.artefacts.join(', ')}`);
  if (manual.length) process.exitCode = 1;
}
