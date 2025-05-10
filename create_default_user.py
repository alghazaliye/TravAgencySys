import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db
from models import User

def create_admin_user(username, password, email):
    """إنشاء مستخدم مسؤول إذا لم يكن موجوداً"""
    with app.app_context():
        # التحقق من وجود المستخدم
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"المستخدم {username} موجود بالفعل")
            return
        
        # إنشاء المستخدم الجديد
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name="مسؤول النظام",
            is_admin=True,
            active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        print(f"تم إنشاء المستخدم {username} بنجاح")

if __name__ == "__main__":
    # إذا لم يتم تمرير معلومات المستخدم، استخدم القيم الافتراضية
    username = "admin"
    password = "admin123"  # يجب تغيير كلمة المرور في بيئة الإنتاج
    email = "admin@travelagency.com"
    
    # إذا تم تمرير معلومات في سطر الأوامر
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 3:
        email = sys.argv[3]
    
    create_admin_user(username, password, email)