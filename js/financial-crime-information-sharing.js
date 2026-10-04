(function () {
  'use strict';

  var GUIDE_ID = 'financial_crime_information_sharing';

  var sentEvents = {};

  function consentGranted() {
    try {
      return localStorage.getItem('fcr_cookie_consent_v2') === 'accepted';
    } catch (error) {
      return false;
    }
  }

  // Sends at most once per key per page load. Only the guide id and aggregate values are ever sent,
  // never a scenario choice, free text, case, customer, account or payment detail. A send that did not
  // happen (no consent, no analytics, or an analytics error) does not use up the key.
  function emitAggregateEvent(key, name, parameters) {
    if (sentEvents[key]) return;
    if (!consentGranted() || typeof window.gtag !== 'function') return;
    try {
      window.gtag('event', name, parameters);
      sentEvents[key] = true;
    } catch (error) {
      // Analytics failure must never affect the guide.
    }
  }

  var menuButton = document.getElementById('navHamburger');
  var mobileNav = document.getElementById('mobileNav');
  if (menuButton && mobileNav) {
    menuButton.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }

  // Set last, once every handler is attached. Buttons and hidden analyses depend on this class,
  // so a script that fails part way leaves the page in its fully readable no-script state.
  document.documentElement.classList.add('js');
}());
