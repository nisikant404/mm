## Milestone v1.0 Requirements

### UI Cleanup
- [ ] **OCR-01**: Remove AI model selection dropdowns/options from all frontend analyzer pages (`medicine_analyzer.html`, `lab_analyzer.html`, `symptom_checker.html`).

### Backend Cleanup
- [ ] **OCR-02**: Ensure backend AI routes (`app/routes/ai.py`) automatically resolve and use the default AI model without requiring a frontend payload parameter.

### Automation
- [ ] **SAVE-01**: Automatically save successfully scanned medicine analysis results to the user's Medical History. 
- [ ] **SAVE-02**: Automatically save successfully scanned prescription analysis results to the user's Medical History.

### Future Requirements
(None yet)

### Out of Scope
- Modifying the underlying AI prompt structure
- Changing the Gemini model being used (just removing the UI selection)

## Traceability
*Updated automatically by roadmap creation*
- **OCR-01**: Planned for Phase 1
- **OCR-02**: Planned for Phase 1
- **SAVE-01**: Planned for Phase 2
- **SAVE-02**: Planned for Phase 2
