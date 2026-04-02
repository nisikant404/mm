from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models.models import User, Appointment, Message, Notification
from app import db
from datetime import datetime

consultation = Blueprint('consultation', __name__)

@consultation.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    target_user = User.query.get_or_404(user_id)
    # Fetch chat history
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    return render_template('consultation/chat.html', target_user=target_user, history=messages)

@consultation.route('/video-call/<int:user_id>')
@login_required
def video_call(user_id):
    target_user = User.query.get_or_404(user_id)
    return render_template('consultation/video_call.html', target_user=target_user)

@consultation.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    reason = data.get('reason')
    
    # In a real app, you'd pick a specific time
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        date=datetime.utcnow(), 
        reason=reason,
        status='pending'
    )
    db.session.add(appointment)
    
    # Add Notification for Doctor
    doctor = User.query.get(doctor_id)
    notification = Notification(
        user_id=doctor_id,
        title="New Appointment Request",
        message=f"Patient {current_user.name} has requested an appointment for: {reason}"
    )
    db.session.add(notification)
    
    db.session.commit()
    return jsonify({"message": "Appointment booked successfully!"})

@consultation.route('/update-appointment-status', methods=['POST'])
@login_required
def update_status():
    data = request.get_json()
    apt_id = data.get('appointment_id')
    new_status = data.get('status')
    
    appointment = Appointment.query.get(apt_id)
    if appointment and (appointment.doctor_id == current_user.id):
        appointment.status = new_status
        
        # Add Notification for Patient
        notification = Notification(
            user_id=appointment.patient_id,
            title="Appointment Status Updated",
            message=f"Dr. {current_user.name} has updated your appointment status to: {new_status}"
        )
        db.session.add(notification)
        
        db.session.commit()
        return jsonify({"message": "Status updated!"})
    return jsonify({"error": "Unauthorized"}), 403

@consultation.route('/set-appointment-date', methods=['POST'])
@login_required
def set_appointment_date():
    """Doctor sets a proposed date that the patient will see."""
    if current_user.role != 'doctor':
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    apt_id = data.get('appointment_id')
    proposed_str = data.get('proposed_date')  # ISO format: "2026-04-10T14:30"

    appointment = Appointment.query.get(apt_id)
    if not appointment or appointment.doctor_id != current_user.id:
        return jsonify({"error": "Not found or unauthorized"}), 403

    try:
        proposed = datetime.strptime(proposed_str, '%Y-%m-%dT%H:%M')
        appointment.proposed_date = proposed
        appointment.status = 'confirmed'

        notification = Notification(
            user_id=appointment.patient_id,
            title="Appointment Confirmed",
            message=f"{current_user.name} has confirmed your appointment on {proposed.strftime('%d %b %Y at %H:%M')}."
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({"message": f"Appointment set for {proposed.strftime('%d %b %Y at %H:%M')}."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

