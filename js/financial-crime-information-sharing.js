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

  // Grades this guide defines. Anything else is ignored for the state attribute.
  var KNOWN_GRADES = ['best', 'incomplete', 'unsupported'];

  function clearDecision(form) {
    var feedback = form.querySelector('.fis-feedback');
    if (feedback) {
      feedback.textContent = '';
      feedback.removeAttribute('data-state');
    }
    form.querySelectorAll('.fis-option').forEach(function (option) {
      option.removeAttribute('data-selected');
    });
    var scope = form.closest('.fis-section');
    if (scope) {
      scope.querySelectorAll('.fis-optfb').forEach(function (block) {
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
      var feedback = form.querySelector('.fis-feedback');
      var scenarioId = form.dataset.scenarioId;
      if (!selected) {
        feedback.textContent = 'Choose an option before recording the decision.';
        feedback.dataset.state = 'caution';
        return;
      }

      clearDecision(form);
      selected.closest('.fis-option').setAttribute('data-selected', 'true');

      var target = null;
      var scope = form.closest('.fis-section');
      if (scope) {
        scope.querySelectorAll('.fis-optfb-set').forEach(function (set) {
          set.setAttribute('data-revealed', 'true');
        });
        scope.querySelectorAll('.fis-optfb').forEach(function (block) {
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

  // Summary image. Everything drawn is read from the page itself (the one-screen summary and the closing
  // Risk, Signal, Response cards), so the image can never carry a claim the body copy does not. The same
  // routine measures and paints, so each block's height always matches the fonts actually drawn.
  var INSET = 64;

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

  function summaryPanel(context, source, textX, top, contentWidth, paint) {
    var textWidth = contentWidth - INSET;
    var y = top + 38;
    source.querySelectorAll('h3').forEach(function (heading) {
      if (paint) context.fillStyle = '#071d2b';
      context.font = '700 25px Arial';
      y = drawWrapped(context, heading.textContent, textX, y, textWidth, 32, paint) + 6;
      var list = heading.nextElementSibling;
      if (!list) return;
      list.querySelectorAll('li').forEach(function (item) {
        var label = item.querySelector('strong').textContent;
        context.font = '700 19px Arial';
        var labelWidth = context.measureText(label + ' ').width;
        if (paint) {
          context.fillStyle = '#0f5e57';
          context.fillText(label, textX, y);
          context.fillStyle = '#203842';
        }
        context.font = '19px Arial';
        y = drawWrapped(context, item.querySelector('span').textContent, textX + labelWidth, y, textWidth - labelWidth, 27, paint) + 8;
      });
      y += 10;
    });
    return y;
  }

  function patternBlock(context, pattern, textX, top, contentWidth, paint) {
    var textWidth = contentWidth - INSET;
    var y = top + 38;
    if (paint) context.fillStyle = '#071d2b';
    context.font = '700 27px Arial';
    y = drawWrapped(context, pattern.querySelector('h3').textContent, textX, y, textWidth, 34, paint) + 6;
    if (paint) context.fillStyle = '#48616b';
    context.font = '20px Arial';
    y = drawWrapped(context, pattern.querySelector('.fis-metaphor').textContent, textX, y, textWidth, 28, paint) + 10;
    pattern.querySelectorAll('.fis-lines div').forEach(function (line) {
      var label = line.querySelector('dt').textContent + ':';
      context.font = '700 19px Arial';
      var labelWidth = context.measureText(label + ' ').width;
      if (paint) {
        context.fillStyle = '#0f5e57';
        context.fillText(label, textX, y);
        context.fillStyle = '#203842';
      }
      context.font = '19px Arial';
      y = drawWrapped(context, line.querySelector('dd').textContent, textX + labelWidth, y, textWidth - labelWidth, 27, paint) + 8;
    });
    return y;
  }

  function exportSummary() {
    var status = document.getElementById('saveSummaryStatus');
    var summary = document.getElementById('fisOperationalSummary');
    var grid = document.getElementById('fisClosingPatterns');
    var patterns = grid ? Array.from(grid.querySelectorAll('.fis-pattern')) : [];
    if (!summary || !patterns.length) {
      status.textContent = 'Export unavailable.';
      return;
    }

    var width = 1200;
    var margin = 72;
    var contentWidth = width - margin * 2;
    var textX = margin + 32;
    var measure = document.createElement('canvas').getContext('2d');
    // The last line ends 8px above the returned position and the line height is 27px, so subtracting 9
    // leaves 26px below the final baseline.
    var blocks = [{ kind: 'summary', node: summary, height: summaryPanel(measure, summary, textX, 0, contentWidth, false) - 9 }]
      .concat(patterns.map(function (pattern) {
        return { kind: 'pattern', node: pattern, height: patternBlock(measure, pattern, textX, 0, contentWidth, false) - 9 };
      }));

    var height = 184 + blocks.reduce(function (total, block) {
      return total + block.height + 24;
    }, 0) + 72;
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');

    ctx.fillStyle = '#071d2b';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#99f6e4';
    ctx.font = '700 22px Arial';
    ctx.fillText('FINCRIMERADAR · GUIDE', margin, 58);
    ctx.fillStyle = '#ffffff';
    ctx.font = '700 42px Georgia';
    ctx.fillText('Financial Crime Information Sharing', margin, 112);
    ctx.fillStyle = '#c8e5df';
    ctx.font = '22px Arial';
    ctx.fillText('Can I tell another bank? One-screen summary, Risk, Signal, Response', margin, 150);

    var y = 184;
    blocks.forEach(function (block) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(margin, y, contentWidth, block.height);
      ctx.fillStyle = '#0f766e';
      ctx.fillRect(margin, y, 8, block.height);
      if (block.kind === 'summary') {
        summaryPanel(ctx, block.node, textX, y, contentWidth, true);
      } else {
        patternBlock(ctx, block.node, textX, y, contentWidth, true);
      }
      y += block.height + 24;
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
      link.download = 'financial-crime-information-sharing-guide-summary.png';
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Some browsers start the download asynchronously, so keep the URL alive briefly.
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      status.textContent = 'Summary image created.';
      emitAggregateEvent('export', 'card_export', {
        guide_id: GUIDE_ID,
        export_type: 'summary_and_patterns'
      });
    }, 'image/png');
  }

  var saveButton = document.getElementById('saveSummaryImage');
  if (saveButton) saveButton.addEventListener('click', exportSummary);

  // Set last, once every handler is attached. Buttons and hidden analyses depend on this class,
  // so a script that fails part way leaves the page in its fully readable no-script state.
  document.documentElement.classList.add('js');
}());
