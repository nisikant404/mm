# Phase 2: Automate Saving - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

## Phase Boundary

Implementing automatic data persistence for OCR scan results, triggered by the AI analysis endpoints (`/ai/analyze-medicine`, `/ai/analyze-lab-report`, `/ai/analyze-risk`). The backend will save the results as medical history records automatically unless opted out. 

## Implementation Decisions

### 1. Automatic Save Timing
- **D-01:** Saving must occur synchronously in the backend before returning the AI response to the frontend. The backend creates the `MedicalRecord` based on the AI output during the same request that generated the analysis.

### 2. Explicit vs Implicit Consent
- **D-02:** Provide an opt-out toggle on the UI (e.g., a "Save to Medical History" checkbox, checked by default) before the user clicks analyze.
- **D-03:** The frontend payload must send this toggle state (e.g., `save_record: bool`) to the backend.

### 3. Notification of Save
- **D-04:** On successful response to the frontend, a toast notification should confirm to the user that the record was automatically saved.

### the agent's Discretion
- The implementer will need to adapt the `MedicalRecord` model creation logic which is currently only handled in `/patient/save-record` route. We may need to refactor or reuse this logic inside `app/routes/ai.py` so the `ai` endpoints can inject into the database cleanly, maintaining DB session contexts properly.
- The UI toggle can be styled as a neat switch next to the analyze button.
- The backend must handle `is_mock` (Simulation) records gracefully, perhaps marking them as simulation in the notes if saving is toggled.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture
- `.planning/codebase/ARCHITECTURE.md`
- `app/routes/patient.py` — for reference on how `MedicalRecord` is normally saved.
- `app/models.py` — for database schema (`MedicalRecord` and `User`).
