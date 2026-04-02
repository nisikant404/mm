from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models.models import MedicalRecord, User, Appointment, Prescription, Notification, LabReport, VitalSigns
from app import db
import json
from datetime import datetime

doctor = Blueprint('doctor', __name__)


@doctor.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('patient.dashboard'))
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.created_at.desc()).all()
    patient_ids = set(a.patient_id for a in appointments)
    record_patients = (db.session.query(User)
                       .join(MedicalRecord, User.id == MedicalRecord.patient_id)
                       .filter(MedicalRecord.doctor_id == current_user.id)
                       .distinct().all())
    for rp in record_patients:
        patient_ids.add(rp.id)
    patients = User.query.filter(User.id.in_(patient_ids)).all() if patient_ids else []
    return render_template('doctor/dashboard.html', appointments=appointments, patients=patients)


@doctor.route('/create-prescription', methods=['POST'])
@login_required
def create_prescription():
    if current_user.role != 'doctor':
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    try:
        prescription = Prescription(
            patient_id=data.get('patient_id'),
            doctor_id=current_user.id,
            appointment_id=data.get('appointment_id'),
            medicines=json.dumps(data.get('medicines', [])),
            notes=data.get('notes', ''),
            diagnosis_at_rx=data.get('diagnosis_at_rx', ''),
            pharmacy_notes=data.get('pharmacy_notes', ''),
            refills_allowed=int(data.get('refills_allowed', 0)),
        )
        db.session.add(prescription)

        notification = Notification(
            user_id=data.get('patient_id'),
            title="New Digital Prescription",
            message=f"{current_user.name} has issued a new prescription for you.",
            type='success'
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({"message": "Prescription generated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@doctor.route('/patient-history/<int:patient_id>')
@login_required
def patient_history(patient_id):
    if current_user.role != 'doctor':
        return jsonify({"error": "Unauthorized"}), 403

    patient = User.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.date.desc()).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.date.desc()).all()
    lab_reports = LabReport.query.filter_by(patient_id=patient_id).order_by(LabReport.date.desc()).all()
    vitals = VitalSigns.query.filter_by(patient_id=patient_id).order_by(VitalSigns.recorded_at.desc()).limit(5).all()

    timeline = []

    for r in records:
        timeline.append({
            'date': r.date.strftime('%d %b %Y'),
            '_sort_date': r.date.isoformat(),
            'type': 'Medical Record',
            'record_type': r.record_type or 'ai_triage',
            'title': r.diagnosis or r.chief_complaint or "General Consultation",
            'detail': r.notes or r.symptoms or '',
            'risk': r.risk_level or 'low',
            'icd_code': r.icd_code or '',
            'source': r.source or 'ai',
        })

    for p in prescriptions:
        try:
            meds = json.loads(p.medicines)
        except Exception:
            meds = []
        med_str = ", ".join(f"{m.get('name','?')} ({m.get('dosage','?')})" for m in meds)
        timeline.append({
            'date': p.date.strftime('%d %b %Y'),
            '_sort_date': p.date.isoformat(),
            'type': 'Prescription',
            'record_type': 'prescription',
            'title': f"By {p.doctor.name if p.doctor else 'Specialist'}",
            'detail': med_str,
            'notes': p.notes or '',
            'diagnosis_at_rx': p.diagnosis_at_rx or '',
            'is_active': p.is_active,
        })

    for lr in lab_reports:
        timeline.append({
            'date': lr.date.strftime('%d %b %Y'),
            '_sort_date': lr.date.isoformat(),
            'type': 'Lab Report',
            'record_type': lr.report_type or 'lab_report',
            'title': (lr.report_type or 'Lab Report').replace('_', ' ').title(),
            'detail': lr.findings or lr.raw_text or '',
            'risk': lr.overall_status or 'normal',
            'lab_name': lr.lab_name or '',
        })

    timeline.sort(key=lambda x: x['_sort_date'], reverse=True)

    # Latest vitals
    vitals_data = None
    if vitals:
        v = vitals[0]
        vitals_data = {
            'bp': f"{v.bp_systolic}/{v.bp_diastolic}" if v.bp_systolic else None,
            'pulse': v.pulse,
            'spo2': v.spo2,
            'weight': v.weight_kg,
            'temp': v.temperature,
            'glucose': v.blood_glucose,
            'recorded_at': v.recorded_at.strftime('%d %b %Y'),
        }

    return jsonify({
        "patient": {
            "name": patient.name,
            "email": patient.email,
            "id": patient.id,
            "dob": patient.dob.strftime('%d %b %Y') if patient.dob else None,
            "blood_group": patient.blood_group or '—',
            "allergies": patient.allergies or '—',
            "chronic_conditions": patient.chronic_conditions or '—',
            "emergency_contact": f"{patient.emergency_contact_name} ({patient.emergency_contact_phone})" if patient.emergency_contact_name else None,
        },
        "vitals": vitals_data,
        "history": timeline
    })


@doctor.route('/toggle-availability', methods=['POST'])
@login_required
def toggle_availability():
    if current_user.role != 'doctor':
        return jsonify({"error": "Unauthorized"}), 403
    current_user.is_available = not current_user.is_available
    db.session.commit()
    return jsonify({"available": current_user.is_available})
