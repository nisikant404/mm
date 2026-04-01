# Concerns

## 🔴 Critical Security Issues

### 1. API Key Exposed in `.env` Committed to Repo
- **File**: `.env` (line 3)
- **Issue**: `GEMINI_API_KEY` is a real API key stored in `.env`. While `.gitignore` lists `.env`, if the repo history contains it or the file was committed before `.gitignore` was added, the key is exposed.
- **Risk**: API key abuse, unexpected billing
- **Fix**: Rotate the API key immediately; verify git history doesn't contain `.env`

### 2. No CSRF Protection
- **Issue**: No CSRF tokens on any forms. Flask-WTF is not installed or used.
- **Risk**: Cross-site request forgery attacks on state-changing endpoints
- **Affected**: All POST endpoints (login, register, book appointment, save record, etc.)

### 3. XSS via Unescaped Chat Messages
- **File**: `app/templates/consultation/chat.html` (line 94)
- **Issue**: Chat messages rendered via `innerHTML` with `${data.content}` — no sanitization
- **Risk**: Stored XSS attack through chat messages
- **Fix**: Use `textContent` instead of `innerHTML`, or sanitize HTML

### 4. SQL Injection Risk in `update_db.py`
- **File**: `update_db.py` (line 15)
- **Issue**: `cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")` uses f-strings
- **Mitigation**: Currently only called with hardcoded values, but the pattern is dangerous
- **Risk**: Low (hardcoded args) but bad practice

### 5. CORS Fully Open
- **File**: `app/__init__.py` (line 15, 27)
- **Issue**: `SocketIO(cors_allowed_origins="*")` and `CORS(app)` with no restrictions
- **Risk**: Any domain can make requests to the API and WebSocket

## 🟠 Significant Technical Debt

### 6. No Input Validation
- **Issue**: No request validation on any endpoint. `request.get_json()` and `request.form.get()` used without type checking, length limits, or sanitization.
- **Affected**: All POST endpoints
- **Risk**: Bad data in database, potential crashes on unexpected input

### 7. No Database Migrations
- **Issue**: Schema changes done via manual `update_db.py` ALTER TABLE scripts. No Alembic or Flask-Migrate.
- **Risk**: Schema drift between environments; error-prone manual process
- **Fix**: Add `Flask-Migrate` (Alembic integration)

### 8. No Logging Framework
- **Issue**: Uses `print()` statements for all error reporting. No structured logging, no log levels, no log files.
- **Affected**: `app/routes/ai.py`, `app/routes/auth.py`
- **Risk**: Difficult debugging in production; no audit trail

### 9. Monolithic `ai.py` (552 lines)
- **File**: `app/routes/ai.py`
- **Issue**: Contains all AI logic — client factory, model resolution, PDF processing, mock responses, simulation helpers, and 4 route handlers — in a single file
- **Fix**: Split into `ai/client.py`, `ai/simulation.py`, `ai/pdf_utils.py`, `ai/routes.py`

### 10. Hardcoded Secrets & Config
- **File**: `app/__init__.py` (line 19)
- **Issue**: `SECRET_KEY` has hardcoded fallback: `'medmining_ultra_secret_2026'`
- **Risk**: If `.env` is missing, the app runs with a predictable secret key

## 🟡 Performance & Scalability

### 11. SQLite in Production
- **Issue**: SQLite is single-writer and file-based. Not suitable for concurrent users.
- **Risk**: Write contention under load, no connection pooling
- **Fix**: Migrate to PostgreSQL for any real deployment

### 12. No Async Processing for AI Calls
- **Issue**: Gemini API calls are synchronous and block the request thread
- **Risk**: Long response times, thread pool exhaustion under load
- **Fix**: Use Celery/RQ for background processing, or async Flask

### 13. All Frontend Assets from CDN
- **Issue**: 6 CDN dependencies (TailwindCSS, Lucide, Chart.js, html2pdf, Socket.IO, SimplePeer). No local fallbacks.
- **Risk**: CDN outage = broken application. Also, `unpkg.com/lucide@latest` is unpinned.
- **Fix**: Pin CDN versions; consider bundling critical assets locally

### 14. No Static File Management
- **Issue**: No `static/` directory. All CSS is inline (Tailwind utilities) or in `<style>` tags. All JS is inline in templates.
- **Risk**: No caching, no minification, poor maintainability for frontend code

## 🟡 Functional Gaps

### 15. Video Call has No TURN Server
- **File**: `app/templates/consultation/video_call.html`
- **Issue**: SimplePeer uses only default STUN. No TURN server configured.
- **Risk**: Video calls will fail behind symmetric NAT, corporate firewalls, or VPNs

### 16. No File Upload Size Limits
- **Issue**: No `MAX_CONTENT_LENGTH` configured on Flask app. No file type validation beyond extension checking.
- **Risk**: Memory exhaustion from large file uploads; malicious file uploads

### 17. Appointment Booking Has No Real Date/Time Selection
- **File**: `app/routes/consultation.py` (line 37)
- **Issue**: `date=datetime.utcnow()` — appointment date is always "now", not a user-selected time
- **Fix**: Add date/time picker in frontend, pass selected datetime to backend

### 18. No Password Reset / Email Verification
- **Issue**: No password reset flow, no email verification on registration
- **Risk**: Locked-out users, fake accounts

### 19. Empty Directories
- `client/` and `server/` directories exist but are empty
- Suggests planned-but-unrealized frontend/backend separation

### 20. No Cascade Delete Rules
- **Issue**: No `cascade` defined on any relationships. Deleting a user leaves orphaned records.
- **Risk**: Data integrity issues if users are ever deleted

## Summary Priority Matrix

| Priority | Issue                          | Effort  |
|----------|--------------------------------|---------|
| P0       | XSS in chat (innerHTML)       | Low     |
| P0       | CSRF protection missing        | Medium  |
| P0       | API key rotation                | Low     |
| P1       | Input validation               | Medium  |
| P1       | CORS restrictions              | Low     |
| P1       | Logging framework              | Medium  |
| P2       | Database migration tooling     | Medium  |
| P2       | Split `ai.py`                  | Medium  |
| P2       | Add test suite                 | High    |
| P3       | SQLite → PostgreSQL            | High    |
| P3       | TURN server for video          | Medium  |
| P3       | Static asset management        | Medium  |
