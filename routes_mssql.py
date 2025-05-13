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


@app.route('/database-import', methods=['GET'])
@login_required
def database_import_page():
    """صفحة استيراد قاعدة بيانات - الواجهة الجديدة"""
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    from database_import import get_import_logs
    
    # الحصول على سجلات الاستيراد السابقة
    import_logs = get_import_logs()
    
    # استرجاع معلومات الاتصال المحفوظة (إن وجدت)
    server = os.environ.get('MSSQL_SERVER', 'localhost')
    database = os.environ.get('MSSQL_DATABASE', 'travelagency')
    username = os.environ.get('MSSQL_USERNAME', 'sa')
    password = os.environ.get('MSSQL_PASSWORD', '')
    
    return render_template('import_database.html', 
                          import_logs=import_logs,
                          server=server,
                          database=database,
                          username=username,
                          password=password)

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

@app.route('/upload-backup-file', methods=['POST'])
@login_required
def upload_backup_file():
    """
    استيراد البيانات من ملف النسخة الاحتياطية المرفوع
    """
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الوظيفة', 'danger')
        return redirect(url_for('database_import_page'))
    
    # التحقق من وجود ملف النسخة الاحتياطية في الطلب
    if 'backup_file' not in request.files:
        # محاولة استخدام الملف المرفق مسبقًا
        import os
        attached_bak_file = os.path.join('attached_assets', 'BackupDBTAMPA_01-08-2024 04-08-22 م.bak')
        
        if os.path.exists(attached_bak_file):
            from database_import import import_from_backup_file
            
            logging.info(f"استخدام ملف النسخة الاحتياطية المرفق: {attached_bak_file}")
            success, message = import_from_backup_file(attached_bak_file, is_path=True)
            
            if success:
                flash(f"تم استيراد البيانات بنجاح من الملف المرفق: {os.path.basename(attached_bak_file)}", 'success')
            else:
                flash(f"فشل استيراد البيانات من الملف المرفق: {message}", 'danger')
            
            return redirect(url_for('database_import_page'))
        else:
            flash('لم يتم اختيار ملف ولا يوجد ملف مرفق مسبقًا', 'danger')
            return redirect(url_for('database_import_page'))
    
    # التعامل مع الملف المرفوع
    backup_file = request.files['backup_file']
    
    if backup_file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('database_import_page'))
    
    # استيراد البيانات من الملف
    from database_import import import_from_backup_file
    
    success, message = import_from_backup_file(backup_file)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('database_import_page'))


@app.route('/import-from-database', methods=['POST'])
@login_required
def import_from_database():
    """
    استيراد البيانات مباشرة من قاعدة بيانات SQL Server
    """
    # التحقق من وجود صلاحيات المسؤول
    if not current_user.is_admin:
        flash('ليس لديك صلاحيات كافية للوصول إلى هذه الوظيفة', 'danger')
        return redirect(url_for('database_import_page'))
    
    # الحصول على بيانات النموذج
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    
    # استيراد البيانات من قاعدة البيانات
    from database_import import import_from_database
    
    success, message = import_from_database(server, database, username, password)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('database_import_page'))


@app.route('/import-mssql-data', methods=['POST'])
@login_required
def import_mssql_data():
    """استيراد البيانات من قاعدة بيانات SQL Server إلى النظام (الطريقة القديمة)"""
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