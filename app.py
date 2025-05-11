import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with Base class
db = SQLAlchemy(model_class=Base)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'  # Default login view route
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'  # تعزيز حماية الجلسة

# Create Flask application
def create_app():
    app = Flask(__name__)
    # Set app configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")  # Fallback for development
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https
    
    # إعدادات الجلسات لتحسين الأمان والاستقرار
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 ساعة بالثواني
    # تعطيل SECURE لتمكين الكوكيز من العمل مع HTTP في بيئة التطوير
    app.config["SESSION_COOKIE_SECURE"] = False if app.debug else True
    
    # Configure database
    db_url = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/travelagency")
    # تعديل سلسلة اتصال قاعدة البيانات إذا كانت تبدأ بـ postgres:// لتكون postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "sslmode": "require"  # استخدام SSL كما هو مطلوب من قاعدة البيانات
        }
    }
    
    # إضافة فلتر مخصص لتنسيق التاريخ
    @app.template_filter('date')
    def date_filter(value, format='%d/%m/%Y'):
        """فلتر لتنسيق التاريخ في قوالب Jinja"""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        return value.strftime(format)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from models import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Create database tables if they don't exist
        db.create_all()
    
    return app

# Create the application instance
app = create_app()

# تضمين إعدادات النظام في كل القوالب
from routes import load_system_settings

@app.context_processor
def inject_settings():
    """تضمين إعدادات النظام في سياق القالب"""
    # الحصول على الإعدادات من الدالة المسؤولة عن تحميلها
    settings = load_system_settings()
    
    # إعادة قاموس settings للتضمين في سياق جميع القوالب
    return dict(settings=settings)
