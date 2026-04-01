# Roadmap: v1.0 OCR Improvements

**2 phases** | **4 requirements mapped**

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | UI & Backend Cleanup | Remove model selectors from UI and backend logic | OCR-01, OCR-02 | 1. `medicine_analyzer.html`, `lab_analyzer.html`, and `symptom_checker.html` do not render model select dropdowns.<br>2. `ai.py` defaults to appropriate Gemini model without expecting `ai_model` param. |
| 2 | Automate Saving | Automatically save OCR scans to Medical History | SAVE-01, SAVE-02 | 1. A successful scan in `medicine_analyzer` triggers a save to the database.<br>2. Saved scans appear in the patient dashboard history. |

## Phase Details

**Phase 1: UI & Backend Cleanup**
Goal: Remove model selectors from UI and backend logic
Requirements: OCR-01, OCR-02
Success criteria:
1. `medicine_analyzer.html`, `lab_analyzer.html`, and `symptom_checker.html` do not render model select dropdowns.
2. `ai.py` defaults to appropriate Gemini model without expecting `ai_model` param.

**Phase 2: Automate Saving**
Goal: Automatically save OCR scans to Medical History
Requirements: SAVE-01, SAVE-02
Success criteria:
1. A successful scan in `medicine_analyzer` triggers a save to the database.
2. Saved scans appear in the patient dashboard history.
