# Architecture

## Pattern

**Server-rendered Monolith** — Flask application with Jinja2 templates, no SPA/frontend framework.

- Backend: Flask (Python) with Blueprint-based route organization
- Frontend: Server-rendered HTML with Tailwind CSS + vanilla JS for interactivity
- Real-time: Socket.IO for chat messaging and WebRTC signaling
- AI: Google Gemini API integration with graceful simulation fallback

## Application Factory

Entry point: `run.py` → `app/__init__.py` :: `create_app()`

```
run.py
  └─ create_app()                    # app/__init__.py
       ├─ Flask config (SECRET_KEY, DATABASE_URI)
       ├─ Extension init (db, bcrypt, login_manager, socketio, CORS)
       ├─ Context processors (notifications)
       ├─ Blueprint registration (5 blueprints)
       ├─ SocketIO event handlers (chat, video signaling)
       └─ db.create_all() within app_context
```

## Blueprints & URL Prefixes

| Blueprint       | Module                         | Prefix           | Purpose                    |
|-----------------|--------------------------------|------------------|----------------------------|
| `auth`          | `app/routes/auth.py`           | `/auth`          | Login, register, logout    |
| `patient`       | `app/routes/patient.py`        | `/patient`       | Patient dashboard & tools  |
| `doctor`        | `app/routes/doctor.py`         | `/doctor`        | Doctor dashboard & actions |
| `ai_bp`         | `app/routes/ai.py`             | `/ai`            | AI analysis endpoints      |
| `consultation`  | `app/routes/consultation.py`   | `/consultation`  | Chat & video call          |

Plus one standalone route: `GET /` → `landing.html` (registered directly on app)

## Data Flow

### Authentication Flow
```
User → POST /auth/login
  → bcrypt.check_password_hash()
  → flask_login.login_user()
  → Redirect based on role (patient/doctor)
```

### AI Analysis Flow
```
Patient → POST /ai/analyze-risk (or medicine/lab-report/symptom-chat)
  → get_genai_client() checks GEMINI_API_KEY
  │
  ├─ Key present → Gemini SDK call → parse JSON response → return
  └─ Key absent  → Simulation/mock response → return
```

### Real-time Chat Flow
```
Client A → socket.emit('send_message', {room, sender, content})
  → Server handler persists Message + creates Notification
  → Server emits 'receive_message' to room
  → Client B receives and appends to DOM
```

### Video Call Flow (WebRTC Signaling)
```
Caller → SimplePeer(initiator:true) → 'signal' event
  → socket.emit('call_user', {signalData, userToCall})
  → Server emits 'call_incoming' to target room
  → Callee creates SimplePeer(initiator:false), signals back
  → socket.emit('answer_call') → Server emits 'call_accepted'
  → Direct P2P stream established
```

## Data Models (6 models in `app/models/models.py`)

| Model             | Key Fields                                     | Relationships           |
|-------------------|-------------------------------------------------|------------------------|
| `User`            | name, email, password, role, specialization, age, gender, blood_group | FK target for all others |
| `MedicalRecord`   | patient_id, doctor_id, symptoms, diagnosis, risk_score, risk_level, ai_suggestions | FK → User (patient, doctor) |
| `Appointment`     | patient_id, doctor_id, date, status, reason, type | FK → User (patient, doctor) |
| `Message`         | sender_id, receiver_id, content, timestamp      | FK → User (sender, receiver) |
| `Prescription`    | patient_id, doctor_id, appointment_id, medicines (JSON string), notes | FK → User, Appointment |
| `Notification`    | user_id, title, message, is_read                | FK → User               |

### Role-Based Access
- `User.role` is either `'patient'` or `'doctor'`
- Dashboard routes check `current_user.role` and redirect accordingly
- Doctor-only actions (prescriptions, appointment updates) check role before proceeding

## Key Abstractions

### AI Client Factory (`get_genai_client()`)
- Returns `genai.Client` if valid API key exists
- Returns `None` for simulation mode
- All AI routes branch on `client` being `None` vs configured

### Model Name Resolution (`resolve_ai_model_name()`)
- Normalizes model name aliases (deprecated names, "chatgpt" → Gemini)
- Returns `(sdk_name, ui_label)` tuple
- Used by all 4 AI endpoints

### JSON Parsing (`parse_json_from_gemini_text()`)
- Strips markdown code fences from Gemini responses
- Falls back to substring extraction (`{...}`)
- Used by medicine and lab report endpoints

## Entry Points

| Entry Point     | File          | Purpose                        |
|-----------------|---------------|--------------------------------|
| `python run.py` | `run.py`      | Start Flask dev server on :5000|
| `python update_db.py` | `update_db.py` | Manual DB schema migration |
