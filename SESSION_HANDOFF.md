# Session Handoff

**Last action:** SAR Sandbox Phase 0 deployed and verified live on Render
(commit `4679aaa`).

**Stopping point:** All Phase 7 checks pass against the live production URL,
whitelist leak check, strong/weak narrative scoring, and rate limiter state
persistence across real requests. Auto-deploy remains off for
`fincrimeradar-api`, deliberately, future pushes need a manual "Deploy
latest commit" on the Render dashboard.

**Immediate next step:** Real mobile device check (still outstanding, only
a static CSS review was done). Decide whether/when to evaluate Haiku as a
cost optimisation now that Sonnet 5 accuracy is proven live.

Also fixed post-deploy: apiBase was stale (still empty) on the live site,
causing SAR Sandbox to fail to load in production. Fixed (commit
`a32483f`), and while fixing it, found KYC/Fraud Detection had silently
lost their local-fallback resilience the moment apiBase went live for all
modules. Restored (commit `de675bc`): live fetch first, 15s timeout, fall
back to local `scenario-lab/data/cases.json` on any failure. All three
modules confirmed working on the real production site as of this fix.

**Open decisions:** None blocking. `EXTRACT_RATE_LIMIT_MAX` confirmed at 20,
Sonnet 5 confirmed as the deliberate model choice.
