"""
استيراد البيانات من قاعدة بيانات SQL Server إلى النظام
"""
import os
import logging
from app import app, db
from models import Account, AccountCategory, Currency, Customer, BankAccount, CashRegister
from mssql_connector import execute_query, get_mssql_connection
from datetime import datetime

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_customers():
    """
    استيراد بيانات العملاء من SQL Server
    """
    logger.info("بدء استيراد بيانات العملاء...")
    
    # استعلام لجلب العملاء من SQL Server
    # قم بتعديل هذا الاستعلام حسب بنية جدول العملاء في SQL Server
    query = """
    SELECT 
        CustomerID,
        CustomerName,
        Phone,
        Email,
        Address,
        City,
        Country,
        IDType,
        IDNumber,
        Notes
    FROM 
        Customers
    """
    
    customers_data = execute_query(query)
    if not customers_data:
        logger.error("فشل في جلب بيانات العملاء من SQL Server")
        return 0
    
    customers_added = 0
    
    try:
        for customer_data in customers_data:
            # التحقق من وجود العميل عن طريق رقم الهوية
            existing_customer = Customer.query.filter_by(id_number=customer_data['IDNumber']).first()
            if existing_customer:
                logger.info(f"العميل موجود بالفعل: {customer_data['CustomerName']}")
                continue
            
            # إنشاء كائن جديد للعميل
            new_customer = Customer()
            new_customer.full_name = customer_data['CustomerName']
            new_customer.phone = customer_data['Phone']
            new_customer.email = customer_data['Email']
            new_customer.address = customer_data['Address']
            new_customer.city = customer_data['City']
            new_customer.country = customer_data['Country']
            new_customer.id_type = customer_data['IDType']
            new_customer.id_number = customer_data['IDNumber']
            new_customer.notes = customer_data['Notes']
            new_customer.is_active = True
            new_customer.created_at = datetime.now()
            
            db.session.add(new_customer)
            customers_added += 1
        
        if customers_added > 0:
            db.session.commit()
            logger.info(f"تم استيراد {customers_added} عميل بنجاح")
        else:
            logger.info("لم يتم استيراد أي عملاء جدد")
        
        return customers_added
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء استيراد العملاء: {str(e)}")
        return 0

def import_accounts():
    """
    استيراد بيانات الحسابات المالية من SQL Server
    """
    logger.info("بدء استيراد بيانات الحسابات المالية...")
    
    # استعلام لجلب فئات الحسابات من SQL Server
    # قم بتعديل هذا الاستعلام حسب بنية جدول الحسابات في SQL Server
    categories_query = """
    SELECT 
        CategoryID,
        CategoryName,
        CategoryCode
    FROM 
        AccountCategories
    """
    
    categories_data = execute_query(categories_query)
    if not categories_data:
        logger.error("فشل في جلب بيانات فئات الحسابات من SQL Server")
        return 0
    
    categories_added = 0
    categories_map = {}  # لتخزين معرفات الفئات المضافة
    
    try:
        # إضافة فئات الحسابات
        for category_data in categories_data:
            # التحقق من وجود الفئة عن طريق الكود
            existing_category = AccountCategory.query.filter_by(code=category_data['CategoryCode']).first()
            if existing_category:
                categories_map[category_data['CategoryID']] = existing_category.id
                continue
            
            # إنشاء كائن جديد للفئة
            new_category = AccountCategory()
            new_category.name = category_data['CategoryName']
            new_category.code = category_data['CategoryCode']
            new_category.is_active = True
            
            db.session.add(new_category)
            db.session.flush()  # للحصول على معرف الفئة بعد الإضافة
            
            categories_map[category_data['CategoryID']] = new_category.id
            categories_added += 1
        
        # استعلام لجلب الحسابات من SQL Server
        accounts_query = """
        SELECT 
            AccountID,
            AccountNumber,
            AccountName,
            AccountType,
            CategoryID,
            IsBankAccount,
            IsCashAccount,
            Balance,
            Description
        FROM 
            Accounts
        """
        
        accounts_data = execute_query(accounts_query)
        if not accounts_data:
            logger.error("فشل في جلب بيانات الحسابات من SQL Server")
            if categories_added > 0:
                db.session.commit()
                logger.info(f"تم استيراد {categories_added} فئة حساب بنجاح")
            return categories_added
        
        accounts_added = 0
        
        # إضافة الحسابات
        for account_data in accounts_data:
            # التحقق من وجود الحساب عن طريق رقم الحساب
            existing_account = Account.query.filter_by(account_number=account_data['AccountNumber']).first()
            if existing_account:
                continue
            
            # إنشاء كائن جديد للحساب
            new_account = Account()
            new_account.name = account_data['AccountName']
            new_account.account_number = account_data['AccountNumber']
            new_account.account_type = account_data['AccountType']
            # ربط الحساب بالفئة إذا كانت موجودة في القاموس
            if account_data['CategoryID'] in categories_map:
                new_account.category_id = categories_map[account_data['CategoryID']]
            
            new_account.is_bank_account = account_data['IsBankAccount']
            new_account.is_cash_account = account_data['IsCashAccount']
            new_account.balance = account_data['Balance'] or 0.0
            new_account.description = account_data['Description']
            new_account.is_active = True
            
            db.session.add(new_account)
            accounts_added += 1
        
        if categories_added > 0 or accounts_added > 0:
            db.session.commit()
            logger.info(f"تم استيراد {categories_added} فئة حساب و {accounts_added} حساب بنجاح")
        else:
            logger.info("لم يتم استيراد أي فئات أو حسابات جديدة")
        
        return categories_added + accounts_added
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء استيراد الحسابات: {str(e)}")
        return 0

def import_bank_accounts():
    """
    استيراد بيانات الحسابات البنكية من SQL Server
    """
    logger.info("بدء استيراد بيانات الحسابات البنكية...")
    
    # استعلام لجلب الحسابات البنكية من SQL Server
    query = """
    SELECT 
        BankID,
        BankName,
        AccountName,
        AccountNumber,
        IBAN,
        SwiftCode,
        Balance,
        CurrencyCode,
        Notes
    FROM 
        BankAccounts
    """
    
    bank_accounts_data = execute_query(query)
    if not bank_accounts_data:
        logger.error("فشل في جلب بيانات الحسابات البنكية من SQL Server")
        return 0
    
    accounts_added = 0
    
    try:
        for account_data in bank_accounts_data:
            # التحقق من وجود الحساب البنكي عن طريق رقم الحساب أو الآيبان
            existing_account = BankAccount.query.filter(
                (BankAccount.account_number == account_data['AccountNumber']) | 
                (BankAccount.iban == account_data['IBAN'])
            ).first()
            
            if existing_account:
                logger.info(f"الحساب البنكي موجود بالفعل: {account_data['BankName']} - {account_data['AccountName']}")
                continue
            
            # البحث عن العملة
            currency = Currency.query.filter_by(code=account_data['CurrencyCode']).first()
            currency_id = currency.id if currency else None
            
            # إنشاء كائن جديد للحساب البنكي
            new_account = BankAccount()
            new_account.bank_name = account_data['BankName']
            new_account.account_name = account_data['AccountName']
            new_account.account_number = account_data['AccountNumber']
            new_account.iban = account_data['IBAN']
            new_account.swift_code = account_data['SwiftCode']
            new_account.balance = account_data['Balance'] or 0.0
            new_account.currency_id = currency_id
            new_account.is_active = True
            new_account.notes = account_data['Notes']
            
            db.session.add(new_account)
            accounts_added += 1
        
        if accounts_added > 0:
            db.session.commit()
            logger.info(f"تم استيراد {accounts_added} حساب بنكي بنجاح")
        else:
            logger.info("لم يتم استيراد أي حسابات بنكية جديدة")
        
        return accounts_added
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء استيراد الحسابات البنكية: {str(e)}")
        return 0

def import_all_data():
    """
    استيراد جميع البيانات من SQL Server إلى النظام
    """
    logger.info("بدء استيراد البيانات من SQL Server...")
    
    with app.app_context():
        try:
            # استيراد بيانات العملاء
            customers_count = import_customers()
            logger.info(f"تم استيراد {customers_count} عميل")
            
            # استيراد بيانات الحسابات
            accounts_count = import_accounts()
            logger.info(f"تم استيراد {accounts_count} حساب/فئة")
            
            # استيراد بيانات الحسابات البنكية
            bank_accounts_count = import_bank_accounts()
            logger.info(f"تم استيراد {bank_accounts_count} حساب بنكي")
            
            # يمكن إضافة المزيد من الوظائف لاستيراد بيانات أخرى هنا
            
            logger.info("تم استيراد البيانات بنجاح")
            return True
        
        except Exception as e:
            logger.error(f"حدث خطأ أثناء استيراد البيانات: {str(e)}")
            return False

# للاختبار
if __name__ == "__main__":
    # تحقق من وجود متغيرات البيئة اللازمة
    required_vars = ['MSSQL_SERVER', 'MSSQL_DATABASE', 'MSSQL_USERNAME', 'MSSQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"المتغيرات البيئية التالية مطلوبة: {', '.join(missing_vars)}")
    else:
        # اختبار الاتصال بقاعدة البيانات
        connection = get_mssql_connection()
        if connection:
            logger.info("تم الاتصال بقاعدة بيانات SQL Server بنجاح")
            connection.close()
            
            # بدء استيراد البيانات
            import_all_data()
        else:
            logger.error("فشل الاتصال بقاعدة بيانات SQL Server")