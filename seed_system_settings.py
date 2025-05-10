"""
سكريبت لإنشاء الإعدادات الافتراضية للنظام في قاعدة البيانات
"""
import logging
from app import app, db
from models import SystemSettings

# قاموس يحتوي على إعدادات النظام الافتراضية
DEFAULT_SETTINGS = {
    # معلومات النظام الأساسية
    'system_name': {
        'value': 'نظام إدارة وكالة السفر والسياحة',
        'type': 'text',
        'description': 'اسم النظام الذي سيظهر في العنوان وجميع أنحاء التطبيق'
    },
    'system_slogan': {
        'value': 'حلول متكاملة لوكالات السفر والسياحة',
        'type': 'text',
        'description': 'شعار أو وصف قصير للنظام'
    },
    'company_name': {
        'value': 'وكالة السفر للسياحة والخدمات',
        'type': 'text',
        'description': 'اسم الشركة أو المؤسسة'
    },
    'company_address': {
        'value': 'الرياض - شارع الملك فهد',
        'type': 'text',
        'description': 'عنوان المقر الرئيسي للشركة'
    },
    'company_phone': {
        'value': '+966 11 1234567',
        'type': 'text',
        'description': 'رقم الهاتف الرئيسي للتواصل'
    },
    'company_email': {
        'value': 'info@travelagency.com',
        'type': 'text',
        'description': 'البريد الإلكتروني الرسمي للشركة'
    },
    
    # إعدادات المظهر والتخصيص
    'dashboard_title': {
        'value': 'لوحة التحكم',
        'type': 'text',
        'description': 'العنوان الذي سيظهر في لوحة التحكم الرئيسية'
    },
    'primary_color': {
        'value': '#007bff',
        'type': 'text',
        'description': 'اللون الرئيسي للنظام'
    },
    'secondary_color': {
        'value': '#6c757d',
        'type': 'text',
        'description': 'اللون الثانوي للنظام'
    },
    'theme_color': {
        'value': 'primary',
        'type': 'text',
        'description': 'اللون الرئيسي للموقع (bootstrap theme)'
    },
    'rtl_mode': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تمكين وضع RTL (من اليمين إلى اليسار)'
    },
    'enable_dark_mode': {
        'value': 'false',
        'type': 'boolean',
        'description': 'تمكين الوضع الداكن افتراضياً'
    },
    'dark_mode': {
        'value': 'auto',
        'type': 'text',
        'description': 'وضع العرض (ليلي/نهاري)'
    },
    'sidebar_collapsed': {
        'value': 'false',
        'type': 'boolean',
        'description': 'هل الشريط الجانبي مطوي افتراضياً'
    },
    
    # الشعارات والرموز
    'use_custom_logo': {
        'value': 'false',
        'type': 'boolean',
        'description': 'استخدام شعار مخصص بدلاً من أيقونة'
    },
    'logo_icon': {
        'value': 'fas fa-plane',
        'type': 'text',
        'description': 'أيقونة الشعار (تظهر عندما لا يتم استخدام شعار مخصص)'
    },
    'custom_logo_url': {
        'value': '',
        'type': 'text',
        'description': 'رابط الشعار المخصص'
    },
    'logo_url': {
        'value': '',
        'type': 'text',
        'description': 'رابط شعار الشركة (يفضل استخدام صورة بحجم 200×60 بكسل)'
    },
    'favicon_url': {
        'value': '',
        'type': 'text',
        'description': 'رابط أيقونة الموقع'
    },
    
    # الإعدادات المالية
    'default_currency': {
        'value': 'SAR',
        'type': 'text',
        'description': 'العملة الافتراضية للمعاملات المالية'
    },
    'default_language': {
        'value': 'ar',
        'type': 'text',
        'description': 'اللغة الافتراضية للنظام'
    },
    'tax_percent': {
        'value': '15',
        'type': 'text',
        'description': 'نسبة الضريبة المضافة على الخدمات'
    },
    'visa_fee': {
        'value': '300',
        'type': 'text',
        'description': 'رسوم التأشيرة الافتراضية'
    },
    'umrah_fee': {
        'value': '500',
        'type': 'text',
        'description': 'رسوم العمرة الافتراضية'
    },
    
    # نصوص التذييل والمعلومات الإضافية
    'system_footer': {
        'value': 'جميع الحقوق محفوظة © 2025 وكالة السفر للسياحة والخدمات',
        'type': 'text',
        'description': 'نص التذييل الذي سيظهر في أسفل جميع الصفحات'
    },
    'receipt_note': {
        'value': 'شكراً لتعاملكم معنا. لا يعتبر هذا الإيصال ساري المفعول إلا بعد تحصيل كامل المبلغ.',
        'type': 'text',
        'description': 'ملاحظات تظهر في جميع الإيصالات'
    },
    
    # إعدادات SEO والتوصيف
    'site_description': {
        'value': 'وكالة سفر متكاملة توفر حلول وخدمات السفر والسياحة والحج والعمرة',
        'type': 'text',
        'description': 'وصف موقع الويب (مفيد لمحركات البحث)'
    },
    'site_keywords': {
        'value': 'سفر,سياحة,حج,عمرة,تذاكر طيران,تأشيرات,فنادق',
        'type': 'text',
        'description': 'الكلمات المفتاحية للموقع (مفيدة لمحركات البحث)'
    },
    
    # روابط التواصل الاجتماعي
    'social_media': {
        'value': 'https://twitter.com/example,https://facebook.com/example,https://instagram.com/example',
        'type': 'text',
        'description': 'روابط لمنصات التواصل الاجتماعي (مفصولة بفاصلة)'
    },
    
    # إعدادات تنسيق التاريخ والوقت
    'date_format': {
        'value': 'DD/MM/YYYY',
        'type': 'text',
        'description': 'تنسيق عرض التاريخ في جميع أنحاء النظام'
    },
    'time_format': {
        'value': 'HH:mm',
        'type': 'text',
        'description': 'تنسيق عرض الوقت في جميع أنحاء النظام'
    },
    'date_separator': {
        'value': '/',
        'type': 'text',
        'description': 'الفاصل المستخدم بين أجزاء التاريخ'
    },
    'use_hijri_dates': {
        'value': 'no',
        'type': 'text',
        'description': 'استخدام التقويم الهجري في النظام'
    },
    'first_day_of_week': {
        'value': '6',
        'type': 'text',
        'description': 'تحديد أول يوم في الأسبوع (6=السبت)'
    },
    
    # إعدادات الإشعارات والتنبيهات
    'enable_notifications': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تفعيل الإشعارات في النظام'
    },
    'notification_position': {
        'value': 'top-right',
        'type': 'text',
        'description': 'موضع ظهور الإشعارات في الشاشة'
    },
    'notification_duration': {
        'value': '5',
        'type': 'text',
        'description': 'مدة ظهور الإشعارات (بالثواني)'
    },
    'sound_notifications': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تفعيل التنبيهات الصوتية مع الإشعارات'
    },
    'notify_new_bookings': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تنبيه عند إنشاء حجز جديد'
    },
    'notify_payment_received': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تنبيه عند استلام مدفوعات'
    },
    'notify_booking_cancellation': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تنبيه عند إلغاء حجز'
    },
    
    # إعدادات التواصل والرسائل
    'sms_service_enabled': {
        'value': 'false',
        'type': 'boolean',
        'description': 'تفعيل خدمة إرسال الرسائل القصيرة'
    },
    'email_notifications_enabled': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تفعيل إرسال إشعارات البريد الإلكتروني'
    },
    'email_signature': {
        'value': 'مع تحيات،\nفريق وكالة السفر للسياحة والخدمات\nهاتف: +966 11 1234567\nالبريد الإلكتروني: info@travelagency.com',
        'type': 'text',
        'description': 'توقيع البريد الإلكتروني للشركة'
    },
    
    # إعدادات الطباعة والتقارير
    'paper_size': {
        'value': 'A4',
        'type': 'text',
        'description': 'حجم الورق الافتراضي للطباعة'
    },
    'print_layout': {
        'value': 'portrait',
        'type': 'text',
        'description': 'اتجاه الطباعة الافتراضي (عمودي أو أفقي)'
    },
    'show_logo_in_reports': {
        'value': 'true',
        'type': 'boolean',
        'description': 'عرض شعار النظام في التقارير المطبوعة'
    },
    'print_footer': {
        'value': 'وكالة السفر للسياحة والخدمات - هاتف: +966 11 1234567',
        'type': 'text',
        'description': 'نص يظهر في تذييل الصفحات المطبوعة'
    },
    'receipt_notes': {
        'value': 'شكراً لتعاملكم معنا. لا يعتبر هذا الإيصال ساري المفعول إلا بعد تحصيل كامل المبلغ.',
        'type': 'text',
        'description': 'ملاحظات تظهر في نهاية إيصالات الحجز والدفع'
    },
    
    # إعدادات متقدمة
    'privacy_policy': {
        'value': 'تلتزم وكالة السفر بالحفاظ على خصوصية بيانات العملاء وعدم مشاركتها مع أي جهة خارجية.',
        'type': 'text',
        'description': 'نص سياسة الخصوصية'
    },
    'terms_conditions': {
        'value': 'يخضع استخدام هذا النظام للشروط والأحكام المنصوص عليها في اتفاقية الاستخدام.',
        'type': 'text',
        'description': 'نص الشروط والأحكام'
    },
    'google_analytics': {
        'value': '',
        'type': 'text',
        'description': 'كود تتبع Google Analytics (إذا كان متاحًا)'
    },
}

def seed_system_settings():
    """إضافة الإعدادات الافتراضية للنظام إلى قاعدة البيانات"""
    with app.app_context():
        for key, data in DEFAULT_SETTINGS.items():
            # تحقق مما إذا كان الإعداد موجودًا بالفعل
            setting = SystemSettings.query.filter_by(setting_key=key).first()
            if not setting:
                # إنشاء إعداد جديد إذا لم يكن موجودًا
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=data['value'],
                    setting_type=data['type'],
                    description=data['description']
                )
                db.session.add(setting)
                logging.info(f"تمت إضافة الإعداد: {key}")
            else:
                logging.info(f"الإعداد موجود بالفعل: {key}")
        
        try:
            db.session.commit()
            logging.info("تم إنشاء جميع إعدادات النظام الافتراضية بنجاح")
        except Exception as e:
            db.session.rollback()
            logging.error(f"حدث خطأ أثناء إنشاء إعدادات النظام: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_system_settings()