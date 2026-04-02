from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import User, Notification
from app import db, bcrypt
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            role = request.form.get('role', 'patient')
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            phone = request.form.get('phone', '').strip()
            gender = request.form.get('gender')
            
            # Parse DOB
            dob_str = request.form.get('dob')
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

            # Check for duplicate email
            if User.query.filter_by(email=email).first():
                flash('An account with this email already exists.', 'danger')
                return render_template('register.html')

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(
                name=name,
                email=email,
                password=hashed_password,
                role=role,
                phone=phone,
                gender=gender,
                dob=dob,
            )

            if role == 'patient':
                user.blood_group = request.form.get('blood_group')
                user.address = request.form.get('address', '').strip()
                user.emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
                user.emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
                user.allergies = request.form.get('allergies', '').strip()
                user.chronic_conditions = request.form.get('chronic_conditions', '').strip()

            elif role == 'doctor':
                user.specialization = request.form.get('specialization', '').strip()
                user.years_experience = int(request.form.get('years_experience') or 0)
                user.medical_license_no = request.form.get('medical_license_no', '').strip()
                user.hospital_affiliation = request.form.get('hospital_affiliation', '').strip()
                user.consultation_fee = float(request.form.get('consultation_fee') or 0)
                user.bio = request.form.get('bio', '').strip()
                user.languages_spoken = request.form.get('languages_spoken', '').strip()

            db.session.add(user)
            db.session.flush()  # Get user.id before commit

            welcome_notif = Notification(
                user_id=user.id,
                title="Welcome to MedMining AI",
                message="Your advanced medical platform is ready. Explore AI tools and connect with specialists.",
                type='success'
            )
            db.session.add(welcome_notif)
            db.session.commit()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template('register.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
