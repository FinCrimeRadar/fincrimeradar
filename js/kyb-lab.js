/**
 * KYB Lab: one UK company's public register readout.
 *
 * Calls GET /api/kyb/company/{number} on the FinCrimeRadar API and renders the
 * response. It also offers a company name search (POST /api/kyb/search with a JSON
 * body, never a query string) that lists candidate companies to pick from.
 * Everything the API returns is untrusted third party text, so every
 * value reaches the page through textContent or createTextNode only. This file
 * must never use innerHTML, outerHTML, insertAdjacentHTML or document.write
 * (scripts/check_kyb_lab.py fails the build if it does). Links are built only
 * from the validated company number, never from a URL in the response.
 */
(function () {
  'use strict';

  var cfg = window.KYB_LAB_CONFIG || {};
  var API_BASE = 'https://fincrimeradar-api.onrender.com';
  var CH_BASE = 'https://find-and-update.company-information.service.gov.uk/company/';
  var TIMEOUT_MS = typeof cfg.timeoutMs === 'number' && cfg.timeoutMs > 0 ? cfg.timeoutMs : 70000;
  var COLD_NOTICE_MS = typeof cfg.coldNoticeMs === 'number' && cfg.coldNoticeMs >= 0 ? cfg.coldNoticeMs : 6000;
  var PAGE_SIZE = 20;
  var NOT_RETURNED_FALLBACK =
    'This register section was not returned. FinCrimeRadar draws no conclusion from its absence.';

  var MSG = {
    422: 'Enter a valid UK company number',
    404: 'No company found with that number',
    503: 'The register lookup is temporarily unavailable',
    other: 'The register lookup could not be completed. Try again shortly.',
    network: 'The lookup service could not be reached. Check your connection and try again.',
    shape: 'The lookup returned an unexpected response. Try again shortly.'
  };

  function timeoutMessage() {
    var secs = Math.max(1, Math.round(TIMEOUT_MS / 1000));
    return 'The lookup timed out after ' + secs + (secs === 1 ? ' second' : ' seconds') + '. Try again.';
  }

  var form = document.getElementById('kybForm');
  var input = document.getElementById('kybNumber');
  var submit = document.getElementById('kybSubmit');
  var statusEl = document.getElementById('kybStatus');
  var errorEl = document.getElementById('kybError');
  var retryBtn = document.getElementById('kybRetry');
  var wrap = document.getElementById('kybResultsWrap');
  var results = document.getElementById('kybResults');
  var dneList = document.getElementById('kybDneList');
  var attribution = document.getElementById('kybAttribution');
  if (!form || !input || !results) return;

  var inflight = null;

  // ---- DOM helpers: text only -------------------------------------------

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function add(parent) {
    for (var i = 1; i < arguments.length; i++) {
      if (arguments[i]) parent.appendChild(arguments[i]);
    }
    return parent;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  // A string from the API, or null when the field is missing or not a string.
  function str(value) {
    return typeof value === 'string' ? value : null;
  }

  // Null, undefined and empty values show as a plain hyphen, never as words.
  function text(value) {
    return value === null || value === undefined || value === '' ? '-' : String(value);
  }

  // The only transform applied to API strings: field keys and enum codes may have
  // underscores and hyphens turned into spaces. Prose is never passed through this.
  function label(key) {
    return String(key).replace(/[_-]/g, ' ');
  }

  // Generic, safe renderer for register evidence of any shape.
  function renderValue(value) {
    if (value === null || value === undefined || value === '') return el('span', 'kyb-muted', '-');
    if (Array.isArray(value)) {
      if (!value.length) return el('span', 'kyb-muted', '-');
      var ul = el('ul', 'kyb-plain');
      value.forEach(function (v) {
        add(ul, add(el('li'), renderValue(v)));
      });
      return ul;
    }
    if (typeof value === 'object') {
      var dl = el('dl', 'kyb-facts kyb-ev');
      Object.keys(value).forEach(function (k) {
        add(dl, el('dt', null, label(k)), add(el('dd'), renderValue(value[k])));
      });
      return dl;
    }
    return document.createTextNode(String(value));
  }

  function facts(rows) {
    var dl = el('dl', 'kyb-facts');
    rows.forEach(function (r) {
      add(dl, el('dt', null, r[0]), el('dd', null, text(r[1])));
    });
    return dl;
  }

  function block(id, title) {
    var s = el('section', 'kyb-block');
    var h = el('h3', 'kyb-h3', title);
    h.id = id;
    s.setAttribute('aria-labelledby', id);
    return add(s, h);
  }

  function notReturned(data) {
    var msg = typeof data.not_returned_notice === 'string' && data.not_returned_notice
      ? data.not_returned_notice
      : NOT_RETURNED_FALLBACK;
    return el('p', 'kyb-notice', msg);
  }

  function note(textValue) {
    return el('p', 'kyb-note', textValue);
  }

  // Long lists: first PAGE_SIZE rows, then a keyboard-operable "show more".
  function pagedList(items, renderItem, noun) {
    var ul = el('ul', 'kyb-list');
    var shown = 0;
    var btn = null;
    function more(fromClick) {
      var end = Math.min(items.length, shown + PAGE_SIZE);
      var firstNew = null;
      for (; shown < end; shown++) {
        var row = renderItem(items[shown]);
        if (!firstNew) firstNew = row;
        add(ul, row);
      }
      if (btn) {
        var left = items.length - shown;
        if (left <= 0) {
          btn.remove();
        } else {
          btn.textContent = 'Show ' + Math.min(PAGE_SIZE, left) + ' more ' + noun + ' (' + left + ' not shown)';
        }
      }
      // The activated button may be removed, so keep the keyboard user's place.
      if (fromClick && firstNew) {
        firstNew.tabIndex = -1;
        firstNew.focus();
      }
    }
    var holder = el('div');
    add(holder, ul);
    if (items.length > PAGE_SIZE) {
      btn = el('button', 'kyb-btn kyb-btn-quiet', '');
      btn.type = 'button';
      btn.addEventListener('click', function () { more(true); });
      add(holder, btn);
    }
    more(false);
    return holder;
  }

  // ---- Sections -----------------------------------------------------------

  // A labelled paragraph whose body is an API string, shown verbatim.
  function verbatim(labelText, value, className) {
    var box = el('div', 'kyb-dne-block');
    add(box, el('span', 'kyb-label', labelText), el('p', className, value));
    return box;
  }

  // Per record identity verification. Everything comes from the API as returned:
  // display text, eligibility, status, evidence and does_not_establish. The page
  // adds only field labels and never infers or rewrites a status.
  function idvBlock(iv) {
    var box = el('div', 'kyb-idv');
    add(box, el('p', 'kyb-idv-display', text(str(iv.display))));
    var state = facts([
      ['Eligibility', iv.eligibility],
      ['Status', iv.status]
    ]);
    state.className += ' kyb-idv-state';
    add(box, state);
    if (iv.evidence_label) add(box, el('p', 'kyb-note', iv.evidence_label));
    if (iv.evidence && Object.keys(iv.evidence).length) add(box, renderValue(iv.evidence));
    add(box, verbatim('Does not establish', text(str(iv.does_not_establish)), 'kyb-idv-dne'));
    return box;
  }

  function renderCompany(data) {
    var c = data.company || {};
    var s = block('kyb-h-company', 'Company');
    add(s, facts([
      ['Name', c.name],
      ['Company number', data.company_number],
      ['Company status', c.status],
      ['Company type', c.type],
      ['Date when the company was created', c.date_of_creation],
      ['Date which the company was converted/closed, dissolved or removed', c.date_of_cessation]
    ]));
    var interp = data.interpretation || {};
    if (interp.scope === 'unsupported_entity_type') {
      add(s, el('p', 'kyb-notice kyb-scope', text(interp.notice)));
    } else if (interp.notice) {
      add(s, note(interp.notice));
    }
    if (data.register_reported_values && typeof data.register_reported_values === 'object') {
      add(s, el('h4', 'kyb-h4', 'Values reported by the register'), renderValue(data.register_reported_values));
    }
    return s;
  }

  function sourceLabel(list) {
    return (list || []).map(function (x) { return text(x && label(x)); }).join(', ');
  }

  function renderIndicators(data) {
    var s = block('kyb-h-indicators', 'Indicators');
    var list = Array.isArray(data.indicators) ? data.indicators : [];
    if (!list.length) {
      add(s, note('No indicators were raised for this record. That is not a statement that the company is low risk.'));
      return s;
    }
    list.forEach(function (ind) {
      var a = el('article', 'kyb-ind');
      add(a, el('h4', 'kyb-h4 kyb-ind-title', text(str(ind.label))));
      var tagLine = el('p', 'kyb-tag-line');
      add(tagLine, el('span', 'kyb-tag', text(ind.evidence_state && label(ind.evidence_state))));
      add(a, tagLine);
      if (ind.evidence && Object.keys(ind.evidence).length) add(a, renderValue(ind.evidence));
      add(a, verbatim('Does not establish', text(str(ind.does_not_establish)), 'kyb-ind-dne'));
      add(a, el('p', 'kyb-source', 'Source: ' + sourceLabel(ind.source_endpoints)));
      add(s, a);
    });
    return s;
  }

  function renderOfficers(data) {
    var o = data.officers || {};
    var s = block('kyb-h-officers', 'Officers');
    if (o.source_status !== 'available') return add(s, notReturned(data));
    var items = o.items || [];
    if (!items.length) add(s, note('The register returned no officer records.'));
    else add(s, pagedList(items, function (it) {
      var li = el('li', 'kyb-row');
      add(li, el('p', 'kyb-row-title', text(it.name) + (it.role ? ', ' + label(it.role) : '')));
      add(li, el('p', 'kyb-row-meta',
        'Appointed ' + text(it.appointed_on) + '. Resigned ' + text(it.resigned_on)));
      if (it.identity_verification) add(li, idvBlock(it.identity_verification));
      return li;
    }, 'officers'));
    if (o.truncated === true) add(s, note('The register holds more officers than were returned. This list is incomplete.'));
    var ev = o.events || [];
    if (ev.length) {
      add(s, el('h4', 'kyb-h4', 'Dated appointments and resignations'));
      add(s, pagedList(ev, function (e) {
        return el('li', 'kyb-row', text(e.date) + ': ' + text(e.event && label(e.event)) + ', ' + text(e.name) + ', ' + text(e.role && label(e.role)));
      }, 'events'));
    }
    return s;
  }

  function statementRow(st) {
    var li = el('li', 'kyb-row');
    add(li, el('p', 'kyb-row-title', st.description ? st.description : text(st.statement && label(st.statement))));
    add(li, el('p', 'kyb-row-meta',
      'Notified ' + text(st.notified_on) + '. Ceased ' + text(st.ceased_on)));
    return li;
  }

  function renderPscs(data) {
    var p = data.pscs || {};
    var s = block('kyb-h-pscs', 'Persons with significant control');
    s.appendChild(el('h4', 'kyb-h4', 'PSC records'));
    if (p.records_source_status !== 'available') add(s, notReturned(data));
    else if (!(p.items || []).length) add(s, note('The register returned no PSC records.'));
    else add(s, pagedList(p.items, function (it) {
      var li = el('li', 'kyb-row');
      add(li, el('p', 'kyb-row-title', text(it.name) + (it.kind ? ', ' + label(it.kind) : '')));
      add(li, el('p', 'kyb-row-meta',
        'Notified ' + text(it.notified_on) + '. Ceased ' + text(it.ceased_on)));
      if (it.identity_verification) add(li, idvBlock(it.identity_verification));
      return li;
    }, 'PSC records'));
    add(s, el('h4', 'kyb-h4', 'PSC statements'));
    if (p.statements_source_status !== 'available') {
      add(s, notReturned(data));
    } else {
      var active = p.active_statements || [];
      var ceased = p.ceased_statements || [];
      if (!active.length && !ceased.length) add(s, note('The register returned no PSC statements.'));
      if (active.length) add(s, el('h5', 'kyb-h5', 'Active'), pagedList(active, statementRow, 'statements'));
      if (ceased.length) add(s, el('h5', 'kyb-h5', 'Ceased'), pagedList(ceased, statementRow, 'statements'));
    }
    if (p.truncated === true) add(s, note('The register holds more PSC records or statements than were returned. These lists are incomplete.'));
    return s;
  }

  function renderFilings(data) {
    var f = data.registered_office_change_filings;
    if (!f) return null;
    var s = block('kyb-h-filings', 'Registered office change filings');
    if (f.source_status !== 'available') return add(s, notReturned(data));
    if (!(f.items || []).length) add(s, note('No registered office change filings were found in the part of the filing history that was returned.'));
    else add(s, pagedList(f.items, function (it) {
      return el('li', 'kyb-row kyb-filing', text(it.date) + ': ' + text(it.description_identifier && label(it.description_identifier)));
    }, 'filings'));
    if (f.truncated === true) add(s, note('The filing history holds more entries than were returned. Older registered office changes may be missing.'));
    return s;
  }

  function indicatorEvidence(data, id) {
    var list = Array.isArray(data.indicators) ? data.indicators : [];
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].id === id) return list[i].evidence || {};
    }
    return null;
  }

  // Charges and insolvency show the returned fields only. There is no frontend
  // sentence about what the absence of a charge or case would mean.
  function renderCharges(data) {
    var r = data.charges;
    if (!r) return null;
    var s = block('kyb-h-charges', 'Charges');
    if (r.source_status !== 'available') return add(s, notReturned(data));
    add(s, facts([['Source status', r.source_status]]));
    var ev = indicatorEvidence(data, 'outstanding_charges');
    if (ev) {
      var rows = [];
      [['Outstanding charges', 'outstanding_count'], ['Charges returned', 'returned_count'], ['Total charges', 'total_count']]
        .forEach(function (p) {
          if (ev[p[1]] !== undefined && ev[p[1]] !== null) rows.push([p[0], ev[p[1]]]);
        });
      if (rows.length) add(s, facts(rows));
      if (Array.isArray(ev.charges) && ev.charges.length) add(s, renderValue(ev.charges));
    }
    return s;
  }

  function renderInsolvency(data) {
    var r = data.insolvency;
    if (!r) return null;
    var s = block('kyb-h-insolvency', 'Insolvency');
    if (r.source_status !== 'available') return add(s, notReturned(data));
    add(s, facts([['Source status', r.source_status]]));
    var ev = indicatorEvidence(data, 'insolvency_history');
    if (ev && Object.keys(ev).length) add(s, renderValue(ev));
    return s;
  }

  function renderDne(data) {
    clear(dneList);
    (Array.isArray(data.does_not_establish) ? data.does_not_establish : []).forEach(function (t) {
      add(dneList, el('li', null, text(str(t))));
    });
    attribution.textContent = text(data.attribution);
  }

  function renderResults(data, normalised) {
    clear(results);
    var head = el('div', 'kyb-result-head');
    var title = el('h2', 'kyb-h2', text(data.company && data.company.name));
    title.id = 'kybResultsHeading';
    title.tabIndex = -1;
    add(head, title);
    add(head, el('p', 'kyb-note', 'Retrieved ' + text(data.retrieved_at) + ' from the ' + text(data.source) + '.'));
    // Link built only from the validated company number, never from the response.
    if (/^[A-Z0-9]{8}$/.test(normalised) && data.company_number === normalised) {
      var a = el('a', 'kyb-link', 'View this company on Companies House');
      a.href = CH_BASE + normalised;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      add(head, a);
    }
    add(results, head, renderCompany(data));
    var unsupported = data.interpretation && data.interpretation.scope === 'unsupported_entity_type';
    if (!unsupported) add(results, renderIndicators(data));
    add(results,
      renderOfficers(data),
      renderPscs(data),
      renderFilings(data),
      renderCharges(data),
      renderInsolvency(data));
    renderDne(data);
    wrap.hidden = false;
  }

  // ---- Request flow ---------------------------------------------------------

  function normalise(raw) {
    var v = String(raw).trim().toUpperCase();
    if (/^[0-9]+$/.test(v) && v.length < 8) v = ('00000000' + v).slice(-8);
    return v;
  }

  function showStatus(message) {
    statusEl.textContent = message;
  }

  function showError(message, canRetry) {
    showStatus('');
    errorEl.textContent = message;
    errorEl.hidden = false;
    retryBtn.hidden = !canRetry;
  }

  function resetMessages() {
    errorEl.hidden = true;
    errorEl.textContent = '';
    retryBtn.hidden = true;
    showStatus('');
  }

  function busy(isBusy) {
    submit.disabled = isBusy;
    input.setAttribute('aria-busy', isBusy ? 'true' : 'false');
  }

  function lookup() {
    var value = normalise(input.value);
    input.value = value;
    resetMessages();
    wrap.hidden = true;
    clear(results);
    if (!value) {
      showError(MSG[422], false);
      input.focus();
      return;
    }
    if (inflight) inflight.abort();
    var controller = new AbortController();
    inflight = controller;
    var timedOut = false;
    busy(true);
    showStatus('Looking up the register. If the service has been idle, the first lookup can take up to a minute while it starts.');
    var coldTimer = setTimeout(function () {
      showStatus('Still working. The service is starting up and this can take up to a minute. Please keep this page open.');
    }, COLD_NOTICE_MS);
    var killTimer = setTimeout(function () {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);

    fetch(API_BASE + '/api/kyb/company/' + encodeURIComponent(value), {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller.signal
    }).then(function (res) {
      if (res.status === 200) {
        return res.json().then(function (data) {
          if (!data || typeof data !== 'object' || !data.company || typeof data.company !== 'object') {
            showError(MSG.shape, true);
            return;
          }
          try {
            renderResults(data, value);
          } catch (renderErr) {
            // Unexpected register shape: never show a half-rendered readout.
            clear(results);
            wrap.hidden = true;
            showError(MSG.shape, true);
            return;
          }
          showStatus('Register record loaded.');
          var h = document.getElementById('kybResultsHeading');
          if (h) h.focus();
        });
      }
      if (res.status === 429) {
        showError('Too many lookups; try again in a minute.', false);
      } else if (MSG[res.status]) {
        showError(MSG[res.status], res.status === 503);
      } else {
        showError(MSG.other, true);
      }
    }).catch(function (err) {
      if (timedOut) showError(timeoutMessage(), true);
      else if (err && err.name === 'AbortError') { if (inflight === controller) showStatus(''); }
      else if (err instanceof SyntaxError) showError(MSG.shape, true);
      else showError(MSG.network, true);
    }).then(function () {
      clearTimeout(coldTimer);
      clearTimeout(killTimer);
      // A superseded request must not re-enable the form or clear the newer one's state.
      if (inflight !== controller) return;
      inflight = null;
      busy(false);
      // The disabled submit button drops keyboard focus to body; return it to the form.
      if (document.activeElement === document.body) input.focus();
    });
  }

  // ---- Company name search (spec v1.9 section 14.7) -----------------------------
  // The term goes only in a JSON POST body. Every returned string, the title above
  // all, is untrusted register text: textContent only, the title inside <bdi> and in
  // its own element so a bidirectional control cannot reorder the trusted fields.

  var nameForm = document.getElementById('kybNameForm');
  var nameInput = document.getElementById('kybName');
  var nameSubmit = document.getElementById('kybNameSubmit');
  var nameStatus = document.getElementById('kybNameStatus');
  var nameError = document.getElementById('kybNameError');
  var nameRetry = document.getElementById('kybNameRetry');
  var cands = document.getElementById('kybCands');
  var candList = document.getElementById('kybCandList');
  var candNotice = document.getElementById('kybCandNotice');
  var candNote = document.getElementById('kybCandNote');
  var nameInflight = null;

  var NAME_MSG = {
    422: 'Enter 2 to 160 characters of text',
    413: 'That search is too long',
    429: 'Too many lookups; try again in a minute',
    503: MSG[503],
    other: MSG.other,
    network: MSG.network,
    shape: MSG.shape
  };
  var EMPTY_MESSAGE = 'No companies were returned for this search.';
  var NOT_INTERPRETED = 'Not interpreted in phase 1';

  function showNameStatus(message) {
    nameStatus.textContent = message;
  }

  function showNameError(message, canRetry) {
    showNameStatus('');
    nameError.textContent = message;
    nameError.hidden = false;
    nameRetry.hidden = !canRetry;
  }

  function resetNameMessages() {
    nameError.hidden = true;
    nameError.textContent = '';
    nameRetry.hidden = true;
    showNameStatus('');
  }

  function hideCands() {
    cands.hidden = true;
    clear(candList);
    candNotice.hidden = true;
    candNote.hidden = true;
    candNote.textContent = '';
  }

  function cell(className, labelText, value) {
    var c = el('div', 'kyb-cand-cell');
    add(c, el('span', 'kyb-cand-lab', labelText), el('span', 'kyb-cand-val ' + className, value));
    return c;
  }

  function candidateRow(c) {
    var li = el('li', 'kyb-cand');
    var titleCell = el('div', 'kyb-cand-titlecell');
    // <bdi> isolates the title's direction from everything around it.
    add(titleCell, el('bdi', 'kyb-cand-title', text(str(c.title))));
    add(li, titleCell);
    add(li, cell('kyb-cand-number', 'Company number', text(str(c.company_number))));
    add(li, cell('kyb-cand-status', 'Status', text(c.company_status && label(c.company_status))));
    add(li, cell('kyb-cand-type', 'Type', text(c.company_type && label(c.company_type))));
    add(li, cell('kyb-cand-date', 'Created', text(c.date_of_creation)));
    var actions = el('div', 'kyb-cand-actions');
    if (c.scope === 'unsupported_entity_type') add(actions, el('span', 'kyb-tag kyb-cand-scope', NOT_INTERPRETED));
    // The button text uses only the trusted fields, never the title.
    var pick = el('button', 'kyb-btn kyb-btn-quiet kyb-cand-pick', 'Look up company ' + text(str(c.company_number)));
    pick.type = 'button';
    pick.addEventListener('click', function () {
      input.value = str(c.company_number) || '';
      lookup();
    });
    add(actions, pick);
    add(li, actions);
    return li;
  }

  function renderCandidates(data) {
    clear(candList);
    var list = data.candidates;
    list.forEach(function (c) { add(candList, candidateRow(c)); });
    cands.hidden = false;
    if (!list.length) {
      candNotice.hidden = true;
      candNote.textContent = EMPTY_MESSAGE;
      candNote.hidden = false;
      return;
    }
    candNotice.textContent = text(str(data.search_notice));
    candNotice.hidden = false;
    if (data.truncated === true) {
      var total = data.reported_total;
      candNote.textContent = (typeof total === 'number' && total > list.length)
        ? 'The register reports ' + String(total) + ' matches. Only ' + String(list.length) + ' are shown.'
        : 'The register did not report a total, so this list may be incomplete.';
      candNote.hidden = false;
    } else {
      candNote.hidden = true;
      candNote.textContent = '';
    }
  }

  function searchByName() {
    var raw = nameInput.value;
    resetNameMessages();
    hideCands();
    if (!raw.trim()) {
      showNameError(NAME_MSG[422], false);
      nameInput.focus();
      return;
    }
    if (nameInflight) nameInflight.abort();
    var controller = new AbortController();
    nameInflight = controller;
    var timedOut = false;
    nameSubmit.disabled = true;
    nameInput.setAttribute('aria-busy', 'true');
    showNameStatus('Searching the register. If the service has been idle, the first search can take up to a minute while it starts.');
    var coldTimer = setTimeout(function () {
      showNameStatus('Still working. The service is starting up and this can take up to a minute. Please keep this page open.');
    }, COLD_NOTICE_MS);
    var killTimer = setTimeout(function () {
      timedOut = true;
      controller.abort();
    }, TIMEOUT_MS);

    fetch(API_BASE + '/api/kyb/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      cache: 'no-store',
      body: JSON.stringify({ q: raw }),
      signal: controller.signal
    }).then(function (res) {
      if (res.status === 200) {
        return res.json().then(function (data) {
          if (!data || typeof data !== 'object' || !Array.isArray(data.candidates) || typeof data.truncated !== 'boolean') {
            showNameError(NAME_MSG.shape, true);
            return;
          }
          try {
            renderCandidates(data);
          } catch (renderErr) {
            hideCands();
            showNameError(NAME_MSG.shape, true);
            return;
          }
          showNameStatus(data.candidates.length ? 'Search results loaded.' : '');
          var h = document.getElementById('kybCandsHeading');
          if (h) h.focus();
        });
      }
      if (NAME_MSG[res.status]) {
        showNameError(NAME_MSG[res.status], res.status === 503);
      } else {
        showNameError(NAME_MSG.other, true);
      }
    }).catch(function (err) {
      if (timedOut) showNameError(timeoutMessage(), true);
      else if (err && err.name === 'AbortError') { if (nameInflight === controller) showNameStatus(''); }
      else if (err instanceof SyntaxError) showNameError(NAME_MSG.shape, true);
      else showNameError(NAME_MSG.network, true);
    }).then(function () {
      clearTimeout(coldTimer);
      clearTimeout(killTimer);
      if (nameInflight !== controller) return;
      nameInflight = null;
      nameSubmit.disabled = false;
      nameInput.setAttribute('aria-busy', 'false');
      if (document.activeElement === document.body) nameInput.focus();
    });
  }

  if (nameForm && nameInput) {
    nameForm.addEventListener('submit', function (e) {
      e.preventDefault();
      searchByName();
    });
    nameRetry.addEventListener('click', searchByName);
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    lookup();
  });
  retryBtn.addEventListener('click', lookup);

  // Wake the API when the reader first focuses either input, once, so a cold start
  // overlaps with typing. Nothing is sent to the API just for opening the page.
  var warmed = false;
  function warm() {
    if (warmed) return;
    warmed = true;
    try {
      fetch(API_BASE + '/api/health', { method: 'GET', cache: 'no-store' }).catch(function () {});
    } catch (e) {}
  }
  input.addEventListener('focus', warm, { once: true });
  if (nameInput) nameInput.addEventListener('focus', warm, { once: true });
})();
