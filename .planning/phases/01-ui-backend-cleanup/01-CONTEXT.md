# Phase 1: UI & Backend Cleanup - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

## Phase Boundary

Removing model selection options from the UI across all analysis pages (`medicine_analyzer.html`, `lab_analyzer.html`, `symptom_checker.html`), and updating the AI routes backend to use a single default model instead of expecting a frontend selection.

## Implementation Decisions

### Selected AI Model
- **D-01:** Default to `gemini-2.5-flash` internally. No model parameter is required from the frontend payloads.
- **D-02:** Gracefully ignore the `ai_model` parameter if it is still sent by legacy frontend calls, to prevent breakage before full cache clears.

### UI Removals
- **D-03:** Completely remove the UI dropdowns/select components for model choice. Wait, we should also maintain the simulation toggle if it does not interfere with the model choice removal since simulation is a useful testing feature. Remove ONLY the model selection.

### the agent's Discretion
- The planner and implementer have discretion on how to refactor repetitive AI resolution logic in `app/routes/ai.py`, ideally reducing the "God file" footprint slightly by skipping `resolve_ai_model_name()` complexity.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `.planning/codebase/ARCHITECTURE.md` — AI Analysis Flow details
- `.planning/codebase/STACK.md` — Gemini configuration context
