(function () {
  'use strict';

  var GUIDE_ID = 'e_commerce_fraud_system_guide';
  var QUIZ_KEY = { 1: 'B', 2: 'C', 3: 'A', 4: 'B', 5: 'C' };
  var GRADE_LABEL = { weak: 'weak', caution: 'caution', strongest: 'strongest' };

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

  function markSelected(form, selector, selected) {
    form.querySelectorAll(selector).forEach(function (option) {
      option.removeAttribute('data-selected');
    });
    if (selected) selected.closest('.ecf-option').setAttribute('data-selected', 'true');
  }

  var scenarioState = {};

  document.querySelectorAll('[data-scenario-form]').forEach(function (form) {
    var scenarioId = form.dataset.scenarioId;
    var article = form.closest('.ecf-scenario');
    var feedback = form.querySelector('.ecf-feedback');
    var confidenceSet = form.querySelector('.ecf-confidence-set');
    var reasoning = article.querySelector('.ecf-reasoning');
    var original = article.querySelector('.ecf-original');
    var reconsider = article.querySelector('[data-cf-form]');

    confidenceSet.hidden = true;

    form.querySelectorAll('input[type="radio"]').forEach(function (input) {
      input.addEventListener('change', function () {
        if (input.name.indexOf('-choice') !== -1) {
          markSelected(form, '.ecf-choice-set .ecf-option', input);
          confidenceSet.hidden = false;
        } else {
          markSelected(form, '.ecf-confidence-set .ecf-option', input);
        }
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (scenarioState[scenarioId]) return;
      var choice = form.querySelector('.ecf-choice-set input:checked');
      var confidence = form.querySelector('.ecf-confidence-set input:checked');

      if (!choice) {
        feedback.textContent = 'Choose one of the three options before recording your decision.';
        feedback.dataset.state = 'caution';
        return;
      }
      if (!confidence) {
        confidenceSet.hidden = false;
        feedback.textContent = 'Choose High, Medium or Low confidence before the reasoning is shown.';
        feedback.dataset.state = 'caution';
        return;
      }

      var grade = choice.dataset.grade;
      var letter = choice.value;
      var band = confidence.value.toLowerCase();
      scenarioState[scenarioId] = { letter: letter, grade: grade, band: band };

      form.querySelectorAll('fieldset').forEach(function (set) { set.disabled = true; });
      var submit = form.querySelector('button[type="submit"]');
      if (submit) submit.disabled = true;

      feedback.dataset.state = grade === 'strongest' ? 'strongest' : grade;
      feedback.textContent = 'Decision recorded: option ' + letter + ', graded ' + GRADE_LABEL[grade] + ', with ' + band +
        ' confidence. The Source, Application and Action reasoning is open below.';

      article.querySelectorAll('.ecf-grades li').forEach(function (item) {
        if (item.dataset.letter === letter) item.setAttribute('data-selected', 'true');
      });
      original.textContent = 'Your original answer: option ' + letter + ', graded ' + GRADE_LABEL[grade] + ', ' + band + ' confidence.';
      original.hidden = false;
      reasoning.open = true;
      if (reconsider) reconsider.hidden = false;

      emitAggregateEvent('scenario_complete', {
        guide_id: GUIDE_ID,
        scenario_id: scenarioId,
        decision_grade: grade,
        confidence_band: band
      });
    });
  });

  document.querySelectorAll('[data-cf-form]').forEach(function (form) {
    var scenarioId = form.dataset.scenarioId;
    var status = form.querySelector('.ecf-cf-status');
    var counterfactual = form.closest('.ecf-reasoning').querySelector('.ecf-counterfactual');
    var done = false;

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (done) return;
      var answer = form.querySelector('input:checked');
      var state = scenarioState[scenarioId];
      if (!answer) {
        status.textContent = 'Choose whether you would reconsider with the changed fact before recording.';
        return;
      }
      if (!state) {
        status.textContent = 'Record your decision above first.';
        return;
      }
      done = true;
      var reconsidered = answer.value === 'yes';
      var changed = counterfactual.textContent.replace(/^\s*Counterfactual:\s*/, '');
      status.textContent = 'Your original answer is kept: option ' + state.letter + ', graded ' + GRADE_LABEL[state.grade] + '. You ' +
        (reconsidered ? 'would reconsider' : 'would keep your decision') + ' with the changed fact. What changed: ' + changed;
      form.querySelectorAll('fieldset').forEach(function (set) { set.disabled = true; });
      var submit = form.querySelector('button[type="submit"]');
      if (submit) submit.disabled = true;

      emitAggregateEvent('counterfactual_complete', {
        guide_id: GUIDE_ID,
        scenario_id: scenarioId,
        reconsidered: reconsidered
      });
    });
  });

  var knowledgeForm = document.getElementById('ecf-kc-form');
  if (knowledgeForm) {
    knowledgeForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var feedback = document.getElementById('ecf-kc-feedback');
      var missing = [];
      var score = 0;
      for (var number = 1; number <= 5; number += 1) {
        var picked = knowledgeForm.querySelector('input[name="ecf-q' + number + '"]:checked');
        if (!picked) missing.push(number);
        else if (picked.value === QUIZ_KEY[number]) score += 1;
      }

      if (missing.length) {
        feedback.textContent = 'Answer all five questions before scoring. Still to answer: ' + missing.join(', ') + '.';
        feedback.dataset.state = 'caution';
        return;
      }

      feedback.textContent = 'Score: ' + score + ' of 5. ' + (score === 5
        ? 'You kept each conclusion at its own decision level.'
        : 'Review the relay fields and the two worked decisions in the answer key below.');
      feedback.dataset.state = score >= 4 ? 'strongest' : 'caution';
      var answers = document.getElementById('ecf-kc-answers');
      if (answers) answers.open = true;

      emitAggregateEvent('knowledge_check_complete', {
        guide_id: GUIDE_ID,
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

  function drawWrapped(context, text, x, y, maxWidth, lineHeight, draw) {
    var lines = wrapLines(context, text, maxWidth);
    if (draw) {
      lines.forEach(function (line, index) {
        context.fillText(line, x, y + index * lineHeight);
      });
    }
    return y + lines.length * lineHeight;
  }

  // One pass lays the card out (draw false) or paints it (draw true), so the canvas height follows the text.
  function layoutCard(context, pattern, x, y, cardWidth, draw, cardHeight) {
    var textX = x + 28;
    var textWidth = cardWidth - 56;
    var textY = y + 42;
    if (draw) {
      context.fillStyle = '#ffffff';
      context.fillRect(x, y, cardWidth, cardHeight);
      context.fillStyle = '#0f766e';
      context.fillRect(x, y, 8, cardHeight);
    }
    context.fillStyle = '#071d2b';
    context.font = '700 26px Georgia';
    textY = drawWrapped(context, pattern.querySelector('h3').textContent, textX, textY, textWidth, 31, draw) + 8;
    context.fillStyle = '#48616b';
    context.font = '18px Arial';
    textY = drawWrapped(context, pattern.querySelector('.ecf-pattern-line').textContent, textX, textY, textWidth, 24, draw) + 10;
    pattern.querySelectorAll('.ecf-pattern-lines div').forEach(function (line) {
      var label = line.querySelector('dt').textContent + ':';
      context.fillStyle = '#0f5e57';
      context.font = '700 17px Arial';
      if (draw) context.fillText(label, textX, textY);
      var labelWidth = context.measureText(label + ' ').width;
      context.fillStyle = '#203842';
      context.font = '17px Arial';
      textY = drawWrapped(context, line.querySelector('dd').textContent, textX + labelWidth, textY, textWidth - labelWidth, 22, draw) + 8;
    });
    return textY - y + 14;
  }

  function exportPatterns() {
    var status = document.getElementById('ecf-export-status');
    var source = document.getElementById('ecf-closing-patterns-grid');
    var patterns = source ? Array.from(source.querySelectorAll('.ecf-pattern')) : [];
    if (!status || !patterns.length) return;

    try {
      var width = 1200;
      var cardWidth = 520;
      var canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = 400;
      var context = canvas.getContext('2d');
      if (!context) {
        status.textContent = 'Export unavailable.';
        return;
      }

      var heights = patterns.map(function (pattern) {
        return layoutCard(context, pattern, 0, 0, cardWidth, false, 0);
      });
      var rowHeights = [];
      patterns.forEach(function (pattern, index) {
        var row = Math.floor(index / 2);
        rowHeights[row] = Math.max(rowHeights[row] || 0, heights[index]);
      });
      var gridTop = 190;
      var gap = 28;
      var gridHeight = rowHeights.reduce(function (sum, value) { return sum + value + gap; }, 0);
      var height = gridTop + gridHeight + 60;
      canvas.width = width;
      canvas.height = height;
      context = canvas.getContext('2d');

      context.fillStyle = '#071d2b';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#99f6e4';
      context.font = '700 22px Arial';
      context.fillText('FINCRIMERADAR | GUIDE', 64, 54);
      context.fillStyle = '#ffffff';
      context.font = '700 42px Georgia';
      context.fillText('E-commerce fraud control patterns', 64, 108);
      context.fillStyle = '#c8e5df';
      context.font = '22px Arial';
      context.fillText('Risk, Signal, Response', 64, 148);

      var rowTop = [];
      var cursor = gridTop;
      rowHeights.forEach(function (value, row) {
        rowTop[row] = cursor;
        cursor += value + gap;
      });
      patterns.forEach(function (pattern, index) {
        var row = Math.floor(index / 2);
        var x = 64 + (index % 2) * 548;
        layoutCard(context, pattern, x, rowTop[row], cardWidth, true, rowHeights[row]);
      });

      context.fillStyle = '#99f6e4';
      context.font = '18px Arial';
      context.fillText('fincrimeradar.org', 64, height - 30);

      canvas.toBlob(function (blob) {
        if (!blob) {
          status.textContent = 'Export unavailable.';
          return;
        }
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'e-commerce-fraud-control-patterns.png';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        status.textContent = 'Summary image created.';
        emitAggregateEvent('card_export', {
          guide_id: GUIDE_ID,
          export_type: 'closing_patterns'
        });
      }, 'image/png');
    } catch (error) {
      status.textContent = 'Export unavailable.';
    }
  }

  var saveButton = document.getElementById('ecf-export-button');
  if (saveButton) saveButton.addEventListener('click', exportPatterns);
}());
