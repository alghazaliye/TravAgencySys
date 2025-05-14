"""
سكريبت لإعادة تعيين قاعدة البيانات - يحذف جميع الجداول ويعيد إنشاء الهيكل
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

# تكوين نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# استيراد إعدادات الاتصال بقاعدة البيانات
from db_config import get_connection_string

# تجاوز سلوك DROP TABLE الافتراضي لـ PostgreSQL
@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

def reset_database():
    """إعادة تعيين قاعدة البيانات بالكامل - حذف كل الجداول وإعادة إنشائها"""
    from app import db, app
    
    # بدء سياق التطبيق
    with app.app_context():
        try:
            logger.info("بدء عملية حذف جميع الجداول...")
            
            # حذف كل الجداول
            db.drop_all()
            logger.info("تم حذف جميع الجداول بنجاح")
            
            # إعادة إنشاء الجداول
            db.create_all()
            logger.info("تم إعادة إنشاء هيكل قاعدة البيانات بنجاح")
            
            return True, "تم إعادة تعيين قاعدة البيانات بنجاح"
        except Exception as e:
            logger.error(f"حدث خطأ أثناء إعادة تعيين قاعدة البيانات: {str(e)}")
            return False, str(e)

if __name__ == "__main__":
    success, message = reset_database()
    if success:
        logger.info(message)
    else:
        logger.error(f"فشل إعادة تعيين قاعدة البيانات: {message}")