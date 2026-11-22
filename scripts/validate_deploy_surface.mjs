// Deployment surface validator.
//   node scripts/validate_deploy_surface.mjs [--list]
// Applies the real .vercelignore rules (gitignore syntax) to the working tree, calculates the upload
// inventory and fails if anything outside the permitted public surface would be uploaded. It also reports
// every retained data file with the deployed files that concretely reference it (a fetch or import, a tag
// attribute or a CSS url; comments, prose and unused strings do not count). The only permitted data file is
// scenario-lab/data/cases.json. Exit code 1 on any violation.
// No runtime dependencies. This script lives in scripts/, which .vercelignore excludes from deployment.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

// ---------- gitignore rule engine ----------

function translate(p) {
  let re = '';
  let i = 0;
  while (i < p.length) {
    const c = p[i];
    if (c === '*') {
      if (p[i + 1] === '*') {
        const prevSlash = i === 0 || p[i - 1] === '/';
        if (prevSlash && p[i + 2] === '/') { re += '(?:.*/)?'; i += 3; continue; }
        if (prevSlash && i + 2 >= p.length) { re += '.*'; i += 2; continue; }
        re += '[^/]*'; i += 2; continue;
      }
      re += '[^/]*'; i++; continue;
    }
    if (c === '?') { re += '[^/]'; i++; continue; }
    if (c === '[') {
      const j = p.indexOf(']', i + 2);
      if (j !== -1) {
        let body = p.slice(i + 1, j).replace(/\\/g, '\\\\');
        if (body[0] === '!' || body[0] === '^') body = '^' + body.slice(1);
        re += '[' + body + ']'; i = j + 1; continue;
      }
    }
    if (c === '\\' && i + 1 < p.length) { re += p[i + 1].replace(/[.*+?^${}()|[\]\\/]/g, '\\$&'); i += 2; continue; }
    re += c.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&'); i++;
  }
  return re;
}

export function parseIgnore(text) {
  const rules = [];
  for (let raw of text.split(/\r?\n/)) {
    let line = raw.replace(/(?<!\\)[ \t]+$/, '');
    if (!line || line.startsWith('#')) continue;
    let negate = false;
    if (line.startsWith('!')) { negate = true; line = line.slice(1); }
    else if (line.startsWith('\\!') || line.startsWith('\\#')) line = line.slice(1);
    let dirOnly = false;
    if (line.endsWith('/')) { dirOnly = true; line = line.slice(0, -1); }
    if (!line) continue;
    let anchored = false;
    if (line.startsWith('/')) { anchored = true; line = line.slice(1); }
    if (line.includes('/')) anchored = true;
    const body = translate(line);
    rules.push({ source: raw, negate, dirOnly, re: new RegExp(anchored ? `^${body}$` : `^(?:.*/)?${body}$`) });
  }
  return rules;
}

export function makeMatcher(text) {
  const rules = parseIgnore(text);
  const decide = (p, isDir) => {
    let ignored = false;
    for (const r of rules) {
      if (r.dirOnly && !isDir) continue;
      if (r.re.test(p)) ignored = !r.negate;
    }
    return ignored;
  };
  // A path inside an excluded directory can never be re-included, exactly as in git.
  return (path, isDir = false) => {
    const parts = path.split('/');
    for (let i = 1; i < parts.length; i++) if (decide(parts.slice(0, i).join('/'), true)) return true;
    return decide(path, isDir);
  };
}

// ---------- inventory ----------

export function computeInventory(root, ignoreText) {
  const isIgnored = makeMatcher(ignoreText);
  const retained = [];
  const excluded = [];
  const walk = (rel) => {
    for (const e of readdirSync(join(root, rel), { withFileTypes: true })) {
      if (e.name === '.git') continue; // never uploaded, never part of the inventory
      const p = rel ? `${rel}/${e.name}` : e.name;
      const dir = e.isDirectory();
      if (isIgnored(p, dir)) { excluded.push(dir ? p + '/' : p); continue; }
      if (dir) walk(p); else retained.push(p);
    }
  };
  walk('');
  return { retained: retained.sort(), excluded: excluded.sort() };
}

// ---------- permitted surface ----------

const CONFIG_FILES = new Set(['ads.txt', 'robots.txt', 'sitemap.xml', 'vercel.json', 'package.json']);
// The complete permitted data surface. Root data/ is excluded as a whole by .vercelignore.
const PERMITTED_DATA = ['scenario-lab/data/cases.json'];
const IMAGE_EXT = /\.(png|jpe?g|gif|webp|svg|ico)$/i;
const FORBIDDEN_SEGMENTS = ['.claude', '.codex', '.agents', '.github', '.vercel', '.git', 'docs', 'tests', 'reports', 'drafts',
  'content-drafts', 'scripts', 'node_modules', '.pytest_cache', '__pycache__'];

export function classify(path) {
  const root = !path.includes('/');
  if (root && CONFIG_FILES.has(path)) return 'config';
  if (path === 'api/subscribe.js') return 'api';
  if (/\.html$/.test(path) && (root || /^(delta|partials)\/[^/]+$/.test(path))) return 'html';
  if (/\.css$/.test(path) && root) return 'css';
  if (/\.js$/.test(path) && (root || /^js\/[^/]+$/.test(path))) return 'js';
  if (IMAGE_EXT.test(path) && root) return 'image';
  if (PERMITTED_DATA.includes(path)) return 'data';
  return null;
}

function violationsFor(path) {
  const out = [];
  const parts = path.split('/');
  const base = parts[parts.length - 1];
  for (const seg of parts.slice(0, -1).concat(base === '.git' ? [base] : [])) {
    if (FORBIDDEN_SEGMENTS.includes(seg)) out.push(['forbidden.directory', `${seg}/ would be uploaded`]);
  }
  if (/\.(diff|patch)$/i.test(base)) out.push(['forbidden.diff', 'diff file would be uploaded']);
  if (parts.length === 1 && /\.md$/i.test(base)) out.push(['forbidden.root_markdown', 'internal root Markdown file would be uploaded']);
  if (base === 'verification-ledger.json') out.push(['forbidden.ledger', 'verification ledger would be uploaded']);
  if (base === 'content_manifest.json') out.push(['forbidden.content_manifest', 'content manifest would be uploaded']);
  if (/(quality|review).*report|report.*(quality|review)/i.test(base)) out.push(['forbidden.report', 'quality or review report would be uploaded']);
  if (/url[-_]?inventor/i.test(base)) out.push(['forbidden.url_inventory', 'URL inventory would be uploaded']);
  if (base === '.env' || base.startsWith('.env.') || /\.(pem|key|p12|pfx|crt)$/i.test(base) || /^id_(rsa|dsa|ecdsa|ed25519)/.test(base)
    || base === '.npmrc' || /^credentials/i.test(base)) out.push(['forbidden.secret', 'secret or environment file would be uploaded']);
  return out;
}

// Visible reader-facing text of an HTML page: comments, scripts, styles and tags removed.
export function visibleText(html) {
  return html.replace(/<!--[\s\S]*?-->/g, ' ').replace(/<(script|style|noscript)\b[\s\S]*?<\/\1>/gi, ' ').replace(/<[^>]+>/g, ' ');
}

// Exact operational filenames excluded by .vercelignore (Markdown, data, diff and script files), by basename,
// plus the generated data and report names that the broad data/ and reports/ rules cover.
const ALWAYS_INTERNAL_NAMES = ['content_manifest.json', 'url_inventory.csv', 'snapshot.json.gz', 'content_quality_report.json'];
export function operationalNames(ignoreText) {
  const names = new Set(ALWAYS_INTERNAL_NAMES);
  for (const raw of ignoreText.split(/\r?\n/)) {
    const l = raw.trim();
    if (!l || l.startsWith('#') || /[*?[!]/.test(l) || l.endsWith('/')) continue;
    if (/\.(md|json|csv|gz|diff|py)$/i.test(l)) names.add(l.split('/').pop());
  }
  return [...names];
}

// ---------- concrete runtime references ----------
// A data file counts as referenced only by code that can actually load it: a fetch, import, Request, URL,
// Worker, XHR open or sendBeacon call (directly, through a string constant that is passed to such a call
// or to a function in the same file that does), a tag attribute (href, src, data, action) or a CSS url().
// Comments, visible prose and unused string constants do not count.
const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const BUILTIN_LOADERS = new Set(['fetch', 'import', 'Request', 'URL', 'Worker', 'open', 'sendBeacon']);

export function stripHtmlComments(src) {
  return src.replace(/<!--[\s\S]*?-->/g, ' ');
}

// Removes block comments (and, for JavaScript, line comments) without touching string or regex literals.
export function stripCodeComments(src, lineComments = true) {
  let out = '';
  let i = 0;
  let prev = '';
  const n = src.length;
  while (i < n) {
    const c = src[i];
    const d = src[i + 1];
    if (c === '/' && d === '*') { const j = src.indexOf('*/', i + 2); out += ' '; i = j === -1 ? n : j + 2; continue; }
    if (lineComments && c === '/' && d === '/') { while (i < n && src[i] !== '\n') i++; continue; }
    if (c === '"' || c === "'" || c === '`') {
      let j = i + 1;
      while (j < n && src[j] !== c) {
        if (src[j] === '\\') j++;
        else if (c !== '`' && src[j] === '\n') break;
        j++;
      }
      out += src.slice(i, j + 1); i = j + 1; prev = c; continue;
    }
    if (lineComments && c === '/' && (prev === '' || '(,=:[!&|?{};'.includes(prev))) {
      let j = i + 1;
      let cls = false;
      while (j < n && src[j] !== '\n') {
        if (src[j] === '\\') j++;
        else if (src[j] === '[') cls = true;
        else if (src[j] === ']') cls = false;
        else if (src[j] === '/' && !cls) break;
        j++;
      }
      out += src.slice(i, j + 1); i = j + 1; prev = '/'; continue;
    }
    out += c;
    if (!/\s/.test(c)) prev = c;
    i++;
  }
  return out;
}

function functionFetches(code, name) {
  const n = escRe(name);
  const m = new RegExp(String.raw`(?:\bfunction\s+${n}\s*\(|\b(?:const|let|var)\s+${n}\s*=\s*(?:async\s*)?(?:function\b[^(]*)?\()`).exec(code);
  if (!m) return false;
  const rest = code.slice(m.index + m[0].length);
  const after = rest.slice(rest.indexOf(')') + 1);
  const start = after.slice(after.match(/^\s*(?:=>\s*)?/)[0].length);
  let body = start.split(/[;\n]/)[0];
  if (start[0] === '{') {
    let depth = 0;
    let k = 0;
    for (; k < start.length; k++) {
      if (start[k] === '{') depth++;
      else if (start[k] === '}' && --depth === 0) break;
    }
    body = start.slice(0, k + 1);
  }
  return /\b(?:fetch|import)\s*\(|\bXMLHttpRequest\b/.test(body);
}

// `code` must already have its comments stripped.
export function jsReferencesPath(code, path) {
  const V = [path, '/' + path].map(escRe).join('|');
  const direct = new RegExp(String.raw`(?:\bfetch|\bimport|\bnew\s+Request|\bnew\s+URL|\bnew\s+Worker|\.open|\.sendBeacon)\s*\(\s*(?:[^()]*?,\s*)?["'\x60](?:${V})(?:[?#][^"'\x60]*)?["'\x60]`);
  if (direct.test(code)) return true;
  const wanted = new Set([path, '/' + path]);
  for (const m of code.matchAll(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*["'`]([^"'`]*)["'`]/g)) {
    if (!wanted.has(m[2].split(/[?#]/)[0])) continue;
    const calls = new RegExp(String.raw`([A-Za-z_$][\w$.]*)\s*\(\s*(?:[^()]*?,\s*)?${escRe(m[1])}\s*[,)]`, 'g');
    for (const c of code.matchAll(calls)) {
      const callee = c[1].split('.').pop();
      if (BUILTIN_LOADERS.has(callee) || functionFetches(code, callee)) return true;
    }
  }
  return false;
}

export function htmlReferencesPath(html, path) {
  const h = stripHtmlComments(html);
  const wanted = new Set([path, '/' + path]);
  for (const m of h.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (/type\s*=\s*["']?(?:application\/(?:ld\+)?json|text\/template)/i.test(m[1])) continue;
    if (m[2].trim() && jsReferencesPath(stripCodeComments(m[2], true), path)) return true;
  }
  for (const m of h.matchAll(/<(?:a|link|img|script|source|iframe|form|object|embed|video|audio)\b[^>]*>/gi)) {
    for (const a of m[0].matchAll(/\b(?:href|src|data|action|data-src|data-url)\s*=\s*["']([^"']*)["']/gi)) {
      if (wanted.has(a[1].split(/[?#]/)[0])) return true;
    }
  }
  return false;
}

export function cssReferencesPath(css, path) {
  const V = [path, '/' + path].map(escRe).join('|');
  return new RegExp(String.raw`url\(\s*["']?(?:${V})(?:[?#][^"')]*)?["']?\s*\)|@import\s+["'](?:${V})["']`).test(stripCodeComments(css, false));
}

function referencesConcretely(file, text, path) {
  const kind = classify(file);
  if (kind === 'html') return htmlReferencesPath(text, path);
  if (kind === 'js' || kind === 'api') return jsReferencesPath(stripCodeComments(text, true), path);
  if (kind === 'css') return cssReferencesPath(text, path);
  return false;
}

function referenceTexts(root, retained) {
  const texts = {};
  for (const p of retained) {
    const c = classify(p);
    if (c === 'html' || c === 'js' || c === 'css' || c === 'api' || p === 'vercel.json' || p === 'robots.txt' || p === 'sitemap.xml') {
      texts[p] = readFileSync(join(root, p), 'utf8');
    }
  }
  return texts;
}

export function validateDeploySurface(root) {
  const ignorePath = join(root, '.vercelignore');
  if (!existsSync(ignorePath)) throw new Error('.vercelignore is missing');
  const { retained, excluded } = computeInventory(root, readFileSync(ignorePath, 'utf8'));
  const violations = [];
  for (const p of retained) {
    for (const [code, message] of violationsFor(p)) violations.push({ code, path: p, message });
    if (classify(p) === null) violations.push({ code: 'surface.not_permitted', path: p, message: 'not part of the permitted deployment surface' });
  }
  const names = operationalNames(readFileSync(ignorePath, 'utf8'));
  for (const p of retained.filter((q) => classify(q) === 'html')) {
    const vis = visibleText(readFileSync(join(root, p), 'utf8'));
    for (const n of names) {
      if (vis.includes(n)) violations.push({ code: 'content.visible_internal_reference', path: p, message: `page text visibly references excluded file ${n}` });
    }
  }
  const texts = referenceTexts(root, retained);
  const referencedBy = (p) => {
    const variants = new Set([p, '/' + p, encodeURI(p), '/' + encodeURI(p), p.replace(/ /g, '+'), p.replace(/ /g, '%20')]);
    return Object.keys(texts).filter((t) => t !== p && [...variants].some((v) => texts[t].includes(v)));
  };
  const isDataLike = (p) => /\.(json|csv|gz)$/i.test(p) && !CONFIG_FILES.has(p);
  const concreteRefs = (p) => Object.keys(texts).filter((t) => t !== p && referencesConcretely(t, texts[t], p));
  const dataFiles = retained.filter(isDataLike).map((p) => ({ path: p, permitted: classify(p) === 'data', references: classify(p) === 'data' ? concreteRefs(p) : [] }));
  for (const d of dataFiles) {
    if (d.permitted && !d.references.length) {
      violations.push({ code: 'data.unreferenced', path: d.path, message: 'retained data file has no concrete runtime reference (a fetch or import, a tag attribute or a CSS url) in any deployed file; comments, prose and unused strings do not count' });
    }
  }
  for (const p of retained.filter((q) => classify(q) === 'image')) {
    if (!referencedBy(p).length) violations.push({ code: 'asset.unreferenced', path: p, message: 'retained image has no reference in any deployed file' });
  }
  return { retained, excluded, violations, dataFiles };
}

export function groupByDirectory(paths) {
  const groups = new Map();
  for (const p of paths) {
    const i = p.lastIndexOf('/');
    const dir = i === -1 ? '(root)' : p.slice(0, i);
    if (!groups.has(dir)) groups.set(dir, []);
    groups.get(dir).push(i === -1 ? p : p.slice(i + 1));
  }
  return groups;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = process.cwd();
  const r = validateDeploySurface(root);
  console.log(`Deploy surface: ${r.retained.length} files retained for upload, ${r.excluded.length} top level paths excluded`);
  if (process.argv.includes('--list')) {
    for (const [dir, names] of groupByDirectory(r.retained)) console.log(`  ${dir}/ (${names.length}): ${names.join(', ')}`);
  }
  console.log(`\nRetained data files (${r.dataFiles.length}):`);
  for (const d of r.dataFiles) console.log(`  ${d.path} <- ${d.references.join(', ') || (d.permitted ? 'NO RUNTIME REFERENCE' : 'NOT PERMITTED')}`);
  if (r.violations.length) {
    console.log(`\nFAILED: ${r.violations.length} violation(s)`);
    for (const v of r.violations) console.log(`  ${v.code}: ${v.path}: ${v.message}`);
    process.exit(1);
  }
  console.log('\nOK: upload inventory contains only the permitted public surface');
}
