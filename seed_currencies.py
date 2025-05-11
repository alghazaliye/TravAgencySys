"""
سكريبت لإنشاء العملات الأساسية في قاعدة البيانات
"""
import logging
from app import app, db
from models import Currency

# قائمة العملات الأساسية
DEFAULT_CURRENCIES = [
    {
        'code': 'SAR',
        'name': 'ريال سعودي',
        'symbol': '﷼',
        'exchange_rate': 1.0,
        'is_default': True,
        'is_active': True
    },
    {
        'code': 'USD',
        'name': 'دولار أمريكي',
        'symbol': '$',
        'exchange_rate': 0.27,
        'is_default': False,
        'is_active': True
    },
    {
        'code': 'EUR',
        'name': 'يورو',
        'symbol': '€',
        'exchange_rate': 0.24,
        'is_default': False,
        'is_active': True
    },
    {
        'code': 'AED',
        'name': 'درهم إماراتي',
        'symbol': 'د.إ',
        'exchange_rate': 0.98,
        'is_default': False,
        'is_active': True
    },
    {
        'code': 'EGP',
        'name': 'جنيه مصري',
        'symbol': 'ج.م',
        'exchange_rate': 12.91,
        'is_default': False,
        'is_active': True
    }
]


def seed_currencies():
    """إضافة العملات الأساسية إلى قاعدة البيانات"""
    created_count = 0
    try:
        for currency_data in DEFAULT_CURRENCIES:
            # التحقق من وجود العملة
            existing = Currency.query.filter_by(code=currency_data['code']).first()
            if not existing:
                # إنشاء عملة جديدة
                currency = Currency(
                    code=currency_data['code'],
                    name=currency_data['name'],
                    symbol=currency_data['symbol'],
                    exchange_rate=currency_data['exchange_rate'],
                    is_default=currency_data['is_default'],
                    is_active=currency_data['is_active']
                )
                db.session.add(currency)
                created_count += 1
        
        if created_count > 0:
            # حفظ التغييرات
            db.session.commit()
            logging.info(f"تم إنشاء {created_count} عملة أساسية")
    except Exception as e:
        db.session.rollback()
        logging.error(f"حدث خطأ أثناء إنشاء العملات الأساسية: {str(e)}")
    
    return created_count


# للاختبار المباشر
if __name__ == "__main__":
    with app.app_context():
        seed_currencies()