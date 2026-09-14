(function () {
  'use strict';

  function consentGranted() {
    try {
      return localStorage.getItem('fcr_cookie_consent_v2') === 'accepted';
    } catch (error) {
      return false;
    }
  }

  function emitAggregateEvent(name, parameters) {
    if (!consentGranted() || typeof window.gtag !== 'function') return;
    window.gtag('event', name, parameters);
  }

  var menuButton = document.getElementById('navHamburger');
  var mobileNav = document.getElementById('mobileNav');
  if (menuButton && mobileNav) {
    menuButton.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }

  document.querySelectorAll('[data-scenario-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var selected = form.querySelector('input[type="radio"]:checked');
      var feedback = form.querySelector('.r16-feedback');
      var reasoning = form.closest('.r16-scenario').querySelector('.r16-reasoning');

      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      form.querySelectorAll('.r16-option').forEach(function (option) {
        option.removeAttribute('data-selected');
      });
      selected.closest('.r16-option').setAttribute('data-selected', 'true');

      var grade = selected.dataset.grade || 'weak';
      if (grade === 'best') {
        feedback.textContent = 'Strongest option. The Source, Application and Action reasoning is open below.';
      } else if (grade === 'caution') {
        feedback.textContent = 'Incomplete approach. Test it against the Source, Application and Action reasoning below.';
      } else {
        feedback.textContent = 'High-risk shortcut. Test it against the Source, Application and Action reasoning below.';
      }
      feedback.dataset.state = grade;
      reasoning.open = true;

      emitAggregateEvent('scenario_complete', {
        guide_id: 'fatf_recommendation_16_intelligence_brief',
        scenario_id: form.dataset.scenarioId,
        decision_grade: grade
      });
    });
  });

  var knowledgeForm = document.getElementById('r16KnowledgeForm');
  if (knowledgeForm) {
    knowledgeForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var groups = ['q1', 'q2', 'q3', 'q4', 'q5'];
      var selected = groups.map(function (name) {
        return knowledgeForm.querySelector('input[name="' + name + '"]:checked');
      });
      var feedback = document.getElementById('r16KnowledgeFeedback');

      if (selected.some(function (answer) { return !answer; })) {
        feedback.textContent = 'Answer all five questions before scoring.';
        feedback.dataset.state = 'caution';
        return;
      }

      var score = selected.filter(function (answer) {
        return answer.dataset.correct === 'true';
      }).length;
      feedback.textContent = 'Score: ' + score + ' of 5. ' + (score === 5 ? 'You can distinguish the adopted standard from the implementation choices.' : 'Review the scenarios and evidence states before trying again.');
      feedback.dataset.state = score >= 4 ? 'best' : 'caution';

      emitAggregateEvent('knowledge_check_complete', {
        guide_id: 'fatf_recommendation_16_intelligence_brief',
        score: score,
        total: 5
      });
    });
  }

  function wrapLines(context, text, maxWidth) {
    var words = text.trim().split(/\s+/);
    var lines = [];
    var current = '';
    words.forEach(function (word) {
      var trial = current ? current + ' ' + word : word;
      if (current && context.measureText(trial).width > maxWidth) {
        lines.push(current);
        current = word;
      } else {
        current = trial;
      }
    });
    if (current) lines.push(current);
    return lines;
  }

  function drawWrapped(context, text, x, y, maxWidth, lineHeight) {
    var lines = wrapLines(context, text, maxWidth);
    lines.forEach(function (line, index) {
      context.fillText(line, x, y + index * lineHeight);
    });
    return y + lines.length * lineHeight;
  }

  function exportPatterns() {
    var status = document.getElementById('saveR16Status');
    var source = document.getElementById('r16ClosingPatterns');
    var patterns = source ? Array.from(source.querySelectorAll('.r16-pattern')) : [];
    if (!status || !patterns.length) return;

    try {
      var width = 1200;
      var height = 1510;
      var canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      var context = canvas.getContext('2d');
      if (!context) {
        status.textContent = 'Export unavailable.';
        return;
      }

      context.fillStyle = '#071d2b';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#99f6e4';
      context.font = '700 22px Arial';
      context.fillText('FINCRIMERADAR | INTELLIGENCE BRIEF', 64, 54);
      context.fillStyle = '#ffffff';
      context.font = '700 42px Georgia';
      context.fillText('Recommendation 16 readiness patterns', 64, 108);
      context.fillStyle = '#c8e5df';
      context.font = '22px Arial';
      context.fillText('Risk, Signal, Response', 64, 148);

      patterns.forEach(function (pattern, index) {
        var column = index % 2;
        var row = Math.floor(index / 2);
        var x = 64 + column * 548;
        var y = 190 + row * 400;
        var cardWidth = 520;
        var cardHeight = 372;
        var textX = x + 28;
        var textWidth = cardWidth - 56;

        context.fillStyle = '#ffffff';
        context.fillRect(x, y, cardWidth, cardHeight);
        context.fillStyle = '#0f766e';
        context.fillRect(x, y, 8, cardHeight);

        var textY = y + 42;
        context.fillStyle = '#071d2b';
        context.font = '700 26px Georgia';
        textY = drawWrapped(context, pattern.querySelector('h3').textContent, textX, textY, textWidth, 31) + 8;
        context.fillStyle = '#48616b';
        context.font = '18px Arial';
        textY = drawWrapped(context, pattern.querySelector('.r16-metaphor').textContent, textX, textY, textWidth, 24) + 10;

        pattern.querySelectorAll('.r16-pattern-lines div').forEach(function (line) {
          context.fillStyle = '#0f5e57';
          context.font = '700 17px Arial';
          var label = line.querySelector('dt').textContent + ':';
          context.fillText(label, textX, textY);
          var labelWidth = context.measureText(label + ' ').width;
          context.fillStyle = '#203842';
          context.font = '17px Arial';
          textY = drawWrapped(context, line.querySelector('dd').textContent, textX + labelWidth, textY, textWidth - labelWidth, 22) + 8;
        });
      });

      context.fillStyle = '#99f6e4';
      context.font = '18px Arial';
      context.fillText('fincrimeradar.org', 64, height - 34);

      canvas.toBlob(function (blob) {
        if (!blob) {
          status.textContent = 'Export unavailable.';
          return;
        }
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'fatf-recommendation-16-readiness-patterns.png';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        status.textContent = 'Summary image created.';
        emitAggregateEvent('card_export', {
          guide_id: 'fatf_recommendation_16_intelligence_brief',
          export_type: 'closing_patterns'
        });
      }, 'image/png');
    } catch (error) {
      status.textContent = 'Export unavailable.';
    }
  }

  var saveButton = document.getElementById('saveR16Patterns');
  if (saveButton) saveButton.addEventListener('click', exportPatterns);
}());
