(function () {
  'use strict';

  var GUIDE_ID = 'de_risking_judgement_call';

  // Buttons and the hidden option analyses depend on this class. Without the script the
  // buttons stay hidden and every analysis stays visible.
  document.documentElement.classList.add('js');

  var sentEvents = {};

  function consentGranted() {
    try {
      return localStorage.getItem('fcr_cookie_consent_v2') === 'accepted';
    } catch (error) {
      return false;
    }
  }

  // Sends at most once per key per page load. A send that did not happen (no consent,
  // no analytics, or an analytics error) does not use up the key.
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

  function clearDecision(form) {
    var feedback = form.querySelector('.fcr-feedback');
    if (feedback) {
      feedback.textContent = '';
      feedback.removeAttribute('data-state');
    }
    form.querySelectorAll('.fcr-option').forEach(function (option) {
      option.removeAttribute('data-selected');
    });
    var scope = form.closest('.fcr-section');
    if (scope) {
      scope.querySelectorAll('.fcr-optfb').forEach(function (block) {
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
      var feedback = form.querySelector('.fcr-feedback');
      var scenarioId = form.dataset.scenarioId;
      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      clearDecision(form);
      selected.closest('.fcr-option').setAttribute('data-selected', 'true');

      var target = null;
      var scope = form.closest('.fcr-section');
      if (scope) {
        scope.querySelectorAll('.fcr-optfb-set').forEach(function (set) {
          set.setAttribute('data-revealed', 'true');
        });
        scope.querySelectorAll('.fcr-optfb').forEach(function (block) {
          if (block.dataset.option === selected.value) {
            block.setAttribute('data-selected', 'true');
            block.setAttribute('tabindex', '-1');
            target = block;
          }
        });
      }

      var grade = selected.dataset.grade || 'ungraded';
      var label = selected.dataset.gradeLabel || '';
      feedback.textContent = 'Recorded: ' + label + '. ';
      if (target && target.id) {
        var link = document.createElement('a');
        link.href = '#' + target.id;
        link.textContent = 'Read the analysis of your choice';
        feedback.appendChild(link);
      }
      feedback.dataset.state = grade;

      emitAggregateEvent('scenario:' + scenarioId, 'scenario_complete', {
        guide_id: GUIDE_ID,
        scenario_id: scenarioId,
        decision_grade: grade
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
      feedback.textContent = 'Score: ' + score + ' of 5. The answer notes below the questions set out the Source, Application and Recommendation for each.';
      feedback.dataset.state = score >= 4 ? 'best' : 'caution';

      emitAggregateEvent('knowledge', 'knowledge_check_complete', {
        guide_id: GUIDE_ID,
        score: score,
        total: 5
      });
    });
  }

  // Card layout. The same routine measures and paints, so the card height always matches
  // the fonts and line heights actually drawn.
  var CARD_TEXT_WIDTH_INSET = 64;

  function wrapLines(context, text, maxWidth) {
    var words = text.trim().split(/\s+/);
    var lines = [];
    var current = '';
    words.forEach(function (word) {
      var trial = current ? current + ' ' + word : word;
      if (context.measureText(trial).width > maxWidth && current) {
        lines.push(current);
        current = word;
      } else {
        current = trial;
      }
    });
    if (current) lines.push(current);
    return lines;
  }

  function drawWrapped(context, text, x, y, maxWidth, lineHeight, paint) {
    var lines = wrapLines(context, text, maxWidth);
    if (paint) {
      lines.forEach(function (line, index) {
        context.fillText(line, x, y + index * lineHeight);
      });
    }
    return y + lines.length * lineHeight;
  }

  function flowCard(context, pattern, textX, top, contentWidth, paint) {
    var textWidth = contentWidth - CARD_TEXT_WIDTH_INSET;
    var textY = top + 38;

    if (paint) context.fillStyle = '#071d2b';
    context.font = '700 27px Arial';
    textY = drawWrapped(context, pattern.querySelector('h3').textContent, textX, textY, textWidth, 34, paint) + 6;

    if (paint) context.fillStyle = '#48616b';
    context.font = '20px Arial';
    textY = drawWrapped(context, pattern.querySelector('.fcr-metaphor').textContent, textX, textY, textWidth, 28, paint) + 10;

    pattern.querySelectorAll('.fcr-lines div').forEach(function (line) {
      var label = line.querySelector('dt').textContent + ':';
      context.font = '700 19px Arial';
      var labelWidth = context.measureText(label + ' ').width;
      if (paint) {
        context.fillStyle = '#0f5e57';
        context.fillText(label, textX, textY);
        context.fillStyle = '#203842';
      }
      context.font = '19px Arial';
      textY = drawWrapped(context, line.querySelector('dd').textContent, textX + labelWidth, textY, textWidth - labelWidth, 27, paint) + 8;
    });
    return textY;
  }

  function exportClosingPatterns() {
    var status = document.getElementById('saveFrameworkStatus');
    var source = document.getElementById('fcrClosingPatterns');
    var patterns = source ? Array.from(source.querySelectorAll('.fcr-pattern')) : [];
    if (!patterns.length) {
      status.textContent = 'Export unavailable.';
      return;
    }

    var width = 1200;
    var margin = 72;
    var contentWidth = width - margin * 2;
    var textX = margin + 32;
    var measure = document.createElement('canvas').getContext('2d');
    var cards = patterns.map(function (pattern) {
      // The last line ends 8px above the returned position and the line height is 27px,
      // so this leaves 26px below the final baseline.
      return { node: pattern, height: flowCard(measure, pattern, textX, 0, contentWidth, false) - 9 };
    });

    var height = 184 + cards.reduce(function (total, card) {
      return total + card.height + 24;
    }, 0) + 72;
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');

    ctx.fillStyle = '#071d2b';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#99f6e4';
    ctx.font = '700 22px Arial';
    ctx.fillText('FINCRIMERADAR · FRAMEWORK', margin, 58);
    ctx.fillStyle = '#ffffff';
    ctx.font = '700 42px Georgia';
    ctx.fillText('The De-Risking Judgement Call', margin, 112);
    ctx.fillStyle = '#c8e5df';
    ctx.font = '22px Arial';
    ctx.fillText('Risk, Signal, Response', margin, 150);

    var y = 184;
    cards.forEach(function (card) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(margin, y, contentWidth, card.height);
      ctx.fillStyle = '#0f766e';
      ctx.fillRect(margin, y, 8, card.height);
      flowCard(ctx, card.node, textX, y, contentWidth, true);
      y += card.height + 24;
    });

    ctx.fillStyle = '#99f6e4';
    ctx.font = '18px Arial';
    ctx.fillText('fincrimeradar.org', margin, height - 34);

    canvas.toBlob(function (blob) {
      if (!blob) {
        status.textContent = 'Export unavailable.';
        return;
      }
      var url = URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = url;
      link.download = 'de-risking-judgement-call-summary.png';
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Some browsers start the download asynchronously, so keep the URL alive briefly.
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      status.textContent = 'Summary image created.';
      emitAggregateEvent('export', 'card_export', {
        guide_id: GUIDE_ID,
        export_type: 'closing_patterns'
      });
    }, 'image/png');
  }

  var saveButton = document.getElementById('saveFrameworkImage');
  if (saveButton) saveButton.addEventListener('click', exportClosingPatterns);
}());
