"""
وحدة إدارة قاعدة البيانات - تتضمن مسارات لإدارة قاعدة البيانات
"""
import os
import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import app, db

# تكوين نظام التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/database/reset', methods=['GET'])
@login_required
def reset_database_view():
    """عرض صفحة إعادة تعيين قاعدة البيانات"""
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    return render_template('reset_database.html')

@app.route('/database/reset', methods=['POST'])
@login_required
def reset_database_action():
    """تنفيذ عملية إعادة تعيين قاعدة البيانات"""
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    # التحقق من تأكيد المستخدم
    confirm = request.form.get('confirm')
    if confirm != 'RESET':
        flash('يرجى كتابة "RESET" لتأكيد إعادة تعيين قاعدة البيانات', 'warning')
        return redirect(url_for('reset_database_view'))
    
    try:
        # حذف جميع الجداول وإعادة إنشائها
        db.reflect()  # استكشاف هيكل قاعدة البيانات
        db.drop_all()  # حذف جميع الجداول
        db.create_all()  # إعادة إنشاء الهيكل
        
        # تهيئة البيانات الأساسية
        from create_default_user import create_admin_user
        create_admin_user('admin', 'admin123', 'admin@example.com')
        
        from create_countries_cities import create_countries_and_cities
        create_countries_and_cities()
        
        from seed_currencies import seed_currencies
        seed_currencies()
        
        from seed_accounting import seed_accounting_data
        seed_accounting_data()
        
        flash('تم إعادة تعيين قاعدة البيانات بنجاح وتهيئة البيانات الأساسية', 'success')
        logger.info("تم إعادة تعيين قاعدة البيانات بنجاح")
        
    except Exception as e:
        flash(f'حدث خطأ أثناء إعادة تعيين قاعدة البيانات: {str(e)}', 'danger')
        logger.error(f"فشل إعادة تعيين قاعدة البيانات: {str(e)}")
    
    return redirect(url_for('index'))