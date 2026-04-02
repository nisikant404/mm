from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """Unified user model for both patients and doctors."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)          # 'patient' | 'doctor'

    # --- Core Identity ---
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    dob = db.Column(db.Date)                                  # Date of birth
    gender = db.Column(db.String(20))
    profile_pic = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Patient-only fields ---
    blood_group = db.Column(db.String(10))
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    allergies = db.Column(db.Text)                            # Comma-separated
    chronic_conditions = db.Column(db.Text)                   # Comma-separated

    # --- Doctor-only fields ---
    specialization = db.Column(db.String(100))
    years_experience = db.Column(db.Integer, default=0)
    medical_license_no = db.Column(db.String(50))
    hospital_affiliation = db.Column(db.String(200))          # Clinic/Hospital name
    consultation_fee = db.Column(db.Float, default=0.0)       # Fee per session (₹ or $)
    bio = db.Column(db.Text)
    languages_spoken = db.Column(db.String(200))              # e.g. "English, Hindi"
    is_available = db.Column(db.Boolean, default=True)        # Accepting patients?
    rating = db.Column(db.Float, default=4.5)                 # Aggregate star rating


class MedicalRecord(db.Model):
    """AI + Doctor generated clinical records."""
    __tablename__ = 'medical_record'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Record Classification
    record_type = db.Column(db.String(30), default='ai_triage')
    # Options: 'ai_triage', 'lab_report', 'medicine_scan', 'doctor_note', 'risk_analysis'
    source = db.Column(db.String(20), default='ai')           # 'ai' | 'doctor' | 'self'

    # Clinical Content
    chief_complaint = db.Column(db.Text)                      # Patient's main concern
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    icd_code = db.Column(db.String(20))                       # ICD-10 diagnosis code
    medications = db.Column(db.Text)
    notes = db.Column(db.Text)
    ai_suggestions = db.Column(db.Text)

    # Risk Assessment
    risk_score = db.Column(db.Integer)                        # 0-100
    risk_level = db.Column(db.String(20))                     # 'low' | 'medium' | 'high' | 'critical'

    # Vitals at time of record (JSON string)
    vitals = db.Column(db.Text)                               # {"bp":"120/80","pulse":72,...}

    # Flags
    is_medicine_report = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)

    date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='medical_records')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_records')


class Appointment(db.Model):
    """Patient-Doctor consultation booking."""
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Scheduling
    date = db.Column(db.DateTime, nullable=False)
    proposed_date = db.Column(db.DateTime)                    # Doctor-confirmed slot
    duration_minutes = db.Column(db.Integer, default=30)     # 15 | 30 | 60

    # Type & Status
    status = db.Column(db.String(20), default='pending')     # pending | confirmed | completed | cancelled | no_show
    type = db.Column(db.String(20), default='in_person')     # in_person | video | chat

    # Content
    reason = db.Column(db.Text)                              # AI triage summary + past history
    chief_complaint = db.Column(db.String(300))              # Brief complaint for scheduling
    doctor_notes = db.Column(db.Text)                        # Post-consultation notes by doctor
    cancel_reason = db.Column(db.Text)

    # Payment
    fee_charged = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending | paid | waived

    # Video Call
    meeting_link = db.Column(db.String(500))

    # Follow-up chain
    followup_of = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')


class Prescription(db.Model):
    """Digital prescriptions issued by doctors."""
    __tablename__ = 'prescription'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    diagnosis_at_rx = db.Column(db.Text)                     # Working diagnosis when issued
    medicines = db.Column(db.Text, nullable=False)            # JSON: [{name, dosage, duration, frequency}]
    notes = db.Column(db.Text)                               # Doctor's advice
    pharmacy_notes = db.Column(db.Text)                      # Notes for pharmacist
    refills_allowed = db.Column(db.Integer, default=0)
    valid_until = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    date = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_prescriptions')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_prescriptions')


class LabReport(db.Model):
    """Lab/Diagnostic reports — AI-analyzed or doctor-ordered."""
    __tablename__ = 'lab_report'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ordered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    report_type = db.Column(db.String(50))                   # blood_test | xray | mri | ecg | urine_test | ct_scan
    lab_name = db.Column(db.String(200))
    raw_text = db.Column(db.Text)                            # OCR / raw extracted text
    findings = db.Column(db.Text)                            # AI or doctor interpretation
    risk_flags = db.Column(db.Text)                          # JSON: [{"parameter":"Glucose","value":"180","normal":"70-110","flag":"HIGH"}]
    overall_status = db.Column(db.String(20), default='normal')  # normal | abnormal | critical

    date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='lab_reports')
    ordering_doctor = db.relationship('User', foreign_keys=[ordered_by], backref='ordered_labs')


class VitalSigns(db.Model):
    """Periodic vitals log — patient self-reported or doctor-recorded."""
    __tablename__ = 'vital_signs'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # None = self-reported
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    bp_systolic = db.Column(db.Integer)                      # mmHg
    bp_diastolic = db.Column(db.Integer)                     # mmHg
    pulse = db.Column(db.Integer)                            # bpm
    temperature = db.Column(db.Float)                        # Celsius
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    spo2 = db.Column(db.Integer)                             # Oxygen saturation %
    blood_glucose = db.Column(db.Float)                      # mg/dL
    notes = db.Column(db.Text)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='vital_signs')


class Message(db.Model):
    """Real-time chat messages between users."""
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    """System + user notifications."""
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='info')          # info | success | warning | alert
    link = db.Column(db.String(300))                         # Optional deep link
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
