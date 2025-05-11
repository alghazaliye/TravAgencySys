"""
وحدة الاتصال بقاعدة بيانات SQL Server
"""
import os
import pyodbc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mssql_connection_string():
    """
    الحصول على سلسلة الاتصال بقاعدة بيانات SQL Server
    """
    server = os.environ.get('MSSQL_SERVER', 'localhost')
    database = os.environ.get('MSSQL_DATABASE', 'travelagency')
    username = os.environ.get('MSSQL_USERNAME', 'sa')
    password = os.environ.get('MSSQL_PASSWORD', '')
    driver = os.environ.get('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # إنشاء سلسلة الاتصال
    connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return connection_string

def get_mssql_connection():
    """
    الحصول على اتصال بقاعدة بيانات SQL Server
    """
    try:
        connection_string = get_mssql_connection_string()
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        logger.error(f"خطأ في الاتصال بقاعدة بيانات SQL Server: {str(e)}")
        return None

def execute_query(query, params=None, fetch_all=True):
    """
    تنفيذ استعلام على قاعدة بيانات SQL Server
    
    :param query: نص الاستعلام SQL
    :param params: معلمات الاستعلام (اختياري)
    :param fetch_all: استرجاع جميع النتائج (True) أو النتيجة الأولى فقط (False)
    :return: نتائج الاستعلام أو None في حالة الخطأ
    """
    connection = get_mssql_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith(('SELECT', 'EXEC')):
            if fetch_all:
                results = cursor.fetchall()
                # تحويل النتائج إلى قائمة من القواميس
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in results]
            else:
                result = cursor.fetchone()
                if result:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, result))
                return None
        else:
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        logger.error(f"خطأ في تنفيذ الاستعلام: {str(e)}")
        connection.rollback()
        return None
    finally:
        connection.close()

def execute_script(script):
    """
    تنفيذ نص SQL كامل على قاعدة بيانات SQL Server
    
    :param script: نص SQL كامل
    :return: True في حالة النجاح، False في حالة الفشل
    """
    connection = get_mssql_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute(script)
        connection.commit()
        return True
    except Exception as e:
        logger.error(f"خطأ في تنفيذ النص البرمجي SQL: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()

def import_mssql_database(backup_file=None):
    """
    استيراد قاعدة بيانات SQL Server من ملف نسخة احتياطية
    
    :param backup_file: مسار ملف النسخة الاحتياطية
    :return: True في حالة النجاح، False في حالة الفشل
    """
    # هذه الوظيفة تحتاج إلى صلاحيات مدير قاعدة البيانات
    # ويفضل استخدام أدوات SQL Server الرسمية مثل SSMS لاستيراد النسخ الاحتياطية
    
    if not backup_file:
        logger.error("لم يتم تحديد ملف النسخة الاحتياطية")
        return False
    
    connection = get_mssql_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        # تحديد اسم قاعدة البيانات من المتغيرات البيئية
        database = os.environ.get('MSSQL_DATABASE', 'travelagency')
        
        # استيراد النسخة الاحتياطية
        # ملاحظة: هذا الأمر قد يحتاج إلى تعديل حسب إصدار SQL Server ومكان ملف النسخة الاحتياطية
        restore_query = f"""
        USE master;
        RESTORE DATABASE {database} 
        FROM DISK = '{backup_file}' 
        WITH REPLACE, RECOVERY;
        """
        
        # تنفيذ استعلام الاستيراد
        cursor.execute(restore_query)
        connection.commit()
        logger.info(f"تم استيراد قاعدة البيانات {database} بنجاح")
        return True
    except Exception as e:
        logger.error(f"خطأ في استيراد قاعدة البيانات: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()

def sync_data_from_mssql_to_postgres():
    """
    مزامنة البيانات من SQL Server إلى PostgreSQL
    
    هذه الوظيفة تقوم بنقل البيانات من SQL Server إلى PostgreSQL
    ويمكن استخدامها للمزامنة الدورية أو لمرة واحدة
    """
    # تنفيذ عملية المزامنة هنا
    # ...
    pass

# للاختبار
if __name__ == "__main__":
    # اختبار الاتصال
    connection = get_mssql_connection()
    if connection:
        print("تم الاتصال بقاعدة بيانات SQL Server بنجاح")
        connection.close()
    else:
        print("فشل الاتصال بقاعدة بيانات SQL Server")