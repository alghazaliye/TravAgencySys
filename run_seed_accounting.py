"""
نص برمجي لتشغيل بذور البيانات المحاسبية
"""
from app import app, db
from seed_accounting import seed_accounting_data
import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)

# تشغيل بذور البيانات المحاسبية
with app.app_context():
    try:
        # إنشاء البيانات المحاسبية
        accounts_created = seed_accounting_data()
        if accounts_created > 0:
            logging.info(f"تم إنشاء {accounts_created} حساب محاسبي بنجاح")
        else:
            logging.info("لم يتم إنشاء أي حسابات جديدة، قد تكون الحسابات موجودة بالفعل")
    except Exception as e:
        logging.error(f"حدث خطأ أثناء إنشاء البيانات المحاسبية: {str(e)}")