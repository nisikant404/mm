# Technology Stack

## Language & Runtime

| Property       | Value                  |
|----------------|------------------------|
| Language        | Python 3.8+            |
| Runtime         | CPython                |
| Package Manager | pip                    |
| Virtual Env     | `.venv/` (standard venv) |

## Framework

| Component       | Technology              |
|-----------------|-------------------------|
| Web Framework   | **Flask** (via `create_app` factory pattern) |
| ORM / Database  | **Flask-SQLAlchemy** (SQLite backend) |
| Authentication  | **Flask-Login** (session-based, bcrypt password hashing) |
| Password Hashing| **Flask-Bcrypt**        |
| Realtime Comms  | **Flask-SocketIO** (WebSocket events for chat & video signaling) |
| CORS            | **Flask-Cors** (`cors_allowed_origins="*"`) |
| Templating      | **Jinja2** (default Flask templating) |

## Dependencies (`requirements.txt`)

| Package          | Purpose                                  |
|------------------|------------------------------------------|
| `Flask`          | Core web framework                       |
| `Flask-SQLAlchemy`| ORM for SQLite database                 |
| `Flask-Login`     | User session management                 |
| `Flask-SocketIO`  | WebSocket support for real-time features|
| `Flask-Cors`      | Cross-origin resource sharing           |
| `Flask-Bcrypt`    | Password hashing                        |
| `python-dotenv`   | Environment variable loading from `.env`|
| `Pillow`          | Image processing (PIL) for medicine image analysis |
| `google-genai`    | Google Gemini AI SDK for LLM integration|
| `pypdf`           | PDF text extraction (fallback/simulation mode) |
| `pymupdf`         | PDF-to-image rasterization for vision OCR |

## Frontend Stack

| Component        | Technology                               |
|------------------|------------------------------------------|
| CSS Framework    | **TailwindCSS** (CDN — `cdn.tailwindcss.com`) |
| Typography       | Google Fonts — `Plus Jakarta Sans`       |
| Icons            | **Lucide** (CDN — `unpkg.com/lucide`)    |
| Charts           | **Chart.js** (CDN)                       |
| PDF Export       | **html2pdf.js** (CDN)                    |
| WebSocket Client | **Socket.IO** client (CDN v4.7.2)       |
| WebRTC           | **SimplePeer** (CDN v9.11.1 for video calls) |
| Interactivity    | Vanilla JavaScript (no frontend framework/SPA) |

## Database

| Property         | Value                                    |
|------------------|------------------------------------------|
| Engine           | **SQLite**                               |
| Location         | `instance/medmining.db`                  |
| URI Config       | `DATABASE_URL` env var, default: `sqlite:///medmining.db` |
| Migration        | Manual via `update_db.py` (ALTER TABLE scripts) |
| Schema Init      | Auto-created via `db.create_all()` in app factory |

## Configuration

| Variable          | Purpose                                 | Source    |
|-------------------|-----------------------------------------|-----------|
| `SECRET_KEY`      | Flask session encryption                | `.env`    |
| `DATABASE_URL`    | SQLAlchemy database URI                 | `.env`    |
| `GEMINI_API_KEY`  | Google Gemini AI API key                | `.env`    |
| `PORT`            | Server port (default 5000)              | `.env`    |

## Dev Server

| Property         | Value                                    |
|------------------|------------------------------------------|
| Entry Point      | `run.py` → `python run.py`              |
| Server           | Flask development server via SocketIO   |
| Port             | 5000                                     |
| Debug Mode       | Enabled (`debug=True`)                   |
| Werkzeug         | `allow_unsafe_werkzeug=True`            |

## Build & Deployment

- No production build pipeline configured
- No Docker/containerization setup
- No CI/CD configuration detected
- Development server used directly (Werkzeug)
