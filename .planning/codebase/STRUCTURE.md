# Directory Structure

## Project Root

```
medmining/
├── .env                          # Environment variables (SECRET_KEY, GEMINI_API_KEY, etc.)
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies (12 packages)
├── run.py                        # Application entry point (9 lines)
├── update_db.py                  # Manual DB schema migration script (34 lines)
│
├── app/                          # Main Flask application package
│   ├── __init__.py               # App factory, extensions, SocketIO handlers (123 lines)
│   │
│   ├── models/
│   │   └── models.py             # All SQLAlchemy models (70 lines, 6 models)
│   │
│   ├── routes/
│   │   ├── auth.py               # Authentication blueprint (75 lines)
│   │   ├── patient.py            # Patient dashboard & tools (86 lines)
│   │   ├── doctor.py             # Doctor dashboard & prescriptions (49 lines)
│   │   ├── ai.py                 # AI analysis endpoints (552 lines — largest file)
│   │   └── consultation.py       # Chat & appointment management (77 lines)
│   │
│   └── templates/
│       ├── base.html             # Base template with nav, notifications (146 lines)
│       ├── landing.html          # Public landing page (112 lines)
│       ├── login.html            # Login form (~ 2KB)
│       ├── register.html         # Registration form with role selection (~ 5KB)
│       │
│       ├── patient/
│       │   ├── dashboard.html    # Patient dashboard (31KB — largest template)
│       │   ├── medicine_analyzer.html  # Medicine OCR/analysis UI (~ 20KB)
│       │   ├── lab_analyzer.html       # Lab report analysis UI (~ 19KB)
│       │   └── symptom_checker.html    # Symptom chat UI (~ 10KB)
│       │
│       ├── doctor/
│       │   └── dashboard.html    # Doctor workspace dashboard (~ 17KB)
│       │
│       └── consultation/
│           ├── chat.html         # Real-time chat interface (105 lines)
│           └── video_call.html   # WebRTC video call interface (122 lines)
│
├── instance/
│   └── medmining.db              # SQLite database file (32KB)
│
├── client/                       # Empty directory (unused)
├── server/                       # Empty directory (unused)
│
├── .venv/                        # Python virtual environment
└── .agent/                       # GSD agent configuration
```

## Key Locations

| What                          | Location                                    |
|-------------------------------|---------------------------------------------|
| Application factory           | `app/__init__.py` :: `create_app()`         |
| All data models               | `app/models/models.py`                      |
| AI logic (largest file)       | `app/routes/ai.py` (552 lines)              |
| Authentication logic          | `app/routes/auth.py`                        |
| Patient features              | `app/routes/patient.py`                     |
| Doctor features               | `app/routes/doctor.py`                      |
| Consultation (chat/video)     | `app/routes/consultation.py`                |
| SocketIO event handlers       | `app/__init__.py` (lines 66-117)            |
| Base template (nav/layout)    | `app/templates/base.html`                   |
| Patient dashboard             | `app/templates/patient/dashboard.html`      |
| Doctor dashboard              | `app/templates/doctor/dashboard.html`       |
| Environment config            | `.env`                                      |
| Database file                 | `instance/medmining.db`                     |
| Schema migration              | `update_db.py`                              |

## File Size Distribution

| Category      | Files | Total Size (approx) | Notes                     |
|---------------|-------|---------------------|---------------------------|
| Python backend| 7     | ~43 KB              | `ai.py` is 28KB alone     |
| Templates     | 10    | ~118 KB             | Patient dashboard is 31KB |
| Config        | 4     | ~4 KB               | `.env`, `.gitignore`, etc.|

## Naming Conventions

| Element          | Convention                           | Examples                |
|------------------|--------------------------------------|-------------------------|
| Blueprint names  | lowercase singular                   | `auth`, `patient`, `doctor` |
| Route files      | lowercase, match blueprint name      | `auth.py`, `patient.py` |
| Template dirs    | match blueprint name                 | `patient/`, `doctor/`, `consultation/` |
| Template files   | lowercase, underscored               | `medicine_analyzer.html`, `video_call.html` |
| Model classes    | PascalCase                           | `MedicalRecord`, `User` |
| DB columns       | snake_case                           | `patient_id`, `risk_score` |
| URL prefixes     | `/{blueprint_name}`                  | `/patient`, `/ai`, `/auth` |

## Empty/Unused Directories

- `client/` — Empty, possibly intended for a future frontend SPA
- `server/` — Empty, possibly a leftover or planned separation
