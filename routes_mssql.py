"""
مسارات خاصة باستيراد بيانات SQL Server
"""
import os
import tempfile
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/import-mssql', methods=['GET'])
@login_required
def import_mssql_page():
    """صفحة استيراد قاعدة بيانات SQL Server"""
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    return render_template('import-mssql.html')

@app.route('/test-mssql-connection', methods=['POST'])
@login_required
def test_mssql_connection():
    """اختبار الاتصال بقاعدة بيانات SQL Server"""
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'ليس لديك صلاحيات كافية'})
    
    # الحصول على معلومات الاتصال من النموذج
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    driver = request.form.get('driver')
    
    # تخزين معلومات الاتصال في متغيرات البيئة مؤقتًا
    os.environ['MSSQL_SERVER'] = server
    os.environ['MSSQL_DATABASE'] = database
    os.environ['MSSQL_USERNAME'] = username
    os.environ['MSSQL_PASSWORD'] = password
    os.environ['MSSQL_DRIVER'] = driver
    
    # اختبار الاتصال
    try:
        from mssql_connector import get_mssql_connection
        
        connection = get_mssql_connection()
        if connection:
            connection.close()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'فشل الاتصال بقاعدة البيانات'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload-mssql-backup', methods=['POST'])
@login_required
def upload_mssql_backup():
    """رفع وتهيئة قاعدة بيانات SQL Server من نسخة احتياطية"""
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'ليس لديك صلاحيات كافية'})
    
    # الحصول على معلومات الاتصال من النموذج
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    driver = request.form.get('driver')
    
    # تخزين معلومات الاتصال في متغيرات البيئة
    os.environ['MSSQL_SERVER'] = server
    os.environ['MSSQL_DATABASE'] = database
    os.environ['MSSQL_USERNAME'] = username
    os.environ['MSSQL_PASSWORD'] = password
    os.environ['MSSQL_DRIVER'] = driver
    
    # الحصول على ملف النسخة الاحتياطية
    if 'backup_file' not in request.files:
        return jsonify({'success': False, 'error': 'لم يتم تحديد ملف النسخة الاحتياطية'})
    
    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        return jsonify({'success': False, 'error': 'لم يتم تحديد ملف النسخة الاحتياطية'})
    
    # حفظ ملف النسخة الاحتياطية مؤقتًا
    try:
        # إنشاء ملف مؤقت لحفظ النسخة الاحتياطية
        temp_backup_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bak')
        backup_file.save(temp_backup_file.name)
        temp_backup_file.close()
        
        # استيراد النسخة الاحتياطية
        from mssql_connector import import_mssql_database
        
        if import_mssql_database(temp_backup_file.name):
            # حذف الملف المؤقت بعد الانتهاء
            os.unlink(temp_backup_file.name)
            return jsonify({'success': True})
        else:
            # حذف الملف المؤقت في حالة الفشل
            os.unlink(temp_backup_file.name)
            return jsonify({'success': False, 'error': 'فشل استيراد النسخة الاحتياطية'})
    
    except Exception as e:
        # حذف الملف المؤقت في حالة حدوث خطأ
        if 'temp_backup_file' in locals() and os.path.exists(temp_backup_file.name):
            os.unlink(temp_backup_file.name)
        
        return jsonify({'success': False, 'error': str(e)})

@app.route('/import-mssql-data', methods=['POST'])
@login_required
def import_mssql_data():
    """استيراد البيانات من قاعدة بيانات SQL Server إلى النظام"""
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'ليس لديك صلاحيات كافية'})
    
    # الحصول على معلومات الاتصال من النموذج
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    driver = request.form.get('driver')
    
    # تخزين معلومات الاتصال في متغيرات البيئة
    os.environ['MSSQL_SERVER'] = server
    os.environ['MSSQL_DATABASE'] = database
    os.environ['MSSQL_USERNAME'] = username
    os.environ['MSSQL_PASSWORD'] = password
    os.environ['MSSQL_DRIVER'] = driver
    
    # تحديد البيانات المطلوب استيرادها
    import_customers = request.form.get('import_customers') == 'true'
    import_accounts = request.form.get('import_accounts') == 'true'
    import_bank_accounts = request.form.get('import_bank_accounts') == 'true'
    import_transactions = request.form.get('import_transactions') == 'true'
    
    try:
        from import_mssql_data import import_customers as import_customers_func
        from import_mssql_data import import_accounts as import_accounts_func
        from import_mssql_data import import_bank_accounts as import_bank_accounts_func
        
        # إعداد قاموس لتخزين نتائج الاستيراد
        import_results = {}
        
        # استيراد بيانات العملاء
        if import_customers:
            customers_count = import_customers_func()
            import_results['customers_count'] = customers_count
        
        # استيراد بيانات الحسابات
        if import_accounts:
            accounts_count = import_accounts_func()
            import_results['accounts_count'] = accounts_count
        
        # استيراد بيانات الحسابات البنكية
        if import_bank_accounts:
            bank_accounts_count = import_bank_accounts_func()
            import_results['bank_accounts_count'] = bank_accounts_count
        
        # استيراد المعاملات المالية (لم يتم تنفيذها بعد)
        if import_transactions:
            # يمكن إضافة وظيفة لاستيراد المعاملات هنا
            import_results['transactions_count'] = 0
        
        return jsonify({'success': True, 'details': import_results})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})