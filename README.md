# MedMining

MedMining is a comprehensive healthcare web application that bridges the gap between patients and doctors through a unified platform. It leverages the power of Large Language Models (LLMs) to provide AI-assisted insights, such as symptom checking, medication analysis, and lab report interpretations. It also features real-time communication tools, including chat and video consultations.

## Features

- **Role-Based Portals**: Dedicated dashboards for Patients and Doctors.
- **Medical Records Management**: Securely store and access patient symptoms, diagnoses, prescriptions, and lab reports.
- **AI-Powered Risk Mining**: Uses Gemini AI to analyze patient symptoms and predict health risks.
- **Smart OCR & Analysis**: Extract and analyze data from uploaded medicine labels, prescriptions, and complex lab reports (PDFs or images).
- **Real-Time Communication**: Integrated Socket.IO for live patient-doctor chat messaging and video consultations.
- **Appointment Scheduling**: Seamless interface for patients to book and manage appointments with specialists.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-SocketIO, Flask-Login
- **Database**: SQLite
- **AI Integration**: Google Gemini (`google-genai`), PyMuPDF (`pymupdf`), Pillow
- **Frontend**: HTML5, CSS3, Jinja2 Templates (Vanilla JS for interactive features)

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- pip (Python package installer)

## Installation & Setup

1. **Clone the repository or navigate to the project directory**
   ```bash
   cd medmining
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   Create a `.env` file in the root directory and add the following context:
   ```env
   # Mandatory for Flask sessions
   SECRET_KEY=your_super_secret_key_here

   # Optional: Defaults to sqlite:///medmining.db
   # DATABASE_URL=sqlite:///medmining.db

   # Mandatory for AI features (Get one from Google AI Studio)
   # Note: If no key is set, the app will run in 'simulation mode' with mock AI responses
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Initialize the Database (Optional)**
   The database tables are generally auto-created on the first run, but you can also run the update script if you need schema migrations:
   ```bash
   python update_db.py
   ```

## Running the Application

1. **Start the Flask server**
   Make sure your virtual environment is activated, then run:
   ```bash
   python run.py
   ```
2. **Access the application**
   Open your web browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)
