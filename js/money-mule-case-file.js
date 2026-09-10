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
    Unknown: 'Unknown',
    StronglyCorroborated: 'Strongly Corroborated',
    NotIdentified: 'Not Identified',
    NotEstablished: 'Not Established'
  };

  var HYPOTHESIS_STATES = ['Leading', 'Plausible', 'Unresolved', 'Weak'];
  var TIMELINE_STATES = ['Unaware', 'ConcernEmerging', 'Suspicious', 'LikelyAware', 'CannotDetermine'];
  var TIMELINE_STATE_LABELS = {
    Unaware: 'Unaware',
    ConcernEmerging: 'Concern emerging',
    Suspicious: 'Suspicious',
    LikelyAware: 'Likely aware',
    CannotDetermine: 'Cannot determine'
  };
  var DECISION_VALUES = ['Yes', 'No', 'CannotDetermine'];
  var DECISION_VALUE_LABELS = { Yes: 'Yes', No: 'No', CannotDetermine: 'Cannot determine' };
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

  // Reusable diff renderer for Decision Point stages (Stage 5 now, Stage 9
  // later per spec §13). Deliberately generic: snapshotA/snapshotB are plain
  // A-E hypothesis maps and labelA/labelB are just labels for the caller to
  // attach meaning to (Stage 5 does not surface them visibly; a later stage
  // may). Never hardcode which snapshot is "initial" or "current" in here.
  //
  // Per spec §13, this must never emit: Correct, Incorrect, Right, Wrong,
  // Pass, Fail, Score. The template below cannot produce any of them, since
  // it only ever inserts a hypothesis name and one of the four
  // HYPOTHESIS_STATES values ('Leading', 'Plausible', 'Unresolved', 'Weak').
  function renderHypothesisDiff(container, snapshotA, snapshotB, labelA, labelB) {
    var ids = ['A', 'B', 'C', 'D', 'E'];
    var list = document.createElement('ul');
    list.className = 'mmc-hypothesis-diff';

    var changedCount = 0;
    ids.forEach(function (id) {
      if (snapshotA[id] === snapshotB[id]) return;
      changedCount += 1;
      var li = document.createElement('li');
      li.textContent = 'Your assessment of ' + MMC_DATA.hypotheses[id].name +
        ' moved from ' + snapshotA[id] + ' to ' + snapshotB[id] + '.';
      list.appendChild(li);
    });

    if (changedCount === 0) {
      var noChangeLi = document.createElement('li');
      noChangeLi.textContent = 'Your assessment did not change across any of the five hypotheses at this point.';
      list.appendChild(noChangeLi);
    }

    container.appendChild(list);
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

  // CaseTimeline. Renders all nine MMC_DATA.timelinePoints in order as a plain
  // <ol>, per spec §14: "At this stage only reveal timeline points already
  // known. Do not reveal future evidence details." A point whose id is not
  // yet in revealedPointIds renders visually empty: no label, no "locked"
  // placeholder text, nothing that hints at what the point is, since even a
  // structural title could spoil the investigation.
  //
  // The unrevealed <li> deliberately does NOT use aria-hidden="true": that
  // would remove it from the accessibility tree entirely, so a screen reader
  // user would hear a 5-item list while a sighted user sees a 9-slot list (5
  // filled, 4 dotted placeholders) - a real AT/sighted equivalence gap. Instead
  // it stays a real, empty list item and carries a visually-hidden span with
  // a neutral "Not yet revealed" label, so AT users get the same 9-item list
  // structure sighted users see, with a reason for the blank item, and zero
  // hint of the point's actual content. `data-revealed` (not aria-hidden) is
  // the CSS hook for the dotted placeholder styling, since data-* attributes
  // do not affect the accessibility tree.
  //
  // Deliberately a plain <ol> with no drag-and-drop or absolute positioning,
  // so ordinary document flow already makes it keyboard navigable.
  function renderCaseTimeline(container, revealedPointIds) {
    var ol = document.createElement('ol');
    ol.className = 'mmc-timeline';

    MMC_DATA.timelinePoints.forEach(function (point) {
      var li = document.createElement('li');
      if (revealedPointIds.indexOf(point.id) !== -1) {
        li.textContent = point.label;
      } else {
        li.setAttribute('data-revealed', 'false');
        var hiddenLabel = document.createElement('span');
        hiddenLabel.className = 'mmc-visually-hidden';
        hiddenLabel.textContent = 'Not yet revealed';
        li.appendChild(hiddenLabel);
      }
      ol.appendChild(li);
    });

    container.appendChild(ol);
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

  function renderStage5(container) {
    var state = getState();
    var data = MMC_DATA.stages[5];

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 5: Decision Point 01';
    wrapper.appendChild(heading);

    // --- What changed? ---
    var decisionSection = document.createElement('section');
    decisionSection.className = 'mmc-decision-point';

    data.intro.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      decisionSection.appendChild(p);
    });

    var diffHeading = document.createElement('h3');
    diffHeading.textContent = 'What changed?';
    decisionSection.appendChild(diffHeading);

    renderHypothesisDiff(
      decisionSection,
      state.hypothesisSnapshots.initial,
      state.hypothesisState,
      'Initial assessment',
      'Current assessment'
    );
    wrapper.appendChild(decisionSection);

    // --- Continue: confirmation only, no further gate. The practitioner
    // already made all required selections in Stages 2 and 4. ---
    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Confirm and continue';
    continueButton.addEventListener('click', function () {
      advanceStage();
    });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  // Tracks whether each of the three Stage 6 timeline controls (entryState,
  // prePaymentThreeState, changePoint) has been touched during this visit,
  // for the continue gate. Same shape and rationale as stage4Touched above:
  // module level so it survives every updateState re-render, null means "not
  // yet initialised this visit", reset to null on advance so a fresh visit
  // re-imposes the gate, bypassed on revisit via highestUnlockedStage > 6.
  var stage6Touched = null;

  function renderStage6(container) {
    var state = getState();
    var data = MMC_DATA.stages[6];

    if (stage6Touched === null) {
      stage6Touched = { entryState: false, prePaymentThreeState: false, changePoint: false };
      if (state.highestUnlockedStage > 6) {
        stage6Touched.entryState = true;
        stage6Touched.prePaymentThreeState = true;
        stage6Touched.changePoint = true;
      }
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 6: Evidence Inject 03';
    wrapper.appendChild(heading);

    // --- The messages change the picture ---
    var historySection = document.createElement('section');
    historySection.className = 'mmc-message-history';
    var historyHeading = document.createElement('h3');
    historyHeading.textContent = data.messageHistory.heading;
    historySection.appendChild(historyHeading);

    data.messageHistory.paragraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      historySection.appendChild(p);
    });

    var quote = document.createElement('p');
    var quoteStrong = document.createElement('strong');
    quoteStrong.textContent = data.messageHistory.quote;
    quote.appendChild(quoteStrong);
    historySection.appendChild(quote);

    data.messageHistory.paragraphsAfterQuote.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      historySection.appendChild(p);
    });
    wrapper.appendChild(historySection);

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

    // --- The Timeline Problem ---
    var problemSection = document.createElement('section');
    problemSection.className = 'mmc-timeline-problem';
    var problemHeading = document.createElement('h3');
    problemHeading.textContent = data.timelineProblem.heading;
    problemSection.appendChild(problemHeading);

    var problemIntro = document.createElement('p');
    problemIntro.textContent = data.timelineProblem.intro;
    problemSection.appendChild(problemIntro);

    var problemDisplay = document.createElement('p');
    problemDisplay.className = 'mmc-callout mmc-callout-prominent';
    var problemDisplayStrong = document.createElement('strong');
    problemDisplayStrong.textContent = data.timelineProblem.display;
    problemDisplay.appendChild(problemDisplayStrong);
    problemSection.appendChild(problemDisplay);
    wrapper.appendChild(problemSection);

    // --- Case timeline (persistent, progressive disclosure) ---
    var timelineSection = document.createElement('section');
    timelineSection.className = 'mmc-case-timeline';
    var timelineHeading = document.createElement('h3');
    timelineHeading.textContent = 'Case timeline';
    timelineSection.appendChild(timelineHeading);
    renderCaseTimeline(timelineSection, data.changePointQuestion.optionIds);
    wrapper.appendChild(timelineSection);

    // --- Timeline assessment ---
    var assessmentSection = document.createElement('section');
    assessmentSection.className = 'mmc-timeline-assessment';
    var assessmentHeading = document.createElement('h3');
    assessmentHeading.textContent = data.timelineAssessment.heading;
    assessmentSection.appendChild(assessmentHeading);

    var assessmentIntro = document.createElement('p');
    assessmentIntro.textContent = data.timelineAssessment.intro;
    assessmentSection.appendChild(assessmentIntro);

    data.timelineAssessment.questions.forEach(function (question) {
      var fieldset = document.createElement('fieldset');
      fieldset.className = 'mmc-timeline-question';

      var legend = document.createElement('legend');
      legend.textContent = question.label;
      fieldset.appendChild(legend);

      var optionsWrap = document.createElement('div');
      optionsWrap.className = 'mmc-hypothesis-options';
      TIMELINE_STATES.forEach(function (stateValue) {
        var inputId = 'tl-' + question.key + '-' + stateValue;
        var label = document.createElement('label');
        label.className = 'mmc-hypothesis-option';
        label.setAttribute('for', inputId);

        var input = document.createElement('input');
        input.type = 'radio';
        input.name = 'tl-' + question.key;
        input.id = inputId;
        input.value = stateValue;
        input.checked = state.knowledgeTimeline[question.key] === stateValue;
        // 'click' (not 'change'), same reasoning as the hypothesis board:
        // re-selecting an already-checked radio must still register as a
        // deliberate touch for the gate.
        input.addEventListener('click', function () {
          stage6Touched[question.key] = true;
          updateState(function (s) {
            s.knowledgeTimeline[question.key] = stateValue;
          });
        });

        label.appendChild(input);
        label.appendChild(document.createTextNode(TIMELINE_STATE_LABELS[stateValue]));
        optionsWrap.appendChild(label);
      });
      fieldset.appendChild(optionsWrap);
      assessmentSection.appendChild(fieldset);
    });

    var assessmentNote = document.createElement('p');
    assessmentNote.className = 'mmc-gate-note';
    assessmentNote.textContent = data.timelineAssessment.note;
    assessmentSection.appendChild(assessmentNote);

    // --- Change point question ---
    var changeFieldset = document.createElement('fieldset');
    changeFieldset.className = 'mmc-timeline-question';

    var changeLegend = document.createElement('legend');
    changeLegend.textContent = data.changePointQuestion.label;
    changeFieldset.appendChild(changeLegend);

    var changeOptionsWrap = document.createElement('div');
    changeOptionsWrap.className = 'mmc-hypothesis-options';
    data.changePointQuestion.optionIds.forEach(function (pointId) {
      var point = MMC_DATA.timelinePoints.filter(function (p) { return p.id === pointId; })[0];
      var inputId = 'tl-changePoint-' + pointId;
      var label = document.createElement('label');
      label.className = 'mmc-hypothesis-option';
      label.setAttribute('for', inputId);

      var input = document.createElement('input');
      input.type = 'radio';
      input.name = 'tl-changePoint';
      input.id = inputId;
      input.value = pointId;
      input.checked = state.knowledgeTimeline.changePoint === pointId;
      input.addEventListener('click', function () {
        stage6Touched.changePoint = true;
        updateState(function (s) {
          s.knowledgeTimeline.changePoint = pointId;
        });
      });

      label.appendChild(input);
      label.appendChild(document.createTextNode(point.label));
      changeOptionsWrap.appendChild(label);
    });
    changeFieldset.appendChild(changeOptionsWrap);
    assessmentSection.appendChild(changeFieldset);
    wrapper.appendChild(assessmentSection);

    // --- Gate note + continue button ---
    var gateNote = document.createElement('p');
    gateNote.className = 'mmc-gate-note';
    gateNote.textContent = data.gateNote;
    wrapper.appendChild(gateNote);

    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Record timeline assessment and continue';
    continueButton.addEventListener('click', function () {
      // Each radio already persists its own field via updateState the moment
      // it is clicked (see below), so by the time the gate allows this
      // button to be enabled all three fields are already saved. This just
      // advances, matching the Stage 4 continue handler's shape.
      stage6Touched = null;
      advanceStage();
    });
    continueButton.disabled = !['entryState', 'prePaymentThreeState', 'changePoint'].every(function (key) {
      return stage6Touched[key];
    });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  // Tracks which of the five hypotheses plus the two coercion decisions
  // (controlDecision, voluntarinessDecision) have been touched during this
  // visit to Stage 7, for the combined continue gate. Same shape and
  // rationale as stage6Touched above: module level so it survives every
  // updateState re-render, null means "not yet initialised this visit",
  // reset to null on advance so a fresh visit re-imposes the gate, bypassed
  // on revisit via highestUnlockedStage > 7 (the Stage 4/6 pattern).
  var stage7Touched = null;

  function renderStage7(container) {
    var state = getState();
    var data = MMC_DATA.stages[7];

    if (stage7Touched === null) {
      stage7Touched = {
        A: false, B: false, C: false, D: false, E: false,
        controlDecision: false, voluntarinessDecision: false
      };
      if (state.highestUnlockedStage > 7) {
        Object.keys(stage7Touched).forEach(function (key) { stage7Touched[key] = true; });
      }
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 7: Evidence Inject 04';
    wrapper.appendChild(heading);

    // --- Attempted disengagement ---
    var disengagementSection = document.createElement('section');
    disengagementSection.className = 'mmc-attempted-exit';
    var disengagementHeading = document.createElement('h3');
    disengagementHeading.textContent = 'Attempted disengagement';
    disengagementSection.appendChild(disengagementHeading);

    data.disengagement.paragraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      disengagementSection.appendChild(p);
    });

    var quoteOne = document.createElement('p');
    var quoteOneStrong = document.createElement('strong');
    quoteOneStrong.textContent = data.disengagement.quoteOne;
    quoteOne.appendChild(quoteOneStrong);
    disengagementSection.appendChild(quoteOne);

    data.disengagement.paragraphsAfterQuoteOne.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      disengagementSection.appendChild(p);
    });

    var quoteTwo = document.createElement('p');
    var quoteTwoStrong = document.createElement('strong');
    quoteTwoStrong.textContent = data.disengagement.quoteTwo;
    quoteTwo.appendChild(quoteTwoStrong);
    disengagementSection.appendChild(quoteTwo);

    data.disengagement.paragraphsAfterQuoteTwo.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      disengagementSection.appendChild(p);
    });
    wrapper.appendChild(disengagementSection);

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

    // --- Case timeline: wider reveal set (Stage 6's five points plus
    // attemptedExit, threats, paymentFour, intervention: all nine). ---
    var timelineSection = document.createElement('section');
    timelineSection.className = 'mmc-case-timeline';
    var timelineHeading = document.createElement('h3');
    timelineHeading.textContent = 'Case timeline';
    timelineSection.appendChild(timelineHeading);
    renderCaseTimeline(timelineSection, data.timelineRevealIds);
    wrapper.appendChild(timelineSection);

    // --- Coercion assessment: control and voluntariness are asked and
    // persisted as two genuinely separate controls, per spec §15 ("Do not
    // merge these questions"). Each is its own fieldset/radio group bound to
    // its own state field; neither handler ever reads or sets the other. ---
    var coercionSection = document.createElement('section');
    coercionSection.className = 'mmc-coercion-assessment';
    var coercionHeading = document.createElement('h3');
    coercionHeading.textContent = 'Coercion assessment';
    coercionSection.appendChild(coercionHeading);

    data.questions.forEach(function (question) {
      var fieldset = document.createElement('fieldset');
      fieldset.className = 'mmc-timeline-question';

      var legend = document.createElement('legend');
      legend.textContent = question.label;
      fieldset.appendChild(legend);

      var optionsWrap = document.createElement('div');
      optionsWrap.className = 'mmc-hypothesis-options';
      DECISION_VALUES.forEach(function (value) {
        var inputId = 'cq-' + question.key + '-' + value;
        var label = document.createElement('label');
        label.className = 'mmc-hypothesis-option';
        label.setAttribute('for', inputId);

        var input = document.createElement('input');
        input.type = 'radio';
        input.name = 'cq-' + question.key;
        input.id = inputId;
        input.value = value;
        input.checked = state[question.key] === value;
        // 'click' (not 'change'), same reasoning as the hypothesis board and
        // Stage 6's timeline controls: re-selecting an already-checked radio
        // must still register as a deliberate touch for the gate.
        input.addEventListener('click', function () {
          stage7Touched[question.key] = true;
          updateState(function (s) {
            s[question.key] = value;
          });
        });

        label.appendChild(input);
        label.appendChild(document.createTextNode(DECISION_VALUE_LABELS[value]));
        optionsWrap.appendChild(label);
      });
      fieldset.appendChild(optionsWrap);
      coercionSection.appendChild(fieldset);
    });

    var coercionCallout = document.createElement('p');
    coercionCallout.className = 'mmc-callout mmc-callout-prominent';
    var coercionCalloutStrong = document.createElement('strong');
    coercionCalloutStrong.textContent = data.coercionCallout;
    coercionCallout.appendChild(coercionCalloutStrong);
    coercionSection.appendChild(coercionCallout);
    wrapper.appendChild(coercionSection);

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

    // --- Hypothesis Board, editable, no suggested block ---
    var boardSection = document.createElement('section');
    boardSection.className = 'mmc-initial-assessment';
    var boardHeading = document.createElement('h3');
    boardHeading.textContent = 'Reassess the hypotheses';
    boardSection.appendChild(boardHeading);

    renderHypothesisBoard(boardSection, state, {
      onTouch: function (id) {
        stage7Touched[id] = true;
      }
    });
    wrapper.appendChild(boardSection);

    // --- Gate note + continue button ---
    var gateNote = document.createElement('p');
    gateNote.className = 'mmc-gate-note';
    gateNote.textContent = data.gateNote;
    wrapper.appendChild(gateNote);

    var continueButton = document.createElement('button');
    continueButton.type = 'button';
    continueButton.className = 'mmc-action';
    continueButton.textContent = 'Continue';
    continueButton.addEventListener('click', function () {
      // Each control already persists its own field via updateState the
      // moment it is set (see above), so by the time the gate allows this
      // button to be enabled everything is already saved. This just
      // advances, matching the Stage 4/6 continue handler's shape.
      stage7Touched = null;
      advanceStage();
    });
    continueButton.disabled = !['A', 'B', 'C', 'D', 'E', 'controlDecision', 'voluntarinessDecision'].every(function (key) {
      return stage7Touched[key];
    });
    wrapper.appendChild(continueButton);

    container.appendChild(wrapper);
  }

  function renderStage8(container) {
    var data = MMC_DATA.stages[8];

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 8: Evidence Inject 05';
    wrapper.appendChild(heading);

    // --- Independent corroboration ---
    var narrativeSection = document.createElement('section');
    narrativeSection.className = 'mmc-corroboration';
    var narrativeHeading = document.createElement('h3');
    narrativeHeading.textContent = data.narrative.heading;
    narrativeSection.appendChild(narrativeHeading);
    data.narrative.paragraphs.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      narrativeSection.appendChild(p);
    });
    wrapper.appendChild(narrativeSection);

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

    // --- Freeze notice: no further evidence follows this stage, per spec
    // §16 ("After this point, freeze evidence disclosure"). Reuses .mmc-callout,
    // the same "read this" narrative-note styling as Stages 3/4's framing and
    // core-message lines, rather than introducing a new visual language for
    // a single sentence. ---
    var freezeNote = document.createElement('p');
    freezeNote.className = 'mmc-callout';
    var freezeNoteStrong = document.createElement('strong');
    freezeNoteStrong.textContent = data.freezeNote;
    freezeNote.appendChild(freezeNoteStrong);
    wrapper.appendChild(freezeNote);

    // --- Continue: no gate. Nothing is recorded at this stage beyond
    // reading, per the brief. ---
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

  // Tracks which of the five hypotheses have been touched during this visit
  // to Stage 9's classify phase, for the continue gate. Same shape and
  // rationale as stage4Touched/stage7Touched above. Once the practitioner
  // confirms, hypothesisSnapshots.final is set and the stage moves into its
  // review phase, where this gate no longer applies, so there is no
  // highestUnlockedStage bypass to worry about here: a revisit can only ever
  // find final already set (review phase) or still null (classify phase,
  // gate re-imposed), never highestUnlockedStage > 9 with final still null.
  var stage9Touched = null;

  // Stage 9: Final Hypothesis Assessment. Two-phase render within the same
  // stage, per the brief: 'classify' (editable board, gated) then, once the
  // practitioner confirms, 'review' (read-only board plus the initial-versus-
  // final diff, then a second Continue that actually advances to Stage 10).
  // The phase is deliberately derived from state.hypothesisSnapshots.final on
  // every render rather than stored as its own persisted or module-level
  // flag: confirming sets `final` via updateState, which re-renders this
  // stage immediately, so the derived phase flips to 'review' on its own; a
  // later revisit via goToStage(9) re-derives the same phase from the same
  // persisted field, so it is never stale and never needs separate persistence.
  function renderStage9(container) {
    var state = getState();
    var data = MMC_DATA.stages[9];
    var phase = state.hypothesisSnapshots.final ? 'review' : 'classify';

    if (stage9Touched === null) {
      stage9Touched = { A: false, B: false, C: false, D: false, E: false };
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'mmc-section';

    var heading = document.createElement('h2');
    heading.textContent = 'Stage 9: Final Hypothesis Assessment';
    wrapper.appendChild(heading);

    data.intro.forEach(function (text) {
      var p = document.createElement('p');
      p.textContent = text;
      wrapper.appendChild(p);
    });

    // --- Hypothesis Board: editable while classifying, read-only once the
    // final snapshot has been confirmed. ---
    var boardSection = document.createElement('section');
    boardSection.className = 'mmc-initial-assessment';
    var boardHeading = document.createElement('h3');
    boardHeading.textContent = 'Final assessment';
    boardSection.appendChild(boardHeading);

    renderHypothesisBoard(boardSection, state, phase === 'review' ? { readOnly: true } : {
      onTouch: function (id) {
        stage9Touched[id] = true;
      }
    });
    wrapper.appendChild(boardSection);

    if (phase === 'classify') {
      var gateNote = document.createElement('p');
      gateNote.className = 'mmc-gate-note';
      gateNote.textContent = data.gateNote;
      wrapper.appendChild(gateNote);

      var confirmButton = document.createElement('button');
      confirmButton.type = 'button';
      confirmButton.className = 'mmc-action';
      confirmButton.textContent = 'Confirm final assessment';
      confirmButton.addEventListener('click', function () {
        updateState(function (s) {
          s.hypothesisSnapshots.final = {
            A: s.hypothesisState.A,
            B: s.hypothesisState.B,
            C: s.hypothesisState.C,
            D: s.hypothesisState.D,
            E: s.hypothesisState.E
          };
        });
        stage9Touched = null;
      });
      confirmButton.disabled = !['A', 'B', 'C', 'D', 'E'].every(function (id) { return stage9Touched[id]; });
      wrapper.appendChild(confirmButton);
    } else {
      // --- Review: initial versus final diff, per spec §17 (side by side
      // comparison, neutral language, FinCrimeRadar's own conclusion not yet
      // revealed). Reuses .mmc-decision-point/renderHypothesisDiff exactly as
      // Stage 5 does, just with a different pair of snapshots and labels. ---
      var decisionSection = document.createElement('section');
      decisionSection.className = 'mmc-decision-point';

      var diffHeading = document.createElement('h3');
      diffHeading.textContent = 'What changed?';
      decisionSection.appendChild(diffHeading);

      renderHypothesisDiff(
        decisionSection,
        state.hypothesisSnapshots.initial,
        state.hypothesisSnapshots.final,
        'Initial assessment',
        'Final assessment'
      );
      wrapper.appendChild(decisionSection);

      var continueButton = document.createElement('button');
      continueButton.type = 'button';
      continueButton.className = 'mmc-action';
      continueButton.textContent = 'Continue';
      continueButton.addEventListener('click', function () {
        advanceStage();
      });
      wrapper.appendChild(continueButton);
    }

    container.appendChild(wrapper);
  }

  var STAGE_RENDERERS = { 2: renderStage2, 3: renderStage3, 4: renderStage4, 5: renderStage5, 6: renderStage6, 7: renderStage7, 8: renderStage8, 9: renderStage9 };
  (function registerPlaceholderStages() {
    var stageNumber;
    for (stageNumber = 10; stageNumber <= 12; stageNumber += 1) {
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
