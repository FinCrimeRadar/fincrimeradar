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

  document.querySelectorAll('[data-scenario-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var selected = form.querySelector('input[type="radio"]:checked');
      var feedback = form.querySelector('.ftpf-feedback');
      var reasoning = form.parentElement.querySelector('.ftpf-reasoning');

      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      form.querySelectorAll('.ftpf-option').forEach(function (option) {
        option.removeAttribute('data-selected');
      });
      selected.closest('.ftpf-option').setAttribute('data-selected', 'true');

      var grade = selected.dataset.grade || 'weak';
      if (grade === 'best') {
        feedback.textContent = 'Strongest option. The Source, Application and Action reasoning is open below.';
      } else if (grade === 'caution') {
        feedback.textContent = 'Incomplete approach. Test it against the Source, Application and Action reasoning below.';
      } else {
        feedback.textContent = 'High-risk shortcut. Test it against the Source, Application and Action reasoning below.';
      }
      feedback.dataset.state = grade;
      if (reasoning) reasoning.open = true;

      emitAggregateEvent('scenario_complete', {
        guide_id: 'failure_to_prevent_fraud_evidence_essay',
        scenario_id: form.dataset.scenarioId,
        decision_grade: grade
      });
    });
  });

  document.querySelectorAll('[data-counterfactual]').forEach(function (details) {
    details.addEventListener('toggle', function () {
      if (!details.open || details.dataset.recorded) return;
      details.dataset.recorded = 'true';
      emitAggregateEvent('counterfactual_complete', {
        guide_id: 'failure_to_prevent_fraud_evidence_essay',
        scenario_id: details.dataset.scenarioId
      });
    });
  });

  var knowledgeForm = document.getElementById('ftpfKnowledgeForm');
  if (knowledgeForm) {
    knowledgeForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var groups = ['ftpf-q1', 'ftpf-q2', 'ftpf-q3', 'ftpf-q4', 'ftpf-q5'];
      var selected = groups.map(function (name) {
        return knowledgeForm.querySelector('input[name="' + name + '"]:checked');
      });
      var feedback = document.getElementById('ftpfKnowledgeFeedback');

      if (selected.some(function (answer) { return !answer; })) {
        feedback.textContent = 'Answer all five questions before scoring.';
        feedback.dataset.state = 'caution';
        return;
      }

      var score = selected.filter(function (answer) {
        return answer.dataset.correct === 'true';
      }).length;
      feedback.textContent = 'Score: ' + score + ' of 5. ' + (score === 5 ? 'You can distinguish the statutory conditions from FinCrimeRadar\'s own analysis.' : 'Review the worked decisions and the statutory context before trying again.');
      feedback.dataset.state = score >= 4 ? 'best' : 'caution';

      emitAggregateEvent('knowledge_check_complete', {
        guide_id: 'failure_to_prevent_fraud_evidence_essay',
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
    var status = document.getElementById('ftpfSaveStatus');
    var source = document.getElementById('ftpfClosingPatterns');
    var patterns = source ? Array.from(source.querySelectorAll('.ftpf-pattern')) : [];
    if (!status || !patterns.length) return;

    try {
      var width = 1200;
      var height = 1750;
      var canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      var context = canvas.getContext('2d');
      if (!context) {
        status.textContent = 'Export unavailable.';
        return;
      }

      context.fillStyle = '#071912';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#f3ecd9';
      context.font = '700 22px Arial';
      context.fillText('FINCRIMERADAR | EVIDENCE ESSAY', 64, 54);
      context.fillStyle = '#ffffff';
      context.font = '700 38px Georgia';
      drawWrapped(context, 'Failure to Prevent Fraud: six failure patterns', 64, 108, width - 128, 44);
      context.fillStyle = '#dbe4e0';
      context.font = '22px Arial';
      context.fillText('Risk, Signal, Response', 64, 170);

      patterns.forEach(function (pattern, index) {
        var column = index % 2;
        var row = Math.floor(index / 2);
        var x = 64 + column * 548;
        var y = 210 + row * 500;
        var cardWidth = 520;
        var cardHeight = 470;
        var textX = x + 28;
        var textWidth = cardWidth - 56;

        context.fillStyle = '#ffffff';
        context.fillRect(x, y, cardWidth, cardHeight);
        context.fillStyle = '#0f766e';
        context.fillRect(x, y, 8, cardHeight);

        var textY = y + 42;
        context.fillStyle = '#071912';
        context.font = '700 24px Georgia';
        textY = drawWrapped(context, pattern.querySelector('h3').textContent, textX, textY, textWidth, 29) + 8;
        context.fillStyle = '#5f6c66';
        context.font = '17px Arial';
        textY = drawWrapped(context, pattern.querySelector('.ftpf-metaphor').textContent, textX, textY, textWidth, 22) + 12;

        pattern.querySelectorAll('.ftpf-pattern-lines div').forEach(function (line) {
          context.fillStyle = '#0b695d';
          context.font = '700 16px Arial';
          var label = line.querySelector('dt').textContent + ':';
          context.fillText(label, textX, textY);
          var labelWidth = context.measureText(label + ' ').width;
          context.fillStyle = '#17231e';
          context.font = '16px Arial';
          textY = drawWrapped(context, line.querySelector('dd').textContent, textX + labelWidth, textY, textWidth - labelWidth, 21) + 14;
        });
      });

      context.fillStyle = '#f3ecd9';
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
        link.download = 'failure-to-prevent-fraud-evidence-essay-patterns.png';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        status.textContent = 'Summary image created.';
        emitAggregateEvent('card_export', {
          guide_id: 'failure_to_prevent_fraud_evidence_essay',
          export_type: 'closing_patterns'
        });
      }, 'image/png');
    } catch (error) {
      status.textContent = 'Export unavailable.';
    }
  }

  var saveButton = document.getElementById('ftpfSavePatterns');
  if (saveButton) saveButton.addEventListener('click', exportPatterns);
}());
