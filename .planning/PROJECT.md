# MedMining

**Core Value:** A unified healthcare platform bridging patients and doctors with AI-assisted insights, smart OCR, and real-time communication.

## Current State

**Shipped Version:** v1.1 AI Symptom Checker

The platform includes an intelligent conversational symptom checker that diagnoses probable issues and dynamically lists relevant doctors (with real-time experience stats and functional booking buttons).

## Next Milestone Goals

*[Run `/gsd-new-milestone` to define goals for the next iteration.]*

<details>
<summary>Previous Milestone: v1.1 AI Symptom Checker</summary>

**Goal:** Build an intelligent conversational symptom checker that diagnoses probable issues and dynamically lists relevant doctors (with experience and booking capabilities) on the side.

**Target features:**
- Interactive AI chatbot for capturing symptoms and diagnosing probable issues
- Dynamic side-panel displaying doctors whose specializations match the AI diagnosis
- Display of doctor experience and credentials in the side-panel
- Inline appointment booking mechanism (ticket creation) from the doctor list
</details>

## Requirements

### Validated

- ✓ Role-based portals (Patient / Doctor)
- ✓ Medical Records Management (symptoms, diagnosis, prescriptions, lab reports)
- ✓ AI-Powered Risk Mining (Gemini integration via POST `/ai/analyze-risk`)
- ✓ Smart OCR analysis (medicine labels, lab reports via Gemini vision)
- ✓ Real-time communication (Socket.IO chat)
- ✓ Real-time consultation (WebRTC video call)
- ✓ Appointment scheduling

- ✓ **OCR-01**: Remove AI model selection dropdowns/options from all frontend analyzer pages (medicine, lab).
- ✓ **OCR-02**: Ensure backend AI routes automatically resolve and use the default AI model without requiring frontend parameter.
- ✓ **SAVE-01**: Automatically save successfully scanned medicine analysis results to the user's Medical History. 
- ✓ **SAVE-02**: Automatically save successfully scanned prescription analysis results to the user's Medical History.
- ✓ **CHK-01**: Symptom checker chatbot interface captures symptoms effectively.
- ✓ **CHK-02**: AI determines probable medical issue/specialization domain.
- ✓ **DOC-01**: Associated domain doctors render dynamically on a side-list.
- ✓ **DOC-02**: Side-list displays doctor experience and relevant credentials.
- ✓ **APT-01**: Side-list includes working "Book Appointment" (ticket) buttons for each doctor.

### Active

- [ ] (Run `/gsd-new-milestone`)

### Out of Scope

- Processing payments for appointments in this milestone
- Real-time scheduling slot selection (basic ticket raising is sufficient)

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
*Last updated: 2026-04-02 after starting v1.1 milestone*
