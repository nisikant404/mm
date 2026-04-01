# Code Conventions

## Python Style

### General
- Standard Python 3.8+ syntax with type hints used sparingly (only in `ai.py`)
- No linter configuration files detected (no `pyproject.toml`, `setup.cfg`, `.flake8`, etc.)
- No formatter configuration (no `black`, `ruff`, `isort` config)
- Indentation: 4 spaces (standard Python)
- Line endings: Mix of CRLF (`ai.py`) and LF (other files)

### Imports
- Standard library imports first, then framework imports, then local imports
- Common pattern in routes:
```python
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import User, Appointment, ...
from app import db
```
- Lazy imports used inside functions in `app/__init__.py` (to avoid circular imports)

### Blueprint Pattern
- Each route module creates a Blueprint at module level:
```python
blueprint_name = Blueprint('blueprint_name', __name__)
```
- Registered in `app/__init__.py` with URL prefix matching the name
- Routes decorated with `@blueprint.route(...)` and `@login_required`

### Error Handling
- Try/except with `db.session.rollback()` on database errors
- Generic `Exception` catching (no custom exception classes)
- Errors returned as `jsonify({"error": str(e)}), 500`
- Print statements for error logging (`print(f"Error: {str(e)}")`) — no structured logging

### Response Patterns
- JSON API endpoints return `jsonify({...})`
- Page routes return `render_template('template.html', **kwargs)`
- Success responses: `jsonify({"message": "..."})`
- Error responses: `jsonify({"error": "..."}), status_code`

### Role-Based Access
- Checked inline at the start of route handlers:
```python
if current_user.role != 'patient':
    return redirect(url_for('doctor.dashboard'))
```
- No decorator-based role enforcement

### AI Module Patterns (`ai.py`)
- Dual-path pattern: every AI endpoint checks `get_genai_client()`
  - If client exists → real Gemini SDK call
  - If `None` → simulated/mock response
- Mock responses include `"is_mock": true` flag for frontend differentiation
- JSON parsing from Gemini uses `parse_json_from_gemini_text()` to strip markdown fences
- Model name resolution handles aliases and deprecated names

## HTML/Template Conventions

### Template Inheritance
```
base.html (nav, notifications, flash messages, scripts)
  ├── landing.html
  ├── login.html
  ├── register.html
  ├── patient/dashboard.html
  ├── patient/medicine_analyzer.html
  ├── patient/lab_analyzer.html
  ├── patient/symptom_checker.html
  ├── doctor/dashboard.html
  ├── consultation/chat.html
  └── consultation/video_call.html
```

### Block Structure
- `{% block title %}` — Page title
- `{% block content %}` — Main page content
- `{% block scripts %}` — Page-specific JavaScript

### Styling Approach
- **TailwindCSS utility classes** used inline throughout all templates
- Glass morphism effect defined as custom CSS: `.glass { backdrop-filter: blur(10px); }`
- Large border-radius values common (`rounded-[2.5rem]`, `rounded-[3rem]`)
- Consistent color palette: `blue-600` (primary), `emerald` (success), `red` (danger), `slate` (neutral)
- Font weights: Predominantly `font-bold`, `font-extrabold`, `font-black`

### JavaScript Conventions
- Inline `<script>` tags in templates (no separate JS files)
- `async/await` for fetch calls
- `fetch()` API for AJAX requests (no axios/jQuery)
- Socket.IO and SimplePeer loaded from CDN
- DOM manipulation via `document.getElementById()` and `document.createElement()`
- Template variables injected directly: `const userId = {{ current_user.id }};`

## Data Conventions

### Database
- All timestamps use `datetime.utcnow` (no timezone awareness)
- Foreign keys use `db.ForeignKey('table.column')` — no cascade rules defined
- Prescriptions store medicines as JSON string (`json.dumps()`) in a `Text` column
- No explicit indexes beyond primary keys and unique constraints

### API Payloads
- Request: `request.get_json()` for JSON, `request.files['key']` for uploads
- Response: Always `jsonify()` wrapped
- No request validation library (no marshmallow, pydantic, etc.)
- No API versioning

### Notification Pattern
- Notifications created inline alongside the triggering action (not via signals/events)
- Pattern: create `Notification()`, add to session, commit with parent action
- Used in: registration, chat messages, appointments, prescriptions
