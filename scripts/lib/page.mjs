// Dependency-free HTML fact extraction for the content pipeline.
// Regex based on purpose: the site is hand-written static HTML with
// predictable head structure. Facts are read from the page, never invented.
import { readFileSync, existsSync } from 'node:fs';
import { classifySources, findBodyAuthor, ldAuthorOf, resolveAuthor } from './classify.mjs';

import { ORIGIN } from './classify.mjs';
export { ORIGIN };
export const PUBLISHER_ID = 'pub-1158691611711023';
export const ADS_TXT_RECORD = `google.com, ${PUBLISHER_ID}, DIRECT, f08c47fec0942fa0`;

const decode = (s) => s
  .replace(/&#x27;|&#39;|&apos;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
const attr = (tag, name) => {
  const m = tag.match(new RegExp(String.raw`\b${name}\s*=\s*(?:"([^"]*)"|'([^']*)')`, 'i'));
  return m ? decode(m[1] ?? m[2]) : null;
};
const tagsOf = (html, name) => html.match(new RegExp(String.raw`<${name}\b[^>]*>`, 'gi')) || [];
const stripTags = (s) => decode(s.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();

export function visibleBody(html) {
  const body = html.match(/<body\b[\s\S]*<\/body>/i)?.[0] ?? html;
  return body.replace(/<(script|style|noscript|template)\b[\s\S]*?<\/\1>/gi, ' ');
}

export function extractJsonLd(html) {
  const out = [];
  const re = /<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  for (const m of html.matchAll(re)) {
    try { out.push({ ok: true, data: JSON.parse(m[1]) }); }
    catch (e) { out.push({ ok: false, error: e.message }); }
  }
  return out;
}

export function jsonLdNodes(blocks) {
  const nodes = [];
  const walk = (n) => {
    if (Array.isArray(n)) return n.forEach(walk);
    if (n && typeof n === 'object') { nodes.push(n); if (n['@graph']) walk(n['@graph']); }
  };
  blocks.filter((b) => b.ok).forEach((b) => walk(b.data));
  return nodes;
}
const typesOf = (n) => [].concat(n['@type'] ?? []);

// Sources section: a heading whose text is Sources/References/etc, counted
// as <li> items (fallback: distinct external links) up to the next h2.
const SRC_HEADING = /^((primary|key|official|legal|regulatory) )?(sources?|references?|sources and (further )?(reading|references)|further reading|notes and sources|legislation and sources)\b/i;
export function sourcesSection(body) {
  for (const m of body.matchAll(/<h([23])\b[^>]*>([\s\S]*?)<\/h\1>/gi)) {
    if (!SRC_HEADING.test(stripTags(m[2]))) continue;
    const start = m.index + m[0].length;
    const rest = body.slice(start);
    const end = rest.search(/<h2\b|<\/main>|<footer\b|<aside\b/i);
    const seg = end === -1 ? rest : rest.slice(0, end);
    const items = (seg.match(/<li\b/gi) || []).length;
    return { found: true, count: items, ...classifySources(seg) };
  }
  return { found: false, count: 0, authoritative: 0, secondary: 0, internal: 0 };
}

// An advertising attribute counts only in a context where it is used, whatever its value:
//   markup:     as an attribute inside a tag (also inside a JavaScript string that builds markup)
//   JavaScript: setAttribute, getAttribute, hasAttribute, removeAttribute, toggleAttribute, querySelector,
//               querySelectorAll, matches, closest with the attribute, and dataset.adClient or dataset["adClient"]
//   CSS:        an attribute selector such as [data-ad-client]
// A bare quoted string, visible prose or an unused string constant that merely contains the name is not usage.
const attrPatterns = (name, camel) => ({
  tag: new RegExp(String.raw`<[A-Za-z][^<>]*?\s${name}(?![\w-])`, 'i'),
  js: new RegExp([
    String.raw`\.\s*(?:setAttribute|getAttribute|hasAttribute|removeAttribute|toggleAttribute)\s*\(\s*["'\x60]${name}["'\x60]`,
    String.raw`\.\s*(?:querySelector(?:All)?|matches|closest)\s*\(\s*["'\x60][^"'\x60]*\[\s*${name}(?![\w-])`,
    String.raw`dataset\s*(?:\.\s*${camel}\b|\[\s*["']${camel}["']\s*\])`,
  ].join('|'), 'i'),
  css: new RegExp(String.raw`\[\s*${name}(?![\w-])`, 'i'),
});
const AD_CLIENT_ATTR = attrPatterns('data-ad-client', 'adClient');
const AD_SLOT_ATTR = attrPatterns('data-ad-slot', 'adSlot');

// kind is 'html' (pages and partials: markup attributes, script bodies as JavaScript, style blocks as CSS),
// 'js' or 'css' (shared files).
function hasAdAttr(text, kind, re) {
  if (kind === 'css') return re.css.test(text);
  if (kind === 'js') return re.tag.test(text) || re.js.test(text);
  if (re.tag.test(text)) return true;
  for (const m of text.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) if (re.js.test(m[1])) return true;
  for (const m of text.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) if (re.css.test(m[1])) return true;
  return false;
}

// Advertising artefacts of any page, partial, shared JavaScript or CSS file. Unexpected publisher
// identifiers are reported separately through publisherIds and never decide which artefacts exist.
export function adsenseInfo(html, kind = 'html') {
  const scripts = html.match(/<script\b[^>]*adsbygoogle\.js[^>]*>/gi) || [];
  const ids = [...html.matchAll(/\bpub-\d{10,}/g)].map((m) => m[0]);
  const artefacts = [];
  if (scripts.length || /pagead2\.googlesyndication\.com\/pagead\/js\/adsbygoogle\.js/i.test(html)) artefacts.push('script');
  if (/<ins\b[^>]*class\s*=\s*["'][^"']*\badsbygoogle\b/i.test(html) || /\bins\.adsbygoogle\b/.test(html)) artefacts.push('ins');
  if (/\badsbygoogle\b[^;]*?\.push\s*\(/.test(html)) artefacts.push('push');
  if (hasAdAttr(html, kind, AD_CLIENT_ATTR)) artefacts.push('ad_client');
  if (hasAdAttr(html, kind, AD_SLOT_ATTR)) artefacts.push('ad_slot');
  return { hasScript: scripts.length > 0, scriptCount: scripts.length, artefacts, publisherIds: [...new Set(ids)] };
}

export function readPage(file) {
  if (!existsSync(file)) return { exists: false };
  const html = readFileSync(file, 'utf8');
  const head = html.match(/<head\b[\s\S]*?<\/head>/i)?.[0] ?? '';
  const body = visibleBody(html);
  const metas = tagsOf(head, 'meta');
  const meta = (key) => {
    const t = metas.find((x) => (attr(x, 'name') || attr(x, 'property') || '').toLowerCase() === key);
    return t ? attr(t, 'content') : null;
  };
  const canonicals = tagsOf(head, 'link').filter((t) => (attr(t, 'rel') || '').toLowerCase() === 'canonical').map((t) => attr(t, 'href'));
  const title = head.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  const ld = extractJsonLd(html);
  const nodes = jsonLdNodes(ld);
  const article = nodes.find((n) => typesOf(n).some((t) => /^(Article|NewsArticle|BlogPosting|TechArticle|ScholarlyArticle)$/.test(t)));
  const timeTags = tagsOf(body, 'time').map((t) => attr(t, 'datetime')).filter(Boolean);
  const authorMeta = meta('author');
  const ldAuthor = ldAuthorOf(article);
  const authorLd = ldAuthor?.name ?? null;
  const bodyAuthor = findBodyAuthor(body, stripTags);
  const resolved = resolveAuthor(bodyAuthor, ldAuthor);
  const text = stripTags(body);
  return {
    exists: true,
    html, body, text,
    wordCount: text ? text.split(' ').length : 0,
    title: title ? stripTags(title[1]) : null,
    description: meta('description'),
    canonicals,
    robots: (meta('robots') || '').toLowerCase(),
    h1Count: (body.match(/<h1\b/gi) || []).length,
    jsonLd: ld,
    ldTypes: [...new Set(nodes.flatMap(typesOf))],
    articleNode: article ?? null,
    authorMeta, authorLd, ldAuthor, bodyAuthor, authorProblem: resolved.problem,
    // Visible byline: author name present in the rendered body text.
    visibleAuthor: resolved.author,
    datePublished: article?.datePublished ?? timeTags[0] ?? null,
    dateModified: article?.dateModified ?? null,
    sources: sourcesSection(body),
    ads: adsenseInfo(html),
    links: [...body.matchAll(/<a\b[^>]*>/gi)].map((m) => attr(m[0], 'href')).filter(Boolean),
    headings: [...body.matchAll(/<h[1-4]\b[^>]*>([\s\S]*?)<\/h[1-4]>/gi)].map((m) => stripTags(m[1])),
    hasBetaLabel: /\bbeta\b/i.test(stripTags(body.match(/<h1\b[\s\S]*?<\/h1>/i)?.[0] ?? '')) || /class="[^"]*\b(beta|badge-beta)\b/i.test(body),
  };
}
