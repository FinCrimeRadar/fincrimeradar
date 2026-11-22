import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { makeMatcher, computeInventory, validateDeploySurface, classify, visibleText, operationalNames, stripCodeComments, jsReferencesPath, htmlReferencesPath, cssReferencesPath } from '../scripts/validate_deploy_surface.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const REAL_IGNORE = readFileSync(join(ROOT, '.vercelignore'), 'utf8');
const SCRIPT = join(ROOT, 'scripts', 'validate_deploy_surface.mjs');
const made = [];
after(() => { for (const d of made) rmSync(d, { recursive: true, force: true }); });

function fixture(files, ignore) {
  const dir = mkdtempSync(join(tmpdir(), 'fcr-deploy-'));
  made.push(dir);
  for (const [p, c] of Object.entries({ ...files, '.vercelignore': ignore })) {
    mkdirSync(join(dir, dirname(p)), { recursive: true });
    writeFileSync(join(dir, p), c);
  }
  return dir;
}

// The real pattern in scenario-lab.js: a constant passed to a function that calls fetch.
const REAL_FETCH_JS = 'const LOCAL_CASES_URL = "/scenario-lab/data/cases.json";\nasync function fetchCasesFrom(url, timeoutMs) {\n  const res = await fetch(url, { credentials: "omit" });\n  return res.json();\n}\nfetchCasesFrom(LOCAL_CASES_URL);\n';
const CASES = 'scenario-lab/data/cases.json';
const PUBLIC = {
  'index.html': '<link rel="stylesheet" href="/brand.css"><script src="/js/site-chrome.js"></script><link rel="icon" href="/favicon.ico"><img src="/logo.png"><meta property="og:image" content="https://x/og-image.png"><img src="/pratik.jpg">',
  'about.html': '<p>about</p>', 'delta/2026-07-04.html': '<p>delta</p>', 'partials/nav.html': '<nav></nav>',
  'brand.css': 'body{}', 'delta.css': 'body{}', 'brand.js': '', 'js/site-chrome.js': '', 'scenario-lab.js': REAL_FETCH_JS,
  'logo.png': 'x', 'favicon.ico': 'x', 'og-image.png': 'x', 'pratik.jpg': 'x', 'api/subscribe.js': 'export default () => {}',
  'ads.txt': 'x', 'robots.txt': 'x', 'sitemap.xml': '<urlset/>', 'vercel.json': '{}', 'package.json': '{}',
  'scenario-lab/data/cases.json': '[]',
};
const FORBIDDEN = {
  '.claude/settings.local.json': '{}', '.codex/rules/x.rules': 'x', '.agents/skills/a.md': 'x', '.github/workflows/ci.yml': 'x',
  '.vercel/project.json': '{}', 'docs/PLAN.md': 'x', 'tests/a.test.mjs': 'x', 'reports/content_quality_report.json': '{}',
  'reports/url_inventory.csv': 'x', 'drafts/d.md': 'x', 'content-drafts/c.md': 'x', 'node_modules/pkg/index.js': 'x',
  '.pytest_cache/README.md': 'x', 'scripts/__pycache__/x.pyc': 'x', 'scripts/lib/site.mjs': 'x', 'js/__pycache__/z.pyc': 'x',
  'perf-fix.diff': 'x', 'other.diff': 'x', 'AGENTS.md': 'x', 'BACKLOG.md': 'x', 'CLAUDE.md': 'x', 'README.md': 'x',
  'GUIDE_STANDARD.md': 'x', 'SESSION_HANDOFF.md': 'x', 'verification-ledger.json': '[]', 'data/content_manifest.json': '{}',
  'data/url_inventory.csv': 'x', 'data/fincrime-week/2026-W44.json': '{}', 'data/snapshot.json.gz': 'x', 'content-relations.json': '{}',
  '.env': 'KEY=1', '.env.local': 'KEY=1', '.gitignore': 'x', '.gitattributes': 'x', '.vercelignore': 'x',
  'convert_existing_snapshot.py': 'x', 'favicon.svg': 'x', 'og-image.svg': 'x',
};

test('1. gitignore semantics of the rule engine', () => {
  const cases = [
    ['docs/', 'docs', true, true], ['docs/', 'docs/a.md', false, true], ['docs/', 'x/docs/a.md', false, true], ['docs/', 'docs', false, false],
    ['README.md', 'README.md', false, true], ['README.md', 'sub/README.md', false, true], ['/README.md', 'sub/README.md', false, false],
    ['*.diff', 'a/b.diff', false, true], ['*.diff', 'a/b.diffx', false, false], ['**/__pycache__/', '__pycache__/x', false, true],
    ['**/__pycache__/', 'a/b/__pycache__/x', false, true], ['a/**/b.txt', 'a/b.txt', false, true], ['a/**/b.txt', 'a/x/y/b.txt', false, true],
    ['a/**', 'a/x/y', false, true], ['dir/*', 'dir/f', false, true], ['dir/*', 'dir/s/f', false, true],
    ['*.log\n!keep.log', 'keep.log', false, false], ['*.log\n!keep.log', 'x.log', false, true],
    ['docs/\n!docs/keep.txt', 'docs/keep.txt', false, true],
    ['# comment\n\n', 'comment', false, false], ['f?.txt', 'fa.txt', false, true], ['f[ab].txt', 'fc.txt', false, false],
    ['Money Mule.png', 'Money Mule.png', false, true],
  ];
  for (const [ignore, path, isDir, want] of cases) {
    assert.equal(makeMatcher(ignore)(path, isDir), want, `${JSON.stringify(ignore)} vs ${path}${isDir ? '/' : ''}`);
  }
});

const hasGit = spawnSync('git', ['--version']).status === 0;
test('2. rule engine agrees with git check-ignore on the real .vercelignore and tricky patterns', { skip: !hasGit && 'git not available' }, () => {
  const extra = '*.log\n!keep.log\n/rooted.txt\na/**/b.txt\ndir/*\n!dir/keep.txt\n**/cache/\nfoo[ab].txt\nq?.txt\ntmp*/\n';
  const text = REAL_IGNORE + '\n' + extra;
  const paths = ['x.log', 'keep.log', 'sub/x.log', 'sub/keep.log', 'rooted.txt', 'sub/rooted.txt', 'a/b.txt', 'a/x/b.txt', 'a/x/y/b.txt', 'a/c.txt',
    'dir/f', 'dir/keep.txt', 'dir/sub/f', 'cache/f', 'p/cache/f', 'fooa.txt', 'fooc.txt', 'qa.txt', 'qab.txt', 'tmp1/x', 'tmpfile',
    '.claude/x', 'docs/a.md', 'scripts/lib/s.mjs', 'a/__pycache__/x.pyc', '__pycache__/x', 'data/content_manifest.json',
    'sub/data/content_manifest.json', 'scenario-lab/data/cases.json', 'sub/data/y.json', 'Crypto Travel Rule Sunrise Guide.png', '.env', '.env.local', 'x/.env', 'foo.diff', 'd/foo.diff',
    'README.md', 'sub/README.md', 'index.html', 'js/site-chrome.js', 'api/subscribe.js', 'favicon.svg', 'favicon.ico', '.github/workflows/a.yml',
    'data/fincrime-week/2026-W44.json', 'data/other.json', 'scenario-lab/data/cases.json', 'CLAUDE.md', 'sub/CLAUDE.md', 'Fraud Vs AML.png'];
  const dir = fixture({}, text);
  assert.equal(spawnSync('git', ['init', '-q'], { cwd: dir }).status, 0);
  writeFileSync(join(dir, '.gitignore'), text);
  const r = spawnSync('git', ['check-ignore', '-z', '--stdin', '--no-index'], { cwd: dir, input: paths.join('\0') + '\0', encoding: 'utf8' });
  const gitIgnored = new Set(r.stdout.split('\0').filter(Boolean));
  const mine = makeMatcher(text);
  for (const p of paths) assert.equal(mine(p, false), gitIgnored.has(p), `disagreement on ${p}`);
});

test('3. the real .vercelignore keeps the required entries and avoids broad Markdown globs', () => {
  const lines = new Set(REAL_IGNORE.split(/\r?\n/));
  const required = ['.agents/', '.github/', '.pytest_cache/', '**/__pycache__/', 'drafts/', 'content-drafts/', 'scripts/', 'verification-ledger.json',
    'CLAUDE.md', 'AGENTS.md', 'BACKLOG.md', '.claude/', '.codex/', '.vercel/', '.git/', 'docs/', 'tests/', 'reports/', 'node_modules/', 'perf-fix.diff',
    'Experiment_04_Claude_Handoff.md', 'classification-asymmetry-DRAFT.md', 'crypto-guide-part1-brief.md', 'gambling-white-label-blind-spot-DRAFT.md',
    'add-logo-dimensions.py', 'GUIDE_STANDARD.md', 'README.md', 'SESSION_HANDOFF.md', '/data/'];
  for (const l of required) assert.ok(lines.has(l), `missing ${l}`);
  assert.ok(![...lines].some((l) => /(^|\/)\*\.md$/.test(l)), 'a broad *.md pattern is not allowed');
  assert.deepEqual([...lines].filter((l) => /^\/?data\//.test(l)), ['/data/'], 'one anchored root data rule and no exact data exclusions');
  assert.ok(!lines.has('data/'), 'a bare data/ would also exclude scenario-lab/data/, the one deployable data directory');
});

test('4. real ignore rules exclude every forbidden class and keep every public file', () => {
  const dir = fixture({ ...PUBLIC, ...FORBIDDEN }, REAL_IGNORE);
  const r = validateDeploySurface(dir);
  assert.deepEqual(r.violations, []);
  const publicPaths = Object.keys(PUBLIC).sort();
  assert.deepEqual(r.retained, publicPaths);
  assert.deepEqual(r.dataFiles.map((d) => d.path), ['scenario-lab/data/cases.json']);
});

test('5. with no ignore rules every forbidden class is reported', () => {
  const dir = fixture({ ...PUBLIC, ...FORBIDDEN }, '');
  const r = validateDeploySurface(dir);
  const codes = new Set(r.violations.map((v) => v.code));
  for (const c of ['forbidden.directory', 'forbidden.diff', 'forbidden.root_markdown', 'forbidden.ledger', 'forbidden.content_manifest', 'forbidden.report',
    'forbidden.url_inventory', 'forbidden.secret', 'surface.not_permitted', 'asset.unreferenced']) assert.ok(codes.has(c), `no ${c} violation`);
  for (const seg of ['.claude', '.codex', '.agents', '.github', '.vercel', 'docs', 'tests', 'reports', 'drafts', 'content-drafts', 'node_modules', '.pytest_cache', '__pycache__']) {
    assert.ok(r.violations.some((v) => v.code === 'forbidden.directory' && v.message.startsWith(seg + '/')), `${seg}/ not reported`);
  }
  for (const p of Object.keys(FORBIDDEN).filter((q) => q !== '.vercelignore')) {
    assert.ok(r.violations.some((v) => v.path === p), `${p} not reported`);
  }
});

const unreferenced = (files) => validateDeploySurface(fixture(files, REAL_IGNORE)).violations.filter((v) => v.code === 'data.unreferenced' && v.path === CASES);
const referenced = (files) => { const r = validateDeploySurface(fixture(files, REAL_IGNORE)); return { v: r.violations, refs: r.dataFiles.find((d) => d.path === CASES)?.references ?? [] }; };

test('6. a new file under the root data/ directory is excluded automatically', () => {
  const extra = { 'data/brand-new.json': '{}', 'data/sub/deep.csv': 'x', 'data/anything.json.gz': 'x', 'data/fincrime-week/2099-W53.json': '{}', 'data/content_manifest.json': '{}' };
  const r = validateDeploySurface(fixture({ ...PUBLIC, ...extra }, REAL_IGNORE));
  assert.deepEqual(r.violations, []);
  assert.ok(!r.retained.some((p) => p.startsWith('data/')), 'a root data file would be uploaded');
  assert.ok(r.excluded.includes('data/'), 'the whole directory is excluded');
  assert.ok(r.retained.includes(CASES), 'scenario-lab/data/cases.json stays retained');
  // the same files would be caught if the rule were missing
  const without = REAL_IGNORE.split(/\r?\n/).filter((l) => l !== '/data/').join('\n');
  const v = validateDeploySurface(fixture({ ...PUBLIC, ...extra }, without)).violations;
  for (const p of Object.keys(extra)) assert.ok(v.some((x) => x.code === 'surface.not_permitted' && x.path === p), p);
});

test('6b. data outside the one permitted file is rejected even when a deployed file names it', () => {
  const r = validateDeploySurface(fixture({ ...PUBLIC, 'scenario-lab/data/other.json': '{}', 'extra-root-data.json': '{}', 'sub/data/y.json': '{}',
    'js/site-chrome.js': 'fetch("/scenario-lab/data/other.json"); fetch("/extra-root-data.json");', 'about.html': '<a href="/extra-root-data.json">x</a>' }, REAL_IGNORE));
  for (const p of ['scenario-lab/data/other.json', 'extra-root-data.json', 'sub/data/y.json']) {
    assert.ok(r.violations.some((x) => x.code === 'surface.not_permitted' && x.path === p), `${p} must not be permitted`);
  }
  assert.deepEqual(r.dataFiles.filter((d) => d.permitted).map((d) => d.path), [CASES]);
});

test('6c. a comment, prose or unused string reference to the data file is not a runtime reference', () => {
  const neutral = 'const x = 1;\n';
  const cases = {
    'html comment': { 'scenario-lab.js': neutral, 'about.html': `<!-- fetch("/${CASES}") -->` },
    'javascript line comment': { 'scenario-lab.js': `// fetch("/${CASES}")\n${neutral}` },
    'javascript block comment': { 'scenario-lab.js': `/* fetch('/${CASES}') */\n${neutral}` },
    'css comment': { 'scenario-lab.js': neutral, 'brand.css': `/* url(/${CASES}) */ body{}` },
    'inline script comment': { 'scenario-lab.js': neutral, 'about.html': `<script>// fetch("/${CASES}")</script>` },
    'visible prose': { 'scenario-lab.js': neutral, 'about.html': `<p>The cases are published at /${CASES} for everyone.</p>` },
    'prose with the bare filename path': { 'scenario-lab.js': neutral, 'about.html': `<p>See ${CASES}</p>` },
    'unused string constant': { 'scenario-lab.js': `const LOCAL_CASES_URL = "/${CASES}";\n` },
    'constant only logged': { 'scenario-lab.js': `const U = "/${CASES}";\nconsole.log(U);\n` },
    'constant passed to a function that never loads': { 'scenario-lab.js': `const U = "/${CASES}";\nfunction show(u) { return u.length; }\nshow(U);\n` },
    'string in an object that is never loaded': { 'scenario-lab.js': `const config = { cases: "/${CASES}" };\n` },
  };
  for (const [label, files] of Object.entries(cases)) {
    assert.equal(unreferenced({ ...PUBLIC, ...files }).length, 1, `${label} must be rejected`);
  }
  const all = Object.assign({}, ...Object.values(cases));
  assert.equal(unreferenced({ ...PUBLIC, ...all }).length, 1, 'every non runtime reference together is still rejected');
});

test('6d. a concrete runtime reference is accepted', () => {
  const ok = {
    'direct fetch literal': { 'scenario-lab.js': `fetch("/${CASES}");\n` },
    'fetch with options': { 'scenario-lab.js': `fetch('/${CASES}', { credentials: "omit" }).then((r) => r.json());\n` },
    'constant passed straight to fetch': { 'scenario-lab.js': `const U = "/${CASES}";\nfetch(U);\n` },
    'constant through a function that fetches (the real pattern)': { 'scenario-lab.js': REAL_FETCH_JS },
    'constant through an arrow function that fetches': { 'scenario-lab.js': `const U = "/${CASES}";\nconst load = (u) => fetch(u);\nload(U);\n` },
    'xhr open': { 'scenario-lab.js': `xhr.open("GET", "/${CASES}");\n` },
    'inline html script': { 'scenario-lab.js': 'const x = 1;\n', 'about.html': `<script>fetch("/${CASES}")</script>` },
    'preload link attribute': { 'scenario-lab.js': 'const x = 1;\n', 'about.html': `<link rel="preload" as="fetch" href="/${CASES}">` },
    'css url': { 'scenario-lab.js': 'const x = 1;\n', 'brand.css': `body { background: url(/${CASES}); }` },
  };
  for (const [label, files] of Object.entries(ok)) {
    const { v, refs } = referenced({ ...PUBLIC, ...files });
    assert.deepEqual(v, [], `${label}: ${JSON.stringify(v)}`);
    assert.ok(refs.length >= 1, `${label} must be reported as referenced`);
  }
  // a real reference still counts next to rejected ones
  const mixed = referenced({ ...PUBLIC, 'about.html': `<!-- /${CASES} --><p>/${CASES}</p>` });
  assert.deepEqual(mixed.v, []);
  assert.deepEqual(mixed.refs, ['scenario-lab.js']);
});

test('6e. comment stripping keeps strings and regex literals intact', () => {
  assert.equal(stripCodeComments('a = 1; // gone\nb = 2; /* gone */ c = 3;').replace(/\s+/g, ' ').trim(), 'a = 1; b = 2; c = 3;');
  assert.match(stripCodeComments('const u = "http://x.example/a"; // c'), /"http:\/\/x\.example\/a"/);
  assert.match(stripCodeComments(`const r = /["']/; fetch("/${CASES}"); // c`), new RegExp(CASES));
  assert.equal(stripCodeComments('x /* keep // inside block */ y', true).includes('keep'), false);
  assert.equal(jsReferencesPath(stripCodeComments(`// fetch("/${CASES}")`), CASES), false);
  assert.equal(htmlReferencesPath(`<!-- <a href="/${CASES}"> -->`, CASES), false);
  assert.equal(htmlReferencesPath(`<a href="/${CASES}?v=2">x</a>`, CASES), true);
  assert.equal(cssReferencesPath(`/* url(/${CASES}) */`, CASES), false);
});

test('7. excluded directories are never descended into, so nothing inside can be re-included', () => {
  const dir = fixture({ ...PUBLIC, 'docs/keep.txt': 'x' }, 'docs/\n!docs/keep.txt\n');
  const inv = computeInventory(dir, 'docs/\n!docs/keep.txt\n');
  assert.ok(!inv.retained.includes('docs/keep.txt'));
});

test('8. classification of the permitted surface', () => {
  const yes = { 'index.html': 'html', 'delta/x.html': 'html', 'partials/nav.html': 'html', 'brand.css': 'css', 'brand.js': 'js', 'js/a.js': 'js',
    'logo.png': 'image', 'api/subscribe.js': 'api', 'vercel.json': 'config', 'scenario-lab/data/cases.json': 'data' };
  for (const [p, c] of Object.entries(yes)) assert.equal(classify(p), c, p);
  for (const p of ['scripts/a.mjs', 'docs/a.html', 'api/other.js', 'x.py', 'notes.md', 'sub/index.html', 'js/sub/a.js', '.env', 'a.diff', 'data/x.json', 'data/fincrime-week/2026-W47.json', 'content-relations.json', 'scenario-lab/data/other.json', 'x.csv', 'snapshot.json.gz']) assert.equal(classify(p), null, p);
});

test('9. the real repository upload inventory is clean and scenario-lab data is a tested runtime dependency', () => {
  const r = validateDeploySurface(ROOT);
  assert.deepEqual(r.violations, []);
  assert.ok(!r.retained.some((p) => p.startsWith('data/')), 'no file under data/ may be uploaded');
  assert.deepEqual(r.dataFiles.map((d) => d.path), [CASES], 'the permitted data surface is exactly scenario-lab/data/cases.json');
  const cases = r.dataFiles.find((d) => d.path === 'scenario-lab/data/cases.json');
  assert.ok(cases && cases.references.includes('scenario-lab.js'), 'scenario-lab/data/cases.json must be retained and referenced by scenario-lab.js');
  const url = readFileSync(join(ROOT, 'scenario-lab.js'), 'utf8').match(/LOCAL_CASES_URL\s*=\s*["']([^"']+)["']/)[1];
  assert.ok(r.retained.includes(url.replace(/^\//, '')), `${url} is not in the upload inventory`);
  JSON.parse(readFileSync(join(ROOT, url.replace(/^\//, '')), 'utf8'));
});

test('10. the command line validator exits 1 on a bad surface and 0 on a clean one', () => {
  const bad = spawnSync(process.execPath, [SCRIPT], { cwd: fixture({ ...PUBLIC, ...FORBIDDEN }, ''), encoding: 'utf8' });
  assert.equal(bad.status, 1);
  assert.match(bad.stdout, /FAILED/);
  const good = spawnSync(process.execPath, [SCRIPT], { cwd: fixture({ ...PUBLIC, ...FORBIDDEN }, REAL_IGNORE), encoding: 'utf8' });
  assert.equal(good.status, 0, good.stdout);
  assert.match(good.stdout, /Retained data files \(1\)/);
  assert.match(good.stdout, /scenario-lab\/data\/cases\.json <- scenario-lab\.js/);
});

test('11. future weekly JSON files are excluded by the data/ rule with no .vercelignore edit', () => {
  const weekly = { 'data/fincrime-week/2026-W99.json': '{}', 'data/fincrime-week/2027-W01.json': '{}', 'data/fincrime-week/2099-W53.json': '{}', 'data/fincrime-week/.gitkeep': '' };
  const r = validateDeploySurface(fixture({ ...PUBLIC, ...weekly }, REAL_IGNORE));
  assert.deepEqual(r.violations, []);
  assert.ok(!r.retained.some((p) => p.startsWith('data/fincrime-week/')), 'a weekly file would be uploaded');
  assert.ok(r.excluded.includes('data/'), 'the root data directory is excluded as a whole');
  const without = REAL_IGNORE.split(/\r?\n/).filter((l) => l !== '/data/').join('\n');
  const v = validateDeploySurface(fixture({ ...PUBLIC, ...weekly }, without)).violations;
  assert.ok(v.some((x) => x.code === 'surface.not_permitted' && x.path === 'data/fincrime-week/2099-W53.json'));
});

test('12. visible page text must not reference an excluded operational filename', () => {
  assert.deepEqual(visibleText('<p>a</p><!-- see BACKLOG.md --><script>// CLAUDE.md</script><style>/* README.md */</style>').match(/BACKLOG|CLAUDE|README/g), null);
  assert.match(visibleText('<p>see BACKLOG.md for the open remainder</p>'), /BACKLOG\.md/);
  const names = operationalNames(REAL_IGNORE);
  for (const n of ['BACKLOG.md', 'CLAUDE.md', 'AGENTS.md', 'README.md', 'GUIDE_STANDARD.md', 'SESSION_HANDOFF.md', 'verification-ledger.json', 'content_manifest.json', 'url_inventory.csv', 'snapshot.json.gz']) {
    assert.ok(names.includes(n), `${n} should be treated as an excluded operational filename`);
  }
  const bad = validateDeploySurface(fixture({ ...PUBLIC, 'about.html': '<p>Open items are tracked in BACKLOG.md and verification-ledger.json.</p>' }, REAL_IGNORE));
  assert.deepEqual(bad.violations.filter((x) => x.code === 'content.visible_internal_reference').map((x) => x.message).sort(),
    ['page text visibly references excluded file BACKLOG.md', 'page text visibly references excluded file verification-ledger.json']);
  const hidden = validateDeploySurface(fixture({ ...PUBLIC, 'about.html': '<!-- see BACKLOG.md --><script>/* CLAUDE.md */</script><p>ok</p>' }, REAL_IGNORE));
  assert.deepEqual(hidden.violations, []);
  // the real deployable pages
  const real = validateDeploySurface(ROOT);
  assert.deepEqual(real.violations.filter((x) => x.code === 'content.visible_internal_reference'), []);
});
