# Testing

## Current State

**No tests exist.** The project has no test files, test directories, test configuration, or CI/CD pipeline.

## What's Missing

| Category              | Status     | Notes                                        |
|-----------------------|-----------|----------------------------------------------|
| Unit tests            | ❌ None    | No `tests/` directory, no `test_*.py` files  |
| Integration tests     | ❌ None    | No API endpoint testing                      |
| E2E / Browser tests   | ❌ None    | No Selenium/Playwright/Cypress               |
| Test framework config | ❌ None    | No `pytest.ini`, `conftest.py`, `tox.ini`    |
| Coverage config       | ❌ None    | No `.coveragerc` or coverage settings        |
| CI/CD pipeline        | ❌ None    | No GitHub Actions, GitLab CI, etc.           |
| Linting               | ❌ None    | No `flake8`, `ruff`, `pylint` config         |
| Type checking         | ❌ None    | No `mypy` config; minimal type hints in code |

## Recommended Test Structure

If tests were to be added:

```
tests/
├── conftest.py              # Flask test client, DB fixtures, mock AI client
├── test_auth.py             # Login, register, logout flows
├── test_patient.py          # Patient dashboard, save records
├── test_doctor.py           # Doctor dashboard, prescriptions
├── test_ai.py               # AI endpoints (mock mode + mocked Gemini)
├── test_consultation.py     # Appointment booking, status updates
└── test_models.py           # Model creation, relationships
```

## Key Areas Needing Tests

1. **Authentication flow** — Registration with role selection, login, logout, redirect logic
2. **Role-based access** — Patient can't access doctor routes, vice versa
3. **AI simulation mode** — Mock responses return expected structure when no API key
4. **AI live mode** — Mocked `genai.Client` calls return properly parsed JSON
5. **PDF processing** — `extract_pdf_text()`, `pdf_to_pil_images()` with sample files
6. **SocketIO events** — Message persistence, notification creation
7. **Model validation** — Required fields, relationships, default values
8. **Notification system** — Creation triggers, mark-as-read endpoint
9. **JSON parsing** — `parse_json_from_gemini_text()` with various Gemini response formats

## Test Dependencies That Would Be Needed

```
pytest
pytest-flask
pytest-socketio  # or flask-socketio test utilities
coverage
```

## Verification Approach (Current)

Without automated tests, verification is done through:
- Manual browser testing
- `print()` statements in route handlers for debugging
- Flask debug mode with auto-reload
