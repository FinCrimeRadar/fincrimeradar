// Source classification and authorship detection.
// Both are rejection oriented heuristics: they can show that a page fails a
// rule, but a pass is never advertising approval (a human grants that).

export const ORIGIN = 'https://fincrimeradar.org';

// Host suffixes treated as authoritative primary sources: governments,
// regulators, legislatures and intergovernmental bodies. Everything else
// external is secondary. This is a heuristic list, reviewed by humans.
const AUTH_HOSTS = [
  /\.gov(\.[a-z]{2})?$/, /\.gov\.uk$/, /\.gouv\.[a-z]{2}$/, /\.gob\.[a-z]{2}$/, /\.gc\.ca$/, /\.mil$/, /\.int$/,
  /(^|\.)europa\.eu$/, /(^|\.)legislation\.gov\.uk$/, /(^|\.)fca\.org\.uk$/, /(^|\.)bankofengland\.co\.uk$/,
  /(^|\.)fatf-gafi\.org$/, /(^|\.)un\.org$/, /(^|\.)imf\.org$/, /(^|\.)worldbank\.org$/, /(^|\.)bis\.org$/,
  /(^|\.)oecd\.org$/, /(^|\.)egmontgroup\.org$/, /(^|\.)judiciary\.uk$/, /(^|\.)supremecourt\.uk$/,
  /(^|\.)fincen\.gov$/, /(^|\.)treasury\.gov$/, /(^|\.)sec\.gov$/,
];

export function classifyHref(href) {
  if (!href) return 'none';
  // Protocol relative URL: an external URL, resolved against the site origin.
  if (href.startsWith('//')) {
    try { href = new URL(href, ORIGIN + '/').href; } catch { return 'none'; }
  }
  if (/^(#|\/(?!\/)|mailto:)/.test(href) || !/^[a-z][a-z0-9+.-]*:/i.test(href)) return 'internal';
  let host;
  try { host = new URL(href).hostname.toLowerCase(); } catch { return 'none'; }
  if (host === 'fincrimeradar.org' || host.endsWith('.fincrimeradar.org')) return 'internal';
  return AUTH_HOSTS.some((re) => re.test(host)) ? 'authoritative' : 'secondary';
}

// Classify one source entry by its strongest external link. An entry with
// internal links only is an internal reference. An unlinked entry cannot be
// verified as authoritative, so it counts as secondary.
export function classifyEntry(html) {
  const kinds = [...html.matchAll(/href\s*=\s*["']([^"']+)["']/gi)].map((m) => classifyHref(m[1]));
  if (kinds.includes('authoritative')) return 'authoritative';
  if (kinds.includes('secondary')) return 'secondary';
  if (kinds.includes('internal')) return 'internal';
  return 'secondary';
}

export function classifySources(segment) {
  const entries = segment.match(/<li\b[\s\S]*?<\/li>/gi) || [];
  const out = { authoritative: 0, secondary: 0, internal: 0 };
  for (const e of entries) out[classifyEntry(e)]++;
  return out;
}

// ---------- authorship ----------
const NAME = String.raw`[A-Z][\p{L}.'’-]+(?:\s+[A-Z][\p{L}.'’-]+){1,3}`;
const BYLINE = new RegExp(String.raw`^(?:Written by|Authored by|Author:?|By)\s+(${NAME})\s*(?:$|[,|·•])`, 'u');

// A byline is a short element whose text starts with "By Name" or similar.
export function findBodyAuthor(bodyHtml, stripTags) {
  for (const m of bodyHtml.matchAll(/<(p|div|span|address|li)\b[^>]*>([\s\S]*?)<\/\1>/gi)) {
    const t = stripTags(m[2]);
    if (t.length > 140) continue;
    const b = t.match(BYLINE);
    if (b) return b[1].trim();
  }
  return null;
}

export function ldAuthorOf(articleNode) {
  const a = articleNode?.author;
  if (!a) return null;
  const first = [].concat(a)[0];
  if (typeof first === 'string') return { name: first, type: null };
  return { name: first?.name ?? null, type: first?.['@type'] ?? null };
}

const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ').trim();
// Returns { author, problem }. author is set only when a visible body byline
// exists, structured data names a Person, and the two agree.
export function resolveAuthor(bodyAuthor, ld) {
  if (!bodyAuthor) return { author: null, problem: 'no visible author byline in the page body' };
  if (!ld?.name) return { author: null, problem: 'structured data names no author' };
  if (ld.type !== 'Person') return { author: null, problem: `structured data author is ${ld.type ?? 'untyped'}, a named Person is required` };
  if (norm(ld.name) !== norm(bodyAuthor)) return { author: null, problem: `body author "${bodyAuthor}" does not match structured data author "${ld.name}"` };
  return { author: bodyAuthor, problem: null };
}
