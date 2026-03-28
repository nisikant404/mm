from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'medmining_ultra_secret_2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///medmining.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    CORS(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Template context processors and filters for notifications
    @app.context_processor
    def utility_processor():
        from app.models.models import Notification
        def get_unread_count(user_id):
            return Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        def get_recent_notifications(user_id):
            return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()
        
        # Register as filters too
        app.jinja_env.filters['get_unread_count'] = get_unread_count
        app.jinja_env.filters['get_recent_notifications'] = get_recent_notifications
        
        return dict(get_unread_count=get_unread_count, get_recent_notifications=get_recent_notifications)

    from app.routes.auth import auth
    from app.routes.patient import patient
    from app.routes.doctor import doctor
    from app.routes.ai import ai_bp
    from app.routes.consultation import consultation

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(patient, url_prefix='/patient')
    app.register_blueprint(doctor, url_prefix='/doctor')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(consultation, url_prefix='/consultation')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('landing.html')

    # SocketIO Event Handlers
    @socketio.on('join_room')
    def handle_join_room(data):
        from flask_socketio import join_room
        room = data.get('room')
        join_room(room)
        print(f"User joined room: {room}")

    @socketio.on('send_message')
    def handle_send_message(data):
        from flask_socketio import emit
        from app.models.models import Message, Notification
        from app import db
        
        room = data.get('room')
        sender_id = data.get('sender')
        content = data.get('content')
        
        # Parse receiver from room name (sender-receiver format)
        parts = room.split('-')
        receiver_id = parts[1] if parts[0] == str(sender_id) else parts[0]
        
        # Save to DB
        new_msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        db.session.add(new_msg)
        
        # Also create a notification for the receiver if they are not in the room
        # For simplicity, we create it always; in a real app, you'd check if they are online
        notification = Notification(
            user_id=receiver_id,
            title="New Message",
            message=f"You have a new message from {sender_id}." # Ideally use sender name
        )
        db.session.add(notification)
        
        db.session.commit()
        
        emit('receive_message', data, room=room)

    @socketio.on('call_user')
    def handle_call_user(data):
        from flask_socketio import emit
        user_to_call = data.get('userToCall')
        emit('call_incoming', {
            'signal': data.get('signalData'),
            'from': data.get('from')
        }, room=user_to_call)

    @socketio.on('answer_call')
    def handle_answer_call(data):
        from flask_socketio import emit
        to = data.get('to')
        emit('call_accepted', data.get('signal'), room=to)

    with app.app_context():
        db.create_all()

    return app
