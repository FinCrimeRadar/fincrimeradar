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

  document.querySelectorAll('[data-decision-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var selected = form.querySelector('input[type="radio"]:checked');
      var feedback = form.querySelector('.fcr-feedback');
      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      form.querySelectorAll('.fcr-option').forEach(function (option) {
        option.removeAttribute('data-selected');
      });
      selected.closest('.fcr-option').setAttribute('data-selected', 'true');

      var grade = selected.dataset.grade || 'ungraded';
      if (grade === 'best') {
        feedback.textContent = 'Reasoned choice recorded. Compare it with the static Source, Application and Action analysis below.';
        feedback.dataset.state = 'best';
      } else {
        feedback.textContent = 'Choice recorded. Test the shortcut against the static Source, Application and Action analysis below.';
        feedback.dataset.state = 'caution';
      }

      emitAggregateEvent('scenario_complete', {
        guide_id: 'app_scam_decision_framework',
        scenario_id: form.dataset.scenarioId,
        decision_grade: grade
      });
    });
  });

  document.querySelectorAll('#practitioner-lens details').forEach(function (detail) {
    detail.addEventListener('toggle', function () {
      if (!detail.open) return;
      var summary = detail.querySelector('summary');
      emitAggregateEvent('practitioner_lens_open', {
        guide_id: 'app_scam_decision_framework',
        lens_id: summary ? summary.textContent.trim().toLowerCase().replace(/[^a-z]+/g, '_').replace(/^_|_$/g, '') : 'unknown'
      });
    });
  });

  var knowledgeForm = document.getElementById('knowledgeForm');
  if (knowledgeForm) {
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
      feedback.textContent = 'Score: ' + score + ' of 5. Review any missed reasoning against the relevant gate and scenario.';
      feedback.dataset.state = score >= 4 ? 'best' : 'caution';

      emitAggregateEvent('knowledge_check_complete', {
        guide_id: 'app_scam_decision_framework',
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

  function drawWrapped(context, text, x, y, maxWidth, lineHeight) {
    var lines = wrapLines(context, text, maxWidth);
    lines.forEach(function (line, index) {
      context.fillText(line, x, y + index * lineHeight);
    });
    return y + lines.length * lineHeight;
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
    var context = document.createElement('canvas').getContext('2d');
    context.font = '26px Arial';
    var measured = patterns.map(function (pattern) {
      var blocks = [
        pattern.querySelector('h3').textContent,
        pattern.querySelector('.fcr-metaphor').textContent
      ];
      pattern.querySelectorAll('.fcr-lines div').forEach(function (line) {
        blocks.push(line.querySelector('dt').textContent + ': ' + line.querySelector('dd').textContent);
      });
      var lineCount = blocks.reduce(function (total, block) {
        return total + wrapLines(context, block, contentWidth - 64).length;
      }, 0);
      return { node: pattern, height: 104 + lineCount * 34 };
    });

    var height = 190 + measured.reduce(function (total, item) {
      return total + item.height + 24;
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
    ctx.fillText('APP Scam Decision Framework', margin, 112);
    ctx.fillStyle = '#c8e5df';
    ctx.font = '22px Arial';
    ctx.fillText('Risk, Signal, Response', margin, 150);

    var y = 184;
    measured.forEach(function (item) {
      var pattern = item.node;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(margin, y, contentWidth, item.height);
      ctx.fillStyle = '#0f766e';
      ctx.fillRect(margin, y, 8, item.height);
      var textX = margin + 32;
      var textY = y + 38;

      ctx.fillStyle = '#071d2b';
      ctx.font = '700 27px Arial';
      textY = drawWrapped(ctx, pattern.querySelector('h3').textContent, textX, textY, contentWidth - 64, 34) + 6;
      ctx.fillStyle = '#48616b';
      ctx.font = '20px Arial';
      textY = drawWrapped(ctx, pattern.querySelector('.fcr-metaphor').textContent, textX, textY, contentWidth - 64, 28) + 10;

      pattern.querySelectorAll('.fcr-lines div').forEach(function (line) {
        ctx.fillStyle = '#0f5e57';
        ctx.font = '700 19px Arial';
        var label = line.querySelector('dt').textContent + ':';
        ctx.fillText(label, textX, textY);
        var labelWidth = ctx.measureText(label + ' ').width;
        ctx.fillStyle = '#203842';
        ctx.font = '19px Arial';
        textY = drawWrapped(ctx, line.querySelector('dd').textContent, textX + labelWidth, textY, contentWidth - 64 - labelWidth, 27) + 8;
      });
      y += item.height + 24;
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
      link.download = 'app-scam-decision-framework-summary.png';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      status.textContent = 'Summary image created.';
      emitAggregateEvent('card_export', {
        guide_id: 'app_scam_decision_framework',
        export_type: 'closing_patterns'
      });
    }, 'image/png');
  }

  var saveButton = document.getElementById('saveFrameworkImage');
  if (saveButton) saveButton.addEventListener('click', exportClosingPatterns);
}());
