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

  var SOURCES = {
    '1': {
      claim: 'Section 199 creates the failure to prevent fraud offence, its associated-person and intended-benefit conditions, the section 199(3) victim exclusion, the section 199(2) subsidiary route and the section 199(4) reasonable-procedures defence.',
      title: 'Economic Crime and Corporate Transparency Act 2023, section 199',
      publisher: 'legislation.gov.uk (UK National Archives)',
      date: 'Current text as enacted',
      verified: '16 September 2026',
      url: 'https://www.legislation.gov.uk/ukpga/2023/56/section/199',
      limit: 'Read together with sections 200 to 202 and Schedule 13, which supply the defined terms this section relies on.'
    },
    '2': {
      claim: 'Schedule 13 lists the base fraud offences, including offences under the Fraud Act 2006, the Theft Act 1968 and section 993 of the Companies Act 2006.',
      title: 'Economic Crime and Corporate Transparency Act 2023, Schedule 13',
      publisher: 'legislation.gov.uk (UK National Archives)',
      date: 'Current text as enacted',
      verified: '16 September 2026',
      url: 'https://www.legislation.gov.uk/ukpga/2023/56/schedule/13',
      limit: 'Only the offences Schedule 13 actually lists qualify as the base offence, not every fraud-related offence in English law.'
    },
    '3': {
      claim: 'A relevant body is a large organisation if it met at least two of three thresholds (turnover, balance sheet total, employee count) in the preceding financial year.',
      title: 'Economic Crime and Corporate Transparency Act 2023, section 201',
      publisher: 'legislation.gov.uk (UK National Archives)',
      date: 'Current text as enacted',
      verified: '16 September 2026',
      url: 'https://www.legislation.gov.uk/ukpga/2023/56/section/201',
      limit: 'Does not itself cover a group structure. See source 8 for the separate group-aggregation rule in section 202.'
    },
    '4': {
      claim: 'The Home Office guidance sets out six principles, disclaims safe-harbour status, places the burden of proof on the organisation on the balance of probabilities, and warns that controls built for a different risk may not be adequate for fraud prevention.',
      title: 'Economic Crime and Corporate Transparency Act 2023: guidance to organisations on the offence of failure to prevent fraud (accessible version)',
      publisher: 'Home Office',
      date: 'Updated 10 October 2025',
      verified: '16 September 2026',
      url: 'https://www.gov.uk/government/publications/offence-of-failure-to-prevent-fraud-introduced-by-eccta/economic-crime-and-corporate-transparency-act-2023-guidance-to-organisations-on-the-offence-of-failure-to-prevent-fraud-accessible-version',
      limit: 'Statutory guidance, not binding law. The guidance itself says it is not a safe harbour and does not bind a court’s own assessment.'
    },
    '5': {
      claim: 'The CPS treats the six Home Office principles as a tool to structure lines of inquiry, identify weaknesses or omissions, and assess the strength of a claimed reasonable-procedures defence.',
      title: 'Corporate Prosecutions guidance',
      publisher: 'Crown Prosecution Service',
      date: 'Updated 10 November 2025',
      verified: '16 September 2026',
      url: 'https://www.cps.gov.uk/prosecution-guidance/corporate-prosecutions',
      limit: 'Prosecutorial guidance describing the CPS’s own approach, not a judicial ruling on any specific set of procedures.'
    },
    '6': {
      claim: 'The SFO names the section 199 defence as a context in which it may evaluate whether a compliance programme operated effectively in practice, as distinct from existing only on paper.',
      title: 'Guidance on Evaluating a Corporate Compliance Programme',
      publisher: 'Serious Fraud Office',
      date: 'Published 26 November 2025',
      verified: '16 September 2026',
      url: 'https://www.gov.uk/government/publications/sfo-guidance-on-evaluating-a-corporate-compliance-programme',
      limit: 'SFO evaluation guidance, not a finding on any particular organisation’s programme, and not binding on a court’s assessment under section 199(4).'
    },
    '7': {
      claim: 'Sections 199 to 206 of, and Schedule 13 to, the Act came into force on 1 September 2025.',
      title: 'The Economic Crime and Corporate Transparency Act 2023 (Commencement No. 4) Regulations 2025 (SI 2025/349)',
      publisher: 'legislation.gov.uk (UK National Archives)',
      date: 'Made 13 March 2025',
      verified: '16 September 2026',
      url: 'https://www.legislation.gov.uk/uksi/2025/349/made',
      limit: 'A commencement instrument fixing the date the offence took effect, not the substantive offence itself.'
    },
    '8': {
      claim: 'A parent undertaking is a large organisation if its group, aggregating each member’s turnover, balance sheet total and employee count under section 201, met at least two of the three thresholds.',
      title: 'Economic Crime and Corporate Transparency Act 2023, section 202',
      publisher: 'legislation.gov.uk (UK National Archives)',
      date: 'Current text as enacted',
      verified: '16 September 2026',
      url: 'https://www.legislation.gov.uk/ukpga/2023/56/section/202',
      limit: 'A specific group structure needs checking against section 202 directly.'
    }
  };

  function escapeHtml(value) {
    var div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }

  function showSource(id) {
    var source = SOURCES[id];
    var body = document.getElementById('ftpfSourcePanelBody');
    if (!source || !body) return;
    body.innerHTML = [
      '<div class="ftpf-source-claim">' + escapeHtml(source.claim) + '</div>',
      '<div class="ftpf-source-field-label">Source</div>',
      '<div class="ftpf-source-field-value">' + escapeHtml(source.title) + '</div>',
      '<div class="ftpf-source-field-label">Publisher</div>',
      '<div class="ftpf-source-field-value">' + escapeHtml(source.publisher) + '</div>',
      '<div class="ftpf-source-field-label">Published</div>',
      '<div class="ftpf-source-field-value">' + escapeHtml(source.date) + '</div>',
      '<div class="ftpf-source-field-label">Verified by FinCrimeRadar</div>',
      '<div class="ftpf-source-field-value">' + escapeHtml(source.verified) + '</div>',
      '<a class="ftpf-source-link" href="' + escapeHtml(source.url) + '" target="_blank" rel="noopener">Open source &rarr;</a>',
      '<div class="ftpf-source-field-label">What this does not establish</div>',
      '<div class="ftpf-source-limit">' + escapeHtml(source.limit) + '</div>'
    ].join('');
  }

  var MOBILE_QUERY = window.matchMedia('(max-width:800px)');
  var sourcePanelEl = document.getElementById('ftpfSourcePanel');
  var sourcePanelHomeParent = sourcePanelEl ? sourcePanelEl.parentNode : null;
  var sourcePanelHomeNext = sourcePanelEl ? sourcePanelEl.nextSibling : null;

  function restoreSourcePanelHome() {
    if (sourcePanelEl && sourcePanelHomeParent) {
      sourcePanelHomeParent.insertBefore(sourcePanelEl, sourcePanelHomeNext);
    }
  }

  document.querySelectorAll('.ftpf-cite[data-src]').forEach(function (el) {
    el.addEventListener('click', function (event) {
      event.preventDefault();
      var id = el.getAttribute('data-src');
      showSource(id);
      if (MOBILE_QUERY.matches && sourcePanelEl) {
        var anchor = el.closest('p, li, dd') || el.parentElement;
        if (anchor && anchor.parentNode) {
          anchor.insertAdjacentElement('afterend', sourcePanelEl);
        }
      }
      emitAggregateEvent('source_record_open', {
        guide_id: 'failure_to_prevent_fraud_evidence_essay',
        source_id: id
      });
    });
  });

  if (MOBILE_QUERY.addEventListener) {
    MOBILE_QUERY.addEventListener('change', function (e) {
      if (!e.matches) restoreSourcePanelHome();
    });
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
