from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import MedicalRecord, User, Appointment, Prescription, Notification
from app import db
import json
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from flask import send_file

patient = Blueprint('patient', __name__)

@patient.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('doctor.dashboard'))
    
    history = MedicalRecord.query.filter_by(patient_id=current_user.id).order_by(MedicalRecord.date.desc()).all()
    doctors = User.query.filter_by(role='doctor').all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).order_by(Prescription.date.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    
    # Prepare chart data (Risk scores over time)
    chart_data = []
    risk_records = MedicalRecord.query.filter_by(patient_id=current_user.id).filter(MedicalRecord.risk_score.isnot(None)).order_by(MedicalRecord.date.asc()).all()
    for r in risk_records:
        chart_data.append({
            "date": r.date.strftime('%d %b'),
            "score": r.risk_score
        })

    # Convert prescriptions JSON to objects for template
    for p in prescriptions:
        p.medicines_list = json.loads(p.medicines)

    return render_template('patient/dashboard.html', 
                         history=history, 
                         doctors=doctors, 
                         appointments=appointments, 
                         prescriptions=prescriptions, 
                         notifications=notifications,
                         chart_data=json.dumps(chart_data))

@patient.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return jsonify({"status": "success"})

@patient.route('/medicine-analyzer')
@login_required
def medicine_analyzer():
    return render_template('patient/medicine_analyzer.html')

@patient.route('/symptom-checker')
@login_required
def symptom_checker():
    return render_template('patient/symptom_checker.html')

@patient.route('/lab-analyzer')
@login_required
def lab_analyzer():
    return render_template('patient/lab_analyzer.html')

@patient.route('/save-record', methods=['POST'])
@login_required
def save_record():
    data = request.get_json()
    try:
        record = MedicalRecord(
            patient_id=current_user.id,
            symptoms=data.get('symptoms'),
            diagnosis=data.get('diagnosis'),
            notes=data.get('notes'),
            risk_score=data.get('risk_score'),
            risk_level=data.get('risk_level'),
            ai_suggestions=data.get('ai_suggestions'),
            is_medicine_report=data.get('is_medicine_report', False)
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Record saved successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@patient.route('/match-doctors/<domain>')
@login_required
def match_doctors(domain):
    # Clean the input domain
    domain_clean = (domain or "").lower().strip().replace('"', '').replace("'", "")
    
    # Comprehensive Mapping Table
    SPECIALIZATION_MAP = {
        "cardiologist": ["cardio", "heart", "blood pressure", "chest pain", "cardiology"],
        "dermatologist": ["skin", "derma", "dermatology", "rash", "acne"],
        "neurologist": ["brain", "nerve", "neurology", "headache", "migraine", "stroke"],
        "orthopedic": ["bone", "joint", "ortho", "orthopedic", "fracture", "back pain", "spine"],
        "gastroenterologist": ["stomach", "gastric", "digestion", "gastro", "liver", "intestine"],
        "pulmonologist": ["lung", "breath", "pulmonary", "pulm", "asthma", "cough"],
        "pediatrician": ["child", "baby", "pediatr", "kids", "neonatal"],
        "ophthalmologist": ["eye", "vision", "ophth", "vision", "cataract"],
        "psychiatrist": ["mental", "shrink", "psychat", "depress", "anxiety", "therapy"],
        "oncologist": ["cancer", "tumor", "onco", "chemo"],
        "urologist": ["kidney", "urinary", "uro", "bladder"],
        "ent": ["ear", "nose", "throat", "ent", "sinus", "hearing"]
    }
    
    target_keywords = [domain_clean]
    # Symmetric matching: 
    # 1. Match AI domain to our known categories
    for spec, aliases in SPECIALIZATION_MAP.items():
        # Check if AI domain is a known spec OR contains a known alias
        # OR if a known alias is in the AI domain
        if (domain_clean == spec or 
            any(alias in domain_clean for alias in aliases) or 
            any(domain_clean in alias for alias in aliases)):
            target_keywords.extend(aliases)
            target_keywords.append(spec)
            break
            
    from sqlalchemy import or_
    query = User.query.filter(User.role == 'doctor')
    
    # 1. First Pass: Try matching keywords against doctor specialization
    filters = [User.specialization.ilike(f"%{kw}%") for kw in target_keywords if len(kw) > 1]
    doctors = []
    if filters:
        doctors = query.filter(or_(*filters)).order_by(User.years_experience.desc()).all()
    
    # 2. Second Pass: If still no doctors, check if doctor's specialization string is inside the AI domain
    if not doctors:
        all_doctors = User.query.filter(User.role == 'doctor').all()
        for d in all_doctors:
            if not d.specialization: continue
            doc_spec = d.specialization.lower()
            if doc_spec in domain_clean or domain_clean in doc_spec:
                doctors.append(d)
                
    # 3. Final Fallback: General Physician
    is_fallback = False
    if not doctors:
        is_fallback = True
        doctors = User.query.filter(User.role == 'doctor', 
                                  or_(User.specialization.ilike("%general%"), 
                                      User.specialization.ilike("%physician%"))).order_by(User.years_experience.desc()).all()

    doc_list = []
    # Deduplicate in case multiple passes matched the same doctor
    seen_ids = set()
    for d in doctors:
        if d.id not in seen_ids:
            doc_list.append({
                "id": d.id,
                "name": d.name,
                "specialization": d.specialization,
                "years_experience": getattr(d, 'years_experience', 0)
            })
            seen_ids.add(d.id)
            
    return jsonify({
        "doctors": doc_list, 
        "is_fallback": is_fallback, 
        "original_search": domain,
        "matched_keywords": target_keywords
    })

@patient.route('/book-ai-appointment', methods=['POST'])
@login_required
def book_ai_appointment():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    chat_summary = data.get('chat_summary', 'No summary provided.')
    
    recent_records = MedicalRecord.query.filter_by(patient_id=current_user.id).order_by(MedicalRecord.date.desc()).limit(3).all()
    past_history = "\n--- Past Records ---"
    for r in recent_records:
         past_history += f"\n[{r.date.strftime('%Y-%m-%d')}] {r.diagnosis} - Risk: {r.risk_level}"
         
    full_reason = f"AI Triage Details:\n{chat_summary}\n{past_history}"

    try:
        from datetime import datetime, timedelta
        appt_date = datetime.utcnow() + timedelta(days=1)
        
        appt = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            date=appt_date,
            status='pending',
            reason=full_reason,
            type='text'
        )
        db.session.add(appt)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@patient.route('/download-records')
@login_required
def download_records():
    # 1. Fetch data
    records = MedicalRecord.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    
    # 2. Merge into a timeline
    timeline = []
    for r in records:
        timeline.append({
            'date': r.date,
            'type': 'Clinical Record',
            'title': r.diagnosis or "General Consultation",
            'detail': f"Symptoms: {r.symptoms or 'N/A'}\nNotes: {r.notes or 'N/A'}",
            'meta': f"Risk: {r.risk_level or 'Unknown'}"
        })
    
    for p in prescriptions:
        # Get doctor name
        doc = User.query.get(p.doctor_id)
        doc_name = doc.name if doc else "Specialist"
        
        # Parse medicines
        try:
            med_list = json.loads(p.medicines)
            med_text = ", ".join([f"{m.get('name')} ({m.get('dosage')})" for m in med_list])
        except:
            med_text = "Medication list unavailable"

        timeline.append({
            'date': p.date,
            'type': 'Prescription',
            'title': f"Prescribed by Dr. {doc_name}",
            'detail': f"Medicines: {med_text}",
            'meta': f"Instructions: {p.notes or 'Follow as directed.'}"
        })
    
    # Sort descending
    timeline.sort(key=lambda x: x['date'], reverse=True)
    
    # 3. Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#94a3b8"),
        leftIndent=10
    )

    elements = []
    
    # Header
    elements.append(Paragraph("Personal Medical Timeline", title_style))
    elements.append(Paragraph(f"Patient Name: {current_user.name}", body_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y, %H:%M')}", body_style))
    elements.append(Spacer(1, 24))
    
    if not timeline:
        elements.append(Paragraph("No medical records or prescriptions found in your account history.", body_style))
    else:
        for entry in timeline:
            # Date and Type
            date_str = entry['date'].strftime('%d %B %Y')
            elements.append(Paragraph(f"{date_str} • {entry['type']}", header_style))
            
            # Title
            elements.append(Paragraph(entry['title'], styles['Heading3']))
            
            # Detail
            elements.append(Paragraph(entry['detail'], body_style))
            
            # Meta
            if entry['meta']:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(entry['meta'], meta_style))
            
            elements.append(Spacer(1, 15))
            # Horizontal line substitute
            elements.append(Paragraph("<hr color='#cbd5e1'/>", body_style))
            elements.append(Spacer(1, 15))

    doc.build(elements)
    
    buffer.seek(0)
    filename = f"Medical_Timeline_{current_user.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
