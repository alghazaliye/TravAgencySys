"""
بذور البيانات المحاسبية الأساسية للنظام
سيتم استخدام هذا الملف لإنشاء بيانات أولية للنظام المحاسبي
"""
import logging
from app import app, db
from models import Account, Currency
from datetime import datetime

# قاموس بالحسابات الأساسية مصنفة حسب نوع الحساب
DEFAULT_ACCOUNTS = {
    'asset': [
        # الأصول المتداولة
        {
            'code': '1000',
            'name': 'الأصول المتداولة',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '1010',
            'name': 'النقد والبنوك',
            'level': 2,
            'parent_code': '1000'
        },
        {
            'code': '1011',
            'name': 'الصندوق النقدي',
            'level': 3,
            'parent_code': '1010'
        },
        {
            'code': '1012',
            'name': 'البنوك',
            'level': 3,
            'parent_code': '1010'
        },
        {
            'code': '1020',
            'name': 'الذمم المدينة',
            'level': 2,
            'parent_code': '1000'
        },
        {
            'code': '1021',
            'name': 'ذمم العملاء',
            'level': 3,
            'parent_code': '1020'
        },
        
        # الأصول الثابتة
        {
            'code': '1200',
            'name': 'الأصول الثابتة',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '1210',
            'name': 'الأثاث والتجهيزات',
            'level': 2,
            'parent_code': '1200'
        },
        {
            'code': '1220',
            'name': 'أجهزة وحواسيب',
            'level': 2,
            'parent_code': '1200'
        },
        {
            'code': '1230',
            'name': 'سيارات',
            'level': 2,
            'parent_code': '1200'
        }
    ],
    'liability': [
        # المطلوبات المتداولة
        {
            'code': '2000',
            'name': 'المطلوبات المتداولة',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '2010',
            'name': 'الذمم الدائنة',
            'level': 2,
            'parent_code': '2000'
        },
        {
            'code': '2011',
            'name': 'ذمم الموردين',
            'level': 3,
            'parent_code': '2010'
        },
        {
            'code': '2020',
            'name': 'الضرائب المستحقة',
            'level': 2,
            'parent_code': '2000'
        },
        
        # المطلوبات طويلة الأجل
        {
            'code': '2200',
            'name': 'المطلوبات طويلة الأجل',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '2210',
            'name': 'قروض طويلة الأجل',
            'level': 2,
            'parent_code': '2200'
        }
    ],
    'equity': [
        # حقوق الملكية
        {
            'code': '3000',
            'name': 'حقوق الملكية',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '3010',
            'name': 'رأس المال',
            'level': 2,
            'parent_code': '3000'
        },
        {
            'code': '3020',
            'name': 'الأرباح المحتجزة',
            'level': 2,
            'parent_code': '3000'
        }
    ],
    'revenue': [
        # الإيرادات
        {
            'code': '4000',
            'name': 'الإيرادات',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '4010',
            'name': 'إيرادات تذاكر الحافلات',
            'level': 2,
            'parent_code': '4000'
        },
        {
            'code': '4020',
            'name': 'إيرادات تذاكر الطيران',
            'level': 2,
            'parent_code': '4000'
        },
        {
            'code': '4030',
            'name': 'إيرادات خدمات التأشيرات',
            'level': 2,
            'parent_code': '4000'
        },
        {
            'code': '4040',
            'name': 'إيرادات خدمات العمرة',
            'level': 2,
            'parent_code': '4000'
        }
    ],
    'expense': [
        # المصروفات
        {
            'code': '5000',
            'name': 'المصروفات',
            'level': 1,
            'parent_id': None
        },
        {
            'code': '5010',
            'name': 'مصروفات تشغيلية',
            'level': 2,
            'parent_code': '5000'
        },
        {
            'code': '5011',
            'name': 'رواتب وأجور',
            'level': 3,
            'parent_code': '5010'
        },
        {
            'code': '5012',
            'name': 'إيجارات',
            'level': 3,
            'parent_code': '5010'
        },
        {
            'code': '5013',
            'name': 'مرافق وخدمات',
            'level': 3,
            'parent_code': '5010'
        },
        {
            'code': '5020',
            'name': 'مصروفات تسويقية',
            'level': 2,
            'parent_code': '5000'
        },
        {
            'code': '5021',
            'name': 'دعاية وإعلان',
            'level': 3,
            'parent_code': '5020'
        },
        {
            'code': '5030',
            'name': 'مصروفات إدارية',
            'level': 2,
            'parent_code': '5000'
        },
        {
            'code': '5031',
            'name': 'قرطاسية ومطبوعات',
            'level': 3,
            'parent_code': '5030'
        },
        {
            'code': '5032',
            'name': 'مصروفات بنكية',
            'level': 3,
            'parent_code': '5030'
        }
    ]
}


def seed_accounting_data():
    """
    إنشاء البيانات الأساسية للنظام المحاسبي
    """
    accounts_created = 0
    accounts_map = {}  # قاموس لتخزين الحسابات المنشأة حسب الكود
    
    try:
        # البحث عن العملة الافتراضية
        default_currency = Currency.query.filter_by(is_default=True).first()
        if not default_currency:
            default_currency = Currency.query.filter_by(code='SAR').first()
        
        if not default_currency:
            logging.warning("لم يتم العثور على العملة الافتراضية. سيتم استخدام العملة الأولى في قاعدة البيانات.")
            default_currency = Currency.query.first()
            
        if not default_currency:
            logging.error("لا توجد عملات في قاعدة البيانات. يرجى إنشاء العملات أولا.")
            return 0
        
        # إنشاء حسابات لكل نوع
        for account_type, accounts in DEFAULT_ACCOUNTS.items():
            for account_data in accounts:
                # التحقق من وجود الحساب
                existing = Account.query.filter_by(code=account_data['code']).first()
                if existing:
                    accounts_map[account_data['code']] = existing
                    continue
                
                # تحديد الحساب الأب
                parent_id = None
                if 'parent_code' in account_data and account_data['parent_code'] in accounts_map:
                    parent_id = accounts_map[account_data['parent_code']].id
                elif 'parent_id' in account_data and account_data['parent_id'] is not None:
                    parent_id = account_data['parent_id']
                
                # إنشاء حساب جديد
                account = Account(
                    code=account_data['code'],
                    name=account_data['name'],
                    account_type=account_type,
                    parent_id=parent_id,
                    level=account_data['level'],
                    is_active=True,
                    notes=f"تم إنشاؤه تلقائيًا في {datetime.now().strftime('%Y-%m-%d')}"
                )
                
                db.session.add(account)
                accounts_map[account_data['code']] = account
                accounts_created += 1
        
        # حفظ التغييرات
        if accounts_created > 0:
            db.session.commit()
            logging.info(f"تم إنشاء {accounts_created} حساب محاسبي")
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"حدث خطأ أثناء إنشاء الحسابات المحاسبية: {str(e)}")
    
    return accounts_created


# للاختبار المباشر
if __name__ == "__main__":
    with app.app_context():
        seed_accounting_data()