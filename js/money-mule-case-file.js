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

  function renderStage2Placeholder(container) {
    var heading = document.createElement('h2');
    heading.textContent = 'Stage 2 placeholder';
    container.appendChild(heading);

    var note = document.createElement('p');
    note.textContent = 'The Case Intake stage content is added in a later task.';
    container.appendChild(note);

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'mmc-action';
    button.textContent = 'Continue';
    button.addEventListener('click', function () {
      advanceStage();
    });
    container.appendChild(button);
  }

  var STAGE_RENDERERS = { 2: renderStage2Placeholder };
  (function registerPlaceholderStages() {
    var stageNumber;
    for (stageNumber = 3; stageNumber <= 12; stageNumber += 1) {
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
