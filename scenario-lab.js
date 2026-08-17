/**
 * FinCrimeRadar Scenario Lab
 * Self contained vanilla JS module. No framework, no build step dependency.
 * Ships against the static cases.json payload for Phase 0, per PRD section 7.
 *
 * Public entry point: initScenarioLab(rootEl, options)
 * options.apiBase  optional string, if set fetches `${apiBase}/scenario-lab/cases`
 *                   instead of the local /scenario-lab/data/cases.json file.
 *                   KYC, Fraud Detection, and Risk Scoring fall back to the
 *                   local file on a failed or slow (>15s) live fetch, see
 *                   fetchCases below, local/scenario-lab/data/cases.json
 *                   already contains all three modules' cases and stays the
 *                   resilience path even though apiBase is now always set to
 *                   the live Render service.
 */
(function () {
  "use strict";

  // No locked modules remain once Risk Scoring ships. appendNextModuleTeaser
  // already no-ops on an empty array, so this stays the single source of
  // truth for what's still "coming soon" without any other code needing to
  // change when the next module unlocks.
  const LOCKED_MODULES = [];

  // SAR Sandbox module. Has its own case picker, renderSarCasePicker, kept
  // separate from KYC/Fraud's renderCasePicker since SAR cases don't share
  // that picker's shape (entity_id/case_number/briefing) or its
  // correct/incorrect progress model, see the Phase 10 audit. It also has
  // no offline path: case data and scoring both come from
  // routes_sar_sandbox.py on the fincrimeradar-api service, there is no
  // local JSON fallback the way KYC/fraud cases have
  // scenario-lab/data/cases.json, so this module only works once
  // options.apiBase points at a reachable backend.

  function initScenarioLab(rootEl, options) {
    options = options || {};
    const state = {
      apiBase: options.apiBase || "",
      cases: [],
      kycCases: [],
      fraudCases: [],
      riskCases: [],
      caseIndex: 0,
      currentCase: null,
      nodeState: {}, // nodeId -> { identified: bool, screened: bool }
      selectedNodeId: null,
      riskToolOn: false,
      fuzzyThreshold: 50,
      pepHintOn: false,
      treeContainer: null,
      nodeDetail: null,
      maxRevealed: 0, // fraud module: highest evidence step revealed
      selected: 0, // fraud module: currently displayed step
      decisionMade: false, // fraud module: decision already committed for this case
      results: [], // { caseId, correct: bool }
      startedAt: null,
      currentModule: null, // "kyc" or "fraud", set by renderCasePicker
      requested: JSON.parse(localStorage.getItem("sl_requested_modules") || "{}"),
    };

    rootEl.innerHTML = "";
    rootEl.classList.add("scenario-lab");

    const header = document.createElement("div");
    header.className = "sl-header";
    header.innerHTML = [
      "<h1>Scenario Lab</h1>",
      "<p>Practice real AML investigation decisions. Identify entities, screen them against sanctions and PEP data, then decide.</p>",
    ].join("");
    rootEl.appendChild(header);

    const dashboard = document.createElement("div");
    dashboard.className = "sl-dashboard";
    rootEl.appendChild(dashboard);

    const workspace = document.createElement("div");
    workspace.className = "sl-workspace";
    rootEl.appendChild(workspace);

    state.dashboardEl = dashboard;

    fetchCases(options.apiBase)
      .then((cases) => {
        // Fraud cases carry an explicit "module" field; KYC's five original
        // cases predate that field, so its absence still means KYC rather
        // than requiring every existing case entry to be touched.
        state.kycCases = cases.filter((c) => (c.module || "kyc") === "kyc");
        state.fraudCases = cases.filter((c) => c.module === "fraud");
        state.riskCases = cases.filter((c) => c.module === "risk_scoring");
        renderDashboard(dashboard, workspace, state);
      })
      .catch((err) => {
        dashboard.innerHTML =
          '<p style="color:var(--sl-danger)">Scenario Lab could not load its case data. Refresh the page, or check the console for details.</p>';
        console.error("Scenario Lab load error:", err);
      });
  }

  const LOCAL_CASES_URL = "/scenario-lab/data/cases.json";
  const LIVE_CASES_TIMEOUT_MS = 15000;

  async function fetchCasesFrom(url, timeoutMs) {
    const controller = new AbortController();
    const timer = timeoutMs ? setTimeout(() => controller.abort(), timeoutMs) : null;
    try {
      const res = await fetch(url, { credentials: "omit", signal: controller.signal });
      if (!res.ok) throw new Error("Cases request failed with status " + res.status);
      const data = await res.json();
      if (!Array.isArray(data) || data.length === 0) {
        throw new Error("Cases payload was empty or malformed");
      }
      return data;
    } finally {
      if (timer) clearTimeout(timer);
    }
  }

  // KYC and Fraud Detection's own case data has no ongoing cost and no reason
  // to ever be unreachable just because the live Render service is cold,
  // rate limited elsewhere, or briefly down, so a failed or slow (>15s) live
  // fetch falls back to the local file, which already carries both modules'
  // cases. SAR Sandbox has no local data of its own, that's expected, its
  // own 429/502 handling in scenario-lab.js's SAR Sandbox section already
  // covers its live-only endpoints, this fallback is deliberately scoped to
  // fetchCases only.
  async function fetchCases(apiBase) {
    if (!apiBase) {
      return fetchCasesFrom(LOCAL_CASES_URL);
    }
    const liveUrl = apiBase.replace(/\/$/, "") + "/scenario-lab/cases";
    try {
      return await fetchCasesFrom(liveUrl, LIVE_CASES_TIMEOUT_MS);
    } catch (err) {
      console.error("Scenario Lab live case fetch failed, falling back to local data:", err);
      return fetchCasesFrom(LOCAL_CASES_URL);
    }
  }

  function renderDashboard(dashboard, workspace, state) {
    dashboard.innerHTML = "";

    const kycTile = document.createElement("div");
    kycTile.className = "sl-tile active";
    kycTile.innerHTML = [
      "<div>",
      "<h3>KYC and Sanctions Investigation</h3>",
      "<p>Build the ownership tree, screen every entity, then decide across five fixed cases.</p>",
      "</div>",
    ].join("");
    kycTile.addEventListener("click", () => startModule(dashboard, workspace, state));
    dashboard.appendChild(kycTile);

    const fraudTile = document.createElement("div");
    fraudTile.className = "sl-tile active";
    fraudTile.innerHTML = [
      "<div>",
      "<h3>Fraud Detection</h3>",
      "<p>Step through live account activity or cross-reference a set of facts, then decide across six cases.</p>",
      "</div>",
    ].join("");
    fraudTile.addEventListener("click", () => startFraudModule(dashboard, workspace, state));
    dashboard.appendChild(fraudTile);

    const sarTile = document.createElement("div");
    sarTile.className = "sl-tile active";
    sarTile.innerHTML = [
      "<div>",
      "<h3>SAR Writing Practice</h3>",
      "<p>Draft a practice Suspicious Activity Report against one case, then get fact-coverage feedback on your narrative.</p>",
      "</div>",
    ].join("");
    sarTile.addEventListener("click", () => startSarModule(dashboard, workspace, state));
    dashboard.appendChild(sarTile);

    const riskTile = document.createElement("div");
    riskTile.className = "sl-tile active";
    riskTile.innerHTML = [
      "<div>",
      "<h3>Risk Scoring</h3>",
      "<p>Weigh a profile of risk signals and choose the proportionate response, then see what was material and what was noise, across six cases.</p>",
      "</div>",
    ].join("");
    riskTile.addEventListener("click", () => startRiskModule(dashboard, workspace, state));
    dashboard.appendChild(riskTile);

    LOCKED_MODULES.forEach((mod) => {
      const tile = document.createElement("div");
      tile.className = "sl-tile locked";
      tile.innerHTML = [
        '<span class="sl-badge">Coming soon</span>',
        "<div>",
        "<h3>" + escapeHtml(mod.title) + "</h3>",
        "<p>" + escapeHtml(mod.description) + "</p>",
        "</div>",
      ].join("");
      appendRequestControl(tile, mod.key, state);
      dashboard.appendChild(tile);
    });
  }

  function appendRequestControl(container, moduleKey, state) {
    const alreadyRequested = !!state.requested[moduleKey];
    const btn = document.createElement("button");
    btn.className = "sl-request-btn";
    btn.textContent = alreadyRequested ? "Requested" : "Request this module";
    btn.disabled = alreadyRequested;
    btn.addEventListener("click", () => {
      fireRequestEvent(moduleKey);
      state.requested[moduleKey] = true;
      localStorage.setItem("sl_requested_modules", JSON.stringify(state.requested));
      btn.disabled = true;
      btn.textContent = "Requested";
      showInlineBanner(container);
    });
    container.appendChild(btn);
  }

  function showInlineBanner(container) {
    const existing = container.querySelector(".sl-inline-banner");
    if (existing) return;
    const banner = document.createElement("div");
    banner.className = "sl-inline-banner";
    banner.innerHTML =
      "<span>Ships to this dashboard when it is built.</span><button aria-label=\"Dismiss\">&times;</button>";
    banner.querySelector("button").addEventListener("click", () => banner.remove());
    container.appendChild(banner);
  }

  function fireRequestEvent(moduleKey) {
    if (typeof window.gtag === "function") {
      window.gtag("event", "scenario_request", { module: moduleKey });
    } else {
      console.info("scenario_request event (gtag unavailable):", moduleKey);
    }
  }

  // ---- Per-case progress, shared by both modules ----
  // Keyed by entity_id in localStorage, same persistence pattern as
  // sl_requested_modules. Read fresh on every call rather than cached on
  // state, the data is small and this guarantees the case picker never
  // shows stale status after a decision updates it.
  function readCaseProgress() {
    return JSON.parse(localStorage.getItem("sl_case_progress") || "{}");
  }

  function recordCaseProgress(entityId, correct) {
    const progress = readCaseProgress();
    progress[entityId] = { attempted: true, correct: correct };
    localStorage.setItem("sl_case_progress", JSON.stringify(progress));
  }

  function caseStatus(entityId) {
    const p = readCaseProgress()[entityId];
    if (!p || !p.attempted) return { label: "Not started", cls: "not-started" };
    if (p.correct) return { label: "Completed", cls: "completed" };
    return { label: "Attempted, review again", cls: "attempted" };
  }

  // "Sources: N" in the case header. No case carries literal cited-source
  // data (Scenario Lab cases are illustrative composites, not sourced
  // claims the way the guides are), so this counts the real structured
  // evidence the case's decision is actually grounded in: screening
  // records consulted for KYC cases, timeline steps for sequential fraud
  // cases, cross-reference facts for the simultaneous-fact cases.
  function caseSourceCount(c) {
    if (c.nodes) return c.nodes.filter((n) => n.screening != null).length;
    if (c.timeline) return c.timeline.length;
    if (c.cross_reference_facts) return c.cross_reference_facts.length;
    return 0;
  }

  // ---- Case picker, shared by both modules ----
  // Entry point for a module from the dashboard, and the destination of
  // "Back to case list" from mid-sequence. Free selection rather than a
  // forced 1-2-3 order: clicking any tile sets state.caseIndex directly
  // and hands off to that module's existing loadCase/loadFraudCase, so
  // auto-advance afterwards continues in array order from wherever the
  // analyst chose to start, exactly like the original sequential flow.
  function renderCasePicker(workspace, state, moduleKey) {
    state.currentModule = moduleKey;
    const cases =
      moduleKey === "kyc" ? state.kycCases : moduleKey === "fraud" ? state.fraudCases : state.riskCases;
    state.cases = cases;
    workspace.dataset.total = String(cases.length);

    workspace.innerHTML = "";
    const picker = document.createElement("div");
    picker.className = "sl-case-picker";
    const title =
      moduleKey === "kyc" ? "KYC and Sanctions Investigation" : moduleKey === "fraud" ? "Fraud Detection" : "Risk Scoring";
    picker.innerHTML = [
      "<h2>" + title + "</h2>",
      "<p>Choose any case to start. Progress on each one is saved on this device.</p>",
    ].join("");
    workspace.appendChild(picker);
    picker.prepend(backToDashboardButton(workspace, state));

    const grid = document.createElement("div");
    grid.className = "sl-case-grid";
    cases.forEach((c, idx) => {
      const status = caseStatus(c.entity_id);
      const tile = document.createElement("button");
      tile.type = "button";
      tile.className = "sl-case-tile";
      tile.innerHTML = [
        '<span class="sl-case-badge ' + status.cls + '">' + status.label + "</span>",
        "<h3>Case " + c.case_number + ": " + escapeHtml(c.title) + "</h3>",
        '<p class="sl-case-tile-briefing">' + escapeHtml(c.briefing) + "</p>",
      ].join("");
      tile.addEventListener("click", () => {
        state.caseIndex = idx;
        if (moduleKey === "kyc") {
          loadCase(workspace, state);
        } else if (moduleKey === "risk_scoring") {
          loadRiskCaseByLayout(workspace, state);
        } else {
          loadFraudCaseByLayout(workspace, state);
        }
      });
      grid.appendChild(tile);
    });
    picker.appendChild(grid);
  }

  // Returns to the case picker for whichever module is currently active,
  // without touching state.results so accuracy on the eventual completion
  // screen still reflects every decision made this session, not just ones
  // made in picker order.
  function backToCaseList(workspace, state) {
    renderCasePicker(workspace, state, state.currentModule);
  }

  // Rendered once a decision has been made, on every decide function across
  // every module: "Next case" is the primary action (advanceToNext runs
  // exactly what used to fire on a timer), "Back to case list" is secondary.
  // Advancing is always manual now, nothing here or elsewhere may schedule
  // a timer to do this automatically, see the standing note above the
  // Fraud Detection module section.
  function appendBackToCaseListControl(workspace, state, afterEl, advanceToNext) {
    const row = document.createElement("div");
    row.className = "sl-post-decision-controls";

    const nextBtn = document.createElement("button");
    nextBtn.className = "sl-btn";
    nextBtn.textContent = "Next case →";
    nextBtn.addEventListener("click", advanceToNext);
    row.appendChild(nextBtn);

    const backBtn = document.createElement("button");
    backBtn.className = "sl-request-btn";
    backBtn.textContent = "Back to case list";
    backBtn.addEventListener("click", () => backToCaseList(workspace, state));
    row.appendChild(backBtn);

    afterEl.insertAdjacentElement("afterend", row);
  }

  function startModule(dashboard, workspace, state) {
    state.results = [];
    state.startedAt = Date.now();
    dashboard.style.display = "none";
    workspace.classList.add("visible");
    renderCasePicker(workspace, state, "kyc");
  }

  function startRiskModule(dashboard, workspace, state) {
    state.results = [];
    state.startedAt = Date.now();
    dashboard.style.display = "none";
    workspace.classList.add("visible");
    renderCasePicker(workspace, state, "risk_scoring");
  }

  function loadCase(workspace, state) {
    const c = state.cases[state.caseIndex];
    state.currentCase = c;
    state.nodeState = {};
    state.selectedNodeId = null;
    state.riskToolOn = false;
    state.fuzzyThreshold = 50;
    state.pepHintOn = false;
    c.nodes.forEach((n) => {
      state.nodeState[n.id] = { identified: false, screened: false };
    });

    workspace.innerHTML = "";

    const caseHeader = document.createElement("div");
    caseHeader.className = "sl-case-header";
    caseHeader.innerHTML = [
      "<h2>Case " + c.case_number + " of " + workspace.dataset.total + ": " + escapeHtml(c.title) + "</h2>",
      "<p>" + escapeHtml(c.briefing) + "</p>",
      '<div class="sl-case-meta"><span>Entities: ' + c.nodes.length + "</span><span>Sources: " + caseSourceCount(c) + "</span></div>",
    ].join("");
    workspace.appendChild(caseHeader);

    const mainGrid = document.createElement("div");
    mainGrid.className = "sl-main-grid";
    workspace.appendChild(mainGrid);

    const treePanel = document.createElement("div");
    treePanel.className = "sl-tree-panel";
    treePanel.innerHTML = "<h3>Ownership structure</h3>";
    const svgHolder = document.createElement("div");
    treePanel.appendChild(svgHolder);
    const nodeDetail = document.createElement("div");
    nodeDetail.className = "sl-node-detail empty";
    nodeDetail.textContent = "Select a node to identify the entity.";
    treePanel.appendChild(nodeDetail);
    mainGrid.appendChild(treePanel);

    const toolsPanel = document.createElement("div");
    toolsPanel.className = "sl-tools-panel";
    mainGrid.appendChild(toolsPanel);

    state.treeContainer = svgHolder;
    state.nodeDetail = nodeDetail;

    renderTree(svgHolder, c, state, nodeDetail);
    renderToolsPanel(toolsPanel, c, state);

    const footer = document.createElement("div");
    footer.className = "sl-action-footer";
    workspace.appendChild(footer);

    const banner = document.createElement("div");
    banner.className = "sl-decision-banner";
    workspace.appendChild(banner);

    renderActionFooter(footer, banner, workspace, state, c);
  }

  // ---- Force directed layout, hand rolled, no external dependency ----
  //
  // Node captions render as full label text below each circle (see
  // renderTree), and SVG <text> never wraps on its own. The physics sim
  // below only ever knew about circle radii, not label width, so two
  // nodes with long labels (e.g. "Shareholder (Son of Designated
  // Official)") could end up close enough that their captions collided
  // even though the circles themselves never touched. SPRING_LENGTH now
  // scales with the longest label in the case, and a post-simulation
  // repair pass guarantees no two nodes end up closer than that floor,
  // regardless of how the spring/repulsion forces settled.
  function estimateMinSeparation(nodes) {
    const AVG_CHAR_WIDTH = 5.4; // conservative estimate at 12px DM Sans
    const maxLabelLen = nodes.reduce((max, n) => Math.max(max, (n.label || "").length), 8);
    return clamp(maxLabelLen * AVG_CHAR_WIDTH * 0.75, 90, 200);
  }

  function resolveMinSeparation(nodes, positions, minSeparation, width, height) {
    const REPAIR_PASSES = 12;
    for (let pass = 0; pass < REPAIR_PASSES; pass++) {
      let moved = false;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = positions[nodes[i].id];
          const b = positions[nodes[j].id];
          let dx = b.x - a.x;
          let dy = b.y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
          if (dist < minSeparation) {
            const push = (minSeparation - dist) / 2;
            dx /= dist;
            dy /= dist;
            a.x -= dx * push;
            a.y -= dy * push;
            b.x += dx * push;
            b.y += dy * push;
            moved = true;
          }
        }
      }
      nodes.forEach((n) => {
        const p = positions[n.id];
        p.x = Math.max(40, Math.min(width - 40, p.x));
        p.y = Math.max(40, Math.min(height - 40, p.y));
      });
      if (!moved) break;
    }
  }

  function computeLayout(nodes, edges, width, height) {
    const positions = {};
    nodes.forEach((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2;
      positions[n.id] = {
        x: width / 2 + Math.cos(angle) * (width / 4),
        y: height / 2 + Math.sin(angle) * (height / 4),
      };
    });

    const REPULSION = 2200;
    const minSeparation = estimateMinSeparation(nodes);
    const SPRING_LENGTH = Math.max(Math.min(width, height) * 0.32, minSeparation);
    const SPRING_STRENGTH = 0.02;
    const CENTER_STRENGTH = 0.01;
    const ITERATIONS = 250;

    for (let iter = 0; iter < ITERATIONS; iter++) {
      const forces = {};
      nodes.forEach((n) => (forces[n.id] = { x: 0, y: 0 }));

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = positions[nodes[i].id];
          const b = positions[nodes[j].id];
          let dx = a.x - b.x;
          let dy = a.y - b.y;
          let distSq = dx * dx + dy * dy || 0.01;
          const force = REPULSION / distSq;
          const dist = Math.sqrt(distSq);
          dx /= dist;
          dy /= dist;
          forces[nodes[i].id].x += dx * force;
          forces[nodes[i].id].y += dy * force;
          forces[nodes[j].id].x -= dx * force;
          forces[nodes[j].id].y -= dy * force;
        }
      }

      edges.forEach((e) => {
        const a = positions[e.from];
        const b = positions[e.to];
        if (!a || !b) return;
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const diff = dist - SPRING_LENGTH;
        dx /= dist;
        dy /= dist;
        const force = diff * SPRING_STRENGTH;
        forces[e.from].x += dx * force;
        forces[e.from].y += dy * force;
        forces[e.to].x -= dx * force;
        forces[e.to].y -= dy * force;
      });

      nodes.forEach((n) => {
        const p = positions[n.id];
        forces[n.id].x += (width / 2 - p.x) * CENTER_STRENGTH;
        forces[n.id].y += (height / 2 - p.y) * CENTER_STRENGTH;
      });

      nodes.forEach((n) => {
        const p = positions[n.id];
        p.x += forces[n.id].x;
        p.y += forces[n.id].y;
        p.x = Math.max(40, Math.min(width - 40, p.x));
        p.y = Math.max(40, Math.min(height - 40, p.y));
      });
    }

    resolveMinSeparation(nodes, positions, minSeparation, width, height);

    return positions;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  // Truncates textEl's content to fit within maxWidth, measured against the
  // font actually applied by CSS (so this adapts automatically to the
  // desktop vs. mobile font-size media query), rather than guessing from
  // character count. Returns the text actually rendered. textEl must
  // already be attached to the document, getBBox() needs live layout.
  function truncateToWidth(textEl, fullText, maxWidth) {
    textEl.textContent = fullText;
    if (textEl.getBBox().width <= maxWidth) return fullText;
    let lo = 0;
    let hi = fullText.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      textEl.textContent = fullText.slice(0, mid).trimEnd() + "…";
      if (textEl.getBBox().width <= maxWidth) {
        lo = mid;
      } else {
        hi = mid - 1;
      }
    }
    const truncated = lo > 0 ? fullText.slice(0, lo).trimEnd() + "…" : "…";
    textEl.textContent = truncated;
    return truncated;
  }

  // A screening match only surfaces when its confidence clears the current
  // fuzzy matching threshold. Below the threshold it reads as no match.
  function matchSurfaced(node, state) {
    if (!node.screening) return false;
    if (node.screening.result === "no_match") return false;
    return node.screening.match_confidence >= state.fuzzyThreshold;
  }

  // A node indicates a PEP connection when its screening data flags one,
  // whether via an explicit pep flag, a pep result, or a PEP list source.
  function isPepConnected(node) {
    const s = node.screening;
    if (!s) return false;
    if (s.pep === true) return true;
    if (typeof s.result === "string" && s.result.toLowerCase().indexOf("pep") !== -1) return true;
    if (typeof s.list_source === "string" && s.list_source.toUpperCase().indexOf("PEP") !== -1) return true;
    return false;
  }

  function renderTree(container, caseData, state, nodeDetail) {
    const width = 480;
    const height = 280;
    const positions = computeLayout(caseData.nodes, caseData.edges, width, height);

    // Distance from each node to its nearest neighbour caps how wide that
    // node's caption is allowed to render before truncating, so two
    // adjacent labels can never overlap regardless of length.
    const nearestDist = {};
    caseData.nodes.forEach((n) => {
      let min = Infinity;
      caseData.nodes.forEach((m) => {
        if (m.id === n.id) return;
        const dx = positions[n.id].x - positions[m.id].x;
        const dy = positions[n.id].y - positions[m.id].y;
        min = Math.min(min, Math.sqrt(dx * dx + dy * dy));
      });
      nearestDist[n.id] = Number.isFinite(min) ? min : width * 0.6;
    });

    const svgns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgns, "svg");
    svg.setAttribute("viewBox", "0 0 " + width + " " + height);
    svg.setAttribute("class", "sl-tree-svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Ownership structure diagram");

    // Text elements needing a post-attach measurement pass (getBBox only
    // returns real values once the SVG is in the live document), collected
    // while building so we do one pass at the end rather than re-querying.
    const captionJobs = [];
    const edgeLabelJobs = [];

    caseData.edges.forEach((e) => {
      const a = positions[e.from];
      const b = positions[e.to];
      if (!a || !b) return;
      const line = document.createElementNS(svgns, "line");
      line.setAttribute("x1", a.x);
      line.setAttribute("y1", a.y);
      line.setAttribute("x2", b.x);
      line.setAttribute("y2", b.y);
      line.setAttribute("class", "sl-edge-line");
      svg.appendChild(line);

      // Unit vector perpendicular to the line's actual angle, used below to
      // push the label off the stroke on diagonal edges too, not just
      // near-horizontal ones, and to search outward if that first position
      // still collides with a node caption once those are finalized.
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      const nx = -dy / len;
      const ny = dx / len;
      const baseX = (a.x + b.x) / 2;
      const baseY = (a.y + b.y) / 2;

      const halo = document.createElementNS(svgns, "rect");
      halo.setAttribute("class", "sl-edge-label-bg");
      svg.appendChild(halo);

      const label = document.createElementNS(svgns, "text");
      label.setAttribute("x", baseX + nx * 9);
      label.setAttribute("y", baseY + ny * 9);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("dominant-baseline", "central");
      label.setAttribute("class", "sl-edge-label");
      label.textContent = e.ownership_pct + "%";
      svg.appendChild(label);

      edgeLabelJobs.push({ label, halo, baseX, baseY, nx, ny });
    });

    caseData.nodes.forEach((n) => {
      const p = positions[n.id];
      const ns = state.nodeState[n.id];
      const g = document.createElementNS(svgns, "g");
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute("aria-label", "Entity node " + (ns.identified ? n.label : "unidentified"));

      // Native SVG tooltip, full label always available on hover/focus,
      // regardless of whether the on-canvas caption below ends up truncated.
      const title = document.createElementNS(svgns, "title");
      title.textContent = ns.identified ? n.label : "Unidentified entity";
      g.appendChild(title);

      const circle = document.createElementNS(svgns, "circle");
      circle.setAttribute("cx", p.x);
      circle.setAttribute("cy", p.y);
      circle.setAttribute("r", 26);
      let cls = "sl-node-circle";
      if (ns.identified) cls += " identified";
      if (ns.identified && n.flag === "shell_suspected") cls += " shell-flag";
      if (ns.screened) {
        cls += matchSurfaced(n, state) ? " screened-match" : " screened-clean";
      }
      circle.setAttribute("class", cls);
      g.appendChild(circle);

      if (ns.identified && n.flag === "shell_suspected") {
        const icon = document.createElementNS(svgns, "path");
        const d =
          "M " + (p.x - 9) + " " + (p.y + 34) + " l 9 -8 l 9 8";
        icon.setAttribute("d", d);
        icon.setAttribute("class", "sl-node-shell-icon");
        g.appendChild(icon);
      }

      const text = document.createElementNS(svgns, "text");
      text.setAttribute("x", p.x);
      text.setAttribute("y", p.y + 4);
      text.setAttribute("text-anchor", "middle");
      text.textContent = ns.identified ? initials(n.label) : "?";
      g.appendChild(text);

      const caption = document.createElementNS(svgns, "text");
      caption.setAttribute("x", p.x);
      caption.setAttribute("y", p.y + 44);
      caption.setAttribute("text-anchor", "middle");
      caption.setAttribute("class", "sl-edge-label");
      const fullCaption = ns.identified ? n.label : "Unidentified entity";
      caption.textContent = fullCaption;
      g.appendChild(caption);

      // Cap caption width at the gap to the nearest node, minus a small
      // clearance margin, floored and ceilinged to keep it legible.
      captionJobs.push({
        el: caption,
        full: fullCaption,
        maxWidth: clamp(nearestDist[n.id] - 16, 60, 170),
      });

      // PEP hint mode: reveal an inline badge on any node whose screening
      // data indicates a PEP connection, hidden when the toggle is off, and
      // never shown before the analyst has identified that node, otherwise
      // the tree would hand out the answer before any investigation happens.
      if (ns.identified && state.pepHintOn && isPepConnected(n)) {
        const badge = document.createElementNS(svgns, "text");
        badge.setAttribute("x", p.x + 30);
        badge.setAttribute("y", p.y - 22);
        badge.setAttribute("text-anchor", "middle");
        badge.setAttribute("class", "sl-pep-badge");
        badge.style.fill = "var(--sl-warning)";
        badge.style.fontSize = "9px";
        badge.style.fontWeight = "700";
        badge.textContent = "PEP";
        g.appendChild(badge);
      }

      g.style.cursor = "pointer";
      const select = () => selectNode(n.id, caseData, state, container, nodeDetail);
      g.addEventListener("click", select);
      g.addEventListener("keydown", (evt) => {
        if (evt.key === "Enter" || evt.key === " ") {
          evt.preventDefault();
          select();
        }
      });

      svg.appendChild(g);
    });

    container.innerHTML = "";
    container.appendChild(svg);

    // Measurement pass, only meaningful once the SVG is attached to the
    // live document so getBBox() reflects the font CSS actually applied
    // (desktop 12px vs. the mobile 20px media query bump). Captions are
    // truncated first, so their final boxes can be treated as fixed
    // obstacles when placing edge labels next, otherwise a short edge
    // between two nodes routinely lands its percentage label on top of
    // one of their captions.
    captionJobs.forEach((job) => truncateToWidth(job.el, job.full, job.maxWidth));

    const obstacles = caseData.nodes
      .map((n) => {
        const p = positions[n.id];
        return { x: p.x - 26, y: p.y - 26, width: 52, height: 52 };
      })
      .concat(
        captionJobs.map((job) => {
          const b = job.el.getBBox();
          return { x: b.x, y: b.y, width: b.width, height: b.height };
        })
      );

    // Compass directions searched at each radius, perpendicular-to-edge
    // first (keeps the common case visually tidy), then the remaining
    // compass points as fallback for geometries where the perpendicular
    // axis alone can't clear a wide caption sitting off to one side.
    function overlapArea(rect, o) {
      const ox = Math.max(0, Math.min(rect.x + rect.width, o.x + o.width) - Math.max(rect.x, o.x));
      const oy = Math.max(0, Math.min(rect.y + rect.height, o.y + o.height) - Math.max(rect.y, o.y));
      return ox * oy;
    }

    edgeLabelJobs.forEach((job) => {
      const size = job.label.getBBox(); // width/height only; stable under re-centering since anchor/baseline are both "middle"
      const halfW = size.width / 2 + 5;
      const halfH = size.height / 2 + 2;
      const directions = [
        { dx: job.nx, dy: job.ny },
        { dx: -job.nx, dy: -job.ny },
        { dx: 0, dy: -1 },
        { dx: 0, dy: 1 },
        { dx: 1, dy: 0 },
        { dx: -1, dy: 0 },
        { dx: 0.707, dy: -0.707 },
        { dx: -0.707, dy: -0.707 },
        { dx: 0.707, dy: 0.707 },
        { dx: -0.707, dy: 0.707 },
      ];
      // Ceiling is generous because the mobile media query renders this
      // same text noticeably larger within the same fixed viewBox, so
      // obstacles take up proportionally more room and need a wider
      // search radius to clear at that scale, not just at desktop size.
      const radii = [9, 16, 24, 34, 46, 60, 76, 94];

      let chosenX = job.baseX + job.nx * 9;
      let chosenY = job.baseY + job.ny * 9;
      let bestOverlap = Infinity;
      let found = false;

      for (let r = 0; r < radii.length && !found; r++) {
        for (let d = 0; d < directions.length; d++) {
          const x = job.baseX + directions[d].dx * radii[r];
          const y = job.baseY + directions[d].dy * radii[r];
          const rect = { x: x - halfW, y: y - halfH, width: halfW * 2, height: halfH * 2 };
          const totalOverlap = obstacles.reduce((sum, o) => sum + overlapArea(rect, o), 0);
          if (totalOverlap < bestOverlap) {
            bestOverlap = totalOverlap;
            chosenX = x;
            chosenY = y;
          }
          if (totalOverlap === 0) {
            found = true;
            break;
          }
        }
      }

      job.label.setAttribute("x", chosenX);
      job.label.setAttribute("y", chosenY);

      const box = job.label.getBBox();
      const padX = 5;
      const padY = 2;
      job.halo.setAttribute("x", box.x - padX);
      job.halo.setAttribute("y", box.y - padY);
      job.halo.setAttribute("width", box.width + padX * 2);
      job.halo.setAttribute("height", box.height + padY * 2);
      job.halo.setAttribute("rx", 3);
    });
  }

  function initials(label) {
    return label
      .split(" ")
      .map((w) => w[0])
      .join("")
      .slice(0, 3)
      .toUpperCase();
  }

  function selectNode(nodeId, caseData, state, treeContainer, nodeDetail) {
    state.selectedNodeId = nodeId;
    const ns = state.nodeState[nodeId];
    if (!ns.identified) {
      ns.identified = true;
    }
    renderTree(treeContainer, caseData, state, nodeDetail);
    renderNodeDetail(nodeDetail, caseData, state, nodeId);
    refreshActionFooterState(state);
    refreshRiskScore(state);
    refreshOwnershipAggregate(state);
  }

  function renderNodeDetail(nodeDetail, caseData, state, nodeId) {
    const node = caseData.nodes.find((n) => n.id === nodeId);
    const ns = state.nodeState[nodeId];
    nodeDetail.classList.remove("empty");
    nodeDetail.innerHTML = "";

    const title = document.createElement("h4");
    title.textContent = node.label;
    nodeDetail.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "sl-node-meta";
    const metaParts = [capitalize(node.type.replace(/_/g, " ")), node.jurisdiction];
    if (node.ownership_pct != null) metaParts.push(node.ownership_pct + "% ownership");
    if (node.flag === "shell_suspected") metaParts.push("Shell structure indicators present");
    meta.textContent = metaParts.join(" \u00b7 ");
    nodeDetail.appendChild(meta);

    if (node.screening === null) {
      const note = document.createElement("p");
      note.style.fontSize = "0.85rem";
      note.style.color = "var(--sl-text-muted)";
      note.textContent = "This entity has no screening requirement in this case.";
      nodeDetail.appendChild(note);
      return;
    }

    const screenBtn = document.createElement("button");
    screenBtn.className = "sl-btn";
    screenBtn.textContent = ns.screened ? "Screened" : "Screen this entity";
    screenBtn.disabled = ns.screened;
    screenBtn.addEventListener("click", () => {
      ns.screened = true;
      renderNodeDetail(nodeDetail, caseData, state, nodeId);
      // Re-render tree via closure is awkward here, so dispatch a custom event
      nodeDetail.dispatchEvent(new CustomEvent("sl:node-screened", { bubbles: true }));
    });
    nodeDetail.appendChild(screenBtn);

    if (ns.screened) {
      const result = document.createElement("div");
      const surfaced = matchSurfaced(node, state);
      result.className = "sl-screening-result " + (surfaced ? "match" : "clean");
      if (!surfaced) {
        result.textContent =
          node.screening.result === "no_match"
            ? "No match against sanctions or PEP data."
            : "No match surfaced at the current fuzzy matching threshold.";
      } else {
        result.innerHTML = [
          "Possible match, ",
          node.screening.match_confidence + "% confidence, ",
          "source: " + escapeHtml(node.screening.list_source) + ". ",
          "Customer DOB " + escapeHtml(node.screening.dob_customer) + " vs list DOB " + escapeHtml(node.screening.dob_match) + ".",
        ].join("");
      }
      nodeDetail.appendChild(result);
    }
  }

  function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  // ---- Investigation Tools panel, risk calculator ----
  function renderToolsPanel(container, caseData, state) {
    container.innerHTML = '<h3>Investigation tools</h3>';

    const toggleRow = document.createElement("div");
    toggleRow.className = "sl-toggle-row";
    toggleRow.innerHTML = "<span>Live risk score</span>";
    const toggle = document.createElement("div");
    toggle.className = "sl-toggle";
    toggle.setAttribute("role", "switch");
    toggle.setAttribute("aria-checked", "false");
    toggleRow.appendChild(toggle);
    container.appendChild(toggleRow);

    const scoreArea = document.createElement("div");
    scoreArea.style.display = "none";
    container.appendChild(scoreArea);

    toggle.addEventListener("click", () => {
      state.riskToolOn = !state.riskToolOn;
      toggle.classList.toggle("on", state.riskToolOn);
      toggle.setAttribute("aria-checked", String(state.riskToolOn));
      scoreArea.style.display = state.riskToolOn ? "block" : "none";
      if (state.riskToolOn) updateRiskScoreDisplay(scoreArea, caseData, state);
    });

    // Fuzzy matching threshold slider. Moving it recomputes, in real time,
    // which screened matches clear the confidence threshold and stay visible.
    const fuzzyRow = document.createElement("div");
    fuzzyRow.className = "sl-toggle-row";
    fuzzyRow.innerHTML = "<span>Fuzzy matching threshold</span>";
    const fuzzyValue = document.createElement("span");
    fuzzyValue.className = "sl-slider-value";
    fuzzyValue.textContent = state.fuzzyThreshold + "%";
    fuzzyRow.appendChild(fuzzyValue);
    container.appendChild(fuzzyRow);

    const fuzzySlider = document.createElement("input");
    fuzzySlider.type = "range";
    fuzzySlider.min = "0";
    fuzzySlider.max = "100";
    fuzzySlider.step = "1";
    fuzzySlider.value = String(state.fuzzyThreshold);
    fuzzySlider.className = "sl-slider";
    fuzzySlider.style.width = "100%";
    fuzzySlider.setAttribute("aria-label", "Fuzzy matching threshold");
    fuzzySlider.addEventListener("input", () => {
      state.fuzzyThreshold = Number(fuzzySlider.value);
      fuzzyValue.textContent = state.fuzzyThreshold + "%";
      refreshMatchVisibility(state);
    });
    container.appendChild(fuzzySlider);

    // PEP hint mode. Same switch pattern as the risk score toggle, reveals a
    // PEP badge in the tree for any node whose screening indicates a PEP link.
    const pepRow = document.createElement("div");
    pepRow.className = "sl-toggle-row";
    pepRow.innerHTML = "<span>PEP hint mode</span>";
    const pepToggle = document.createElement("div");
    pepToggle.className = "sl-toggle";
    pepToggle.setAttribute("role", "switch");
    pepToggle.setAttribute("aria-checked", "false");
    pepRow.appendChild(pepToggle);
    container.appendChild(pepRow);

    pepToggle.addEventListener("click", () => {
      state.pepHintOn = !state.pepHintOn;
      pepToggle.classList.toggle("on", state.pepHintOn);
      pepToggle.setAttribute("aria-checked", String(state.pepHintOn));
      refreshMatchVisibility(state);
    });

    // Aggregate listed ownership, Case 3 (risk-aggregate-ownership-103)
    // only: always visible when the case opts in, no manual toggle, since
    // it starts at 0% with nothing identified/screened yet and only grows
    // as the analyst actually screens each shareholder, the running total
    // is never shown ahead of the work that produces it.
    let aggregateArea = null;
    if (caseData.track_listed_ownership_aggregate) {
      const aggHeading = document.createElement("div");
      aggHeading.className = "sl-toggle-row";
      aggHeading.innerHTML = "<span>Aggregate listed ownership</span>";
      container.appendChild(aggHeading);

      aggregateArea = document.createElement("div");
      container.appendChild(aggregateArea);
    }

    container._scoreArea = scoreArea;
    container._caseData = caseData;
    container._aggregateArea = aggregateArea;
    state.toolsPanel = container;

    if (aggregateArea) updateOwnershipAggregateDisplay(aggregateArea, caseData, state);
  }

  // Sums ownership_pct across only the nodes the analyst has actually
  // screened AND whose result surfaces as a match at the current fuzzy
  // threshold, mirroring matchSurfaced's own gating exactly, so this never
  // credits a shareholder the analyst hasn't screened or one screening
  // cleared. Same .sl-risk-score visual component as the KYC calculator,
  // banded against the 50 percent aggregation threshold rather than the
  // calculator's points-based bands, the semantics differ (a percentage of
  // ownership, not an additive risk score) even though the look matches.
  function computeListedOwnershipAggregate(caseData, state) {
    let pct = 0;
    const breakdown = [];
    caseData.nodes.forEach((n) => {
      const ns = state.nodeState[n.id];
      if (!ns.screened || !matchSurfaced(n, state) || n.ownership_pct == null) return;
      pct += n.ownership_pct;
      breakdown.push(n.label + ": +" + n.ownership_pct + "%");
    });
    return { pct, breakdown };
  }

  function ownershipAggregateBand(pct) {
    if (pct >= 50) return "high";
    if (pct >= 25) return "medium";
    return "low";
  }

  function updateOwnershipAggregateDisplay(aggregateArea, caseData, state) {
    const { pct, breakdown } = computeListedOwnershipAggregate(caseData, state);
    aggregateArea.innerHTML = [
      '<div class="sl-risk-score ' + ownershipAggregateBand(pct) + '">' + pct + "%</div>",
      '<div class="sl-risk-breakdown">' +
        (breakdown.length ? breakdown.map(escapeHtml).join("<br>") : "No listed ownership identified yet.") +
        "</div>",
    ].join("");
  }

  function refreshOwnershipAggregate(state) {
    if (!state.toolsPanel || !state.toolsPanel._aggregateArea) return;
    updateOwnershipAggregateDisplay(state.toolsPanel._aggregateArea, state.toolsPanel._caseData, state);
  }

  // Re-render the tree and any open node detail so fuzzy threshold and PEP
  // hint changes take effect immediately, mirroring the risk score refresh.
  function refreshMatchVisibility(state) {
    if (!state.currentCase || !state.treeContainer) return;
    renderTree(state.treeContainer, state.currentCase, state, state.nodeDetail);
    if (state.selectedNodeId) {
      renderNodeDetail(state.nodeDetail, state.currentCase, state, state.selectedNodeId);
    }
  }

  function refreshRiskScore(state) {
    if (!state.riskToolOn || !state.toolsPanel) return;
    updateRiskScoreDisplay(state.toolsPanel._scoreArea, state.toolsPanel._caseData, state);
  }

  const JURISDICTION_RISK = {
    UK: 1,
    BVI: 4,
    default: 2,
  };

  function computeRiskScore(caseData, state) {
    let score = 0;
    const breakdown = [];
    caseData.nodes.forEach((n) => {
      const ns = state.nodeState[n.id];
      if (!ns.identified) return;
      const jRisk = JURISDICTION_RISK[n.jurisdiction] ?? JURISDICTION_RISK.default;
      score += jRisk;
      breakdown.push(n.label + " jurisdiction (" + n.jurisdiction + "): +" + jRisk);
      if (n.flag === "shell_suspected") {
        score += 5;
        breakdown.push(n.label + " shell structure indicator: +5");
      }
    });
    // Ownership layer depth, one point per edge in the identified graph
    const identifiedIds = new Set(
      caseData.nodes.filter((n) => state.nodeState[n.id].identified).map((n) => n.id)
    );
    const depthEdges = caseData.edges.filter(
      (e) => identifiedIds.has(e.from) && identifiedIds.has(e.to)
    ).length;
    if (depthEdges > 0) {
      score += depthEdges * 2;
      breakdown.push("Ownership layers identified: +" + depthEdges * 2);
    }
    return { score, breakdown };
  }

  function bandForScore(score) {
    if (score >= 12) return "high";
    if (score >= 6) return "medium";
    return "low";
  }

  // Shared by the KYC tree's live risk score toggle and Risk Scoring's
  // Case 4 signal panel below: same score dial, same band colours, same
  // breakdown list, whether the score comes from ownership/jurisdiction
  // data (computeRiskScore) or a flat list of case-supplied flags
  // (computeSignalScore). Only the score source differs.
  function renderRiskScoreDisplay(scoreArea, score, breakdown) {
    scoreArea.innerHTML = [
      '<div class="sl-risk-score ' + bandForScore(score) + '">' + score + "</div>",
      '<div class="sl-risk-breakdown">' + breakdown.map(escapeHtml).join("<br>") + "</div>",
    ].join("");
  }

  // Case 4's naive additive model: every flag in caseData.risk_signals just
  // adds its points, no jurisdiction/ownership logic involved, deliberately
  // mirroring the false precision the case is built to critique.
  function computeSignalScore(signals) {
    let score = 0;
    const breakdown = [];
    signals.forEach((s) => {
      score += s.points;
      breakdown.push(s.label + ": +" + s.points);
    });
    return { score, breakdown };
  }

  function updateRiskScoreDisplay(scoreArea, caseData, state) {
    const { score, breakdown } = computeRiskScore(caseData, state);
    renderRiskScoreDisplay(scoreArea, score, breakdown);
  }

  // ---- Action footer, disposition logic ----
  const DEFAULT_KYC_DISPOSITIONS = [
    { key: "approve", label: "Approve" },
    { key: "reject", label: "Reject" },
    { key: "request_more_info", label: "Request more information" },
  ];

  function nodesRequiringScreening(caseData) {
    return caseData.nodes.filter((n) => n.screening !== null);
  }

  function allRequiredScreeningsDone(caseData, state) {
    return nodesRequiringScreening(caseData).every((n) => state.nodeState[n.id].screened);
  }

  function renderActionFooter(footer, banner, workspace, state, caseData) {
    footer.innerHTML = "";
    const label = document.createElement("span");
    label.style.color = "var(--sl-text-muted)";
    label.style.fontSize = "0.85rem";
    label.textContent = allRequiredScreeningsDone(caseData, state)
      ? "All required screening complete. Make your decision."
      : "Identify and screen every flagged entity before deciding.";
    footer.appendChild(label);

    const btnRow = document.createElement("div");
    btnRow.className = "sl-action-buttons";
    // KYC's five original cases carry no disposition_options field, so the
    // three-way approve/reject/request-more-info default covers them
    // unchanged. Risk Scoring's Case 3 supplies its own four-option graded
    // set (Standard/EDD/Escalate to MLRO/Block or SAR) via disposition_options,
    // same shape the cross-reference cases already use.
    const dispositions = caseData.disposition_options || DEFAULT_KYC_DISPOSITIONS;
    dispositions.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "sl-btn";
      btn.textContent = opt.label;
      btn.disabled = !allRequiredScreeningsDone(caseData, state);
      btn.addEventListener("click", () => decide(opt.key, footer, banner, workspace, state, caseData));
      btnRow.appendChild(btn);
    });
    footer.appendChild(btnRow);

    footer._label = label;
    footer._caseData = caseData;

    // Listen for screening completions bubbling up from node detail cards.
    // Guarded so this attaches once per workspace element, not once per case load.
    if (!workspace._slScreeningListenerAttached) {
      workspace.addEventListener("sl:node-screened", () => {
        refreshActionFooterState(state);
        refreshOwnershipAggregate(state);
      });
      workspace._slScreeningListenerAttached = true;
    }
  }

  function refreshActionFooterState(state) {
    // Re-render is triggered from the sl:node-screened listener context;
    // find the current footer in the DOM and update its buttons directly.
    document.querySelectorAll(".sl-action-footer").forEach((footer) => {
      const caseData = footer._caseData;
      if (!caseData) return;
      const ready = allRequiredScreeningsDone(caseData, state);
      footer.querySelectorAll("button").forEach((b) => (b.disabled = !ready));
      if (footer._label) {
        footer._label.textContent = ready
          ? "All required screening complete. Make your decision."
          : "Identify and screen every flagged entity before deciding.";
      }
    });
  }

  // Renders caseData.related_guide, if present, as a small secondary card
  // inside the decision banner, below the rationale text. Deliberately
  // muted relative to the correct/incorrect feedback itself, this is a
  // pointer to further reading, not part of the verdict.
  function appendRelatedGuide(banner, caseData) {
    const guide = caseData.related_guide;
    if (!guide) return;
    const card = document.createElement("div");
    card.className = "sl-related-guide";
    card.innerHTML =
      '<span class="sl-related-guide-label">Related guide</span>' +
      '<a class="sl-related-guide-link" href="' + escapeHtml(guide.url) + '">' + escapeHtml(guide.title) + "</a>" +
      '<p class="sl-related-guide-reason">' + escapeHtml(guide.reason) + "</p>";
    banner.appendChild(card);
  }

  function decide(disposition, footer, banner, workspace, state, caseData) {
    const isCorrect = caseData.correct_disposition.includes(disposition);

    state.results.push({ caseId: caseData.entity_id, correct: isCorrect });
    recordCaseProgress(caseData.entity_id, isCorrect);

    banner.className = "sl-decision-banner show " + (isCorrect ? "correct" : "incorrect");
    banner.textContent = (isCorrect ? "Correct. " : "Not quite. ") + caseData.rationale;
    appendRelatedGuide(banner, caseData);

    footer.querySelectorAll("button").forEach((b) => (b.disabled = true));

    appendBackToCaseListControl(workspace, state, banner, () => advanceToNextCase(workspace, state));
  }

  // Every decide function's "Next case" callback funnels through here so
  // state.currentModule (set by renderCasePicker) decides which loader and
  // completion screen to advance to, rather than each decide function
  // hardcoding its own module's pair. Keeps decide()/decideFraud()/
  // decideCrossReference() reusable across modules instead of each one only
  // ever knowing how to advance its own original module.
  function advanceToNextCase(workspace, state) {
    state.caseIndex += 1;
    if (state.caseIndex < state.cases.length) {
      if (state.currentModule === "kyc") loadCase(workspace, state);
      else if (state.currentModule === "risk_scoring") loadRiskCaseByLayout(workspace, state);
      else loadFraudCaseByLayout(workspace, state);
    } else {
      if (state.currentModule === "kyc") renderCompletionScreen(workspace, state);
      else if (state.currentModule === "risk_scoring") renderRiskCompletionScreen(workspace, state);
      else renderFraudCompletionScreen(workspace, state);
    }
  }

  // Returns to the dashboard from a completion screen, re-rendering it so
  // any "Requested" state picked up since page load still shows correctly.
  // Needed now that two modules are reachable from the same dashboard:
  // without it, finishing one module would strand the analyst on its
  // completion card with no way back to the other.
  function backToDashboardButton(workspace, state) {
    const btn = document.createElement("button");
    btn.className = "sl-request-btn";
    btn.textContent = "Back to dashboard";
    btn.style.marginBottom = "16px";
    btn.addEventListener("click", () => {
      workspace.classList.remove("visible");
      workspace.innerHTML = "";
      state.dashboardEl.style.display = "";
      renderDashboard(state.dashboardEl, workspace, state);
    });
    return btn;
  }

  // What's still locked after finishing a module. Reads LOCKED_MODULES
  // directly rather than naming a specific module, so this stays correct
  // on its own as modules unlock over time.
  function appendNextModuleTeaser(container, state) {
    if (LOCKED_MODULES.length === 0) return;
    const mod = LOCKED_MODULES[0];
    const nextTile = document.createElement("div");
    nextTile.className = "sl-tile locked";
    nextTile.style.marginTop = "16px";
    nextTile.innerHTML = [
      '<span class="sl-badge">Coming soon</span>',
      "<div><h3>" + escapeHtml(mod.title) + "</h3><p>" + escapeHtml(mod.description) + "</p></div>",
    ].join("");
    appendRequestControl(nextTile, mod.key, state);
    container.appendChild(nextTile);
  }

  function pickUpRestButton(workspace, state, moduleKey) {
    const btn = document.createElement("button");
    btn.className = "sl-btn";
    btn.textContent = "Pick up the rest";
    btn.style.marginTop = "16px";
    btn.addEventListener("click", () => renderCasePicker(workspace, state, moduleKey));
    return btn;
  }

  // Shared by both completion screens. The case picker means a session can
  // now end here after only some of the module's cases, not just after all
  // of them in order, so this only ever calls it "complete" when every case
  // in the module was actually attempted this session (results.length vs.
  // state.cases.length, not just having reached the end of the array via
  // auto-advance). Otherwise the heading, copy, and stats are honest about
  // a partial session, and a direct link back to the picker covers the rest.
  function renderCompletionBody(complete, workspace, state, moduleKey, fullIntro) {
    // A re-attempted case (via "Back to case list") pushes a second result
    // for the same entity_id, so dedupe here, most recent attempt wins,
    // before computing accuracy/attempted stats.
    const deduped = Array.from(
      state.results.reduce((map, r) => map.set(r.caseId, r), new Map()).values()
    );
    const attempted = deduped.length;
    const totalCases = state.cases.length;
    const correct = deduped.filter((r) => r.correct).length;
    const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;
    const elapsedSeconds = Math.round((Date.now() - state.startedAt) / 1000);
    const minutes = Math.floor(elapsedSeconds / 60);
    const seconds = elapsedSeconds % 60;
    const isFullSession = attempted >= totalCases;

    const heading = isFullSession
      ? moduleKey === "kyc"
        ? "Module complete"
        : "Session complete"
      : "Cases complete for this session";

    const remaining = totalCases - attempted;
    const intro = isFullSession
      ? fullIntro
      : attempted +
        " of " +
        totalCases +
        " cases attempted this session, " +
        remaining +
        " case" +
        (remaining === 1 ? "" : "s") +
        " still untried.";

    complete.innerHTML = [
      "<h2>" + heading + "</h2>",
      "<p>" + intro + "</p>",
      '<div class="sl-stats">',
      '<div><div class="sl-stat-value">' + accuracy + '%</div><div class="sl-stat-label">Accuracy</div></div>',
      '<div><div class="sl-stat-value">' +
        minutes +
        "m " +
        seconds +
        's</div><div class="sl-stat-label">Time elapsed</div></div>',
      "</div>",
    ].join("");

    if (!isFullSession) {
      complete.appendChild(pickUpRestButton(workspace, state, moduleKey));
    }
  }

  function renderCompletionScreen(workspace, state) {
    workspace.innerHTML = "";
    const complete = document.createElement("div");
    complete.className = "sl-complete";
    workspace.appendChild(complete);
    renderCompletionBody(complete, workspace, state, "kyc", "KYC and Sanctions Investigation, all five cases.");
    complete.prepend(backToDashboardButton(workspace, state));
    appendNextModuleTeaser(complete, state);
  }

  // ---- Fraud Detection module ----
  // Mounted from the same dashboard and workspace shell as the KYC module
  // above, reusing its sl-tree-panel/sl-tools-panel card shells, sl-btn
  // buttons, sl-node-detail wrapper, and sl-decision-banner feedback rather
  // than a second copy of any of them. A fraud case is a sequence of
  // evidence events with a decision at the end, not a relationship graph,
  // so it carries its own header_scene and timeline fields in cases.json
  // instead of nodes/edges, while still using the shared entity_id,
  // case_number, correct_disposition, rationale and related_guide fields
  // KYC's cases already use. related_guide is optional: { title, url, reason },
  // rendered as a secondary card under the decision banner when present.
  // Future cases (Risk Scoring, Cases 5/6) should follow the same
  // related_guide shape. Cases are told apart by the "module" field split out in
  // initScenarioLab. Only genuinely new UI, the header scene, the evidence
  // stepper, and the risk bar, gets its own fd- prefixed rules in
  // scenario-lab.css, and those still reference the --sl- custom
  // properties directly rather than a parallel token layer.
  //
  // Standing standard, applies to every module, not just this one: no
  // decide function may auto-advance to the next case on a timer. Every
  // decide function (KYC's decide(), decideFraud(), decideCrossReference(),
  // and any future module's own decide function, Risk Scoring included)
  // must call appendBackToCaseListControl with an advanceToNext callback
  // and let the analyst click "Next case" themselves. Do not reintroduce
  // a setTimeout here.

  function startFraudModule(dashboard, workspace, state) {
    state.results = [];
    state.startedAt = Date.now();
    dashboard.style.display = "none";
    workspace.classList.add("visible");
    renderCasePicker(workspace, state, "fraud");
  }

  function loadFraudCase(workspace, state) {
    const c = state.cases[state.caseIndex];
    state.currentCase = c;
    state.maxRevealed = 0;
    state.selected = 0;
    state.decisionMade = false;

    workspace.innerHTML = "";

    const caseHeader = document.createElement("div");
    caseHeader.className = "sl-case-header";
    caseHeader.innerHTML = [
      "<h2>Case " + c.case_number + ": " + escapeHtml(c.title) + "</h2>",
      "<p>" + escapeHtml(c.briefing) + "</p>",
      '<div class="sl-case-meta"><span>Sources: ' + caseSourceCount(c) + "</span></div>",
    ].join("");
    workspace.appendChild(caseHeader);

    // The header scene sits above the timeline and stays fixed through
    // every step and the final decision, so it is rendered once here and
    // never touched again by the stepper below.
    const scenePanel = document.createElement("div");
    scenePanel.className = "sl-tree-panel";
    workspace.appendChild(scenePanel);
    renderHeaderScene(scenePanel, c.header_scene);

    const timelinePanel = document.createElement("div");
    timelinePanel.className = "sl-tools-panel";
    workspace.appendChild(timelinePanel);

    const stepperEl = document.createElement("div");
    stepperEl.className = "fd-stepper";
    timelinePanel.appendChild(stepperEl);

    const riskPanel = document.createElement("div");
    riskPanel.className = "fd-risk-panel";
    riskPanel.innerHTML = [
      '<div class="fd-risk-row"><span class="fd-risk-caption">Risk signal</span><span class="fd-risk-value"></span></div>',
      '<div class="fd-risk-track"><div class="fd-risk-fill"></div></div>',
    ].join("");
    timelinePanel.appendChild(riskPanel);

    const bodyEl = document.createElement("div");
    bodyEl.className = "sl-node-detail";
    timelinePanel.appendChild(bodyEl);

    state.stepperEl = stepperEl;
    state.riskPanel = riskPanel;
    state.bodyEl = bodyEl;
    state.workspace = workspace;

    renderFraudStepper(state);
    renderFraudRisk(state);
    renderFraudStepBody(state);
  }

  // Cases 5/6 are a set of facts that all exist simultaneously rather than
  // a sequence, so they carry "layout": "cross_reference" and route to the
  // fact card grid below instead of the timeline stepper. Every other fraud
  // case has no "layout" field and keeps using the stepper, which is why
  // every load/advance path calls this dispatcher rather than loadFraudCase
  // directly.
  function loadFraudCaseByLayout(workspace, state) {
    const c = state.cases[state.caseIndex];
    if (c.layout === "cross_reference") {
      loadCrossReferenceCase(workspace, state);
    } else {
      loadFraudCase(workspace, state);
    }
  }

  // Risk Scoring's Case 3 (aggregate ownership) carries "layout":
  // "ownership_tree" and reuses the KYC module's loadCase unchanged, nodes,
  // edges, and screening already there. Every other Risk Scoring case
  // reuses the cross-reference fact-card component above, same as Fraud's
  // Cases 5/6, per docs/risk-scoring-module-spec.md's component reuse map.
  function loadRiskCaseByLayout(workspace, state) {
    const c = state.cases[state.caseIndex];
    if (c.layout === "ownership_tree") {
      loadCase(workspace, state);
    } else {
      loadCrossReferenceCase(workspace, state);
    }
  }

  // Nodes are grouped into columns by topological depth, how many hops
  // from a node with no incoming edge, so a fan-in shape, several sources
  // converging on one node, works the same as a simple chain without any
  // bespoke per-case layout code.
  function computeSceneColumns(nodes, edges) {
    const incoming = {};
    nodes.forEach((n) => (incoming[n.id] = []));
    edges.forEach((e) => {
      if (incoming[e.to]) incoming[e.to].push(e.from);
    });

    const levelCache = {};
    function levelOf(id) {
      if (levelCache[id] != null) return levelCache[id];
      const preds = incoming[id] || [];
      const lvl = preds.length === 0 ? 0 : 1 + Math.max.apply(null, preds.map(levelOf));
      levelCache[id] = lvl;
      return lvl;
    }
    nodes.forEach((n) => levelOf(n.id));

    const columns = [];
    nodes.forEach((n) => {
      const lvl = levelCache[n.id];
      if (!columns[lvl]) columns[lvl] = [];
      columns[lvl].push(n);
    });
    return columns;
  }

  function renderHeaderScene(container, scene) {
    const svgns = "http://www.w3.org/2000/svg";
    const width = 640;
    const columns = computeSceneColumns(scene.nodes, scene.edges);
    const maxColumnSize = columns.reduce((max, col) => Math.max(max, col.length), 1);
    // 76px keeps a stacked column's caption (node radius 20 + label at +34
    // + sublabel at +47) clear of the next node's circle, which starts at
    // +ROW_HEIGHT-20. Anything under about 71px causes the sublabel text
    // to visually collide with the circle below it.
    const ROW_HEIGHT = 76;
    const MARGIN_Y = 34;
    const height = Math.max(160, maxColumnSize * ROW_HEIGHT + MARGIN_Y * 2 - ROW_HEIGHT);

    const positions = {};
    const marginX = 76;
    const colSpacing = columns.length > 1 ? (width - marginX * 2) / (columns.length - 1) : 0;
    columns.forEach((col, colIndex) => {
      const x = columns.length > 1 ? marginX + colIndex * colSpacing : width / 2;
      const rowSpacing = col.length > 1 ? (height - MARGIN_Y * 2) / (col.length - 1) : 0;
      col.forEach((n, rowIndex) => {
        const y = col.length > 1 ? MARGIN_Y + rowIndex * rowSpacing : height / 2;
        positions[n.id] = { x: x, y: y };
      });
    });

    const svg = document.createElementNS(svgns, "svg");
    svg.setAttribute("viewBox", "0 0 " + width + " " + height);
    svg.setAttribute("class", "sl-tree-svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Case overview diagram");

    const defs = document.createElementNS(svgns, "defs");
    defs.innerHTML =
      '<marker id="fd-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M0,0L10,5L0,10z" class="fd-scene-arrow-fill"></path></marker>';
    svg.appendChild(defs);

    scene.edges.forEach((e) => {
      const a = positions[e.from];
      const b = positions[e.to];
      if (!a || !b) return;
      const r = 20;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      const ux = dx / len;
      const uy = dy / len;

      const line = document.createElementNS(svgns, "line");
      line.setAttribute("x1", a.x + ux * r);
      line.setAttribute("y1", a.y + uy * r);
      line.setAttribute("x2", b.x - ux * (r + 8));
      line.setAttribute("y2", b.y - uy * (r + 8));
      line.setAttribute("class", "sl-edge-line fd-scene-edge-line");
      svg.appendChild(line);

      if (e.label) {
        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2 - 10;
        const label = document.createElementNS(svgns, "text");
        label.setAttribute("x", midX);
        label.setAttribute("y", midY);
        label.setAttribute("text-anchor", "middle");
        label.setAttribute("class", "sl-edge-label");
        label.textContent = e.label;
        svg.appendChild(label);
      }
    });

    scene.nodes.forEach((n) => {
      const p = positions[n.id];
      const color = n.color || "teal";

      const circle = document.createElementNS(svgns, "circle");
      circle.setAttribute("cx", p.x);
      circle.setAttribute("cy", p.y);
      circle.setAttribute("r", 20);
      circle.setAttribute("class", "fd-scene-node-circle " + color);
      svg.appendChild(circle);

      const icon = document.createElementNS(svgns, "path");
      icon.setAttribute("d", sceneIconPath(color, p.x, p.y));
      icon.setAttribute("class", "fd-scene-node-icon " + color);
      svg.appendChild(icon);

      const label = document.createElementNS(svgns, "text");
      label.setAttribute("x", p.x);
      label.setAttribute("y", p.y + 34);
      label.setAttribute("class", "fd-scene-label");
      label.textContent = n.label;
      svg.appendChild(label);

      if (n.sublabel) {
        const sub = document.createElementNS(svgns, "text");
        sub.setAttribute("x", p.x);
        sub.setAttribute("y", p.y + 47);
        sub.setAttribute("class", "fd-scene-sublabel");
        sub.textContent = n.sublabel;
        svg.appendChild(sub);
      }
    });

    container.innerHTML = "";
    container.appendChild(svg);
  }

  // Small glyph per node color: a person mark for a clean or neutral
  // entity (teal), a document mark for an account or holding entity under
  // review (amber), an alert mark for the escalated outcome (red).
  // Coordinates are offsets from the node's own center.
  function sceneIconPath(color, cx, cy) {
    if (color === "amber") {
      return (
        "M " + (cx - 6) + " " + (cy - 6) + " h 12 v 12 h -12 z " +
        "M " + (cx - 6) + " " + (cy - 2) + " h 12"
      );
    }
    if (color === "red") {
      return (
        "M " + cx + " " + (cy - 7) + " l 7 12 h -14 z " +
        "M " + cx + " " + (cy - 1) + " v 3 " +
        "M " + cx + " " + (cy + 4) + " v 0.5"
      );
    }
    return (
      "M " + cx + " " + (cy - 7) + " a 3 3 0 1 1 0.01 0 z " +
      "M " + (cx - 6) + " " + (cy + 7) + " a 6 6 0 0 1 12 0"
    );
  }

  const FRAUD_STEP_ICONS = {
    login:
      '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/>',
    transfer:
      '<path d="M17 3l4 4-4 4"/><path d="M21 7H8a4 4 0 0 0-4 4v1"/><path d="M7 21l-4-4 4-4"/><path d="M3 17h13a4 4 0 0 0 4-4v-1"/>',
    device: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    message: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    cash: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>',
    decision: '<path d="M4 22V4a1 1 0 0 1 1-1h12l-2 5 2 5H7a1 1 0 0 0-1 1v8"/>',
    id: '<rect x="2" y="4" width="20" height="16" rx="2"/><circle cx="8" cy="10" r="2"/><path d="M5 17c0-1.7 1.3-3 3-3s3 1.3 3 3"/><path d="M14 9h6M14 13h4"/>',
    home: '<path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    biometric: '<circle cx="12" cy="12" r="9"/><path d="M8 13a4 4 0 0 1 8 0"/><path d="M12 13v5"/><path d="M9.5 8.5a3.5 3.5 0 0 1 5 0"/>',
    credit: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/>',
    pattern: '<path d="M12 2l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    network: '<circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="19" r="2.5"/><path d="M6.8 8.2L10.5 16.8M17.2 8.2L13.5 16.8"/>',
  };

  function fraudStepIconSvg(key) {
    const inner = FRAUD_STEP_ICONS[key] || '<circle cx="12" cy="12" r="4"/>';
    return (
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round">' +
      inner +
      "</svg>"
    );
  }

  function fraudDecisionIndex(caseData) {
    return caseData.timeline.length;
  }

  function renderFraudStepper(state) {
    const c = state.currentCase;
    const total = fraudDecisionIndex(c) + 1;
    state.stepperEl.innerHTML = "";

    for (let i = 0; i < total; i++) {
      const isDecision = i === fraudDecisionIndex(c);
      const iconKey = isDecision ? "decision" : c.timeline[i].icon;
      const label = isDecision ? "Decision" : c.timeline[i].title;

      const btn = document.createElement("button");
      btn.type = "button";
      const isLocked = i > state.maxRevealed + 1;
      let cls = "fd-step";
      if (i <= state.maxRevealed) cls += " viewed";
      if (i === state.selected) cls += " active";
      if (isLocked) cls += " locked";
      btn.className = cls;
      btn.setAttribute("aria-label", label + (isLocked ? " (not yet reached)" : ""));
      btn.disabled = isLocked;
      btn.innerHTML = [
        '<span class="fd-step-marker">' + fraudStepIconSvg(iconKey) + "</span>",
        '<span class="fd-step-label">' + escapeHtml(label) + "</span>",
      ].join("");
      btn.addEventListener("click", () => selectFraudStep(state, i));
      state.stepperEl.appendChild(btn);
    }
  }

  // Gated here, not just visually: a step beyond maxRevealed + 1 simply
  // never advances, and the button for it is also rendered disabled above,
  // matching the same defense-in-depth principle KYC's screening gate uses.
  function selectFraudStep(state, index) {
    if (index > state.maxRevealed + 1) return;
    if (index > state.maxRevealed) state.maxRevealed = index;
    state.selected = index;
    renderFraudStepper(state);
    renderFraudRisk(state);
    renderFraudStepBody(state);
  }

  function currentFraudRiskValue(state) {
    const c = state.currentCase;
    const idx = state.selected === fraudDecisionIndex(c) ? c.timeline.length - 1 : state.selected;
    return c.timeline[idx].risk;
  }

  function fraudRiskBand(value) {
    if (value >= 70) return "red";
    if (value >= 30) return "amber";
    return "green";
  }

  function renderFraudRisk(state) {
    const value = currentFraudRiskValue(state);
    const band = fraudRiskBand(value);
    const valueEl = state.riskPanel.querySelector(".fd-risk-value");
    const fillEl = state.riskPanel.querySelector(".fd-risk-fill");
    valueEl.textContent = value + " / 100";
    valueEl.className = "fd-risk-value " + band;
    fillEl.className = "fd-risk-fill " + band;
    fillEl.style.width = value + "%";
  }

  function renderFraudStepBody(state) {
    const c = state.currentCase;
    state.bodyEl.innerHTML = "";

    if (state.selected === fraudDecisionIndex(c)) {
      renderFraudDecisionPanel(state);
      return;
    }

    const step = c.timeline[state.selected];
    state.bodyEl.innerHTML = [
      '<div class="fd-evidence-time">' + escapeHtml(step.time) + "</div>",
      "<h4>" + escapeHtml(step.title) + "</h4>",
      '<p class="fd-evidence-body">' + escapeHtml(step.body) + "</p>",
    ].join("");

    const nextBtn = document.createElement("button");
    nextBtn.className = "sl-btn";
    nextBtn.textContent = state.selected === fraudDecisionIndex(c) - 1 ? "Continue to decision" : "Next";
    nextBtn.addEventListener("click", () => selectFraudStep(state, state.selected + 1));
    state.bodyEl.appendChild(nextBtn);
  }

  // Disposition buttons and the correct/incorrect rationale are gated here
  // in JS, not just visually: this panel only ever builds the buttons once
  // maxRevealed has actually reached the decision step in order, the same
  // discipline scenario-lab.js uses to keep KYC's screening results behind
  // ns.identified rather than a CSS only hide.
  function renderFraudDecisionPanel(state) {
    const c = state.currentCase;
    const reachedNaturally = state.maxRevealed === fraudDecisionIndex(c);

    if (!reachedNaturally) {
      state.bodyEl.innerHTML = '<p class="fd-decision-intro">Review every event above before deciding.</p>';
      return;
    }

    state.bodyEl.innerHTML = '<p class="fd-decision-intro">All evidence reviewed. What is your disposition?</p>';

    const btnRow = document.createElement("div");
    btnRow.className = "fd-decision-buttons";
    c.disposition_options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "sl-btn";
      btn.textContent = opt.label;
      btn.disabled = state.decisionMade;
      btn.addEventListener("click", () => decideFraud(state, opt.key));
      btnRow.appendChild(btn);
    });
    state.bodyEl.appendChild(btnRow);

    const banner = document.createElement("div");
    banner.className = "sl-decision-banner";
    state.bodyEl.appendChild(banner);
    state.fraudBanner = banner;
  }

  function decideFraud(state, dispositionKey) {
    const c = state.currentCase;
    if (state.decisionMade) return; // defense in depth against a stray double click
    if (state.selected !== fraudDecisionIndex(c) || state.maxRevealed !== fraudDecisionIndex(c)) return;

    state.decisionMade = true;
    const isCorrect = c.correct_disposition.includes(dispositionKey);
    state.results.push({ caseId: c.entity_id, correct: isCorrect });
    recordCaseProgress(c.entity_id, isCorrect);

    state.bodyEl.querySelectorAll(".fd-decision-buttons button").forEach((b) => (b.disabled = true));

    const banner = state.fraudBanner;
    banner.className = "sl-decision-banner show " + (isCorrect ? "correct" : "incorrect");
    banner.textContent = (isCorrect ? "Correct. " : "Not quite. ") + c.rationale;
    appendRelatedGuide(banner, c);

    appendBackToCaseListControl(state.workspace, state, banner, () => advanceToNextCase(state.workspace, state));
  }

  // ---- Cross-reference fact card component (Cases 5/6, and Risk Scoring's
  // Cases 1/2/4/5/6, see docs/risk-scoring-module-spec.md) ----
  // Reuses the header scene renderer, disposition panel button/banner
  // pattern, and back-to-case-list/related-guide helpers unchanged. The
  // only new interactive surface is the fact card grid immediately below:
  // order-independent, gated by count of distinct cards revealed rather
  // than the timeline's locked step-by-step index.
  function loadCrossReferenceCase(workspace, state) {
    const c = state.cases[state.caseIndex];
    state.currentCase = c;
    state.revealedFacts = {}; // fact index -> true, once clicked
    state.decisionMade = false;

    workspace.innerHTML = "";

    const caseHeader = document.createElement("div");
    caseHeader.className = "sl-case-header";
    caseHeader.innerHTML = [
      "<h2>Case " + c.case_number + ": " + escapeHtml(c.title) + "</h2>",
      "<p>" + escapeHtml(c.briefing) + "</p>",
      '<div class="sl-case-meta"><span>Sources: ' + caseSourceCount(c) + "</span></div>",
    ].join("");
    workspace.appendChild(caseHeader);

    const scenePanel = document.createElement("div");
    scenePanel.className = "sl-tree-panel";
    workspace.appendChild(scenePanel);
    renderHeaderScene(scenePanel, c.header_scene);

    const factsPanel = document.createElement("div");
    factsPanel.className = "sl-tools-panel";
    workspace.appendChild(factsPanel);

    const introEl = document.createElement("p");
    introEl.className = "fd-decision-intro";
    introEl.textContent = "These facts exist at once, not in sequence. Reveal every card below, in any order, then decide.";
    factsPanel.appendChild(introEl);

    const grid = document.createElement("div");
    grid.className = "fd-fact-grid";
    factsPanel.appendChild(grid);

    const bodyEl = document.createElement("div");
    bodyEl.className = "sl-node-detail";
    factsPanel.appendChild(bodyEl);

    state.factsGridEl = grid;
    state.bodyEl = bodyEl;
    state.workspace = workspace;

    renderFactCards(state);
    renderCrossReferenceDecisionPanel(state);
  }

  function renderFactCards(state) {
    const c = state.currentCase;
    state.factsGridEl.innerHTML = "";
    c.cross_reference_facts.forEach((fact, idx) => {
      const revealed = !!state.revealedFacts[idx];
      const card = document.createElement("button");
      card.type = "button";
      card.className = "fd-fact-card" + (revealed ? " revealed" : "");
      card.setAttribute("aria-expanded", revealed ? "true" : "false");
      card.innerHTML = [
        '<span class="fd-fact-icon">' + fraudStepIconSvg(fact.icon) + "</span>",
        "<h4>" + escapeHtml(fact.title) + "</h4>",
        revealed
          ? '<p class="fd-fact-body">' + escapeHtml(fact.body) + "</p>"
          : '<span class="fd-fact-hint">Click to reveal</span>',
      ].join("");
      card.addEventListener("click", () => revealFact(state, idx));
      state.factsGridEl.appendChild(card);
    });
  }

  function revealFact(state, idx) {
    if (state.revealedFacts[idx]) return;
    state.revealedFacts[idx] = true;
    renderFactCards(state);
    renderCrossReferenceDecisionPanel(state);
  }

  function allFactsRevealed(state) {
    const c = state.currentCase;
    return c.cross_reference_facts.every((_, idx) => !!state.revealedFacts[idx]);
  }

  // Gated the same way renderFraudDecisionPanel gates the timeline cases:
  // in JS, by an actual count check, not just by hiding the panel with CSS.
  function renderCrossReferenceDecisionPanel(state) {
    const c = state.currentCase;
    state.bodyEl.innerHTML = "";

    if (!allFactsRevealed(state)) {
      state.bodyEl.innerHTML = '<p class="fd-decision-intro">Reveal every fact above before deciding.</p>';
      return;
    }

    state.bodyEl.innerHTML = '<p class="fd-decision-intro">All facts reviewed. What is your disposition?</p>';

    // Risk Scoring's Case 4 (the "over scored customer") is the only case
    // carrying risk_signals: it reuses the same illustrative additive score
    // display Investigation Tools already shows on the KYC tree, wired to
    // this case's own flags instead of ownership/jurisdiction data. See
    // computeSignalScore/renderRiskScoreDisplay below.
    if (c.risk_signals) {
      const scorePanel = document.createElement("div");
      scorePanel.className = "sl-risk-signals-panel";
      const { score, breakdown } = computeSignalScore(c.risk_signals);
      renderRiskScoreDisplay(scorePanel, score, breakdown);
      const note = document.createElement("p");
      note.style.fontSize = "0.8rem";
      note.style.color = "var(--sl-text-muted)";
      note.style.marginTop = "8px";
      note.textContent = "Illustrative training model, not a regulatory risk weighting.";
      scorePanel.appendChild(note);
      state.bodyEl.appendChild(scorePanel);
    }

    // A case can require a documented override rationale (Case 4: the score
    // says High, the analyst has to write down why they're not following
    // it) before any disposition button enables, so a silent override isn't
    // possible. The buttons are built after this so their initial disabled
    // state can already account for the empty textarea.
    let overrideFilled = !c.requires_override_note;
    if (c.requires_override_note) {
      const label = document.createElement("label");
      label.className = "fd-decision-intro";
      label.style.display = "block";
      label.style.marginTop = "12px";
      label.textContent = "Document your rationale before deciding:";
      state.bodyEl.appendChild(label);

      const noteInput = document.createElement("textarea");
      noteInput.className = "sl-textarea";
      noteInput.rows = 3;
      noteInput.placeholder = "Why does (or doesn't) the model's score reflect the actual risk here?";
      noteInput.setAttribute("aria-label", "Documented override rationale");
      state.bodyEl.appendChild(noteInput);

      noteInput.addEventListener("input", () => {
        overrideFilled = noteInput.value.trim().length > 0;
        state.bodyEl.querySelectorAll(".fd-decision-buttons button").forEach((b) => {
          b.disabled = state.decisionMade || !overrideFilled;
        });
      });
    }

    const btnRow = document.createElement("div");
    btnRow.className = "fd-decision-buttons";
    c.disposition_options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "sl-btn";
      btn.textContent = opt.label;
      btn.disabled = state.decisionMade || !overrideFilled;
      btn.addEventListener("click", () => decideCrossReference(state, opt.key));
      btnRow.appendChild(btn);
    });
    state.bodyEl.appendChild(btnRow);

    const banner = document.createElement("div");
    banner.className = "sl-decision-banner";
    state.bodyEl.appendChild(banner);
    state.fraudBanner = banner;
  }

  function decideCrossReference(state, dispositionKey) {
    const c = state.currentCase;
    if (state.decisionMade) return; // defense in depth against a stray double click
    if (!allFactsRevealed(state)) return;
    if (c.requires_override_note) {
      const noteInput = state.bodyEl.querySelector(".sl-textarea");
      if (!noteInput || !noteInput.value.trim()) return; // defense in depth, buttons are already disabled for this
    }

    state.decisionMade = true;
    const isCorrect = c.correct_disposition.includes(dispositionKey);
    state.results.push({ caseId: c.entity_id, correct: isCorrect });
    recordCaseProgress(c.entity_id, isCorrect);

    state.bodyEl.querySelectorAll(".fd-decision-buttons button").forEach((b) => (b.disabled = true));

    const banner = state.fraudBanner;
    banner.className = "sl-decision-banner show " + (isCorrect ? "correct" : "incorrect");
    banner.textContent = (isCorrect ? "Correct. " : "Not quite. ") + c.rationale;
    appendRelatedGuide(banner, c);

    appendBackToCaseListControl(state.workspace, state, banner, () => advanceToNextCase(state.workspace, state));
  }

  function renderFraudCompletionScreen(workspace, state) {
    workspace.innerHTML = "";
    const complete = document.createElement("div");
    complete.className = "sl-complete";
    workspace.appendChild(complete);
    const totalCases = state.cases.length;
    renderCompletionBody(
      complete,
      workspace,
      state,
      "fraud",
      "Fraud Detection preview, " + totalCases + " case" + (totalCases === 1 ? "" : "s") + "."
    );
    complete.prepend(backToDashboardButton(workspace, state));
    appendNextModuleTeaser(complete, state);
  }

  function renderRiskCompletionScreen(workspace, state) {
    workspace.innerHTML = "";
    const complete = document.createElement("div");
    complete.className = "sl-complete";
    workspace.appendChild(complete);
    const totalCases = state.cases.length;
    renderCompletionBody(
      complete,
      workspace,
      state,
      "risk_scoring",
      "Risk Scoring, " + totalCases + " case" + (totalCases === 1 ? "" : "s") + "."
    );
    complete.prepend(backToDashboardButton(workspace, state));
    appendNextModuleTeaser(complete, state);
  }

  // ---- SAR Sandbox module ----
  // Three screens, no case picker (one case), no auto-advance anywhere, no
  // decide()-style scoring loop back into state.results: this module is
  // self contained, it never touches the KYC/Fraud completion or accuracy
  // tracking. Standing standard from the Fraud Detection section above still
  // applies here too: nothing in this module may auto-advance on a timer,
  // and a second case must never be added as an auto-advancing sequence
  // later, per the no-auto-advance rule that's locked for every module.

  function sarSandboxUrl(state, path) {
    return (state.apiBase || "").replace(/\/$/, "") + path;
  }

  function startSarModule(dashboard, workspace, state) {
    dashboard.style.display = "none";
    workspace.classList.add("visible");
    renderSarCasePicker(workspace, state);
  }

  function renderSarLoadError(workspace, state, message) {
    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));
    const banner = document.createElement("div");
    banner.className = "sl-decision-banner show error";
    banner.textContent = message;
    workspace.appendChild(banner);
  }

  // SAR-specific case picker, deliberately not sharing code with the
  // KYC/Fraud renderCasePicker: SAR cases carry case_id/title only, no
  // entity_id/case_number/briefing, and there is no correct/incorrect
  // progress badge for this module, so a tile here is just a title.
  async function renderSarCasePicker(workspace, state) {
    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));
    const loading = document.createElement("p");
    loading.textContent = "Loading cases…";
    workspace.appendChild(loading);

    let cases;
    try {
      const res = await fetch(sarSandboxUrl(state, "/api/sar-sandbox/cases"), {
        credentials: "omit",
      });
      if (!res.ok) throw new Error("Cases request failed with status " + res.status);
      cases = await res.json();
    } catch (err) {
      console.error("SAR Sandbox case list load error:", err);
      renderSarLoadError(
        workspace,
        state,
        "The case list could not be loaded. Refresh the page, or check the console for details."
      );
      return;
    }

    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));

    const header = document.createElement("div");
    header.className = "sl-case-header";
    header.innerHTML = [
      "<h2>SAR Writing Practice</h2>",
      "<p>Choose a case to draft a practice narrative against.</p>",
    ].join("");
    workspace.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "sl-case-grid";
    cases.forEach((c) => {
      const tile = document.createElement("button");
      tile.type = "button";
      tile.className = "sl-case-tile";
      tile.innerHTML = "<h3>" + escapeHtml(c.title) + "</h3>";
      tile.addEventListener("click", () => loadSarCaseBrief(workspace, state, c.case_id));
      grid.appendChild(tile);
    });
    workspace.appendChild(grid);
  }

  async function loadSarCaseBrief(workspace, state, caseId) {
    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));
    const loading = document.createElement("p");
    loading.textContent = "Loading case…";
    workspace.appendChild(loading);

    let caseData;
    try {
      const res = await fetch(sarSandboxUrl(state, "/api/sar-sandbox/case/" + caseId), {
        credentials: "omit",
      });
      if (!res.ok) throw new Error("Case request failed with status " + res.status);
      caseData = await res.json();
    } catch (err) {
      console.error("SAR Sandbox case load error:", err);
      renderSarLoadError(
        workspace,
        state,
        "This case could not be loaded. Refresh the page, or check the console for details."
      );
      return;
    }

    renderSarBrief(workspace, state, caseData, caseId);
  }

  // Shared by the case brief screen and the collapsible case reference panel
  // on the editor screen, same content, two places, same discipline as the
  // Trap/Tell/Do visual summary cards elsewhere on the site that render
  // identically in more than one placement. Returns markup only, the caller
  // decides where it gets mounted.
  function renderCaseBriefMarkup(caseData) {
    const txnRows = caseData.transactions
      .map(
        (t) =>
          "<tr><td>" +
          escapeHtml(t.date) +
          "</td><td>" +
          escapeHtml(t.from) +
          "</td><td>£" +
          Number(t.amount_gbp).toLocaleString("en-GB") +
          "</td><td>" +
          escapeHtml(t.description) +
          "</td></tr>"
      )
      .join("");

    const factItems = caseData.supporting_facts.map((f) => "<li>" + escapeHtml(f) + "</li>").join("");

    // Generated, not hardcoded: cases don't share one subject shape (a
    // business account case names entity_type/director, a personal account
    // case names customer_type/established_profile), so every key present
    // gets a row, in whatever order the case JSON defines, formatted into a
    // label rather than requiring every future case to match case 1's field
    // names. entity_name is excluded here since it's already shown as the
    // heading whenever it's present.
    const subjectRows = Object.entries(caseData.subject)
      .filter(([key]) => key !== "entity_name")
      .map(([key, value]) => {
        const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        return "<div><dt>" + escapeHtml(label) + "</dt><dd>" + escapeHtml(value) + "</dd></div>";
      })
      .join("");

    return [
      "<section>",
      "<h4>Subject</h4>",
      '<dl class="sar-brief-list">',
      subjectRows,
      "</dl>",
      "</section>",
      "<section>",
      "<h4>Activity window</h4>",
      "<p>" + escapeHtml(caseData.activity_window.start) + " to " + escapeHtml(caseData.activity_window.end) + "</p>",
      "</section>",
      "<section>",
      "<h4>Transactions</h4>",
      '<div class="sar-table-scroll">',
      '<table class="sar-transactions-table">',
      "<thead><tr><th>Date</th><th>From</th><th>Amount</th><th>Description</th></tr></thead>",
      "<tbody>" + txnRows + "</tbody>",
      "</table>",
      "</div>",
      "</section>",
      "<section>",
      "<h4>Onward movement</h4>",
      "<p>" + escapeHtml(caseData.onward_movement.pattern) + "</p>",
      "<p>" + escapeHtml(caseData.onward_movement.destination_note) + "</p>",
      "<p>Total moved: £" + Number(caseData.onward_movement.total_moved_gbp).toLocaleString("en-GB") + "</p>",
      "</section>",
      "<section>",
      "<h4>Supporting facts</h4>",
      "<ul>" + factItems + "</ul>",
      "</section>",
    ].join("");
  }

  function renderSarBrief(workspace, state, caseData, caseId) {
    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));

    // Not every case's subject has a single named entity, a personal
    // account case has no equivalent of case 1's entity_name, so the
    // heading falls back to the case title in that situation.
    const heading = caseData.subject.entity_name || caseData.title;

    const header = document.createElement("div");
    header.className = "sl-case-header";
    header.innerHTML = [
      "<h2>" + escapeHtml(heading) + "</h2>",
      "<p>Read the case brief below, then draft a practice SAR narrative against it.</p>",
    ].join("");
    workspace.appendChild(header);

    const brief = document.createElement("div");
    brief.className = "sar-brief";
    brief.innerHTML = renderCaseBriefMarkup(caseData);
    workspace.appendChild(brief);

    const continueBtn = document.createElement("button");
    continueBtn.className = "sl-btn";
    continueBtn.textContent = "Continue to narrative →";
    continueBtn.addEventListener("click", () => renderSarEditor(workspace, state, caseData, caseId));
    workspace.appendChild(continueBtn);
  }

  function renderSarEditor(workspace, state, caseData, caseId) {
    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));

    const header = document.createElement("div");
    header.className = "sl-case-header";
    header.innerHTML = [
      "<h2>Draft your SAR narrative</h2>",
      "<p>Write each section in your own words. Refer back to the case details below as you write. All three are required before you can submit.</p>",
    ].join("");
    workspace.appendChild(header);

    const caseReference = document.createElement("details");
    caseReference.className = "sar-case-reference";
    caseReference.innerHTML = [
      "<summary>View case details</summary>",
      '<div class="sar-brief">' + renderCaseBriefMarkup(caseData) + "</div>",
    ].join("");
    workspace.appendChild(caseReference);

    const editor = document.createElement("div");
    editor.className = "sar-editor";
    editor.innerHTML = [
      '<div class="sar-editor-field">',
      '<label for="sar-field-intro">Intro</label>',
      '<textarea id="sar-field-intro" class="sl-textarea" rows="4" ' +
        'placeholder="Who is this SAR about, and why is it being filed?"></textarea>',
      "</div>",
      '<div class="sar-editor-field">',
      '<label for="sar-field-body">Investigative Body</label>',
      '<textarea id="sar-field-body" class="sl-textarea" rows="8" ' +
        'placeholder="What happened, when, and how does the activity depart from what is expected?"></textarea>',
      "</div>",
      '<div class="sar-editor-field">',
      '<label for="sar-field-disposition">Final Disposition</label>',
      '<textarea id="sar-field-disposition" class="sl-textarea" rows="4" ' +
        'placeholder="What is your conclusion, and what happens next?"></textarea>',
      "</div>",
    ].join("");
    workspace.appendChild(editor);

    const submitBtn = document.createElement("button");
    submitBtn.className = "sl-btn";
    submitBtn.textContent = "Submit for feedback";
    submitBtn.disabled = true;
    workspace.appendChild(submitBtn);

    const errorBanner = document.createElement("div");
    errorBanner.className = "sl-decision-banner error";
    workspace.appendChild(errorBanner);

    const introEl = editor.querySelector("#sar-field-intro");
    const bodyEl = editor.querySelector("#sar-field-body");
    const dispositionEl = editor.querySelector("#sar-field-disposition");

    function updateSubmitState() {
      const ready = introEl.value.trim() && bodyEl.value.trim() && dispositionEl.value.trim();
      submitBtn.disabled = !ready;
    }
    [introEl, bodyEl, dispositionEl].forEach((el) => el.addEventListener("input", updateSubmitState));

    submitBtn.addEventListener("click", () => {
      submitSarNarrative(
        workspace,
        state,
        caseData,
        caseId,
        {
          intro: introEl.value.trim(),
          investigative_body: bodyEl.value.trim(),
          final_disposition: dispositionEl.value.trim(),
        },
        submitBtn,
        errorBanner,
        [introEl, bodyEl, dispositionEl]
      );
    });
  }

  async function submitSarNarrative(workspace, state, caseData, caseId, narrative, submitBtn, errorBanner, fields) {
    errorBanner.className = "sl-decision-banner error";
    submitBtn.disabled = true;
    submitBtn.textContent = "Scoring…";
    fields.forEach((el) => (el.disabled = true));

    function fail(message) {
      errorBanner.textContent = message;
      errorBanner.className = "sl-decision-banner show error";
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit for feedback";
      fields.forEach((el) => (el.disabled = false));
    }

    let res;
    try {
      res = await fetch(sarSandboxUrl(state, "/api/sar-sandbox/extract"), {
        method: "POST",
        credentials: "omit",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: caseId,
          intro: narrative.intro,
          investigative_body: narrative.investigative_body,
          final_disposition: narrative.final_disposition,
        }),
      });
    } catch (err) {
      console.error("SAR Sandbox extraction network error:", err);
      fail("Something went wrong marking your submission, nothing was scored, you can try submitting again.");
      return;
    }

    if (res.status === 429) {
      console.error("SAR Sandbox extraction rate limited");
      fail("You've reached the practice limit for this hour, try again later.");
      return;
    }

    if (res.status === 502) {
      let detail = null;
      try {
        detail = (await res.json()).detail;
      } catch (err) {
        /* body wasn't JSON, nothing more to log */
      }
      console.error("SAR Sandbox extraction failed (502):", detail);
      fail("Something went wrong marking your submission, nothing was scored, you can try submitting again.");
      return;
    }

    if (!res.ok) {
      console.error("SAR Sandbox extraction failed with status", res.status);
      fail("Something went wrong marking your submission, nothing was scored, you can try submitting again.");
      return;
    }

    let result;
    try {
      result = await res.json();
    } catch (err) {
      console.error("SAR Sandbox extraction response was not valid JSON:", err);
      fail("Something went wrong marking your submission, nothing was scored, you can try submitting again.");
      return;
    }

    renderSarResults(workspace, state, caseData, result);
  }

  function renderSarResults(workspace, state, caseData, result) {
    const extraction = result.extraction;
    const scoring = result.scoring;

    workspace.innerHTML = "";
    workspace.appendChild(backToDashboardButton(workspace, state));

    const header = document.createElement("div");
    header.className = "sl-case-header";
    header.innerHTML = "<h2>Feedback on your narrative</h2>";
    workspace.appendChild(header);

    if (scoring.structural_incomplete) {
      const labels = { intro: "Intro", investigative_body: "Investigative Body", final_disposition: "Final Disposition" };
      const missing = Object.keys(labels)
        .filter((key) => !extraction.sections_present[key])
        .map((key) => labels[key]);
      const notice = document.createElement("div");
      notice.className = "sl-decision-banner show notice";
      notice.textContent =
        "Your score was capped at 40 because " +
        (missing.length === 1 ? "the " + missing[0] + " section was" : missing.join(" and ") + " sections were") +
        " left blank. A complete SAR must cover all three sections.";
      workspace.appendChild(notice);
    }

    const fiveWsCount = Object.values(extraction.five_ws).filter((w) => w.addressed).length;
    const redFlagsCount = scoring.red_flags_score / 5;
    const transactionCited = scoring.transaction_score > 0;
    const speculativeNote =
      scoring.speculative_score >= 10
        ? "Clean language, no unsupported claims."
        : "Some phrasing overstated certainty, review your wording for unsupported claims.";

    const results = document.createElement("div");
    results.className = "sar-results";
    results.innerHTML = [
      '<div class="sar-result-row"><span class="sar-result-label">Core facts</span>' +
        '<span class="sar-result-value">' +
        fiveWsCount +
        " of 5 core facts covered</span></div>",
      '<div class="sar-result-row"><span class="sar-result-label">Red flags</span>' +
        '<span class="sar-result-value">' +
        redFlagsCount +
        " of 6 red flags identified</span></div>",
      '<div class="sar-result-row"><span class="sar-result-label">Transaction detail</span>' +
        '<span class="sar-result-value">Transaction detail cited: ' +
        (transactionCited ? "yes" : "no") +
        "</span></div>",
      '<div class="sar-result-row"><span class="sar-result-label">Language</span>' +
        '<span class="sar-result-value">' +
        escapeHtml(speculativeNote) +
        "</span></div>",
    ].join("");
    workspace.appendChild(results);
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  window.initScenarioLab = initScenarioLab;
})();
