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

**Open decisions:** None blocking. `EXTRACT_RATE_LIMIT_MAX` confirmed at 20,
Sonnet 5 confirmed as the deliberate model choice.
