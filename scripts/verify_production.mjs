// Read-only production endpoint verification. Never run from pre-deploy CI.
//   node scripts/verify_production.mjs [--origin https://fincrimeradar.org]
// Exit code 1 and a clear message when any check fails.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { ADS_TXT_RECORD, ORIGIN } from './lib/page.mjs';
import { parseSitemap } from './lib/site.mjs';

const MAX_REDIRECTS = 3;

// Follows redirects manually so hops, loops and the final URL can be judged.
export async function fetchChain(url, fetchImpl = fetch) {
  const hops = [];
  const seen = new Set();
  let current = url;
  for (;;) {
    if (seen.has(current)) return { error: `redirect loop at ${current}`, hops };
    seen.add(current);
    let res;
    try {
      res = await fetchImpl(current, { redirect: 'manual', headers: { 'user-agent': 'fincrimeradar-verify/1.0', 'cache-control': 'no-cache' } });
    } catch (e) { return { error: `request failed: ${e.message}`, hops }; }
    if (res.status >= 300 && res.status < 400 && res.headers.get('location')) {
      hops.push({ from: current, status: res.status });
      current = new URL(res.headers.get('location'), current).href;
      if (hops.length > MAX_REDIRECTS) return { error: `more than ${MAX_REDIRECTS} redirects (${hops.length}+)`, hops };
      continue;
    }
    return { res, finalUrl: current, hops, body: await res.text() };
  }
}

export async function verifyAdsTxt(origin = ORIGIN, fetchImpl = fetch) {
  const url = `${origin}/ads.txt`;
  const failures = [];
  const r = await fetchChain(url, fetchImpl);
  if (r.error) return { url, ok: false, failures: [r.error], status: null, finalUrl: null, contentType: null };
  const contentType = r.res.headers.get('content-type') || '';
  if (r.res.status !== 200) failures.push(`status ${r.res.status}, expected 200`);
  if (r.finalUrl !== url) failures.push(`final URL ${r.finalUrl} differs from ${url} (${r.hops.length} redirect(s))`);
  if (!/^text\/plain\b/i.test(contentType)) failures.push(`content-type "${contentType}", expected text/plain`);
  if (/^\s*</.test(r.body)) failures.push('response body looks like HTML');
  const lines = r.body.split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
  if (!lines.includes(ADS_TXT_RECORD)) failures.push(`publisher record "${ADS_TXT_RECORD}" not found`);
  return { url, ok: failures.length === 0, failures, status: r.res.status, finalUrl: r.finalUrl, contentType, redirects: r.hops.length };
}

export async function verifySitemap(origin = ORIGIN, fetchImpl = fetch, localXml = null) {
  const url = `${origin}/sitemap.xml`;
  const failures = [];
  const r = await fetchChain(url, fetchImpl);
  if (r.error) return { url, ok: false, failures: [r.error] };
  if (r.res.status !== 200) failures.push(`status ${r.res.status}, expected 200`);
  if (!/xml/i.test(r.res.headers.get('content-type') || '')) failures.push(`content-type "${r.res.headers.get('content-type')}", expected XML`);
  if (localXml) {
    const live = parseSitemap(r.body).map((s) => s.loc).sort().join('\n');
    const local = parseSitemap(localXml).map((s) => s.loc).sort().join('\n');
    if (live !== local) failures.push('production sitemap URL set differs from the repository sitemap.xml (deployment pending or stale CDN)');
  }
  return { url, ok: failures.length === 0, failures, status: r.res.status, finalUrl: r.finalUrl };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const i = process.argv.indexOf('--origin');
  const origin = i > -1 ? process.argv[i + 1].replace(/\/$/, '') : ORIGIN;
  let local = null;
  try { local = readFileSync('sitemap.xml', 'utf8'); } catch { /* repository copy optional */ }
  const results = [await verifyAdsTxt(origin), await verifySitemap(origin, fetch, local)];
  for (const r of results) {
    console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.url} (status ${r.status ?? 'n/a'}, final ${r.finalUrl ?? 'n/a'}${r.contentType ? `, ${r.contentType}` : ''})`);
    for (const f of r.failures) console.log(`     - ${f}`);
  }
  process.exit(results.every((r) => r.ok) ? 0 : 1);
}
