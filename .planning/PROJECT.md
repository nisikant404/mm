# MedMining

**Core Value:** A unified healthcare platform bridging patients and doctors with AI-assisted insights, smart OCR, and real-time communication.

## Current Milestone: v1.0 OCR Improvements

**Goal:** Remove manual model selection from the OCR interface and automate the saving of scanned medicines and prescriptions.

**Target features:**
- Remove AI model/agent selectors from OCR UIs (medicine, prescription, lab report)
- Default to the configured primary model (or simulation) under the hood
- Implement automatic saving of OCR results as medical records

## Requirements

### Validated

- ✓ Role-based portals (Patient / Doctor)
- ✓ Medical Records Management (symptoms, diagnosis, prescriptions, lab reports)
- ✓ AI-Powered Risk Mining (Gemini integration via POST `/ai/analyze-risk`)
- ✓ Smart OCR analysis (medicine labels, lab reports via Gemini vision)
- ✓ Real-time communication (Socket.IO chat)
- ✓ Real-time consultation (WebRTC video call)
- ✓ Appointment scheduling

### Active

- [ ] **OCR-01**: Remove AI model selection dropdowns/options from all frontend analyzer pages (medicine, lab).
- [ ] **OCR-02**: Ensure backend AI routes automatically resolve and use the default AI model without requiring frontend parameter.
- [ ] **SAVE-01**: Automatically save successfully scanned medicine analysis results to the user's Medical History. 
- [ ] **SAVE-02**: Automatically save successfully scanned prescription analysis results to the user's Medical History.

### Out of Scope

- Modifying the underlying AI prompt structure (out of scope for this milestone)
- Changing the Gemini model being used (just removing the UI selection)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Automating record saves | Users shouldn't need a separate "save" action after waiting for OCR results; it improves UX. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-02 after initialization*
