"""
بذور البيانات المحاسبية الأساسية للنظام
سيتم استخدام هذا الملف لإنشاء بيانات أولية للنظام المحاسبي
"""

from datetime import datetime, date
from app import (
    db, AccountCategory, Account, Currency, TaxSettings,
    FinancialSettings, BankAccount, CashRegister, FinancialPeriod
)

def seed_accounting_data():
    """
    إنشاء البيانات الأساسية للنظام المحاسبي
    """
    print("بدء إنشاء البيانات المحاسبية الأساسية...")
    
    # إنشاء العملات
    print("إنشاء العملات...")
    currencies = {
        'sar': Currency(
            name="ريال سعودي",
            code="SAR",
            symbol="ر.س",
            exchange_rate=1.0,
            is_base_currency=True,
            is_active=True
        ),
        'usd': Currency(
            name="دولار أمريكي",
            code="USD",
            symbol="$",
            exchange_rate=0.27,  # 1 SAR = 0.27 USD
            is_base_currency=False,
            is_active=True
        ),
        'eur': Currency(
            name="يورو",
            code="EUR",
            symbol="€",
            exchange_rate=0.24,  # 1 SAR = 0.24 EUR
            is_base_currency=False,
            is_active=True
        )
    }
    
    for currency in currencies.values():
        existing = Currency.query.filter_by(code=currency.code).first()
        if not existing:
            db.session.add(currency)
    
    db.session.commit()
    print("تم إنشاء العملات بنجاح.")
    
    # إنشاء فئات الحسابات
    print("إنشاء فئات الحسابات...")
    account_categories = {
        'assets': AccountCategory(
            name="الأصول",
            code="1",
            description="الممتلكات والأموال التي تملكها المنشأة"
        ),
        'liabilities': AccountCategory(
            name="الخصوم والالتزامات",
            code="2",
            description="الالتزامات المالية المستحقة على المنشأة"
        ),
        'equity': AccountCategory(
            name="حقوق الملكية",
            code="3",
            description="حقوق أصحاب المنشأة"
        ),
        'revenue': AccountCategory(
            name="الإيرادات",
            code="4",
            description="المبالغ المكتسبة من أنشطة المنشأة"
        ),
        'expenses': AccountCategory(
            name="المصروفات",
            code="5",
            description="المبالغ المدفوعة لتشغيل المنشأة"
        )
    }
    
    for category in account_categories.values():
        existing = AccountCategory.query.filter_by(code=category.code).first()
        if not existing:
            db.session.add(category)
    
    db.session.commit()
    print("تم إنشاء فئات الحسابات بنجاح.")
    
    # الحصول على فئات الحسابات من قاعدة البيانات
    assets = AccountCategory.query.filter_by(code="1").first()
    liabilities = AccountCategory.query.filter_by(code="2").first()
    equity = AccountCategory.query.filter_by(code="3").first()
    revenue = AccountCategory.query.filter_by(code="4").first()
    expenses = AccountCategory.query.filter_by(code="5").first()
    
    # إنشاء الحسابات الرئيسية
    print("إنشاء الحسابات الرئيسية...")
    accounts = [
        # الأصول المتداولة
        Account(
            name="الصندوق الرئيسي", 
            account_number="101",
            category=assets,
            account_type="أصول متداولة",
            is_cash_account=True,
            description="الصندوق الرئيسي للمنشأة",
        ),
        Account(
            name="حساب البنك الرئيسي", 
            account_number="102",
            category=assets,
            account_type="أصول متداولة",
            is_bank_account=True,
            description="الحساب البنكي الرئيسي للمنشأة",
        ),
        Account(
            name="العملاء", 
            account_number="120",
            category=assets,
            account_type="أصول متداولة - ذمم مدينة",
            description="الذمم المدينة للعملاء",
        ),
        
        # الالتزامات المتداولة
        Account(
            name="الموردين", 
            account_number="201",
            category=liabilities,
            account_type="التزامات متداولة - ذمم دائنة",
            description="الذمم الدائنة للموردين",
        ),
        Account(
            name="ضريبة القيمة المضافة", 
            account_number="210",
            category=liabilities,
            account_type="التزامات متداولة - ضرائب",
            description="ضريبة القيمة المضافة المستحقة",
        ),
        
        # حقوق الملكية
        Account(
            name="رأس المال", 
            account_number="301",
            category=equity,
            account_type="حقوق ملكية",
            description="رأس مال المنشأة",
        ),
        Account(
            name="الأرباح المحتجزة", 
            account_number="302",
            category=equity,
            account_type="حقوق ملكية",
            description="الأرباح المحتجزة للمنشأة",
        ),
        
        # الإيرادات
        Account(
            name="إيرادات تذاكر الطيران", 
            account_number="401",
            category=revenue,
            account_type="إيرادات تشغيلية",
            description="إيرادات بيع تذاكر الطيران",
        ),
        Account(
            name="إيرادات تذاكر الحافلات", 
            account_number="402",
            category=revenue,
            account_type="إيرادات تشغيلية",
            description="إيرادات بيع تذاكر الحافلات",
        ),
        Account(
            name="إيرادات خدمات التأشيرات", 
            account_number="403",
            category=revenue,
            account_type="إيرادات تشغيلية",
            description="إيرادات خدمات التأشيرات",
        ),
        
        # المصروفات
        Account(
            name="تكلفة تذاكر الطيران", 
            account_number="501",
            category=expenses,
            account_type="مصروفات تشغيلية",
            description="تكلفة شراء تذاكر الطيران",
        ),
        Account(
            name="تكلفة تذاكر الحافلات", 
            account_number="502",
            category=expenses,
            account_type="مصروفات تشغيلية",
            description="تكلفة شراء تذاكر الحافلات",
        ),
        Account(
            name="رواتب الموظفين", 
            account_number="510",
            category=expenses,
            account_type="مصروفات إدارية",
            description="رواتب ومكافآت الموظفين",
        ),
        Account(
            name="إيجارات", 
            account_number="520",
            category=expenses,
            account_type="مصروفات إدارية",
            description="إيجارات المكاتب والفروع",
        ),
        Account(
            name="مصروفات عمومية وإدارية", 
            account_number="590",
            category=expenses,
            account_type="مصروفات إدارية",
            description="مصروفات عمومية وإدارية متنوعة",
        ),
    ]
    
    for account in accounts:
        existing = Account.query.filter_by(account_number=account.account_number).first()
        if not existing:
            db.session.add(account)
    
    db.session.commit()
    print("تم إنشاء الحسابات الرئيسية بنجاح.")
    
    # إنشاء الحسابات البنكية
    print("إنشاء الحسابات البنكية...")
    bank_account_db = Account.query.filter_by(account_number="102").first()
    cash_account_db = Account.query.filter_by(account_number="101").first()
    sar_currency = Currency.query.filter_by(code="SAR").first()
    
    bank_accounts = [
        BankAccount(
            account=bank_account_db,
            bank_name="البنك الأهلي السعودي",
            account_number="1234567890",
            iban="SA123456789012345678",
            swift_code="NCBKSAJE",
            branch_name="الفرع الرئيسي",
            branch_code="001",
            currency=sar_currency,
            opening_balance=100000.0,
            current_balance=100000.0,
            notes="الحساب البنكي الرئيسي للمنشأة"
        )
    ]
    
    for bank_account in bank_accounts:
        existing = BankAccount.query.filter_by(account_number=bank_account.account_number).first()
        if not existing:
            db.session.add(bank_account)
    
    # إنشاء صناديق النقد
    print("إنشاء صناديق النقد...")
    cash_registers = [
        CashRegister(
            account=cash_account_db,
            name="الصندوق الرئيسي",
            location="المكتب الرئيسي",
            currency=sar_currency,
            opening_balance=5000.0,
            current_balance=5000.0,
            notes="الصندوق الرئيسي للمنشأة"
        )
    ]
    
    for cash_register in cash_registers:
        existing = CashRegister.query.filter_by(name=cash_register.name).first()
        if not existing:
            db.session.add(cash_register)
    
    # إنشاء الإعدادات الضريبية
    print("إنشاء الإعدادات الضريبية...")
    tax_settings = [
        TaxSettings(
            name="ضريبة القيمة المضافة 15%",
            rate=0.15,
            is_default=True,
            is_active=True
        ),
        TaxSettings(
            name="معفى من الضريبة",
            rate=0.0,
            is_default=False,
            is_active=True
        )
    ]
    
    for tax_setting in tax_settings:
        existing = TaxSettings.query.filter_by(name=tax_setting.name).first()
        if not existing:
            db.session.add(tax_setting)
    
    db.session.commit()
    
    # إنشاء الفترة المالية الحالية
    print("إنشاء الفترة المالية...")
    current_year = datetime.now().year
    financial_period = FinancialPeriod(
        name=f"السنة المالية {current_year}",
        start_date=date(current_year, 1, 1),
        end_date=date(current_year, 12, 31),
        is_closed=False,
        notes="الفترة المالية الحالية"
    )
    
    existing_period = FinancialPeriod.query.filter_by(name=financial_period.name).first()
    if not existing_period:
        db.session.add(financial_period)
    
    # إنشاء الإعدادات المالية
    print("إنشاء الإعدادات المالية...")
    sar_currency = Currency.query.filter_by(code="SAR").first()
    default_tax = TaxSettings.query.filter_by(is_default=True).first()
    cash_account = Account.query.filter_by(account_number="101").first()
    bank_account = Account.query.filter_by(account_number="102").first()
    
    financial_settings = FinancialSettings(
        company_name="وكالة السفر والسياحة",
        fiscal_year_start=date(current_year, 1, 1),
        base_currency=sar_currency,
        default_tax=default_tax,
        enable_cost_centers=False,
        enable_budgets=False,
        default_cash_account=cash_account,
        default_bank_account=bank_account
    )
    
    existing_settings = FinancialSettings.query.first()
    if not existing_settings:
        db.session.add(financial_settings)
    
    db.session.commit()
    
    print("تم إنشاء البيانات المحاسبية الأساسية بنجاح.")

if __name__ == "__main__":
    seed_accounting_data()