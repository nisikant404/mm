# External Integrations

## Google Gemini AI (Primary AI Provider)

| Property         | Value                                          |
|------------------|-------------------------------------------------|
| SDK              | `google-genai` (Python)                         |
| Client Init      | `genai.Client(api_key=...)` in `app/routes/ai.py` |
| Config           | `GEMINI_API_KEY` env var                        |
| Default Model    | `gemini-2.5-flash`                              |
| Supported Models | `gemini-2.5-flash`, `gemini-2.5-pro`           |

### Model Resolution (`resolve_ai_model_name()`)
- Maps deprecated model names (`gemini-1.5-flash` → `gemini-2.5-flash`, etc.)
- Maps "chatgpt/gpt/openai" aliases to `gemini-2.5-flash` (no actual OpenAI integration)
- Returns tuple: `(sdk_model_name, ui_label_name)`

### AI Endpoints

| Endpoint                   | Purpose                          | Input              |
|----------------------------|----------------------------------|---------------------|
| `POST /ai/analyze-risk`    | Symptom-based risk prediction    | JSON symptoms list  |
| `POST /ai/analyze-medicine`| Medicine image/PDF OCR & analysis| Multipart file upload |
| `POST /ai/analyze-lab-report`| Lab report OCR & interpretation| Multipart file upload |
| `POST /ai/symptom-chat`    | Conversational symptom checker   | JSON message + history |

### Simulation Mode
When `GEMINI_API_KEY` is missing or placeholder:
- All AI endpoints return **mock/simulated responses**
- PDF text extraction still works via `pypdf` (text layer only)
- Image OCR is unavailable in simulation
- Mock responses include `"is_mock": true` flag
- Responses are prefixed with `[Simulation Mode — MODEL_NAME]`

### Vision/OCR Pipeline
- **Images**: Loaded via `Pillow` (PIL), sent directly as `Image` objects to Gemini
- **PDFs**: Converted to PIL images via `PyMuPDF` (`fitz`), max 3 pages at 200 DPI
- **Fallback**: `pypdf` text extraction for simulation mode (text layer PDFs only)

## Socket.IO (Real-time Communication)

| Property          | Value                                         |
|-------------------|-----------------------------------------------|
| Server            | `Flask-SocketIO` (Python)                     |
| Client            | `socket.io.js` v4.7.2 (CDN)                  |
| CORS              | `cors_allowed_origins="*"`                    |

### Events

| Event             | Direction      | Purpose                              |
|-------------------|----------------|--------------------------------------|
| `join_room`       | Client → Server | Join a chat/signaling room          |
| `send_message`    | Client → Server | Send chat message (persisted to DB) |
| `receive_message` | Server → Client | Broadcast received message to room  |
| `call_user`       | Client → Server | Initiate WebRTC call signaling      |
| `call_incoming`   | Server → Client | Notify target of incoming call      |
| `answer_call`     | Client → Server | Accept WebRTC call                  |
| `call_accepted`   | Server → Client | Confirm call accepted with signal   |

### Chat Room Naming
- Room ID format: `{lower_user_id}-{higher_user_id}` (sorted)
- Messages persisted to `Message` model with sender/receiver IDs

## WebRTC (Video Calls)

| Property          | Value                                         |
|-------------------|-----------------------------------------------|
| Library           | **SimplePeer** v9.11.1 (CDN)                 |
| Signaling         | Via Socket.IO (above)                         |
| STUN/TURN         | Default browser STUN servers (no custom config)|
| Template          | `app/templates/consultation/video_call.html`  |

### Limitations
- No TURN server configured (will fail behind strict NATs/firewalls)
- No call state management (reload on peer disconnect)
- Signaling uses user ID as room (not a dedicated signaling room)

## CDN Dependencies

| Library           | CDN URL                                        | Purpose              |
|-------------------|------------------------------------------------|----------------------|
| TailwindCSS       | `cdn.tailwindcss.com`                          | CSS framework        |
| Lucide Icons      | `unpkg.com/lucide@latest`                      | Icon library         |
| Chart.js          | `cdn.jsdelivr.net/npm/chart.js`                | Charting             |
| html2pdf.js       | `cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1` | PDF export     |
| Socket.IO client  | `cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2` | WebSocket client  |
| SimplePeer        | `cdnjs.cloudflare.com/ajax/libs/simple-peer/9.11.1` | WebRTC wrapper   |

## Database

| Property          | Value                                         |
|-------------------|-----------------------------------------------|
| Type              | **SQLite** (file-based)                       |
| File Path         | `instance/medmining.db`                       |
| ORM               | Flask-SQLAlchemy                              |
| Authentication    | Flask-Login + Flask-Bcrypt                    |

*No external database service, no Redis, no message broker.*
