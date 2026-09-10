(function () {
  'use strict';

  var STORAGE_KEY = 'fcr_case_money_mule_v1';
  var CASE_VERSION = 1;

  var DEFAULT_STATE = {
    caseVersion: CASE_VERSION,
    currentStage: 1,
    highestUnlockedStage: 1,
    hypothesisState: { A: 'Unresolved', B: 'Unresolved', C: 'Unresolved', D: 'Unresolved', E: 'Unresolved' },
    hypothesisSnapshots: { initial: null, final: null },
    knowledgeTimeline: { entryState: null, prePaymentThreeState: null, changePoint: null },
    controlDecision: null,
    voluntarinessDecision: null,
    decisionRecord: { activity: null, control: null, knowledge: null, exploitation: null, evidence: null },
    redTeamCompleted: {
      transactionBias: false, authenticationBias: false, outcomeBias: false,
      vulnerabilityBias: false, culpabilityBias: false, narrativeBias: false,
      suspicionThreshold: false, corroboration: false, counterfactual: false, proportionality: false
    },
    decisionChangeSelections: {
      item1: false, item2: false, item3: false, item4: false,
      item5: false, item6: false, item7: false, item8: false, item9: false
    },
    reasoningShift: null,
    caseCompleted: false
  };

  var EVIDENCE_STATUS_LABELS = {
    Observed: 'Observed',
    SelfReported: 'Self Reported',
    Corroborated: 'Corroborated',
    Inferred: 'Inferred',
    Unknown: 'Unknown'
  };

  var HYPOTHESIS_STATES = ['Leading', 'Plausible', 'Unresolved', 'Weak'];
  var TIMELINE_STATES = ['Unaware', 'ConcernEmerging', 'Suspicious', 'LikelyAware', 'CannotDetermine'];
  var DECISION_VALUES = ['Yes', 'No', 'CannotDetermine'];
  var REASONING_SHIFT_VALUES = ['Substantially', 'Somewhat', 'NoMaterialChange'];

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

  function defaultState() {
    return JSON.parse(JSON.stringify(DEFAULT_STATE));
  }

  function isPlainObject(value) {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
  }

  function hasExactKeys(obj, keys) {
    if (!isPlainObject(obj)) return false;
    var objKeys = Object.keys(obj);
    if (objKeys.length !== keys.length) return false;
    return keys.every(function (key) {
      return Object.prototype.hasOwnProperty.call(obj, key);
    });
  }

  function isBooleanMap(obj, keys) {
    if (!hasExactKeys(obj, keys)) return false;
    return keys.every(function (key) { return typeof obj[key] === 'boolean'; });
  }

  function isNullOr(value, predicate) {
    return value === null || predicate(value);
  }

  function isValidHypothesisMap(map) {
    return hasExactKeys(map, ['A', 'B', 'C', 'D', 'E']) &&
      ['A', 'B', 'C', 'D', 'E'].every(function (key) {
        return HYPOTHESIS_STATES.indexOf(map[key]) !== -1;
      });
  }

  function isValidStageNumber(value) {
    return typeof value === 'number' && Math.floor(value) === value && value >= 1 && value <= 12;
  }

  // Validation deliberately checks shape and allowed values field by field rather
  // than a blanket typeof comparison against DEFAULT_STATE: several fields default
  // to null but hold a string once the practitioner answers, so a single typeof
  // rule cannot describe both states correctly. Any parse failure, version
  // mismatch or shape mismatch here must return false, never throw.
  function isValidState(candidate) {
    if (!isPlainObject(candidate)) return false;
    if (candidate.caseVersion !== CASE_VERSION) return false;

    var topKeys = Object.keys(DEFAULT_STATE);
    if (!topKeys.every(function (key) { return Object.prototype.hasOwnProperty.call(candidate, key); })) return false;

    if (!isValidStageNumber(candidate.currentStage)) return false;
    if (!isValidStageNumber(candidate.highestUnlockedStage)) return false;
    if (!isValidHypothesisMap(candidate.hypothesisState)) return false;

    if (!hasExactKeys(candidate.hypothesisSnapshots, ['initial', 'final'])) return false;
    if (!isNullOr(candidate.hypothesisSnapshots.initial, isValidHypothesisMap)) return false;
    if (!isNullOr(candidate.hypothesisSnapshots.final, isValidHypothesisMap)) return false;

    if (!hasExactKeys(candidate.knowledgeTimeline, ['entryState', 'prePaymentThreeState', 'changePoint'])) return false;
    if (!isNullOr(candidate.knowledgeTimeline.entryState, function (v) { return TIMELINE_STATES.indexOf(v) !== -1; })) return false;
    if (!isNullOr(candidate.knowledgeTimeline.prePaymentThreeState, function (v) { return TIMELINE_STATES.indexOf(v) !== -1; })) return false;
    if (!isNullOr(candidate.knowledgeTimeline.changePoint, function (v) { return typeof v === 'string'; })) return false;

    if (!isNullOr(candidate.controlDecision, function (v) { return DECISION_VALUES.indexOf(v) !== -1; })) return false;
    if (!isNullOr(candidate.voluntarinessDecision, function (v) { return DECISION_VALUES.indexOf(v) !== -1; })) return false;

    var decisionRecordKeys = ['activity', 'control', 'knowledge', 'exploitation', 'evidence'];
    if (!hasExactKeys(candidate.decisionRecord, decisionRecordKeys)) return false;
    if (!decisionRecordKeys.every(function (key) {
      return isNullOr(candidate.decisionRecord[key], function (v) { return typeof v === 'string'; });
    })) return false;

    if (!isBooleanMap(candidate.redTeamCompleted, Object.keys(DEFAULT_STATE.redTeamCompleted))) return false;
    if (!isBooleanMap(candidate.decisionChangeSelections, Object.keys(DEFAULT_STATE.decisionChangeSelections))) return false;

    if (!isNullOr(candidate.reasoningShift, function (v) { return REASONING_SHIFT_VALUES.indexOf(v) !== -1; })) return false;
    if (typeof candidate.caseCompleted !== 'boolean') return false;

    return true;
  }

  function loadState() {
    var raw;
    try {
      raw = localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      return defaultState();
    }
    if (!raw) return defaultState();

    var parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (error) {
      return defaultState();
    }

    if (!isValidState(parsed)) return defaultState();
    return parsed;
  }

  function saveState(candidate) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(candidate));
    } catch (error) {
      // ponytail: storage may be full or blocked (private browsing); the case
      // still works for the rest of this session, it just will not resume on reload.
    }
  }

  var state = loadState();

  function getState() {
    return state;
  }

  function updateState(mutatorFn) {
    mutatorFn(state);
    saveState(state);
    renderCurrentStage();
  }

  function advanceStage() {
    state.currentStage = Math.min(12, state.currentStage + 1);
    state.highestUnlockedStage = Math.max(state.highestUnlockedStage, state.currentStage);
    saveState(state);
    emitAggregateEvent('case_file_stage_complete', { case_id: 'money_mule_or_victim', stage: state.currentStage });
    renderCurrentStage();
  }

  function goToStage(n) {
    if (!isValidStageNumber(n) || n > state.highestUnlockedStage) return;
    state.currentStage = n;
    saveState(state);
    renderCurrentStage();
  }

  function clearRoot(root) {
    while (root.firstChild) root.removeChild(root.firstChild);
  }

  function renderNotYetImplemented(container, stageNumber) {
    var heading = document.createElement('h2');
    heading.textContent = 'Stage ' + stageNumber;
    container.appendChild(heading);

    var note = document.createElement('p');
    note.textContent = 'Not yet implemented.';
    container.appendChild(note);
  }

  function formatGBP(amount) {
    return '£' + amount.toLocaleString('en-GB');
  }

  // EvidenceCard. Status is never conveyed by colour alone: the glyph
  // (CSS ::before on .mmc-evidence-status, keyed off data-status) is a
  // decorative reinforcement for sighted users, and the text label
  // ("Self Reported", "Corroborated", etc, from EVIDENCE_STATUS_LABELS) is
  // the actual textContent, so it reaches assistive technology regardless of
  // whether the generated glyph does. `body` and `note` are optional: several
  // spec §11/§12 evidence items are a bare title plus status (or status plus
  // a short qualifier), with no separate descriptive paragraph.
  function renderEvidenceCard(container, item) {
    var card = document.createElement('article');
    card.className = 'mmc-evidence-card';

    var heading = document.createElement('h3');
    heading.textContent = item.title;
    card.appendChild(heading);

    if (item.body) {
      var bodyParagraphs = Array.isArray(item.body) ? item.body : [item.body];
      bodyParagraphs.forEach(function (text) {
        var p = document.createElement('p');
        p.textContent = text;
        card.appendChild(p);
      });
    }

    var status = document.createElement('span');
    status.className = 'mmc-evidence-status';
    status.setAttribute('data-status', item.status);
    status.textContent = EVIDENCE_STATUS_LABELS[item.status];
    card.appendChild(status);

    if (item.note) {
      var note = document.createElement('p');
      note.className = 'mmc-evidence-note';
      note.textContent = item.note;
      card.appendChild(note);
    }

    container.appendChild(card);
  }

  // Reusable board for Stages 2, 4, 5, 7, 9. `state` is the full CaseFileShell
  // state object (not just the hypothesisState map), because later stages need
  // to read from it in read-only/comparison form too.
  //
  // options:
  //   readOnly (boolean) - render the recorded value as text instead of radios.
  //   suggested (object A-E -> state string) - FinCrimeRadar's suggested starting
  //     positions, Stage 2 only. Rendered as a separate labelled block above the
  //     practitioner's own controls. Never used to pre-check a radio.
  //   onTouch (function(id)) - called when the practitioner interacts with a
  //     hypothesis's controls, before the state mutation. Used by Stage 2 to
  //     drive the continue-button gate.
  function renderHypothesisBoard(container, state, options) {
    options = options || {};
    var ids = ['A', 'B', 'C', 'D', 'E'];

    if (options.suggested) {
      var suggestedBoard = document.createElement('div');
      suggestedBoard.className = 'mmc-suggested-board';

      var suggestedLabel = document.createElement('p');
      suggestedLabel.className = 'mmc-suggested-board-label';
      suggestedLabel.textContent = 'FinCrimeRadar’s suggested starting position';
      suggestedBoard.appendChild(suggestedLabel);

      var suggestedList = document.createElement('dl');
      suggestedList.className = 'mmc-suggested-board-list';
      ids.forEach(function (id) {
        var dt = document.createElement('dt');
        dt.textContent = MMC_DATA.hypotheses[id].name;
        var dd = document.createElement('dd');
        dd.textContent = options.suggested[id];
        suggestedList.appendChild(dt);
        suggestedList.appendChild(dd);
      });
      suggestedBoard.appendChild(suggestedList);
      container.appendChild(suggestedBoard);

      var practitionerLabel = document.createElement('p');
      practitionerLabel.className = 'mmc-practitioner-board-label';
      practitionerLabel.textContent = 'Your own assessment';
      container.appendChild(practitionerLabel);
    }

    var board = document.createElement('div');
    board.className = 'mmc-hypothesis-board';

    ids.forEach(function (id) {
      var hypothesis = MMC_DATA.hypotheses[id];
      var fieldset = document.createElement('fieldset');
      fieldset.className = 'mmc-hypothesis';

      var legend = document.createElement('legend');
      var nameEl = document.createElement('strong');
      nameEl.textContent = hypothesis.name;
      legend.appendChild(nameEl);
      legend.appendChild(document.createTextNode(': ' + hypothesis.description));
      fieldset.appendChild(legend);

      if (options.readOnly) {
        var readOnlyValue = document.createElement('p');
        readOnlyValue.className = 'mmc-hypothesis-readonly-value';
        readOnlyValue.textContent = state.hypothesisState[id];
        fieldset.appendChild(readOnlyValue);
      } else {
        var optionsWrap = document.createElement('div');
        optionsWrap.className = 'mmc-hypothesis-options';
        HYPOTHESIS_STATES.forEach(function (stateValue) {
          var inputId = 'hyp-' + id + '-' + stateValue;
          var label = document.createElement('label');
          label.className = 'mmc-hypothesis-option';
          label.setAttribute('for', inputId);

          var input = document.createElement('input');
          input.type = 'radio';
          input.name = 'hyp-' + id;
          input.id = inputId;
          input.value = stateValue;
          input.checked = state.hypothesisState[id] === stateValue;
          // 'click' (not 'change') so re-selecting an already-checked radio
          // still registers as a deliberate touch for the Stage 2 gate: browsers
          // do not fire 'change' when the checked radio does not actually change.
          input.addEventListener('click', function () {
            if (typeof options.onTouch === 'function') options.onTouch(id);
            updateState(function (s) {
              s.hypothesisState[id] = stateValue;
            });
          });

          label.appendChild(input);
          label.appendChild(document.createTextNode(stateValue));
          optionsWrap.appendChild(label);
        });
        fieldset.appendChild(optionsWrap);
      }

      board.appendChild(fieldset);
    });
    container.appendChild(board);
  }

  // Tracks which of the five hypotheses the practitioner has clicked this page
  // load, for the Stage 2 continue gate. 'Unresolved' is both the untouched
  // default and a valid deliberate choice, so the gate cannot key off value !==
  // default; it keys off deliberate interaction instead. Module level (not a
  // variable local to renderStage2) so it survives the re-render every
  // updateState call triggers. Initialised once per page load: null means
  // "not yet initialised", not "reset on every render".
  var stage2Touched = null;

  function renderStage2(container) {
    var state = getState();
    var data = MMC_DATA.stages[2];

    if (stage2Touched === null) {
      stage2Touched = {};
      // Re-entering a stage already completed (e.g. via back navigation) should
      // not re-impose the gate: the practitioner already recorded an initial
      // assessment, so treat all five as touched.
      if (state.hypothesisSnapshots.initial) {
        ['A', 'B', 'C', 'D', 'E'].forEach(function (id) { stage2Touched[id] = true; });
      }
    }

    // Reuses the existing .mmc-section card styling that Stage 1's orientation
    // essay already ships (see money-mule-or-victim-case-file.html), rather than
    // introducing new CSS for this task.
    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 2: Case Intake and Initial Assessment';
    wrapper.appendChild(heading);

    // --- The Alert ---
    var alertSection = document.createElement('section');
    alertSection.className = 'mmc-alert';
    var alertHeading = document.createElement('h3');
    alertHeading.textContent = data.alert.heading;
    alertSection.appendChild(alertHeading);
    data.alert.paragraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      alertSection.appendChild(p);
    });
    wrapper.appendChild(alertSection);

    // --- Customer profile ---
    var profileSection = document.createElement('section');
    profileSection.className = 'mmc-profile';
    var profileHeading = document.createElement('h3');
    profileHeading.textContent = data.profile.heading;
    profileSection.appendChild(profileHeading);

    var profileList = document.createElement('dl');
    profileList.className = 'mmc-profile-list';
    data.profile.fields.forEach(function (field) {
      var dt = document.createElement('dt');
      dt.textContent = field.label;
      var dd = document.createElement('dd');
      dd.textContent = field.value;
      profileList.appendChild(dt);
      profileList.appendChild(dd);
    });
    profileSection.appendChild(profileList);

    var vulnerabilityCallout = document.createElement('p');
    vulnerabilityCallout.className = 'mmc-callout';
    var vulnerabilityStrong = document.createElement('strong');
    vulnerabilityStrong.textContent = data.profile.vulnerabilityCallout;
    vulnerabilityCallout.appendChild(vulnerabilityStrong);
    profileSection.appendChild(vulnerabilityCallout);
    wrapper.appendChild(profileSection);

    // --- Transaction chronology ---
    var chronologySection = document.createElement('section');
    chronologySection.className = 'mmc-chronology';
    var chronologyHeading = document.createElement('h3');
    chronologyHeading.textContent = 'Transaction chronology';
    chronologySection.appendChild(chronologyHeading);

    var table = document.createElement('table');
    table.className = 'mmc-chronology-table';
    var caption = document.createElement('caption');
    caption.textContent = 'Transaction chronology for Customer R’s account, Day 1 to Day 4';
    table.appendChild(caption);

    var thead = document.createElement('thead');
    var headRow = document.createElement('tr');
    ['Day', 'Incoming payment', 'Outgoing movement', 'Time to move'].forEach(function (label) {
      var th = document.createElement('th');
      th.setAttribute('scope', 'col');
      th.textContent = label;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = document.createElement('tbody');
    data.chronology.forEach(function (entry) {
      var row = document.createElement('tr');

      var dayTh = document.createElement('th');
      dayTh.setAttribute('scope', 'row');
      dayTh.textContent = 'Day ' + entry.day;
      row.appendChild(dayTh);

      var incomingTd = document.createElement('td');
      incomingTd.textContent = 'Incoming payment from ' + entry.incoming.sender + ': ' + formatGBP(entry.incoming.amount);
      row.appendChild(incomingTd);

      var outgoingTd = document.createElement('td');
      var outgoingText = entry.outgoing.type === 'withdrawal'
        ? 'Cash withdrawal: ' + formatGBP(entry.outgoing.amount)
        : 'Transfer to ' + entry.outgoing.beneficiary + ': ' + formatGBP(entry.outgoing.amount);
      outgoingTd.textContent = outgoingText;
      row.appendChild(outgoingTd);

      var timeTd = document.createElement('td');
      timeTd.textContent = entry.timeToMoveLabel + ': ' + entry.timeToMove;
      row.appendChild(timeTd);

      tbody.appendChild(row);
    });
    table.appendChild(tbody);

    // Reuses the sitewide .table-scroll wrapper (brand.css section 8) instead of
    // writing new mobile-overflow CSS for this table.
    var tableScroll = document.createElement('div');
    tableScroll.className = 'table-scroll';
    tableScroll.appendChild(table);
    chronologySection.appendChild(tableScroll);

    var totalsList = document.createElement('dl');
    totalsList.className = 'mmc-chronology-totals';
    [
      ['Total received', formatGBP(data.totals.received)],
      ['Total moved onwards or withdrawn', formatGBP(data.totals.moved)],
      ['Difference', formatGBP(data.totals.difference)]
    ].forEach(function (pair) {
      var dt = document.createElement('dt');
      dt.textContent = pair[0];
      var dd = document.createElement('dd');
      var strong = document.createElement('strong');
      strong.textContent = pair[1];
      dd.appendChild(strong);
      totalsList.appendChild(dt);
      totalsList.appendChild(dd);
    });
    chronologySection.appendChild(totalsList);
    wrapper.appendChild(chronologySection);

    // --- Initial assessment: Hypothesis Board ---
    var assessmentSection = document.createElement('section');
    assessmentSection.className = 'mmc-initial-assessment';
    var assessmentHeading = document.createElement('h3');
    assessmentHeading.textContent = 'Initial assessment';
    assessmentSection.appendChild(assessmentHeading);

    renderHypothesisBoard(assessmentSection, state, {
      suggested: data.suggestedHypotheses,
      onTouch: function (id) {
        stage2Touched[id] = true;
      }
    });
    wrapper.appendChild(assessmentSection);

    // --- Practitioner Lens ---
    var lensSection = document.createElement('section');
    lensSection.className = 'mmc-practitioner-lens';
    var lensHeading = document.createElement('h3');
    lensHeading.textContent = 'Practitioner Lens';
    lensSection.appendChild(lensHeading);

    var lensIntro = document.createElement('p');
    var lensIntroStrong = document.createElement('strong');
    lensIntroStrong.textContent = data.practitionerLensIntro;
    lensIntro.appendChild(lensIntroStrong);
    lensSection.appendChild(lensIntro);

    var canList = document.createElement('ul');
    canList.className = 'mmc-lens-can';
    data.practitionerLensCanEstablish.forEach(function (text) {
      var li = document.createElement('li');
      li.textContent = text;
      canList.appendChild(li);
    });
    lensSection.appendChild(canList);

    var cannotList = document.createElement('ul');
    cannotList.className = 'mmc-lens-cannot';
    data.practitionerLensCannotEstablish.forEach(function (text) {
      var li = document.createElement('li');
      li.textContent = text;
      cannotList.appendChild(li);
    });
    lensSection.appendChild(cannotList);

    var lensClosing = document.createElement('p');
    var lensClosingStrong = document.createElement('strong');
    lensClosingStrong.textContent = data.practitionerLensClosing;
    lensClosing.appendChild(lensClosingStrong);
    lensSection.appendChild(lensClosing);
    wrapper.appendChild(lensSection);

    // --- Gate note + continue button ---
    var gateNote = document.createElement('p');
    gateNote.className = 'mmc-gate-note';
    gateNote.textContent = data.gateNote;
    wrapper.appendChild(gateNote);

    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Record initial assessment and continue';
    continueButton.addEventListener('click', function () {
      updateState(function (s) {
        s.hypothesisSnapshots.initial = {
          A: s.hypothesisState.A,
          B: s.hypothesisState.B,
          C: s.hypothesisState.C,
          D: s.hypothesisState.D,
          E: s.hypothesisState.E
        };
      });
      stage2Touched = null;
      advanceStage();
    });
    continueButton.disabled = !['A', 'B', 'C', 'D', 'E'].every(function (id) { return stage2Touched[id]; });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  function renderStage3(container) {
    var data = MMC_DATA.stages[3];

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 3: Evidence Inject 01';
    wrapper.appendChild(heading);

    // --- Customer explanation ---
    var explanationSection = document.createElement('section');
    explanationSection.className = 'mmc-customer-explanation';
    var explanationHeading = document.createElement('h3');
    explanationHeading.textContent = 'Customer explanation';
    explanationSection.appendChild(explanationHeading);

    data.customerExplanation.intro.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      explanationSection.appendChild(p);
    });

    var roleTitle = document.createElement('p');
    var roleTitleStrong = document.createElement('strong');
    roleTitleStrong.textContent = data.customerExplanation.roleTitle;
    roleTitle.appendChild(roleTitleStrong);
    explanationSection.appendChild(roleTitle);

    data.customerExplanation.roleParagraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      explanationSection.appendChild(p);
    });

    var providedIntro = document.createElement('p');
    providedIntro.textContent = 'Customer R provides:';
    explanationSection.appendChild(providedIntro);

    var providedList = document.createElement('ul');
    providedList.className = 'mmc-provided-list';
    data.provided.forEach(function (text) {
      var li = document.createElement('li');
      li.textContent = text;
      providedList.appendChild(li);
    });
    explanationSection.appendChild(providedList);

    var retainedFunds = document.createElement('p');
    retainedFunds.textContent = data.retainedFundsExplanation;
    explanationSection.appendChild(retainedFunds);

    var framing = document.createElement('p');
    framing.className = 'mmc-callout';
    var framingStrong = document.createElement('strong');
    framingStrong.textContent = data.framingLine;
    framing.appendChild(framingStrong);
    explanationSection.appendChild(framing);

    wrapper.appendChild(explanationSection);

    // --- Evidence classification ---
    var evidenceSection = document.createElement('section');
    evidenceSection.className = 'mmc-evidence-section';
    var evidenceHeading = document.createElement('h3');
    evidenceHeading.textContent = 'Evidence classification';
    evidenceSection.appendChild(evidenceHeading);

    var evidenceGrid = document.createElement('div');
    evidenceGrid.className = 'mmc-evidence-grid';
    data.evidenceItems.forEach(function (item) {
      renderEvidenceCard(evidenceGrid, item);
    });
    evidenceSection.appendChild(evidenceGrid);
    wrapper.appendChild(evidenceSection);

    // --- Hypothesis impact (narration only, not editable) ---
    var impactSection = document.createElement('section');
    impactSection.className = 'mmc-hypothesis-impact';
    var impactHeading = document.createElement('h3');
    impactHeading.textContent = 'Hypothesis impact';
    impactSection.appendChild(impactHeading);

    var impactList = document.createElement('dl');
    impactList.className = 'mmc-hypothesis-impact-list';
    ['A', 'B', 'C', 'D', 'E'].forEach(function (id) {
      var dt = document.createElement('dt');
      dt.textContent = MMC_DATA.hypotheses[id].name;
      var dd = document.createElement('dd');
      dd.textContent = data.hypothesisImpact[id];
      impactList.appendChild(dt);
      impactList.appendChild(dd);
    });
    impactSection.appendChild(impactList);
    wrapper.appendChild(impactSection);

    // --- Practitioner Lens, including the non scored investigation actions ---
    var lensSection = document.createElement('section');
    lensSection.className = 'mmc-practitioner-lens';
    var lensHeading = document.createElement('h3');
    lensHeading.textContent = 'Practitioner Lens';
    lensSection.appendChild(lensHeading);

    var lensOpening = document.createElement('p');
    var lensOpeningStrong = document.createElement('strong');
    lensOpeningStrong.textContent = data.practitionerLens.heading;
    lensOpening.appendChild(lensOpeningStrong);
    lensSection.appendChild(lensOpening);

    var lensBody = document.createElement('p');
    lensBody.textContent = data.practitionerLens.body;
    lensSection.appendChild(lensBody);

    var lensClosing = document.createElement('p');
    var lensClosingStrong = document.createElement('strong');
    lensClosingStrong.textContent = data.practitionerLens.closing;
    lensClosing.appendChild(lensClosingStrong);
    lensSection.appendChild(lensClosing);

    var actionsList = document.createElement('ul');
    actionsList.className = 'mmc-investigation-actions';
    data.investigationActions.forEach(function (text) {
      var li = document.createElement('li');
      var label = document.createElement('label');
      label.className = 'mmc-investigation-action';
      var checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      // Purely reflective, per spec §11: "No selection should be marked
      // correct or incorrect." No onTouch/onChange handler is attached, so
      // this never calls updateState, is never persisted to localStorage
      // and has no bearing on the continue button below.
      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(text));
      li.appendChild(label);
      actionsList.appendChild(li);
    });
    lensSection.appendChild(actionsList);

    var actionsNote = document.createElement('p');
    actionsNote.className = 'mmc-gate-note';
    actionsNote.textContent = data.investigationActionsNote;
    lensSection.appendChild(actionsNote);

    wrapper.appendChild(lensSection);

    // --- Continue: no gate. Nothing structured is recorded at this stage
    // beyond reading, per the brief. ---
    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Continue';
    continueButton.addEventListener('click', function () {
      advanceStage();
    });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  // Tracks which of the five hypotheses have been clicked during this visit
  // to Stage 4, for the continue gate. Same rationale and shape as
  // stage2Touched above: module level so it survives the re-render every
  // updateState call triggers, null means "not yet initialised this visit".
  var stage4Touched = null;

  function renderStage4(container) {
    var state = getState();
    var data = MMC_DATA.stages[4];

    if (stage4Touched === null) {
      stage4Touched = { A: false, B: false, C: false, D: false, E: false };
      // Revisiting a stage already completed (e.g. future back navigation,
      // or a Decision Point comparison stage looking back at this one)
      // should not re-impose the gate. There is no per-stage "Stage 4
      // confirmed" flag in the persisted state (unlike Stage 2's
      // hypothesisSnapshots.initial), so highestUnlockedStage > 4 is used
      // instead: it means the practitioner has already advanced past this
      // stage before, so this is a revisit, not a first pass. This check is
      // schema-free and is the pattern later Stages 5, 7 and 9 should reuse
      // when they re-show the hypothesis board.
      if (state.highestUnlockedStage > 4) {
        ['A', 'B', 'C', 'D', 'E'].forEach(function (id) { stage4Touched[id] = true; });
      }
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 4: Evidence Inject 02';
    wrapper.appendChild(heading);

    // --- Digital evidence ---
    var digitalSection = document.createElement('section');
    digitalSection.className = 'mmc-digital-evidence';
    var digitalHeading = document.createElement('h3');
    digitalHeading.textContent = 'Digital evidence';
    digitalSection.appendChild(digitalHeading);
    data.digitalEvidence.paragraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      digitalSection.appendChild(p);
    });
    wrapper.appendChild(digitalSection);

    // --- Evidence status ---
    var evidenceSection = document.createElement('section');
    evidenceSection.className = 'mmc-evidence-section';
    var evidenceHeading = document.createElement('h3');
    evidenceHeading.textContent = 'Evidence status';
    evidenceSection.appendChild(evidenceHeading);
    var evidenceGrid = document.createElement('div');
    evidenceGrid.className = 'mmc-evidence-grid';
    data.evidenceItems.forEach(function (item) {
      renderEvidenceCard(evidenceGrid, item);
    });
    evidenceSection.appendChild(evidenceGrid);
    wrapper.appendChild(evidenceSection);

    // --- Core message ---
    var callout = document.createElement('p');
    callout.className = 'mmc-callout mmc-callout-prominent';
    var calloutStrong = document.createElement('strong');
    calloutStrong.textContent = data.coreMessage;
    callout.appendChild(calloutStrong);
    wrapper.appendChild(callout);

    // --- Practitioner Lens ---
    var lensSection = document.createElement('section');
    lensSection.className = 'mmc-practitioner-lens';
    var lensHeading = document.createElement('h3');
    lensHeading.textContent = 'Practitioner Lens';
    lensSection.appendChild(lensHeading);

    var lensOpening = document.createElement('p');
    var lensOpeningStrong = document.createElement('strong');
    lensOpeningStrong.textContent = data.practitionerLens.heading;
    lensOpening.appendChild(lensOpeningStrong);
    lensSection.appendChild(lensOpening);

    var lensBody = document.createElement('p');
    lensBody.textContent = data.practitionerLens.body;
    lensSection.appendChild(lensBody);
    wrapper.appendChild(lensSection);

    // --- Hypothesis Board, editable, no suggested block this time ---
    var boardSection = document.createElement('section');
    boardSection.className = 'mmc-initial-assessment';
    var boardHeading = document.createElement('h3');
    boardHeading.textContent = 'Reassess the hypotheses';
    boardSection.appendChild(boardHeading);

    renderHypothesisBoard(boardSection, state, {
      onTouch: function (id) {
        stage4Touched[id] = true;
      }
    });
    wrapper.appendChild(boardSection);

    var gateNote = document.createElement('p');
    gateNote.className = 'mmc-gate-note';
    gateNote.textContent = data.gateNote;
    wrapper.appendChild(gateNote);

    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Continue';
    continueButton.addEventListener('click', function () {
      stage4Touched = null;
      advanceStage();
    });
    continueButton.disabled = !['A', 'B', 'C', 'D', 'E'].every(function (id) { return stage4Touched[id]; });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  var STAGE_RENDERERS = { 2: renderStage2, 3: renderStage3, 4: renderStage4 };
  (function registerPlaceholderStages() {
    var stageNumber;
    for (stageNumber = 5; stageNumber <= 12; stageNumber += 1) {
      STAGE_RENDERERS[stageNumber] = (function (n) {
        return function (container) { renderNotYetImplemented(container, n); };
      }(stageNumber));
    }
  }());

  function renderCurrentStage() {
    var root = document.getElementById('caseFileApp');
    if (!root) return;
    clearRoot(root);
    var renderer = STAGE_RENDERERS[state.currentStage];
    if (renderer) renderer(root);
  }

  function openCase() {
    var root = document.getElementById('caseFileApp');
    var openButton = document.getElementById('openCaseFile');
    if (root) root.hidden = false;
    if (openButton) {
      openButton.hidden = true;
      openButton.disabled = true;
    }
    // Stage 1 is the static orientation essay above #caseFileApp and has no
    // STAGE_RENDERERS entry. Opening the case from a fresh (or reset) state
    // is the transition into the first interactive stage, so it advances.
    // A reload that resumes at currentStage > 1 skips this branch entirely
    // (see wireOpenCaseFile) and only re-renders where the practitioner left off.
    if (state.currentStage === 1) {
      advanceStage();
    } else {
      renderCurrentStage();
    }
  }

  function resetCase() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      // ponytail: nothing to clean up if storage is already unavailable.
    }
    state = defaultState();

    var root = document.getElementById('caseFileApp');
    var openButton = document.getElementById('openCaseFile');
    var resetButton = document.getElementById('mmcResetCase');
    var confirmRow = document.getElementById('mmcResetConfirm');
    if (root) {
      clearRoot(root);
      root.hidden = true;
    }
    if (openButton) {
      openButton.hidden = false;
      openButton.disabled = false;
    }
    // Also restore the reset control itself, so a direct CaseFileShell.resetCase()
    // console call leaves consistent UI even if the confirm row happened to be open.
    if (confirmRow) confirmRow.hidden = true;
    if (resetButton) resetButton.hidden = false;
  }

  function wireOpenCaseFile() {
    var openButton = document.getElementById('openCaseFile');
    // The listener is always attached, not only when currentStage is 1 at
    // load time: Reset Case can restore the button's visibility later in the
    // same page instance (after a reload that resumed past Stage 1, where the
    // button was never clicked this load), and it must still work then.
    if (openButton) {
      openButton.addEventListener('click', openCase);
    }
    if (state.currentStage > 1) {
      openCase();
    }
  }

  function wireResetControls() {
    var resetButton = document.getElementById('mmcResetCase');
    var confirmRow = document.getElementById('mmcResetConfirm');
    var yesButton = document.getElementById('mmcResetYes');
    var noButton = document.getElementById('mmcResetNo');
    if (!resetButton || !confirmRow || !yesButton || !noButton) return;

    resetButton.addEventListener('click', function () {
      resetButton.hidden = true;
      confirmRow.hidden = false;
      noButton.focus();
    });

    noButton.addEventListener('click', function () {
      confirmRow.hidden = true;
      resetButton.hidden = false;
      resetButton.focus();
    });

    yesButton.addEventListener('click', function () {
      resetCase();
      resetButton.focus();
    });
  }

  wireOpenCaseFile();
  wireResetControls();

  window.CaseFileShell = {
    getState: getState,
    updateState: updateState,
    advanceStage: advanceStage,
    goToStage: goToStage,
    renderCurrentStage: renderCurrentStage,
    resetCase: resetCase
  };
}());
