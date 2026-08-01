# Session Handoff

**Last action:** Phase 7 verification complete for SAR Sandbox Phase 0.

**Stopping point:** Extraction, scoring, and all three frontend screens built
and verified against `fincrimeradar-api` running locally. Not yet deployed
to Render.

**Immediate next step:** Confirm `ANTHROPIC_API_KEY` is actually set on the
live Render dashboard for `fincrimeradar-api` (never verified live, only
confirmed via local `.env` and its existing use in `routes_guide_chat.py`).
Then deploy and run the same Phase 7 checks against the live URL, not just
localhost.

**Open decisions:**
- `EXTRACT_RATE_LIMIT_MAX` (currently 20/hour) may need lowering given
  confirmed real cost of roughly 2.6 Claude calls per submission, not the
  originally assumed 1.
- Real mobile device check still outstanding, static CSS review only so far.
