"""
وحدة تكوين اتصال قاعدة البيانات
تدعم اختيار نوع قاعدة البيانات (MySQL أو PostgreSQL) من خلال متغير البيئة DB_TYPE
"""
import os

# تحديد نوع قاعدة البيانات (mysql أو postgresql)
DB_TYPE = os.environ.get('DB_TYPE', 'postgresql')

# إعدادات اتصال قاعدة البيانات المشتركة
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_DATABASE = os.environ.get('DB_DATABASE', 'travelagency')

# إعدادات خاصة بـ MySQL
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')

# إعدادات خاصة بـ PostgreSQL
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')

# بناء سلسلة اتصال قاعدة البيانات للـ SQLAlchemy
def get_connection_string():
    """إنشاء سلسلة اتصال قاعدة البيانات بناءً على النوع المحدد"""
    if DB_TYPE.lower() == 'mysql':
        # استخدام MySQL
        return f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{MYSQL_PORT}/{DB_DATABASE}"
    else:
        # استخدام PostgreSQL (افتراضي)
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            # تعديل سلسلة اتصال قاعدة البيانات إذا كانت تبدأ بـ postgres:// لتكون postgresql://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            return db_url
        else:
            # بناء سلسلة اتصال PostgreSQL من المتغيرات
            return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{DB_DATABASE}"