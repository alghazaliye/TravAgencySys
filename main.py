from app import app  # noqa: F401
import routes  # Import all routes
import os
import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)

# إعداد مفتاح الجلسة إذا لم يكن موجودًا - استخدام مفتاح أكثر قوة
if not os.environ.get("SESSION_SECRET"):
    # استخدام مفتاح طويل 32 بايت للتشفير القوي
    import secrets
    os.environ["SESSION_SECRET"] = secrets.token_hex(32)

# إنشاء الإعدادات الافتراضية للنظام
with app.app_context():
    try:
        created_count = routes.create_default_settings()
        if created_count > 0:
            logging.info(f"تم إنشاء {created_count} إعداد افتراضي للنظام")
    except Exception as e:
        logging.error(f"خطأ في إنشاء الإعدادات الافتراضية: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
