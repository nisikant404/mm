from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import MedicalRecord, User, Appointment, Prescription, Notification
from app import db
import json

doctor = Blueprint('doctor', __name__)

@doctor.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('patient.dashboard'))
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.date.desc()).all()
    patients = db.session.query(User).join(MedicalRecord, User.id == MedicalRecord.patient_id).filter(MedicalRecord.doctor_id == current_user.id).distinct().all()
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
            medicines=json.dumps(data.get('medicines')),
            notes=data.get('notes')
        )
        db.session.add(prescription)
        
        # Add Notification for Patient
        notification = Notification(
            user_id=data.get('patient_id'),
            title="New Digital Prescription",
            message=f"Dr. {current_user.name} has generated a new digital prescription for you."
        )
        db.session.add(notification)
        
        db.session.commit()
        return jsonify({"message": "Digital Prescription generated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

