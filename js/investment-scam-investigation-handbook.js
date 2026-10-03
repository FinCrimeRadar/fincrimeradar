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

  var knowledgeForm = document.getElementById('knowledgeForm');
  if (knowledgeForm) {
    knowledgeForm.addEventListener('change', function () {
      var feedback = document.getElementById('knowledgeFeedback');
      feedback.textContent = '';
      feedback.removeAttribute('data-state');
    });

    knowledgeForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var groups = ['q1', 'q2', 'q3', 'q4', 'q5'];
      var selected = groups.map(function (name) {
        return knowledgeForm.querySelector('input[name="' + name + '"]:checked');
      });
      var feedback = document.getElementById('knowledgeFeedback');

      if (selected.some(function (answer) { return !answer; })) {
        feedback.textContent = 'Answer all five questions before scoring.';
        feedback.dataset.state = 'caution';
        return;
      }

      var score = selected.filter(function (answer) {
        return answer.dataset.correct === 'true';
      }).length;
      feedback.textContent = 'Score: ' + score + ' of 5. The answer notes below the questions set out the Source, Application and Action for each.';
      feedback.dataset.state = score >= 4 ? 'best' : 'caution';

      // Aggregate score only. Individual answers are never sent.
      emitAggregateEvent('knowledge', 'knowledge_check_complete', {
        guide_id: GUIDE_ID,
        score: score,
        total: 5
      });
    });
  }

  // Set last, once every handler is attached. Buttons and hidden analyses depend on this class,
  // so a script that fails part way leaves the page in its fully readable no-script state.
  document.documentElement.classList.add('js');
}());
