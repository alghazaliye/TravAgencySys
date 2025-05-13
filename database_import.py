"""
وحدة استيراد قاعدة البيانات من SQL Server إلى PostgreSQL
"""
import os
import logging
import tempfile
from datetime import datetime
from flask_login import current_user
from werkzeug.utils import secure_filename
from mssql_connector import get_mssql_connection, execute_query, import_mssql_database
from import_mssql_data import import_all_data
from app import db
from models import DatabaseImportLog

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# الدليل المؤقت لتخزين ملفات النسخ الاحتياطية
TEMP_UPLOAD_FOLDER = tempfile.gettempdir()

def allowed_file(filename):
    """
    التحقق من أن الملف له امتداد .bak
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'bak'

def set_mssql_env_vars(server, database, username, password):
    """
    تعيين متغيرات البيئة للاتصال بـ SQL Server
    """
    os.environ['MSSQL_SERVER'] = server
    os.environ['MSSQL_DATABASE'] = database
    os.environ['MSSQL_USERNAME'] = username
    os.environ['MSSQL_PASSWORD'] = password

def import_from_backup_file(file, is_path=False):
    """
    استيراد البيانات من ملف نسخة احتياطية
    
    :param file: ملف النسخة الاحتياطية أو مسار الملف إذا كان is_path=True
    :param is_path: إذا كان True، فإن file هو مسار للملف وليس كائن ملف
    :return: (نجاح/فشل، رسالة)
    """
    # التعامل مع حالة المسار المباشر
    if is_path:
        file_path = file
        filename = os.path.basename(file_path)
        
        if not os.path.exists(file_path) or not allowed_file(filename):
            return False, f"الملف غير موجود أو غير صالح: {filename}"
        
        logger.info(f"استخدام ملف النسخة الاحتياطية من المسار: {file_path}")
        
        try:
            # استيراد قاعدة البيانات من الملف
            server = os.environ.get('MSSQL_SERVER', 'localhost')
            logger.info(f"جاري الاتصال بالخادم: {server}")
            
            # محاولة إعداد متغيرات البيئة إذا لم تكن معدة
            if not os.environ.get('MSSQL_SERVER'):
                os.environ['MSSQL_SERVER'] = 'localhost'
                os.environ['MSSQL_DATABASE'] = 'travelagency'
                os.environ['MSSQL_USERNAME'] = 'sa'
                os.environ['MSSQL_PASSWORD'] = 'P@ssw0rd'
            
            success = import_mssql_database(file_path)
            logger.info(f"نتيجة استيراد قاعدة البيانات: {success}")
            
            if success:
                # استيراد البيانات من SQL Server إلى PostgreSQL
                data_import_success = import_all_data()
                
                # إضافة سجل الاستيراد إلى قاعدة البيانات
                import_log = DatabaseImportLog(
                    date=datetime.now(),
                    import_type="ملف نسخة احتياطية (مسار)",
                    filename=filename,
                    success=data_import_success,
                    imported_by=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(import_log)
                db.session.commit()
                
                return True, "تم استيراد البيانات بنجاح"
            else:
                # إضافة سجل الاستيراد الفاشل
                import_log = DatabaseImportLog(
                    date=datetime.now(),
                    import_type="ملف نسخة احتياطية (مسار)",
                    filename=filename,
                    success=False,
                    error_message="فشل في استيراد البيانات من ملف النسخة الاحتياطية",
                    imported_by=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(import_log)
                db.session.commit()
                
                return False, "فشل في استيراد البيانات من ملف النسخة الاحتياطية"
                
        except Exception as e:
            logger.error(f"خطأ في استيراد البيانات من المسار: {str(e)}")
            
            # إضافة سجل الخطأ
            import_log = DatabaseImportLog(
                date=datetime.now(),
                import_type="ملف نسخة احتياطية (مسار)",
                filename=filename,
                success=False,
                error_message=str(e),
                imported_by=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(import_log)
            db.session.commit()
            
            return False, f"حدث خطأ أثناء استيراد البيانات: {str(e)}"
    
    # التعامل مع حالة كائن الملف المرفوع
    elif file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(TEMP_UPLOAD_FOLDER, filename)
        
        try:
            # حفظ الملف مؤقتًا
            file.save(temp_path)
            logger.info(f"تم حفظ الملف {filename} مؤقتًا في {temp_path}")
            
            # استيراد قاعدة البيانات من الملف
            success = import_mssql_database(temp_path)
            
            if success:
                # استيراد البيانات من SQL Server إلى PostgreSQL
                data_import_success = import_all_data()
                
                # إضافة سجل الاستيراد إلى قاعدة البيانات
                import_log = DatabaseImportLog(
                    date=datetime.now(),
                    import_type="ملف نسخة احتياطية",
                    filename=filename,
                    success=data_import_success,
                    imported_by=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(import_log)
                db.session.commit()
                
                return True, "تم استيراد البيانات بنجاح"
            else:
                # إضافة سجل الاستيراد الفاشل
                import_log = DatabaseImportLog(
                    date=datetime.now(),
                    import_type="ملف نسخة احتياطية",
                    filename=filename,
                    success=False,
                    error_message="فشل في استيراد البيانات من ملف النسخة الاحتياطية",
                    imported_by=current_user.id if current_user.is_authenticated else None
                )
                db.session.add(import_log)
                db.session.commit()
                
                return False, "فشل في استيراد البيانات من ملف النسخة الاحتياطية"
                
        except Exception as e:
            logger.error(f"خطأ في استيراد البيانات: {str(e)}")
            
            # إضافة سجل الخطأ
            import_log = DatabaseImportLog(
                date=datetime.now(),
                import_type="ملف نسخة احتياطية",
                filename=filename,
                success=False,
                error_message=str(e),
                imported_by=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(import_log)
            db.session.commit()
            
            return False, f"حدث خطأ أثناء استيراد البيانات: {str(e)}"
        finally:
            # حذف الملف المؤقت
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"تم حذف الملف المؤقت {temp_path}")
    
    return False, "الملف غير صالح أو لم يتم تحديده"

def import_from_database(server, database, username, password):
    """
    استيراد البيانات مباشرة من قاعدة بيانات SQL Server
    """
    try:
        # تعيين متغيرات البيئة
        set_mssql_env_vars(server, database, username, password)
        
        # اختبار الاتصال
        connection = get_mssql_connection()
        if not connection:
            logger.error("فشل الاتصال بقاعدة بيانات SQL Server")
            
            # إضافة سجل فشل الاتصال
            import_log = DatabaseImportLog(
                date=datetime.now(),
                import_type="اتصال مباشر",
                filename=f"{server}/{database}",
                success=False,
                error_message="فشل الاتصال بقاعدة بيانات SQL Server",
                imported_by=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(import_log)
            db.session.commit()
            
            return False, "فشل الاتصال بقاعدة بيانات SQL Server"
        
        connection.close()
        
        # استيراد البيانات
        success = import_all_data()
        
        # إضافة سجل الاستيراد
        import_log = DatabaseImportLog(
            date=datetime.now(),
            import_type="اتصال مباشر",
            filename=f"{server}/{database}",
            success=success,
            error_message=None if success else "فشل في استيراد البيانات من الاتصال المباشر",
            imported_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(import_log)
        db.session.commit()
        
        if success:
            return True, "تم استيراد البيانات بنجاح"
        else:
            return False, "فشل في استيراد البيانات"
    
    except Exception as e:
        logger.error(f"خطأ في استيراد البيانات: {str(e)}")
        
        # إضافة سجل الخطأ
        import_log = DatabaseImportLog(
            date=datetime.now(),
            import_type="اتصال مباشر",
            filename=f"{server}/{database}",
            success=False,
            error_message=str(e),
            imported_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(import_log)
        db.session.commit()
        
        return False, f"حدث خطأ أثناء استيراد البيانات: {str(e)}"
    
def get_import_logs():
    """
    الحصول على سجلات الاستيراد السابقة من قاعدة البيانات
    """
    return DatabaseImportLog.query.order_by(DatabaseImportLog.date.desc()).all()