/**
 * site-chrome.js
 *
 * Single source of truth for the nav, mobile nav, footer, and cookie banner
 * used across every page on fincrimeradar.org.
 *
 * Each page must include two empty mount points and this script:
 *   <div id="site-nav"></div>
 *   ...page content...
 *   <div id="site-footer"></div>
 *   <script defer src="/js/site-chrome.js"></script>
 *
 * Editing the nav or footer for the whole site now means editing
 * /partials/nav.html or /partials/footer.html once, not every page.
 */

(function () {
  'use strict';

  var NAV_PARTIAL_URL = '/partials/nav.html';
  var FOOTER_PARTIAL_URL = '/partials/footer.html';
  var COOKIE_CONSENT_KEY = 'fcr_cookie_consent_v2';
  var FUNDING_CHOICES_POLL_MS = 500;

  // Only one Funding Choices watcher may run at a time. Holds the active
  // watcher's cleanup function, or null when no watcher is running.
  var activeFundingChoicesCleanup = null;

  // Minimal inline fallbacks used only if a partial fails to load,
  // so a network blip never leaves a page with no way home and no legal footer.
  var FALLBACK_NAV =
    '<nav><a class="nav-brand" href="/"><span class="nav-name">FinCrimeRadar</span></a>' +
    '<div class="nav-links"><a href="/">Back to home</a></div></nav>';

  var FALLBACK_FOOTER =
    '<footer>© 2026 FinCrimeRadar · <a href="/">Home</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a>' +
    '<div class="footer-legal">FinCrimeRadar Ltd · Registered in England and Wales · Company number 17324449 · ' +
    'Registered office: 128 City Road, London, EC1V 2NX</div></footer>';

  /**
   * Fetches a partial and injects it into the given mount element.
   * Falls back to inline markup on any network or HTTP error so the
   * page never renders with a missing nav or footer.
   */
  function loadPartial(url, mountId, fallbackHtml) {
    var mount = document.getElementById(mountId);
    if (!mount) return Promise.resolve();

    return fetch(url, { cache: 'default' })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Partial fetch failed: ' + url + ' (' + response.status + ')');
        }
        return response.text();
      })
      .then(function (html) {
        mount.innerHTML = html;
      })
      .catch(function (error) {
        console.error(error);
        mount.innerHTML = fallbackHtml;
      });
  }

  function toggleMobileNav() {
    var nav = document.getElementById('mobileNav');
    var btn = document.getElementById('navHamburger');
    if (!nav || !btn) return;
    var open = nav.classList.toggle('open');
    btn.innerHTML = open ? '&#10005;' : '&#9776;';
    document.body.style.overflow = open ? 'hidden' : '';
  }

  function closeMobileNavOnOutsideClick(event) {
    var nav = document.getElementById('mobileNav');
    var btn = document.getElementById('navHamburger');
    if (nav && nav.classList.contains('open') && !nav.contains(event.target) && event.target !== btn) {
      nav.classList.remove('open');
      if (btn) btn.innerHTML = '&#9776;';
      document.body.style.overflow = '';
    }
  }

  // This banner is analytics-only. Google Funding Choices (loaded separately)
  // is the sole authority for advertising and TCF consent; it must never be
  // granted, denied, or otherwise touched from here. See CLAUDE.md's consent
  // architecture note for the rationale.
  function acceptCookies() {
    localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        'analytics_storage': 'granted'
      });
    }
    document.getElementById('cookieBanner').style.display = 'none';
  }

  function rejectCookies() {
    localStorage.setItem('fcr_cookie_consent_v2', 'rejected');
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        'analytics_storage': 'denied'
      });
    }
    document.getElementById('cookieBanner').style.display = 'none';
  }

  /**
   * True only on pages that actually load the GA4 gtag.js loader tag. This is
   * a static DOM check, not a runtime one: the <script> element is present
   * the instant the HTML parser reaches it in <head>, well before this
   * deferred script runs, so unlike `typeof gtag === 'function'` it carries
   * no load-timing race. Pages such as privacy.html and fincrime-week.html
   * deliberately carry no GA, so there is no analytics choice to make there
   * and the banner must not appear.
   */
  function pageHasAnalytics() {
    return !!document.querySelector('script[src*="googletagmanager.com/gtag/js"]');
  }

  /**
   * Watches Funding Choices' displayStatus until it is no longer 'visible',
   * then reveals the analytics banner. Combines two mechanisms because
   * neither is safe alone:
   *
   * - addEventListener reacts fast, but this CMP (and potentially others)
   *   does not put displayStatus on the tcData object it delivers, so a
   *   listener firing tells us nothing by itself, only that it's worth
   *   re-checking via ping right now.
   * - A recurring ping poll is the only mechanism actually guaranteed to
   *   notice the visible-to-hidden transition: nothing requires Funding
   *   Choices to emit another TCF event when its UI clears, so a
   *   listener-only design can wait forever for an event that never comes.
   *
   * Recursive setTimeout, not setInterval, so a slow ping can never cause
   * overlapping polls. Only one watcher may be active per page at a time.
   * Cleans up its timer and listener exactly once, on resolution or on
   * pagehide, whichever comes first. Never forces Funding Choices visible,
   * never touches its iframe, never uses getTCData, never writes or
   * manufactures TCF consent state, only reads ping's own displayStatus.
   */
  function watchFundingChoicesUntilClear(banner) {
    if (activeFundingChoicesCleanup) return;

    var resolved = false;
    var timerId = null;
    var listenerId = null;

    function cleanup() {
      if (resolved) return;
      resolved = true;
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
      if (listenerId) {
        try {
          window.__tcfapi('removeEventListener', 2, function () {}, listenerId);
        } catch (error) {
          console.error('Could not remove TCF listener:', error);
        }
        listenerId = null;
      }
      document.removeEventListener('pagehide', cleanup);
      activeFundingChoicesCleanup = null;
    }

    function reveal() {
      if (resolved) return;
      banner.style.display = 'flex';
      cleanup();
    }

    function checkNow() {
      if (resolved) return;
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
      try {
        window.__tcfapi('ping', 2, function (pingReturn) {
          if (resolved) return;
          if (!pingReturn || pingReturn.displayStatus !== 'visible') {
            reveal();
          } else {
            timerId = setTimeout(checkNow, FUNDING_CHOICES_POLL_MS);
          }
        });
      } catch (error) {
        console.error('TCF polling check failed:', error);
        reveal();
      }
    }

    activeFundingChoicesCleanup = cleanup;
    document.addEventListener('pagehide', cleanup);

    try {
      window.__tcfapi('addEventListener', 2, function (tcData, success) {
        if (resolved || !success) return;
        listenerId = tcData && tcData.listenerId;
        checkNow();
      });
    } catch (error) {
      console.error('TCF listener registration failed:', error);
    }

    // Bootstraps the first poll. Guarded rather than unconditional: if the
    // addEventListener callback above already fired synchronously and its
    // own checkNow() already resolved or scheduled a timer, this must not
    // overwrite timerId and orphan that pending timer.
    if (!resolved && !timerId) {
      timerId = setTimeout(checkNow, FUNDING_CHOICES_POLL_MS);
    }
  }

  /**
   * Shows the analytics banner, unless Funding Choices is actively displaying
   * its own TCF UI right now, in which case it waits for that to clear first
   * so the two consent interfaces never stack. Uses only the supported TCF
   * API surface (ping, addEventListener, removeEventListener); getTCData is
   * deprecated and deliberately not used. Never touches Funding Choices'
   * own visibility or state, only reads it.
   *
   * The banner defaults to hidden and is only ever flipped visible from the
   * one branch that decides to show it, synchronously where possible, so it
   * never flashes visible for a frame before being hidden again.
   */
  function initCookieBanner() {
    var banner = document.getElementById('cookieBanner');
    if (!banner) return;

    if (!pageHasAnalytics()) {
      banner.style.display = 'none';
      return;
    }

    var consent = null;
    try {
      consent = localStorage.getItem(COOKIE_CONSENT_KEY);
    } catch (error) {
      console.error('Could not read cookie consent:', error);
    }

    if (consent) {
      banner.style.display = 'none';
      return;
    }

    banner.style.display = 'none';

    var coordinated = false;
    try {
      if (typeof window.__tcfapi === 'function') {
        coordinated = true;
        window.__tcfapi('ping', 2, function (pingReturn) {
          if (pingReturn && pingReturn.displayStatus === 'visible') {
            watchFundingChoicesUntilClear(banner);
          } else {
            banner.style.display = 'flex';
          }
        });
      }
    } catch (error) {
      console.error('TCF coordination check failed:', error);
      coordinated = false;
    }

    if (!coordinated) {
      banner.style.display = 'flex';
    }
  }

  /**
   * Collapses a pathname to a canonical form so "/", "/index.html", and
   * "/foo.html/" all compare equal to their counterparts. Used to match
   * nav link hrefs against the current page regardless of which of these
   * equivalent forms either side happens to be written in.
   */
  function normalizePath(path) {
    path = path.replace(/\/index\.html$/, '/');
    if (path.length > 1 && path.charAt(path.length - 1) === '/') {
      path = path.slice(0, -1);
    }
    return path || '/';
  }

  /**
   * Marks whichever injected nav link points at the current page as
   * active. Works against whatever anchors happen to exist in #site-nav,
   * desktop nav-links and mobile-nav alike, so it isn't tied to Variant
   * A's specific link set and keeps working once other nav variants are
   * added. The CTA link is deliberately skipped, it's an action button,
   * not a "you are here" indicator, on every variant seen so far.
   */
  function applyActiveNavState() {
    var mount = document.getElementById('site-nav');
    if (!mount) return;

    var currentPath = normalizePath(window.location.pathname);
    var links = mount.querySelectorAll('a[href]');

    for (var i = 0; i < links.length; i++) {
      var link = links[i];
      if (link.classList.contains('nav-cta')) continue;

      var linkPath;
      try {
        linkPath = normalizePath(new URL(link.getAttribute('href'), window.location.origin).pathname);
      } catch (error) {
        continue;
      }

      if (linkPath === currentPath) {
        link.classList.add('active');
      }
    }
  }

  /**
   * Optional per-page footer disclaimer. A page opts in by placing
   * <div id="page-disclaimer" data-disclaimer="..."></div> just above
   * its #site-footer mount. If that element isn't present, this is a
   * no-op and the footer renders with no disclaimer, unchanged from
   * today's behavior for every page that doesn't use the slot.
   */
  function applyPageDisclaimer() {
    var source = document.getElementById('page-disclaimer');
    if (!source) return;

    var text = source.getAttribute('data-disclaimer');
    if (!text) return;

    var footer = document.querySelector('#site-footer footer');
    if (!footer) return;

    footer.appendChild(document.createElement('br'));
    footer.appendChild(document.createElement('br'));

    var span = document.createElement('span');
    span.style.fontSize = '11px';
    span.style.color = '#9ca3af';
    span.textContent = text;
    footer.appendChild(span);
  }

  // Expose the handlers the injected markup calls via inline onclick attributes.
  // These must be global because the HTML they're wired to is injected at runtime.
  window.toggleMobileNav = toggleMobileNav;
  window.acceptCookies = acceptCookies;
  window.rejectCookies = rejectCookies;

  document.addEventListener('DOMContentLoaded', function () {
    Promise.all([
      loadPartial(NAV_PARTIAL_URL, 'site-nav', FALLBACK_NAV),
      loadPartial(FOOTER_PARTIAL_URL, 'site-footer', FALLBACK_FOOTER)
    ]).then(function () {
      initCookieBanner();
      applyActiveNavState();
      applyPageDisclaimer();
      document.addEventListener('click', closeMobileNavOnOutsideClick);
    });
  });
})();
