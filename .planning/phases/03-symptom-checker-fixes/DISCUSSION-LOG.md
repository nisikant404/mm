# Phase 3: Symptom Checker & Doctor Listing Fixes - Discussion Log

## Q&A Session (2026-04-02)

**Q:** Which areas do you want to discuss for Phase 3? (Parser Fallback, Specialization Matching, Empty Doctor State)
**A:** silent auto retry, lemient fuzzy match, book general practictioner.

### Parser Fallback
- **Choice:** Silent auto-retry.
- **Rationale:** Minimizes user-visible errors and improves resilience against intermittent AI formatting issues.

### Specialization Matching
- **Choice:** Lenient fuzzy match.
- **Rationale:** Ensures that minor differences in terminology (e.g., cardiologist vs Cardiology) don't prevent doctors from appearing.

### Empty Doctor State
- **Choice:** Book general practitioner.
- **Rationale:** Provides a clear path forward for the user even when a specific specialist is not available in the database.
