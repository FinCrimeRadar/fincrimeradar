/**
 * KYB Lab: one UK company's public register readout.
 *
 * Calls GET /api/kyb/company/{number} on the FinCrimeRadar API and renders the
 * response. Everything the API returns is untrusted third party text, so every
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
    timeout: 'The lookup timed out after 70 seconds. Try again.',
    shape: 'The lookup returned an unexpected response. Try again shortly.'
  };

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

  function text(value, fallback) {
    if (value === null || value === undefined || value === '') return fallback || 'Not recorded';
    return String(value);
  }

  function label(key) {
    return String(key).replace(/_/g, ' ');
  }

  // Generic, safe renderer for register evidence of any shape.
  function renderValue(value) {
    if (value === null || value === undefined) return el('span', 'kyb-muted', 'Not recorded');
    if (Array.isArray(value)) {
      if (!value.length) return el('span', 'kyb-muted', 'None');
      var ul = el('ul', 'kyb-plain');
      value.forEach(function (v) {
        add(ul, add(el('li'), renderValue(v)));
      });
      return ul;
    }
    if (typeof value === 'object') {
      var dl = el('dl', 'kyb-facts');
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
    function more() {
      var end = Math.min(items.length, shown + PAGE_SIZE);
      for (; shown < end; shown++) add(ul, renderItem(items[shown]));
      if (btn) {
        var left = items.length - shown;
        if (left <= 0) {
          btn.remove();
        } else {
          btn.textContent = 'Show ' + Math.min(PAGE_SIZE, left) + ' more ' + noun + ' (' + left + ' not shown)';
        }
      }
    }
    var holder = el('div');
    add(holder, ul);
    if (items.length > PAGE_SIZE) {
      btn = el('button', 'kyb-btn kyb-btn-quiet', '');
      btn.type = 'button';
      btn.addEventListener('click', more);
      add(holder, btn);
    }
    more();
    return holder;
  }

  // ---- Sections -----------------------------------------------------------

  function idvBlock(iv) {
    var box = el('div', 'kyb-idv');
    add(box, el('p', 'kyb-idv-display', iv.display));
    if (iv.evidence_label) add(box, el('p', 'kyb-note', iv.evidence_label));
    if (iv.evidence && Object.keys(iv.evidence).length) add(box, renderValue(iv.evidence));
    if (iv.does_not_establish) add(box, el('p', 'kyb-dne-inline', 'Does not establish: ' + iv.does_not_establish));
    return box;
  }

  function renderCompany(data) {
    var c = data.company || {};
    var s = block('kyb-h-company', 'Company');
    add(s, facts([
      ['Name', c.name],
      ['Company number', data.company_number],
      ['Status', c.status],
      ['Type', c.type],
      ['Incorporated', c.date_of_creation],
      ['Dissolved', c.date_of_cessation]
    ]));
    var interp = data.interpretation || {};
    if (interp.scope === 'unsupported_entity_type') {
      add(s, el('p', 'kyb-notice kyb-scope', text(interp.notice, 'This entity type is not interpreted in phase 1.')));
    } else if (interp.notice) {
      add(s, note(interp.notice));
    }
    if (data.register_reported_values && typeof data.register_reported_values === 'object') {
      add(s, el('h4', 'kyb-h4', 'Values reported by the register'), renderValue(data.register_reported_values));
    }
    return s;
  }

  function sourceLabel(list) {
    return (list || []).map(label).join(', ');
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
      var head = el('div', 'kyb-ind-head');
      add(head, el('h4', 'kyb-h4', ind.label));
      add(head, el('span', 'kyb-tag', ind.evidence_state === 'register_fact' ? 'Register fact' : 'FinCrimeRadar assessment'));
      add(a, head);
      if (ind.evidence && Object.keys(ind.evidence).length) add(a, renderValue(ind.evidence));
      add(a, el('p', 'kyb-dne-inline', 'Does not establish: ' + text(ind.does_not_establish, '')));
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
        'Appointed ' + text(it.appointed_on) + (it.resigned_on ? '. Resigned ' + it.resigned_on : '. Not recorded as resigned')));
      if (it.identity_verification) add(li, idvBlock(it.identity_verification));
      return li;
    }, 'officers'));
    if (o.truncated === true) add(s, note('The register holds more officers than were returned. This list is incomplete.'));
    var ev = o.events || [];
    if (ev.length) {
      add(s, el('h4', 'kyb-h4', 'Dated appointments and resignations'));
      add(s, pagedList(ev, function (e) {
        return el('li', 'kyb-row', e.date + ': ' + label(e.event) + ', ' + text(e.name) + (e.role ? ', ' + label(e.role) : ''));
      }, 'events'));
    }
    return s;
  }

  function statementRow(st) {
    var li = el('li', 'kyb-row');
    add(li, el('p', 'kyb-row-title', text(st.description || st.statement)));
    add(li, el('p', 'kyb-row-meta',
      'Notified ' + text(st.notified_on) + (st.ceased_on ? '. Ceased ' + st.ceased_on : '')));
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
        'Notified ' + text(it.notified_on) + (it.ceased_on ? '. Ceased ' + it.ceased_on : '. Not recorded as ceased')));
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
      return el('li', 'kyb-row', text(it.date) + ': ' + text(it.description_identifier) + (it.transaction_id ? ' (transaction ' + it.transaction_id + ')' : ''));
    }, 'filings'));
    if (f.truncated === true) add(s, note('The filing history holds more entries than were returned. Older registered office changes may be missing.'));
    return s;
  }

  function renderRecord(data, key, title, id, present) {
    var r = data[key];
    if (!r) return null;
    var s = block(id, title);
    if (r.source_status !== 'available') return add(s, notReturned(data));
    return add(s, note(present));
  }

  function renderDne(data) {
    clear(dneList);
    (Array.isArray(data.does_not_establish) ? data.does_not_establish : []).forEach(function (t) {
      add(dneList, el('li', null, t));
    });
    attribution.textContent = text(data.attribution, '');
  }

  function renderResults(data, normalised) {
    clear(results);
    var head = el('div', 'kyb-result-head');
    var title = el('h2', 'kyb-h2', text(data.company && data.company.name, 'Company readout'));
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
      renderRecord(data, 'charges', 'Charges', 'kyb-h-charges',
        'The register holds charge records for this company. The charge list is not shown in this readout.'),
      renderRecord(data, 'insolvency', 'Insolvency', 'kyb-h-insolvency',
        'The register holds an insolvency record for this company. The detail is not shown in this readout.'));
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

  function retryAfterText(res) {
    var raw = res.headers && res.headers.get('Retry-After');
    var n = raw ? parseInt(raw, 10) : NaN;
    return n > 0 && n < 3600 ? 'in ' + (n === 1 ? '1 second' : n + ' seconds') : 'in a minute';
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
        showError('Too many lookups; try again ' + retryAfterText(res) + '.', false);
      } else if (MSG[res.status]) {
        showError(MSG[res.status], res.status === 503);
      } else {
        showError(MSG.other, true);
      }
    }).catch(function (err) {
      if (timedOut) showError(MSG.timeout, true);
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

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    lookup();
  });
  retryBtn.addEventListener('click', lookup);

  // Wake the API so a cold start overlaps with the reader typing a number.
  try {
    fetch(API_BASE + '/api/health', { method: 'GET', cache: 'no-store' }).catch(function () {});
  } catch (e) {}
})();
