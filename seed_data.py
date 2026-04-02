"""
Seed MedMining database with realistic test data.
Run: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
import json
from app import create_app, db, bcrypt
from app.models.models import (User, MedicalRecord, Appointment, Prescription,
                                LabReport, VitalSigns, Notification, Message)

app = create_app()

with app.app_context():
    print("🗑  Dropping all tables...")
    db.drop_all()
    print("🏗  Creating all tables...")
    db.create_all()

    pw = bcrypt.generate_password_hash("password123").decode('utf-8')

    # ─────────────── DOCTORS ───────────────
    doctors_data = [
        {
            "name": "Dr. Arjun Mehta", "email": "arjun.mehta@medmining.ai",
            "specialization": "Cardiologist", "years_experience": 14,
            "medical_license_no": "MCI-40912", "hospital_affiliation": "Apollo Hospital, Mumbai",
            "consultation_fee": 800.0, "languages_spoken": "English, Hindi, Gujarati",
            "dob": date(1978, 3, 15), "gender": "Male", "phone": "+91 98100 11001",
            "bio": "Senior interventional cardiologist with expertise in complex coronary interventions and heart failure management. Published 35+ peer-reviewed papers.",
            "rating": 4.9,
        },
        {
            "name": "Dr. Priya Nair", "email": "priya.nair@medmining.ai",
            "specialization": "Neurologist", "years_experience": 10,
            "medical_license_no": "MCI-55231", "hospital_affiliation": "AIIMS, New Delhi",
            "consultation_fee": 700.0, "languages_spoken": "English, Hindi, Malayalam",
            "dob": date(1982, 7, 22), "gender": "Female", "phone": "+91 99001 22002",
            "bio": "Specialist in movement disorders, epilepsy, and neuro-oncology. Fellowship trained at Johns Hopkins.",
            "rating": 4.8,
        },
        {
            "name": "Dr. Ravi Kumar", "email": "ravi.kumar@medmining.ai",
            "specialization": "General Physician", "years_experience": 8,
            "medical_license_no": "MCI-61842", "hospital_affiliation": "Fortis Healthcare, Bangalore",
            "consultation_fee": 400.0, "languages_spoken": "English, Hindi, Kannada, Tamil",
            "dob": date(1985, 11, 5), "gender": "Male", "phone": "+91 97200 33003",
            "bio": "Experienced general physician specializing in preventive care, diabetes management, and lifestyle diseases.",
            "rating": 4.6,
        },
        {
            "name": "Dr. Sneha Reddy", "email": "sneha.reddy@medmining.ai",
            "specialization": "Dermatologist", "years_experience": 6,
            "medical_license_no": "MCI-72341", "hospital_affiliation": "Skin & Hair Clinic, Hyderabad",
            "consultation_fee": 600.0, "languages_spoken": "English, Telugu, Hindi",
            "dob": date(1988, 4, 12), "gender": "Female", "phone": "+91 96300 44004",
            "bio": "Cosmetic and clinical dermatologist with special interest in acne, psoriasis, and aesthetic procedures.",
            "rating": 4.7,
        },
        {
            "name": "Dr. Vikram Singh", "email": "vikram.singh@medmining.ai",
            "specialization": "Orthopedics", "years_experience": 18,
            "medical_license_no": "MCI-28923", "hospital_affiliation": "Max Hospital, Delhi",
            "consultation_fee": 900.0, "languages_spoken": "English, Hindi, Punjabi",
            "dob": date(1974, 9, 28), "gender": "Male", "phone": "+91 95400 55005",
            "bio": "Chief orthopedic surgeon specializing in joint replacement, sports injuries, and spinal surgery. 2000+ successful surgeries.",
            "rating": 4.9,
        },
    ]

    doctors = []
    for d in doctors_data:
        doc = User(
            role='doctor', password=pw,
            name=d['name'], email=d['email'], phone=d.get('phone'),
            dob=d.get('dob'), gender=d.get('gender'),
            specialization=d['specialization'], years_experience=d['years_experience'],
            medical_license_no=d['medical_license_no'],
            hospital_affiliation=d['hospital_affiliation'],
            consultation_fee=d['consultation_fee'],
            languages_spoken=d['languages_spoken'],
            bio=d['bio'], rating=d['rating'], is_available=True,
        )
        db.session.add(doc)
        doctors.append(doc)
    db.session.flush()
    print(f"✅ Created {len(doctors)} doctors")

    # ─────────────── PATIENTS ───────────────
    patients_data = [
        {
            "name": "Rahul Sharma", "email": "rahul.sharma@patient.com",
            "dob": date(1995, 6, 10), "gender": "Male", "phone": "+91 90001 10001",
            "blood_group": "O+", "address": "45 MG Road, Pune 411001",
            "allergies": "Penicillin, Sulfa drugs",
            "chronic_conditions": "Type 2 Diabetes, Hypertension",
            "emergency_contact_name": "Pooja Sharma (Wife)",
            "emergency_contact_phone": "+91 90001 10002",
        },
        {
            "name": "Ananya Patel", "email": "ananya.patel@patient.com",
            "dob": date(2000, 2, 25), "gender": "Female", "phone": "+91 88002 20002",
            "blood_group": "B+", "address": "12 Satellite Road, Ahmedabad 380015",
            "allergies": "None known",
            "chronic_conditions": "Asthma (mild)",
            "emergency_contact_name": "Nikhil Patel (Father)",
            "emergency_contact_phone": "+91 88002 20003",
        },
    ]

    patients = []
    for p in patients_data:
        pat = User(
            role='patient', password=pw,
            name=p['name'], email=p['email'], phone=p.get('phone'),
            dob=p.get('dob'), gender=p.get('gender'),
            blood_group=p.get('blood_group'), address=p.get('address'),
            allergies=p.get('allergies'), chronic_conditions=p.get('chronic_conditions'),
            emergency_contact_name=p.get('emergency_contact_name'),
            emergency_contact_phone=p.get('emergency_contact_phone'),
        )
        db.session.add(pat)
        patients.append(pat)
    db.session.flush()
    print(f"✅ Created {len(patients)} patients")

    patient1, patient2 = patients[0], patients[1]
    dr_cardiologist, dr_neurologist, dr_gp = doctors[0], doctors[1], doctors[2]

    # ─────────────── APPOINTMENTS ───────────────
    apt1 = Appointment(
        patient_id=patient1.id, doctor_id=dr_cardiologist.id,
        date=datetime.utcnow() - timedelta(days=10),
        proposed_date=datetime.utcnow() - timedelta(days=10),
        status='completed', type='in_person',
        chief_complaint="Chest pain and shortness of breath on exertion",
        reason="AI Triage: Patient reports chest tightness, radiating to left arm. Risk: HIGH. History: Diabetic for 5 years, smoker.",
        duration_minutes=30, fee_charged=800.0, payment_status='paid',
        doctor_notes="Ordered ECG and stress test. Started on Aspirin 75mg. Follow-up in 2 weeks.",
    )
    apt2 = Appointment(
        patient_id=patient1.id, doctor_id=dr_gp.id,
        date=datetime.utcnow() - timedelta(days=3),
        proposed_date=datetime.utcnow() + timedelta(days=2),
        status='confirmed', type='video',
        chief_complaint="Follow-up: blood sugar control",
        reason="AI Triage: Patient concerned about blood sugar spike. Risk: MEDIUM.",
        duration_minutes=15, fee_charged=400.0, payment_status='pending',
    )
    apt3 = Appointment(
        patient_id=patient2.id, doctor_id=dr_neurologist.id,
        date=datetime.utcnow() - timedelta(days=1),
        status='pending', type='in_person',
        chief_complaint="Severe headaches, blurred vision for 2 weeks",
        reason="AI Triage: Persistent headache, photophobia, no fever. Risk: HIGH. Family history of migraines.",
        duration_minutes=30, fee_charged=700.0, payment_status='pending',
    )
    db.session.add_all([apt1, apt2, apt3])
    db.session.flush()
    print("✅ Created appointments")

    # ─────────────── MEDICAL RECORDS ───────────────
    rec1 = MedicalRecord(
        patient_id=patient1.id, doctor_id=dr_cardiologist.id,
        record_type='doctor_note', source='doctor',
        chief_complaint="Chest pain on exertion",
        symptoms="Angina pectoris, dyspnoea on exertion, mild ankle oedema",
        diagnosis="Stable Angina, possible CAD — awaiting stress test results",
        icd_code="I20.9",
        risk_level='high', risk_score=78,
        notes="Patient to avoid strenuous activity. Start Nitrates PRN. Urgent cardiology review.",
        follow_up_date=date.today() + timedelta(days=14),
        vitals=json.dumps({"bp": "148/92", "pulse": 88, "temp": 37.1, "spo2": 97}),
        date=datetime.utcnow() - timedelta(days=10),
    )
    rec2 = MedicalRecord(
        patient_id=patient1.id, doctor_id=None,
        record_type='ai_triage', source='ai',
        chief_complaint="Blood sugar high, feeling fatigued",
        symptoms="Polyuria, polydipsia, fatigue, blurred vision",
        diagnosis="Suspected hyperglycaemic episode — HbA1c likely elevated",
        icd_code="E11.9",
        risk_level='medium', risk_score=55,
        ai_suggestions="Recommend HbA1c test, fasting glucose. Metformin dose review.",
        date=datetime.utcnow() - timedelta(days=30),
    )
    rec3 = MedicalRecord(
        patient_id=patient2.id, doctor_id=None,
        record_type='ai_triage', source='ai',
        chief_complaint="Persistent headaches and photophobia",
        symptoms="Throbbing bilateral headache, nausea, light sensitivity",
        diagnosis="Likely migraine — tension headache differential",
        icd_code="G43.909",
        risk_level='medium', risk_score=52,
        ai_suggestions="Neurology consultation recommended. Avoid triggers. Sumatriptan PRN.",
        date=datetime.utcnow() - timedelta(days=5),
    )
    db.session.add_all([rec1, rec2, rec3])
    db.session.flush()
    print("✅ Created medical records")

    # ─────────────── PRESCRIPTIONS ───────────────
    rx1 = Prescription(
        patient_id=patient1.id, doctor_id=dr_cardiologist.id, appointment_id=apt1.id,
        diagnosis_at_rx="Stable Angina, Hypertension",
        medicines=json.dumps([
            {"name": "Aspirin", "dosage": "75mg", "frequency": "Once daily", "duration": "90 days"},
            {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once at night", "duration": "90 days"},
            {"name": "Isosorbide Mononitrate", "dosage": "10mg", "frequency": "Twice daily", "duration": "30 days"},
        ]),
        notes="Take Aspirin with food. Avoid alcohol. Return immediately if chest pain persists.",
        pharmacy_notes="Patient is penicillin allergic — avoid amoxicillin if antibiotic needed.",
        refills_allowed=2,
        valid_until=date.today() + timedelta(days=90),
        is_active=True,
        date=datetime.utcnow() - timedelta(days=10),
    )
    db.session.add(rx1)
    db.session.flush()
    print("✅ Created prescriptions")

    # ─────────────── LAB REPORTS ───────────────
    lab1 = LabReport(
        patient_id=patient1.id, ordered_by=dr_cardiologist.id, appointment_id=apt1.id,
        report_type='blood_test', lab_name='Apollo Diagnostics',
        findings="HbA1c: 8.2% (HIGH - target <7%). LDL Cholesterol: 142 mg/dL (HIGH). Fasting Glucose: 178 mg/dL (HIGH). Creatinine: 1.1 mg/dL (NORMAL).",
        risk_flags=json.dumps([
            {"parameter": "HbA1c", "value": "8.2%", "normal": "<7%", "flag": "HIGH"},
            {"parameter": "LDL Cholesterol", "value": "142 mg/dL", "normal": "<100 mg/dL", "flag": "HIGH"},
            {"parameter": "Fasting Glucose", "value": "178 mg/dL", "normal": "70-110 mg/dL", "flag": "HIGH"},
        ]),
        overall_status='abnormal',
        date=datetime.utcnow() - timedelta(days=9),
    )
    db.session.add(lab1)
    db.session.flush()
    print("✅ Created lab reports")

    # ─────────────── VITAL SIGNS ───────────────
    vitals_data = [
        {"patient_id": patient1.id, "recorded_by": dr_cardiologist.id,
         "bp_systolic": 148, "bp_diastolic": 92, "pulse": 88,
         "temperature": 37.1, "weight_kg": 84.5, "height_cm": 172,
         "spo2": 97, "blood_glucose": 178.0,
         "recorded_at": datetime.utcnow() - timedelta(days=10)},
        {"patient_id": patient1.id, "recorded_by": None,
         "bp_systolic": 138, "bp_diastolic": 86, "pulse": 82,
         "weight_kg": 84.0, "spo2": 98, "blood_glucose": 142.0,
         "recorded_at": datetime.utcnow() - timedelta(days=5)},
        {"patient_id": patient2.id, "recorded_by": None,
         "bp_systolic": 118, "bp_diastolic": 76, "pulse": 72,
         "temperature": 36.8, "weight_kg": 58.0, "height_cm": 163,
         "spo2": 99, "blood_glucose": 92.0,
         "recorded_at": datetime.utcnow() - timedelta(days=2)},
    ]
    for v in vitals_data:
        vs = VitalSigns(**v)
        db.session.add(vs)
    db.session.flush()
    print("✅ Created vital signs")

    # ─────────────── NOTIFICATIONS ───────────────
    notifs = [
        Notification(user_id=patient1.id, title="Welcome to MedMining AI", type='success',
                     message="Your health platform is ready. Explore AI tools and book specialists."),
        Notification(user_id=patient1.id, title="Lab Results Available",
                     type='alert', message="Your blood test results from Apollo Diagnostics are ready. Please review."),
        Notification(user_id=patient1.id, title="Appointment Confirmed",
                     type='success', message="Dr. Ravi Kumar confirmed your video consultation for tomorrow."),
        Notification(user_id=patient2.id, title="Welcome to MedMining AI", type='success',
                     message="Your health platform is ready. Start by checking your symptoms with our AI."),
        Notification(user_id=dr_cardiologist.id, title="New Patient Ticket",
                     type='info', message="Rahul Sharma has booked a cardiac consultation. Review the AI triage."),
        Notification(user_id=dr_neurologist.id, title="New Patient Ticket",
                     type='info', message="Ananya Patel has booked a neurology consultation with high-priority triage."),
    ]
    for n in notifs:
        db.session.add(n)

    db.session.commit()
    print("\n" + "="*50)
    print("✅ DATABASE SEEDED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 Test Accounts:")
    print("\n  DOCTORS:")
    for d in doctors_data:
        print(f"    Email: {d['email']}")
        print(f"    Name:  {d['name']} ({d['specialization']})")
        print(f"    Pass:  password123\n")
    print("  PATIENTS:")
    for p in patients_data:
        print(f"    Email: {p['email']}")
        print(f"    Name:  {p['name']}")
        print(f"    Pass:  password123\n")
