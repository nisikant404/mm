from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import MedicalRecord, User, Appointment, Prescription, Notification
from app import db
import json

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

