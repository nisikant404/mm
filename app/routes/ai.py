from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import MedicalRecord
import google.genai as genai
import os
import json
from PIL import Image
import io

ai_bp = Blueprint('ai', __name__)

def get_genai_client():
    """Return a configured genai.Client or None when the key is missing/placeholder."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def resolve_ai_model_name(requested_name: str | None, default: str = 'gemini-2.5-flash') -> tuple[str, str]:
    """
    Returns (provider_model_name_for_gemini_sdk, label_name_for_ui).
    We accept 'chatgpt' as a UI choice; unless OpenAI is integrated, it maps to Gemini.
    Deprecated 1.5 model names are mapped to their 2.5 equivalents.
    """
    name = (requested_name or default).strip()
    lowered = name.lower()
    if lowered in {'chatgpt', 'gpt', 'gpt-4', 'gpt-4o', 'openai'}:
        return ('gemini-2.5-flash', 'chatgpt')
    # Map deprecated 1.5 model names to current equivalents
    _MODEL_ALIASES = {
        'gemini-1.5-flash': 'gemini-2.5-flash',
        'gemini-1.5-pro': 'gemini-2.5-pro',
        'gemini-25-flash': 'gemini-2.5-flash',
        'gemini-25-pro': 'gemini-2.5-pro',
    }
    resolved = _MODEL_ALIASES.get(lowered, name)
    return (resolved, resolved)

def _safe_snip(text: str, limit: int = 1200) -> str:
    text = (text or '').strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"

def extract_pdf_text(file_bytes: bytes) -> tuple[str, str]:
    """
    Best-effort PDF text extraction for simulation mode.
    Returns (text, note). If extraction isn't available, text will be empty and note explains why.
    """
    try:
        from pypdf import PdfReader  # optional dependency
    except Exception:
        return ("", "PDF text extraction unavailable (install `pypdf` to improve simulation).")

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        parts: list[str] = []
        for i, page in enumerate(reader.pages[:5]):
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                parts.append("")
        text = "\n".join([p for p in parts if p.strip()])
        return (text.strip(), "Extracted up to first 5 pages (text layer only).")
    except Exception as e:
        return ("", f"Could not extract PDF text: {str(e)}")

def pdf_to_pil_images(file_bytes: bytes, max_pages: int = 3, dpi: int = 200) -> tuple[list[Image.Image], str]:
    """
    Convert a PDF into a small list of PIL images for Gemini vision OCR.
    Used when GEMINI_API_KEY is configured (live OCR path).
    """
    try:
        import fitz  # PyMuPDF
    except Exception:
        return [], "PDF->image conversion unavailable. Install `pymupdf`."

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return [], f"Could not open PDF: {str(e)}"

    images: list[Image.Image] = []
    page_count = min(len(doc), max_pages)
    try:
        for i in range(page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            images.append(img)
    except Exception as e:
        return [], f"Could not rasterize PDF pages: {str(e)}"

    return images, f"Converted {len(images)} page(s) to images at {dpi} DPI."

def simulated_medicine_response(filename: str, file_bytes: bytes) -> dict:
    name = "Unknown"
    kind = "document"
    raw = ""
    note = ""

    if filename.endswith(".pdf"):
        raw, note = extract_pdf_text(file_bytes)
    else:
        note = "Image OCR not available in simulation mode (no vision/OCR key configured)."

    low = raw.lower()
    if any(k in low for k in ["tablet", "capsule", "mg", "ml", "dose", "dosage", "amoxicillin", "paracetamol", "ibuprofen"]):
        kind = "medicine"
    if any(k in low for k in ["rx", "sig:", "take", "bd", "tds", "od", "bid", "tid"]):
        kind = "prescription"

    # crude "name" guess
    for candidate in ["amoxicillin", "paracetamol", "acetaminophen", "ibuprofen", "azithromycin", "metformin", "omeprazole"]:
        if candidate in low:
            name = candidate.title()
            break

    detailed = (
        f"**File received**: `{filename}`\n\n"
        f"{'PDF text note' if filename.endswith('.pdf') else 'Note'}: {note}\n\n"
        "This is a **simulation** response generated locally because the live AI key is not configured. "
        "If your PDF contains selectable text, I’ll base the summary on it; scanned PDFs/images need a vision OCR model.\n\n"
        f"**What I could read (snippet)**:\n{_safe_snip(raw, 900) if raw else '(no extractable text found)'}\n\n"
        "If you configure the API key, the system can do full OCR/vision and produce a richer analysis."
    )

    return {
        "type": kind,
        "confidence_score": 55 if raw else 15,
        "name": name if name != "Unknown" else ("Multiple" if kind == "prescription" else "Unknown"),
        "is_mock": True,
        "detailed_analysis": detailed,
        "risk_profile": {
            "severity": "medium" if kind in {"medicine", "prescription"} else "low",
            "warnings": [
                "Do not self-medicate; confirm drug name and dose with a pharmacist/doctor.",
                "Seek urgent care for swelling of face/lips, trouble breathing, or severe rash."
            ],
            "side_effects": ["Depends on medication; needs proper identification."],
            "precautions": ["Share allergies, pregnancy status, and current meds with clinician."]
        },
        "extracted_data": {
            "composition": "Unknown (simulation)",
            "dosage_instructions": "Unknown (simulation)",
            "expiry": "",
            "is_handwritten": kind == "prescription"
        },
        "raw_ocr": _safe_snip(raw, 1200) if raw else ""
    }

def simulated_lab_response(filename: str, file_bytes: bytes) -> dict:
    raw = ""
    note = ""
    if filename.endswith(".pdf"):
        raw, note = extract_pdf_text(file_bytes)
    else:
        note = "Image OCR not available in simulation mode (no vision/OCR key configured)."

    low = raw.lower()
    report_type = "Lab Report"
    if any(k in low for k in ["hemoglobin", "wbc", "rbc", "platelet", "cbc"]):
        report_type = "Complete Blood Count (CBC)"
    elif any(k in low for k in ["cholesterol", "hdl", "ldl", "triglycerides", "lipid"]):
        report_type = "Lipid Profile"
    elif any(k in low for k in ["glucose", "hba1c", "a1c"]):
        report_type = "Glucose / HbA1c"

    interpretation = (
        f"**File received**: `{filename}`\n\n"
        f"{'PDF text note' if filename.endswith('.pdf') else 'Note'}: {note}\n\n"
        "This is a **simulation** response generated locally because the live AI key is not configured. "
        "For scanned PDFs/images, enable a vision model to extract numbers accurately.\n\n"
        f"**What I could read (snippet)**:\n{_safe_snip(raw, 900) if raw else '(no extractable text found)'}\n\n"
        "If you paste the key values (e.g., Hb, WBC, Platelets) I can interpret them even in simulation."
    )

    level = "low" if raw else "medium"
    return {
        "report_type": report_type,
        "patient_info": "From uploaded file (simulation)" if raw else "Unknown (simulation)",
        "is_mock": True,
        "detailed_interpretation": interpretation,
        "findings": [],
        "risk_assessment": {
            "level": level,
            "primary_concerns": ["Unable to extract structured values in simulation"] if not raw else ["Review extracted text for key parameters"],
            "action_plan": [
                "If this is a scanned report, upload again after enabling AI key (vision/OCR).",
                "If PDF has selectable text, ensure it isn't an image-only scan.",
                "You can also paste the test values here for interpretation."
            ]
        }
    }

def parse_json_from_gemini_text(text: str) -> dict:
    """
    Gemini sometimes wraps JSON in markdown fences or adds leading text.
    This helper extracts the most likely JSON object and parses it.
    """
    cleaned = (text or '').strip()
    cleaned = cleaned.replace('```json', '').replace('```', '').strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise

def auto_save_record(result: dict, kind: str, symptoms_val: str = "") -> bool:
    try:
        if kind == "risk":
            record = MedicalRecord(
                patient_id=current_user.id,
                symptoms=symptoms_val,
                diagnosis=f"Risk Analysis: {result.get('riskLevel', 'unknown')} Risk",
                notes=result.get('analysis', ''),
                risk_score=result.get('riskScore'),
                risk_level=result.get('riskLevel'),
                ai_suggestions=", ".join(result.get('suggestions', [])),
                is_medicine_report=False
            )
        elif kind == "medicine":
            record = MedicalRecord(
                patient_id=current_user.id,
                symptoms="Medicine Analysis",
                diagnosis=result.get('name', ''),
                notes=result.get('detailed_analysis', ''),
                risk_score=50 if result.get('risk_profile', {}).get('severity') == 'medium' else (80 if result.get('risk_profile', {}).get('severity') == 'high' else 20),
                risk_level=result.get('risk_profile', {}).get('severity', 'low'),
                ai_suggestions=", ".join(result.get('risk_profile', {}).get('precautions', []) + result.get('risk_profile', {}).get('warnings', [])),
                is_medicine_report=True
            )
        elif kind == "lab":
            detailed_interp = result.get('detailed_interpretation', '')
            record = MedicalRecord(
                patient_id=current_user.id,
                symptoms=f"Lab Risk Mining: {result.get('report_type', '')}",
                diagnosis=detailed_interp[:200] + '...' if detailed_interp else "",
                notes=f"Primary Concerns: {', '.join(result.get('risk_assessment', {}).get('primary_concerns', []))}",
                risk_score=75 if any(f.get('status') != 'normal' for f in result.get('findings', [])) else 15,
                risk_level=result.get('risk_assessment', {}).get('level', 'low'),
                ai_suggestions=", ".join(result.get('risk_assessment', {}).get('action_plan', [])),
                is_medicine_report=False
            )
        else:
            return False
            
        db.session.add(record)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"DB auto-save Error: {str(e)}")
        return False

def get_mock_risk_analysis(symptoms):
    return {
        "riskScore": 72,
        "riskLevel": "high",
        "recommendedSpecialist": "Cardiologist",
        "is_mock": True,
        "analysis": f"Based on the symptoms provided ({', '.join(symptoms)}), our Risk Mining engine has identified a high correlation with cardiovascular distress. \n\nThe presence of these symptoms suggests an acute physiological strain that requires immediate clinical correlation. In a typical ChatGPT-style analysis, we would observe that the 'Risk Mining' algorithms are flagging potential issues with myocardial oxygen demand. \n\nThis simulation indicates that your profile matches patterns often associated with hypertensive urgency or early-stage ischemic events. The risk mining process identifies these as high-priority signals that should not be ignored. \n\nPlease note that this is a simulated report because the live AI API key is not currently configured in your .env file.",
        "suggestions": [
            "Monitor blood pressure every 4 hours",
            "Avoid strenuous physical activity immediately",
            "Schedule an urgent consultation with a Cardiologist",
            "Maintain a low-sodium diet and stay hydrated"
        ]
    }

def get_mock_medicine_analysis():
    return {
        "type": "medicine",
        "confidence_score": 98,
        "name": "Amoxicillin 500mg",
        "is_mock": True,
        "detailed_analysis": "Amoxicillin is a broad-spectrum penicillin-type antibiotic used to treat various bacterial infections. It works by stopping the growth of bacteria. \n\nIn this Risk Mining profile, we analyze the pharmacological impact of Amoxicillin on the patient's current health state. It is highly effective for respiratory tract infections, urinary tract infections, and skin infections. \n\nHowever, the Risk Mining engine flags potential gastrointestinal distress as a common side effect. It is crucial to complete the full course of the antibiotic as prescribed to prevent the development of antibiotic-resistant bacteria. \n\nThis is a simulated analysis provided for demonstration purposes while the AI API key is being configured.",
        "risk_profile": {
            "severity": "low",
            "warnings": ["Do not use if allergic to penicillin", "May decrease effectiveness of oral contraceptives"],
            "side_effects": ["Nausea", "Diarrhea", "Rash", "Vomiting"],
            "precautions": ["Take with food to minimize stomach upset", "Complete the entire prescribed course"]
        },
        "extracted_data": {
            "composition": "Amoxicillin Trihydrate",
            "dosage_instructions": "One capsule every 8 hours (TDS) for 7 days",
            "expiry": "12/2027",
            "is_handwritten": False
        },
        "raw_ocr": "AMOXICILLIN CAPSULES BP 500mg. Each capsule contains Amoxicillin Trihydrate equivalent to Amoxicillin 500mg."
    }

def get_mock_lab_analysis():
    return {
        "report_type": "Complete Blood Count (CBC)",
        "patient_info": "Simulated Patient Data",
        "is_mock": True,
        "detailed_interpretation": "This simulated CBC report shows several key parameters that the Risk Mining engine has analyzed. The Hemoglobin levels appear slightly below the reference range, suggesting mild anemia. \n\nThe White Blood Cell (WBC) count is at the upper limit of normal, which could indicate a minor underlying inflammatory response or recent recovery from an infection. \n\nRisk Mining helps connect these dots: low hemoglobin combined with borderline high WBC often points towards a need for iron-deficiency screening or further investigation into inflammatory markers. \n\nThis ChatGPT-style interpretation is a simulation provided to show how MedMining AI handles clinical data once a valid API key is set.",
        "findings": [
            {
                "parameter": "Hemoglobin",
                "value": "11.2",
                "unit": "g/dL",
                "reference_range": "13.5 - 17.5",
                "status": "low",
                "risk_explanation": "Low hemoglobin levels reduce oxygen transport capacity, leading to fatigue and potential cardiac strain."
            },
            {
                "parameter": "WBC Count",
                "value": "10.8",
                "unit": "10^3/uL",
                "reference_range": "4.5 - 11.0",
                "status": "normal",
                "risk_explanation": "WBC is within normal range but at the higher end, suggesting a vigilant immune system."
            }
        ],
        "risk_assessment": {
            "level": "medium",
            "primary_concerns": ["Mild Anemia", "Borderline Inflammatory Response"],
            "action_plan": [
                "Consult a physician regarding iron supplements",
                "Repeat CBC test in 4 weeks",
                "Increase intake of iron-rich foods (spinach, red meat)"
            ]
        }
    }

@ai_bp.route('/analyze-risk', methods=['POST'])
@login_required
def analyze_risk():
    data = request.get_json()
    symptoms = data.get('symptoms', [])
    sdk_model_name, label_model_name = resolve_ai_model_name(None, default='gemini-2.5-flash')
    
    client = get_genai_client()
    if not client:
        mock_res = get_mock_risk_analysis(symptoms)
        mock_res['analysis'] = f"**[Simulation Mode - {label_model_name.upper()}]**\n\n" + mock_res['analysis']
        if data.get('save_record'):
            if auto_save_record(mock_res, 'risk', ",".join(symptoms)):
                mock_res['saved'] = True
        return jsonify(mock_res)
    
    try:
        prompt = f"""You are 'MedMining AI', an advanced Predictive Risk Mining engine.
        Patient Symptoms: {', '.join(symptoms)}
        Patient History: None provided
        
        Perform a deep 'Risk Mining' analysis. Provide a ChatGPT-style comprehensive response.
        
        Format the response as a strict JSON object:
        {{
          "riskScore": 0-100,
          "riskLevel": "low" | "medium" | "high" | "critical",
          "recommendedSpecialist": "e.g. Cardiologist",
          "analysis": "A very long, detailed, ChatGPT-style clinical interpretation (4-5 paragraphs). Explain the physiological connections between the symptoms and the mined risks.",
          "suggestions": ["list of detailed mitigation strategies"]
        }}"""

        response = client.models.generate_content(model=sdk_model_name, contents=prompt)
        json_str = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(json_str)
        if data.get('save_record'):
            if auto_save_record(result, 'risk', ",".join(symptoms)):
                result['saved'] = True
        return jsonify(result)
    except Exception as e:
        print(f"Risk Analysis Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/analyze-medicine', methods=['POST'])
@login_required
def analyze_medicine():
    sdk_model_name, label_model_name = resolve_ai_model_name(None, default='gemini-2.5-flash')
    
    client = get_genai_client()
    if not client:
        if 'medicineImage' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['medicineImage']
        filename = (file.filename or "upload").lower()
        file_bytes = file.read()
        res = simulated_medicine_response(filename, file_bytes)
        res['detailed_analysis'] = f"**[Simulation Mode - {label_model_name.upper()}]**\n\n" + res['detailed_analysis']
        if request.form.get('save_record') == 'true':
            if auto_save_record(res, 'medicine'):
                res['saved'] = True
        return jsonify(res)
    
    try:
        if 'medicineImage' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['medicineImage']
        filename = file.filename.lower()

        prompt = """You are 'MedMining AI', an elite Medical Risk Mining specialist. 
        Analyze the provided image or document (medicine bottle, blister pack, or handwritten prescription) with extreme accuracy.
        
        Your goal is to provide a 'ChatGPT-style' comprehensive and detailed analysis, focusing on RISK MINING and safety.
        
        Perform the following tasks:
        1. OCR: Extract all text from the image/document, including handwritten notes.
        2. Classification: Determine if this is a 'Medicine Label', 'Handwritten Prescription', or 'Medical Document'.
        3. Detailed Analysis:
           - If it's a medicine: Provide an in-depth profile including Chemical Composition, Pharmacological Action, Primary Uses, and Contraindications.
           - If it's a prescription: Decode the doctor's handwriting, list all medicines, their dosages, and the intended treatment plan.
        
        4. Risk Assessment: Evaluate potential side effects, drug-drug interactions (if multiple are visible), and critical safety warnings.
        
        Format the response as a strict JSON object:
        {
          "type": "medicine" | "prescription" | "document",
          "confidence_score": 0-100,
          "name": "Primary medicine name or 'Multiple' for prescriptions",
          "detailed_analysis": "A long, detailed, ChatGPT-style explanation (4-5 paragraphs) covering everything about the medicine/prescription, its role in treatment, and what the patient needs to know.",
          "risk_profile": {
            "severity": "low" | "medium" | "high",
            "warnings": ["detailed list of safety warnings"],
            "side_effects": ["comprehensive list of possible side effects"],
            "precautions": ["critical precautions to take"]
          },
          "extracted_data": {
            "composition": "list of active ingredients",
            "dosage_instructions": "clear summary of frequency and timing",
            "expiry": "extracted expiry date",
            "is_handwritten": true | false
          },
          "raw_ocr": "full text extracted for reference"
        }"""
        
        # Handle PDF vs Image (live OCR)
        content_parts = []
        if filename.endswith('.pdf'):
            file_bytes = file.read()
            images, note = pdf_to_pil_images(file_bytes, max_pages=3, dpi=200)
            if not images:
                raise ValueError(note)
            # Put prompt first, then images for OCR/vision.
            content_parts = [prompt] + images
        else:
            img = Image.open(io.BytesIO(file.read()))
            content_parts = [prompt, img]

        response = client.models.generate_content(model=sdk_model_name, contents=content_parts)
        result = parse_json_from_gemini_text(response.text)
        if request.form.get('save_record') == 'true':
            if auto_save_record(result, 'medicine'):
                result['saved'] = True
        return jsonify(result)
    except Exception as e:
        print(f"AI Vision Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/analyze-lab-report', methods=['POST'])
@login_required
def analyze_lab_report():
    sdk_model_name, label_model_name = resolve_ai_model_name(None, default='gemini-2.5-flash')

    client = get_genai_client()
    if not client:
        if 'labReport' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['labReport']
        filename = (file.filename or "upload").lower()
        file_bytes = file.read()
        res = simulated_lab_response(filename, file_bytes)
        res['detailed_interpretation'] = f"**[Simulation Mode - {label_model_name.upper()}]**\n\n" + res['detailed_interpretation']
        if request.form.get('save_record') == 'true':
            if auto_save_record(res, 'lab'):
                res['saved'] = True
        return jsonify(res)
    
    try:
        if 'labReport' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['labReport']
        filename = file.filename.lower()

        prompt = """You are 'MedMining AI', a specialized Clinical Risk Analyst. 
        Analyze the provided lab report image or PDF with clinical precision.
        
        Your goal is to provide a 'ChatGPT-style' deep dive into the lab results, identifying potential health risks through 'Risk Mining'.
        
        Tasks:
        1. Parameter Extraction: Identify every test parameter, its value, unit, and reference range.
        2. Risk Mining: For every abnormal result, explain WHY it is a risk and what health systems it might affect.
        3. Comprehensive Summary: Provide a long, detailed explanation (4-5 paragraphs) of the entire report, how the parameters relate to each other, and the overall health status.
        
        Format as a strict JSON:
        {
          "report_type": "string (e.g. CBC, Lipid Profile)",
          "patient_info": "extracted patient name and details",
          "detailed_interpretation": "A long, detailed, ChatGPT-style interpretation of the entire lab report. Connect different findings to provide a holistic view of the patient's health and potential underlying risks.",
          "findings": [
            {
              "parameter": "name of test",
              "value": "extracted value",
              "unit": "e.g. mg/dL",
              "reference_range": "e.g. 70-100",
              "status": "normal" | "high" | "low",
              "risk_explanation": "Detailed explanation of what this specific result means for the patient's health"
            }
          ],
          "risk_assessment": {
            "level": "low" | "medium" | "high",
            "primary_concerns": ["list of major health concerns found"],
            "action_plan": ["step-by-step recommendations"]
          }
        }"""

        if filename.endswith('.pdf'):
            file_bytes = file.read()
            images, note = pdf_to_pil_images(file_bytes, max_pages=3, dpi=200)
            if not images:
                raise ValueError(note)
            content_parts = [prompt] + images
        else:
            img = Image.open(io.BytesIO(file.read()))
            content_parts = [prompt, img]

        response = client.models.generate_content(model=sdk_model_name, contents=content_parts)
        result = parse_json_from_gemini_text(response.text)
        if request.form.get('save_record') == 'true':
            if auto_save_record(result, 'lab'):
                result['saved'] = True
        return jsonify(result)
    except Exception as e:
        print(f"Lab Report AI Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/symptom-chat', methods=['POST'])
@login_required
def symptom_chat():
    try:
        data = request.get_json()
        user_message = (data.get('message') or '').strip()
        chat_history = data.get('history', [])
        sdk_model_name, label_model_name = resolve_ai_model_name(None, default='gemini-2.5-flash')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        client = get_genai_client()
        if not client:
            msg_lower = user_message.lower()
            urgent = any(k in msg_lower for k in [
                "chest pain", "pressure in chest", "shortness of breath", "difficulty breathing",
                "faint", "passed out", "unconscious", "stroke", "slurred", "one-sided weakness",
                "severe bleeding", "vomiting blood", "blood in vomit"
            ])
            specialist = "General Physician"
            if any(k in msg_lower for k in ["chest", "heart", "palpitations"]):
                specialist = "Cardiologist"
            elif any(k in msg_lower for k in ["cough", "breath", "asthma", "wheeze"]):
                specialist = "Pulmonologist"
            elif any(k in msg_lower for k in ["headache", "migraine", "seizure", "numb", "tingling"]):
                specialist = "Neurologist"
            elif any(k in msg_lower for k in ["skin", "rash", "itch", "eczema"]):
                specialist = "Dermatologist"
            elif any(k in msg_lower for k in ["stomach", "abdominal", "vomit", "diarrhea"]):
                specialist = "Gastroenterologist"

            followups = [
                "How long has this been happening?",
                "How severe is it (0–10)?",
                "Do you have fever, dizziness, or shortness of breath?",
                "Any known conditions or medicines you're taking?"
            ]
            response = (
                f"**[Simulation Mode — {label_model_name.upper()}]**\n\n"
                f"Here's a quick triage-style summary based on what you wrote:\n"
                f"- **Possible concern areas**: depends on duration/severity and associated symptoms.\n"
                f"- **Recommended specialist**: **{specialist}**\n\n"
                + ("**Urgent warning**: Your symptoms could be serious. Please seek **emergency care immediately** or call your local emergency number.\n\n" if urgent else "")
                + "**Follow-up questions** (reply with answers):\n"
                + "\n".join([f"- {q}" for q in followups])
                + "\n\n**Disclaimer**: This is AI triage, not a diagnosis. If symptoms worsen, seek medical care."
            )
            return jsonify({"response": response, "is_mock": True, "ai_model": label_model_name})

        # System prompt for the symptom checker
        system_prompt = """You are 'MedMining AI Assistant', a professional medical triage specialist. 
        Your goal is to help patients understand their symptoms and provide preliminary advice.
        
        Guidelines:
        1. Be professional, empathetic, and clear.
        2. Always include a disclaimer: 'This is an AI-powered triage and not a final diagnosis. Please consult a professional doctor for serious conditions.'
        3. Ask follow-up questions to better understand the patient's condition (e.g., 'How long have you had this?', 'Is there any pain?').
        4. If symptoms sound critical (e.g., chest pain, difficulty breathing), immediately advise seeking emergency care.
        5. Suggest a possible specialist the patient might need to see.
        6. Keep responses concise and structured using bullet points where necessary."""

        # Build conversation history for the API call
        contents = []
        for i, message in enumerate(chat_history[-6:]):
            role = 'user' if i % 2 == 0 else 'model'
            contents.append(genai.types.Content(role=role, parts=[genai.types.Part.from_text(text=message)]))

        # For the first turn, prepend the system prompt to the user message.
        message_to_send = user_message
        if not chat_history:
            message_to_send = f"{system_prompt}\n\nPatient: {user_message}"

        contents.append(genai.types.Content(role='user', parts=[genai.types.Part.from_text(text=message_to_send)]))

        response = client.models.generate_content(model=sdk_model_name, contents=contents)
        return jsonify({"response": response.text, "ai_model": label_model_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
