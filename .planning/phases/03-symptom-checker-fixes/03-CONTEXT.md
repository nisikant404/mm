# Phase 3: Symptom Checker & Doctor Listing Fixes - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Resolve functional bugs in the AI Symptom Checker chat flow and ensure that doctors correctly populate the side-panel based on the final AI diagnosis.

</domain>

<decisions>
## Implementation Decisions

### Parser Fallback
- **D-01:** Implement a silent auto-retry (up to 2 times) if the AI returns malformed JSON during the diagnosis parsing step.
- **D-02:** If the retry fails, provide a graceful frontend notification rather than crashing the chat session.

### Specialization Matching
- **D-03:** Use lenient fuzzy/partial matching to map AI-predicted specializations (e.g., "cardiologist") to database specialization values (e.g., "Cardiology").
- **D-04:** Ensure matching is case-insensitive and handles common variations in medical terminology.

### Empty Doctor State
- **D-05:** If no specialists are found for the diagnosis, the UI must display a clear message: "No specialists found for this condition."
- **D-06:** Provide a prominent fallback action: "Book a General Practitioner" which filtered the doctor list to show GPs available.

### the agent's Discretion
- Choosing the specific fuzzy matching library or algorithm (e.g., SequenceMatcher or basic string inclusivity).
- The exact UI styling for the "Book a General Practitioner" fallback button.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Logic & Routing
- `app/routes/ai.py` — Core AI analysis and parsing logic.
- `app/routes/doctor.py` — Doctor retrieval and filtering logic.
- `app/templates/patient/symptom_checker.html` — Frontend chat and side-panel implementation.

### Data Models
- `app/models/models.py` — User and Doctor models highlighting specialization fields.

</canonical_refs>
