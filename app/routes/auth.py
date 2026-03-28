from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import User, Notification
from app import db, bcrypt

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
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        print("Registration attempt received")
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            specialization = request.form.get('specialization')
            age = request.form.get('age')
            gender = request.form.get('gender')
            
            print(f"User data: {name}, {email}, {role}")
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(
                name=name, 
                email=email, 
                password=hashed_password, 
                role=role, 
                specialization=specialization,
                age=age,
                gender=gender
            )
            db.session.add(user)
            db.session.commit()
            print("User created successfully")
            
            # Auto-create first notification
            welcome_notif = Notification(
                user_id=user.id,
                title="Welcome to MedMining AI",
                message="Your advanced medical platform is ready. Explore AI tools and connect with specialists."
            )
            db.session.add(welcome_notif)
            db.session.commit()
            
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Registration error: {str(e)}")
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
    return render_template('register.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
