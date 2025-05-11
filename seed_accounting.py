"""
بذور البيانات المحاسبية الأساسية للنظام
سيتم استخدام هذا الملف لإنشاء بيانات أولية للنظام المحاسبي
"""
import logging
from app import app, db
from models import Account, AccountCategory, Currency
from datetime import datetime

# قاموس بفئات الحسابات الأساسية
DEFAULT_ACCOUNT_CATEGORIES = [
    # فئات الأصول
    {
        'code': 'A1000',
        'name': 'الأصول المتداولة',
        'category_type': 'asset',
        'parent_id': None
    },
    {
        'code': 'A2000',
        'name': 'الأصول الثابتة',
        'category_type': 'asset',
        'parent_id': None
    },
    
    # فئات الخصوم
    {
        'code': 'L1000',
        'name': 'المطلوبات المتداولة',
        'category_type': 'liability',
        'parent_id': None
    },
    {
        'code': 'L2000',
        'name': 'المطلوبات طويلة الأجل',
        'category_type': 'liability',
        'parent_id': None
    },
    
    # فئات حقوق الملكية
    {
        'code': 'E1000',
        'name': 'حقوق الملكية',
        'category_type': 'equity',
        'parent_id': None
    },
    
    # فئات الإيرادات
    {
        'code': 'R1000',
        'name': 'الإيرادات',
        'category_type': 'revenue',
        'parent_id': None
    },
    
    # فئات المصروفات
    {
        'code': 'X1000',
        'name': 'المصروفات التشغيلية',
        'category_type': 'expense',
        'parent_id': None
    },
    {
        'code': 'X2000',
        'name': 'المصروفات الإدارية',
        'category_type': 'expense',
        'parent_id': None
    }
]

# قاموس بالحسابات الأساسية
DEFAULT_ACCOUNTS = [
    # حسابات الأصول المتداولة
    {
        'account_number': '1010',
        'name': 'الصندوق الرئيسي',
        'account_type': 'asset',
        'is_cash_account': True,
        'category_code': 'A1000',
        'parent_id': None
    },
    {
        'account_number': '1020',
        'name': 'البنك الأهلي',
        'account_type': 'asset',
        'is_bank_account': True,
        'category_code': 'A1000',
        'parent_id': None
    },
    {
        'account_number': '1030',
        'name': 'ذمم العملاء',
        'account_type': 'asset',
        'category_code': 'A1000',
        'parent_id': None
    },
    
    # حسابات الأصول الثابتة
    {
        'account_number': '1210',
        'name': 'أثاث وتجهيزات',
        'account_type': 'asset',
        'category_code': 'A2000',
        'parent_id': None
    },
    {
        'account_number': '1220',
        'name': 'أجهزة وحواسيب',
        'account_type': 'asset',
        'category_code': 'A2000',
        'parent_id': None
    },
    
    # حسابات المطلوبات
    {
        'account_number': '2010',
        'name': 'ذمم الموردين',
        'account_type': 'liability',
        'category_code': 'L1000',
        'parent_id': None
    },
    {
        'account_number': '2020',
        'name': 'الضرائب المستحقة',
        'account_type': 'liability',
        'category_code': 'L1000',
        'parent_id': None
    },
    
    # حقوق الملكية
    {
        'account_number': '3010',
        'name': 'رأس المال',
        'account_type': 'equity',
        'category_code': 'E1000',
        'parent_id': None
    },
    {
        'account_number': '3020',
        'name': 'الأرباح المحتجزة',
        'account_type': 'equity',
        'category_code': 'E1000',
        'parent_id': None
    },
    
    # الإيرادات
    {
        'account_number': '4010',
        'name': 'إيرادات تذاكر الحافلات',
        'account_type': 'revenue',
        'category_code': 'R1000',
        'parent_id': None
    },
    {
        'account_number': '4020',
        'name': 'إيرادات تذاكر الطيران',
        'account_type': 'revenue',
        'category_code': 'R1000',
        'parent_id': None
    },
    {
        'account_number': '4030',
        'name': 'إيرادات خدمات التأشيرات',
        'account_type': 'revenue',
        'category_code': 'R1000',
        'parent_id': None
    },
    {
        'account_number': '4040',
        'name': 'إيرادات خدمات العمرة',
        'account_type': 'revenue',
        'category_code': 'R1000',
        'parent_id': None
    },
    
    # المصروفات
    {
        'account_number': '5010',
        'name': 'رواتب وأجور',
        'account_type': 'expense',
        'category_code': 'X1000',
        'parent_id': None
    },
    {
        'account_number': '5020',
        'name': 'إيجارات',
        'account_type': 'expense',
        'category_code': 'X1000',
        'parent_id': None
    },
    {
        'account_number': '5030',
        'name': 'مرافق وخدمات',
        'account_type': 'expense',
        'category_code': 'X1000',
        'parent_id': None
    },
    {
        'account_number': '5110',
        'name': 'دعاية وإعلان',
        'account_type': 'expense',
        'category_code': 'X2000',
        'parent_id': None
    },
    {
        'account_number': '5120',
        'name': 'قرطاسية ومطبوعات',
        'account_type': 'expense',
        'category_code': 'X2000',
        'parent_id': None
    },
    {
        'account_number': '5130',
        'name': 'مصروفات بنكية',
        'account_type': 'expense',
        'category_code': 'X2000',
        'parent_id': None
    }
]


def seed_account_categories():
    """
    إنشاء فئات الحسابات الأساسية
    """
    categories_created = 0
    categories_map = {}  # قاموس لتخزين الفئات المنشأة حسب الكود
    
    try:
        for category_data in DEFAULT_ACCOUNT_CATEGORIES:
            # التحقق من وجود الفئة
            existing = AccountCategory.query.filter_by(code=category_data['code']).first()
            if existing:
                categories_map[category_data['code']] = existing
                continue
                
            # إنشاء فئة جديدة
            category = AccountCategory()
            category.code = category_data['code']
            category.name = category_data['name']
            # category_type غير موجود في الجدول
            # category.category_type = category_data['category_type']
            # parent_id يبدو غير موجود أيضًا
            # category.parent_id = category_data['parent_id']
            category.is_active = True
            category.description = f"تم إنشاؤها تلقائيًا في {datetime.now().strftime('%Y-%m-%d')}"
            
            db.session.add(category)
            categories_map[category_data['code']] = category
            categories_created += 1
        
        # حفظ التغييرات
        if categories_created > 0:
            db.session.commit()
            logging.info(f"تم إنشاء {categories_created} فئة حسابات")
        
        return categories_map
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"حدث خطأ أثناء إنشاء فئات الحسابات: {str(e)}")
        return {}


def seed_accounts(categories_map):
    """
    إنشاء الحسابات الأساسية
    """
    accounts_created = 0
    
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
        
        # إنشاء الحسابات
        for account_data in DEFAULT_ACCOUNTS:
            # التحقق من وجود الحساب
            existing = Account.query.filter_by(account_number=account_data['account_number']).first()
            if existing:
                continue
            
            # تحديد فئة الحساب
            category_id = None
            if 'category_code' in account_data and account_data['category_code'] in categories_map:
                category_id = categories_map[account_data['category_code']].id
            
            # إنشاء حساب جديد
            account = Account()
            account.account_number = account_data['account_number']
            account.name = account_data['name']
            account.account_type = account_data['account_type']
            account.category_id = category_id
            account.parent_id = account_data.get('parent_id')
            account.is_bank_account = account_data.get('is_bank_account', False)
            account.is_cash_account = account_data.get('is_cash_account', False)
            account.balance = 0.0
            account.is_active = True
            account.description = f"تم إنشاؤه تلقائيًا في {datetime.now().strftime('%Y-%m-%d')}"
            
            db.session.add(account)
            accounts_created += 1
        
        # حفظ التغييرات
        if accounts_created > 0:
            db.session.commit()
            logging.info(f"تم إنشاء {accounts_created} حساب محاسبي")
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"حدث خطأ أثناء إنشاء الحسابات المحاسبية: {str(e)}")
    
    return accounts_created


def seed_accounting_data():
    """
    إنشاء البيانات الأساسية للنظام المحاسبي
    """
    try:
        # إنشاء فئات الحسابات
        categories_map = seed_account_categories()
        
        # إنشاء الحسابات
        accounts_count = seed_accounts(categories_map)
        
        return accounts_count
    
    except Exception as e:
        logging.error(f"حدث خطأ عام أثناء إنشاء البيانات المحاسبية: {str(e)}")
        return 0


# للاختبار المباشر
if __name__ == "__main__":
    with app.app_context():
        seed_accounting_data()