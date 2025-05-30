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
# Set login view route and messages
login_manager.login_view = 'login'  # type: ignore # Default login view route
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
    
    # Configure database to use the appropriate database type
    from db_config import get_connection_string
    app.config["SQLALCHEMY_DATABASE_URI"] = get_connection_string()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "max_overflow": 15,
        "pool_size": 5
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
@app.context_processor
def inject_settings():
    """تضمين إعدادات النظام في سياق القالب"""
    try:
        # الحصول على الإعدادات من الدالة المسؤولة عن تحميلها
        # نستخدم استيراد محلي لتجنب الاستيراد الدائري
        from routes import load_system_settings
        settings = load_system_settings()
        return dict(settings=settings)
    except Exception as e:
        import logging
        logging.error(f"خطأ في تحميل الإعدادات للقالب: {str(e)}")
        # في حالة حدوث خطأ، قم بإرجاع قاموس فارغ لتجنب توقف التطبيق
        return dict(settings={})
