(function () {
  'use strict';

  var GUIDE_ID = 'investment_scam_investigation_handbook';

  var sentEvents = {};

  function consentGranted() {
    try {
      return localStorage.getItem('fcr_cookie_consent_v2') === 'accepted';
    } catch (error) {
      return false;
    }
  }

  // Sends at most once per key per page load. Only the guide id and aggregate counts are ever sent,
  // never a scenario choice, free text, case, customer, payment or wallet detail. A send that did not
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

  // Grades this guide defines. Anything else is ignored for the state attribute.
  var KNOWN_GRADES = ['best', 'incomplete', 'unsupported'];

  function clearDecision(form) {
    var feedback = form.querySelector('.isi-feedback');
    if (feedback) {
      feedback.textContent = '';
      feedback.removeAttribute('data-state');
    }
    form.querySelectorAll('.isi-option').forEach(function (option) {
      option.removeAttribute('data-selected');
    });
    var scope = form.closest('.isi-section');
    if (scope) {
      scope.querySelectorAll('.isi-optfb').forEach(function (block) {
        block.removeAttribute('data-selected');
      });
    }
  }

  document.querySelectorAll('[data-decision-form]').forEach(function (form) {
    form.addEventListener('change', function () {
      clearDecision(form);
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var selected = form.querySelector('input[type="radio"]:checked');
      var feedback = form.querySelector('.isi-feedback');
      var scenarioId = form.dataset.scenarioId;
      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      clearDecision(form);
      selected.closest('.isi-option').setAttribute('data-selected', 'true');

      var target = null;
      var scope = form.closest('.isi-section');
      if (scope) {
        scope.querySelectorAll('.isi-optfb-set').forEach(function (set) {
          set.setAttribute('data-revealed', 'true');
        });
        scope.querySelectorAll('.isi-optfb').forEach(function (block) {
          if (block.dataset.option === selected.value) {
            block.setAttribute('data-selected', 'true');
            block.setAttribute('tabindex', '-1');
            target = block;
          }
        });
      }

      var grade = KNOWN_GRADES.indexOf(selected.dataset.grade) !== -1 ? selected.dataset.grade : null;
      feedback.textContent = 'Recorded: ' + (selected.dataset.gradeLabel || '') + '. ';
      if (target && target.id) {
        var link = document.createElement('a');
        link.href = '#' + target.id;
        link.textContent = 'Read the analysis of your choice';
        feedback.appendChild(link);
      }
      if (grade) feedback.dataset.state = grade;
      // Completion only. The option chosen and its grade are never sent.
      emitAggregateEvent('scenario:' + scenarioId, 'scenario_complete', {
        guide_id: GUIDE_ID,
        scenario_id: scenarioId
      });
    });
  });

  // Set last, once every handler is attached. Buttons and hidden analyses depend on this class,
  // so a script that fails part way leaves the page in its fully readable no-script state.
  document.documentElement.classList.add('js');
}());
