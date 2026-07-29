# Rich footer centering fix (about.html, screen.html, knowledge.html)

## Problem

`about.html`, `screen.html`, and `knowledge.html` each ship the rich dark
footer (`<footer style="background:#071912;color:#94a3b8;margin-top:0;">`),
but each page also still carries a legacy `footer { ... }` rule (plus
`footer a` / `footer a:hover`) left over from before the rich footer
replaced the old simple centered footer.

Inline styles on the `<footer>` element only set `background`, `color`, and
`margin-top`. They don't set `text-align`, `padding`, `border-top`, or link
`margin`, so the legacy element-selector rule's values for those properties
still apply. Result: the rich footer renders centered instead of
left-aligned per its own inline grid layout, with the wrong padding, a
stray `border-top`, and cramped `margin:0 8px` link spacing.

`brand.css` section 6 was written to neutralize exactly this
(`footer[style*="0f2044"] { text-align:left !important; padding:0
!important; border-top:none !important; }`), but its selector targets the
*old* footer background color (`0f2044`), not the current one (`071912`),
so it silently stopped matching when the footer's background changed.

`tm-guide.html` (and `sanctions-compliance-guide.html`) don't have this bug
because they never carried the legacy rule.

## Root cause confirmed in code

- `about.html:155-157`
- `screen.html:240` (no separate `footer a` rules on this page)
- `knowledge.html:202-204`

Each is the same shape:

```css
footer { background:...; border-top:1px solid var(--border); padding:2rem;
          text-align:center; font-size:12px; color:var(--muted); ... }
footer a { color:var(--muted); text-decoration:none; margin:0 8px; }
footer a:hover { color:var(--teal); }
```

Each page also has exactly one `<footer>` element (the rich one), so
nothing else on the page depends on this rule.

## Fix

Delete the legacy `footer { ... }`, `footer a { ... }`, and `footer
a:hover { ... }` rules from the `<style>` block on all three pages:

- `about.html` lines 155-157
- `screen.html` line 240
- `knowledge.html` lines 202-204

Nothing else changes. Markup, `brand.css`, and each page's mobile media
query block are untouched.

## Explicitly out of scope

- **The mobile media query block** on each page (`footer { flex-direction:
  column !important }`, grid-collapse rules, and `#footerEmail {
  font-size:16px !important }`). This is not the source of the reported
  bug (a desktop-only symptom) and includes a real, working iOS Safari
  auto-zoom fix on the newsletter email input that isn't duplicated
  anywhere in `brand.css`. Deleting it would regress mobile UX. Tracked
  separately in `BACKLOG.md` under "Consolidate rich-footer mobile CSS
  into brand.css."
- `brand.css` section 6's stale `0f2044` selector.
- The `.footer-links` class referenced in the mobile media query (possible
  dead code, unverified).
- Any `site-chrome.js` / partials consolidation of the footer itself.

## Verification

For each of `about.html`, `screen.html`, `knowledge.html`, in-browser:

**Desktop width:**
- Footer background/link colors unchanged (still the dark `#071912` theme)
- Footer content left-aligned per its own inline grid layout, not centered
- No visible `border-top` above the footer
- Nav-link spacing follows the grid's own `gap`, not the old `margin:0 8px`

**Mobile width (~375px):**
- Newsletter row, nav grid, and email input layout unchanged from before
  the fix (confirms the untouched media query still works)
- Email input still uses 16px font size on focus (no iOS auto-zoom)

**No side effects on other pages:**
- `sanctions-compliance-guide.html` and `tm-guide.html` remain unaffected
  (spot-checked, unchanged), confirms this fix has no shared-component
  side effects, since the deletions are per-page inline `<style>` block
  edits, not changes to `brand.css` or any shared partial

No automated tests exist for this site's HTML/CSS; verification is
in-browser only.
