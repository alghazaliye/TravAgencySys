"""
مسارات خاصة بالعمليات المالية
"""
import os
import json
import uuid
from datetime import datetime, date
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, or_, func
from app import app, db
from models import Account, AccountCategory, JournalEntry, JournalLine, AccountTransaction
from models import PaymentVoucher, ReceiptVoucher, Currency, Customer, BankAccount, CashRegister
import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_date(obj):
    """تحويل الكائنات من نوع التاريخ إلى نصوص"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/journal-entries', methods=['GET'])
@login_required
def journal_entries():
    """صفحة عرض القيود المحاسبية"""
    # جلب معلمات التصفية
    page = int(request.args.get('page', 1))
    per_page = 10
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    entry_number = request.args.get('entry_number')
    status = request.args.get('status')
    
    # بناء الاستعلام
    query = JournalEntry.query
    
    # تطبيق الفلاتر
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(JournalEntry.date >= date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(JournalEntry.date <= date_to_obj)
    
    if entry_number:
        query = query.filter(JournalEntry.entry_number.like(f'%{entry_number}%'))
    
    if status:
        if status == 'posted':
            query = query.filter(JournalEntry.is_posted == True)
        elif status == 'draft':
            query = query.filter(JournalEntry.is_posted == False)
    
    # الترتيب والتقسيم إلى صفحات
    query = query.order_by(desc(JournalEntry.date), desc(JournalEntry.id))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # جلب سجلات الصفحة الحالية
    journal_entries = pagination.items
    
    # جلب فئات الحسابات والحسابات لنافذة القيد الجديد
    account_categories = AccountCategory.query.all()
    accounts = Account.query.filter_by(is_active=True).all()
    
    return render_template('journal-entries.html',
                           journal_entries=journal_entries,
                           account_categories=account_categories,
                           accounts=accounts,
                           page=page,
                           has_next=pagination.has_next,
                           has_prev=pagination.has_prev)

@app.route('/journal-entries/create', methods=['POST'])
@login_required
def create_journal_entry():
    """إنشاء قيد محاسبي جديد"""
    try:
        # استلام البيانات
        entry_date = request.form.get('entry_date')
        entry_type = request.form.get('entry_type')
        description = request.form.get('description')
        reference = request.form.get('reference')
        is_posted = request.form.get('is_posted') == 'true'
        total_debit = float(request.form.get('total_debit', 0))
        total_credit = float(request.form.get('total_credit', 0))
        lines_json = request.form.get('lines')
        
        if not lines_json:
            return jsonify({'success': False, 'error': 'لم يتم توفير سطور للقيد المحاسبي'})
        
        # تحويل النص إلى كائن JSON
        lines_data = json.loads(lines_json)
        
        # التحقق من وجود سطور على الأقل
        if not lines_data:
            return jsonify({'success': False, 'error': 'يجب إضافة سطر واحد على الأقل للقيد'})
        
        # التحقق من توازن القيد
        if total_debit != total_credit:
            return jsonify({'success': False, 'error': 'يجب أن يكون إجمالي المدين مساوياً لإجمالي الدائن'})
        
        # إنشاء رقم فريد للقيد
        entry_number = f"JE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4]}"
        
        # تحويل التاريخ
        entry_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
        
        # إنشاء كائن القيد المحاسبي
        new_entry = JournalEntry()
        new_entry.entry_number = entry_number
        new_entry.date = entry_date_obj
        new_entry.reference_type = entry_type
        new_entry.reference_id = reference
        new_entry.description = description
        new_entry.entry_type = entry_type
        new_entry.status = 'posted' if is_posted else 'draft'
        new_entry.is_posted = is_posted
        new_entry.total_debit = total_debit
        new_entry.total_credit = total_credit
        new_entry.created_by = current_user.id
        
        if is_posted:
            new_entry.posted_by = current_user.id
            new_entry.posted_at = datetime.now()
        
        # إضافة القيد إلى قاعدة البيانات
        db.session.add(new_entry)
        db.session.flush()  # للحصول على معرف القيد
        
        # إنشاء سطور القيد
        for line_data in lines_data:
            account_id = line_data.get('account_id')
            debit = float(line_data.get('debit', 0))
            credit = float(line_data.get('credit', 0))
            line_description = line_data.get('description', '')
            
            # التحقق من وجود الحساب
            account = Account.query.get(account_id)
            if not account:
                db.session.rollback()
                return jsonify({'success': False, 'error': f'الحساب غير موجود: {account_id}'})
            
            # إنشاء سطر القيد
            new_line = JournalLine()
            new_line.journal_id = new_entry.id
            new_line.account_id = account_id
            new_line.debit = debit
            new_line.credit = credit
            new_line.description = line_description
            
            db.session.add(new_line)
            
            # تحديث رصيد الحساب إذا كان القيد مرحلاً
            if is_posted:
                # إنشاء حركة على الحساب
                transaction = AccountTransaction()
                transaction.account_id = account_id
                transaction.journal_id = new_entry.id
                transaction.transaction_date = entry_date_obj
                
                if debit > 0:
                    transaction.amount = debit
                    transaction.transaction_type = 'debit'
                    
                    # تحديث رصيد الحساب
                    if account.account_type in ['asset', 'expense']:
                        account.balance += debit
                    else:
                        account.balance -= debit
                else:
                    transaction.amount = credit
                    transaction.transaction_type = 'credit'
                    
                    # تحديث رصيد الحساب
                    if account.account_type in ['liability', 'equity', 'revenue']:
                        account.balance += credit
                    else:
                        account.balance -= credit
                
                transaction.description = description
                transaction.reference_type = entry_type
                transaction.reference_id = entry_number
                
                db.session.add(transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({'success': True, 'entry_id': new_entry.id})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء إنشاء القيد المحاسبي: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/journal-entries/view/<int:entry_id>', methods=['GET'])
@login_required
def view_journal_entry(entry_id):
    """عرض تفاصيل قيد محاسبي"""
    # جلب القيد المحاسبي
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # جلب سطور القيد
    lines = JournalLine.query.filter_by(journal_id=entry_id).all()
    
    return render_template('journal-entry-view.html', entry=entry, lines=lines)

@app.route('/journal-entries/edit/<int:entry_id>', methods=['GET'])
@login_required
def edit_journal_entry(entry_id):
    """صفحة تعديل قيد محاسبي"""
    # جلب القيد المحاسبي
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # التحقق من أن القيد غير مرحل
    if entry.is_posted:
        flash('لا يمكن تعديل القيود المرحلة', 'danger')
        return redirect(url_for('journal_entries'))
    
    # جلب سطور القيد
    lines = JournalLine.query.filter_by(journal_id=entry_id).all()
    
    # جلب فئات الحسابات والحسابات
    account_categories = AccountCategory.query.all()
    accounts = Account.query.filter_by(is_active=True).all()
    
    return render_template('journal-entry-edit.html',
                           entry=entry,
                           lines=lines,
                           account_categories=account_categories,
                           accounts=accounts)

@app.route('/journal-entries/update/<int:entry_id>', methods=['POST'])
@login_required
def update_journal_entry(entry_id):
    """تحديث قيد محاسبي"""
    try:
        # جلب القيد المحاسبي
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # التحقق من أن القيد غير مرحل
        if entry.is_posted:
            return jsonify({'success': False, 'error': 'لا يمكن تعديل القيود المرحلة'})
        
        # استلام البيانات
        entry_date = request.form.get('entry_date')
        entry_type = request.form.get('entry_type')
        description = request.form.get('description')
        reference = request.form.get('reference')
        is_posted = request.form.get('is_posted') == 'true'
        total_debit = float(request.form.get('total_debit', 0))
        total_credit = float(request.form.get('total_credit', 0))
        lines_json = request.form.get('lines')
        
        if not lines_json:
            return jsonify({'success': False, 'error': 'لم يتم توفير سطور للقيد المحاسبي'})
        
        # تحويل النص إلى كائن JSON
        lines_data = json.loads(lines_json)
        
        # التحقق من وجود سطور على الأقل
        if not lines_data:
            return jsonify({'success': False, 'error': 'يجب إضافة سطر واحد على الأقل للقيد'})
        
        # التحقق من توازن القيد
        if total_debit != total_credit:
            return jsonify({'success': False, 'error': 'يجب أن يكون إجمالي المدين مساوياً لإجمالي الدائن'})
        
        # تحويل التاريخ
        entry_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
        
        # تحديث بيانات القيد
        entry.date = entry_date_obj
        entry.reference_type = entry_type
        entry.reference_id = reference
        entry.description = description
        entry.entry_type = entry_type
        entry.total_debit = total_debit
        entry.total_credit = total_credit
        entry.updated_at = datetime.now()
        
        if is_posted:
            entry.is_posted = True
            entry.status = 'posted'
            entry.posted_by = current_user.id
            entry.posted_at = datetime.now()
        
        # حذف سطور القيد الحالية
        JournalLine.query.filter_by(journal_id=entry_id).delete()
        
        # إنشاء سطور القيد الجديدة
        for line_data in lines_data:
            account_id = line_data.get('account_id')
            debit = float(line_data.get('debit', 0))
            credit = float(line_data.get('credit', 0))
            line_description = line_data.get('description', '')
            
            # التحقق من وجود الحساب
            account = Account.query.get(account_id)
            if not account:
                db.session.rollback()
                return jsonify({'success': False, 'error': f'الحساب غير موجود: {account_id}'})
            
            # إنشاء سطر القيد
            new_line = JournalLine()
            new_line.journal_id = entry.id
            new_line.account_id = account_id
            new_line.debit = debit
            new_line.credit = credit
            new_line.description = line_description
            
            db.session.add(new_line)
            
            # تحديث رصيد الحساب إذا كان القيد مرحلاً
            if is_posted:
                # إنشاء حركة على الحساب
                transaction = AccountTransaction()
                transaction.account_id = account_id
                transaction.journal_id = entry.id
                transaction.transaction_date = entry_date_obj
                
                if debit > 0:
                    transaction.amount = debit
                    transaction.transaction_type = 'debit'
                    
                    # تحديث رصيد الحساب
                    if account.account_type in ['asset', 'expense']:
                        account.balance += debit
                    else:
                        account.balance -= debit
                else:
                    transaction.amount = credit
                    transaction.transaction_type = 'credit'
                    
                    # تحديث رصيد الحساب
                    if account.account_type in ['liability', 'equity', 'revenue']:
                        account.balance += credit
                    else:
                        account.balance -= credit
                
                transaction.description = description
                transaction.reference_type = entry_type
                transaction.reference_id = entry.entry_number
                
                db.session.add(transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء تحديث القيد المحاسبي: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/journal-entries/post/<int:entry_id>', methods=['POST'])
@login_required
def post_journal_entry(entry_id):
    """ترحيل قيد محاسبي"""
    try:
        # جلب القيد المحاسبي
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # التحقق من أن القيد غير مرحل
        if entry.is_posted:
            return jsonify({'success': False, 'error': 'القيد مرحل بالفعل'})
        
        # جلب سطور القيد
        lines = JournalLine.query.filter_by(journal_id=entry_id).all()
        
        # ترحيل القيد
        entry.is_posted = True
        entry.status = 'posted'
        entry.posted_by = current_user.id
        entry.posted_at = datetime.now()
        
        # إنشاء حركات على الحسابات وتحديث الأرصدة
        for line in lines:
            account = Account.query.get(line.account_id)
            
            # إنشاء حركة على الحساب
            transaction = AccountTransaction()
            transaction.account_id = line.account_id
            transaction.journal_id = entry.id
            transaction.transaction_date = entry.date
            
            if line.debit > 0:
                transaction.amount = line.debit
                transaction.transaction_type = 'debit'
                
                # تحديث رصيد الحساب
                if account.account_type in ['asset', 'expense']:
                    account.balance += line.debit
                else:
                    account.balance -= line.debit
            else:
                transaction.amount = line.credit
                transaction.transaction_type = 'credit'
                
                # تحديث رصيد الحساب
                if account.account_type in ['liability', 'equity', 'revenue']:
                    account.balance += line.credit
                else:
                    account.balance -= line.credit
            
            transaction.description = entry.description
            transaction.reference_type = entry.entry_type
            transaction.reference_id = entry.entry_number
            
            db.session.add(transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء ترحيل القيد المحاسبي: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/journal-entries/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_journal_entry(entry_id):
    """حذف قيد محاسبي"""
    try:
        # جلب القيد المحاسبي
        entry = JournalEntry.query.get_or_404(entry_id)
        
        # التحقق من أن القيد غير مرحل
        if entry.is_posted:
            return jsonify({'success': False, 'error': 'لا يمكن حذف القيود المرحلة'})
        
        # التحقق من صلاحيات المستخدم
        if not current_user.is_admin:
            return jsonify({'success': False, 'error': 'ليس لديك صلاحيات كافية لحذف القيود المحاسبية'})
        
        # حذف سطور القيد
        JournalLine.query.filter_by(journal_id=entry_id).delete()
        
        # حذف القيد
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء حذف القيد المحاسبي: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/financial/payment-vouchers', methods=['GET'])
@login_required
def financial_payment_vouchers():
    """صفحة عرض سندات الصرف"""
    # جلب معلمات التصفية
    page = int(request.args.get('page', 1))
    per_page = 10
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    voucher_number = request.args.get('voucher_number')
    beneficiary = request.args.get('beneficiary')
    
    # بناء الاستعلام
    query = PaymentVoucher.query
    
    # تطبيق الفلاتر
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(PaymentVoucher.voucher_date >= date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(PaymentVoucher.voucher_date <= date_to_obj)
    
    if voucher_number:
        query = query.filter(PaymentVoucher.voucher_number.like(f'%{voucher_number}%'))
    
    if beneficiary:
        query = query.filter(PaymentVoucher.beneficiary.like(f'%{beneficiary}%'))
    
    # الترتيب والتقسيم إلى صفحات
    query = query.order_by(desc(PaymentVoucher.voucher_date), desc(PaymentVoucher.id))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # جلب سجلات الصفحة الحالية
    vouchers = pagination.items
    
    # جلب الحسابات والعملات للنموذج
    accounts = Account.query.filter(
        Account.is_active == True,
        or_(Account.is_cash_account == True, Account.is_bank_account == True)
    ).all()
    
    currencies = Currency.query.filter_by(is_active=True).all()
    
    return render_template('payment-vouchers.html',
                          vouchers=vouchers,
                          accounts=accounts,
                          currencies=currencies,
                          page=page,
                          has_next=pagination.has_next,
                          has_prev=pagination.has_prev)

@app.route('/financial/receipt-vouchers', methods=['GET'])
@login_required
def financial_receipt_vouchers():
    """صفحة عرض سندات القبض"""
    # جلب معلمات التصفية
    page = int(request.args.get('page', 1))
    per_page = 10
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    voucher_number = request.args.get('voucher_number')
    customer_name = request.args.get('customer_name')
    
    # بناء الاستعلام
    query = ReceiptVoucher.query
    
    # تطبيق الفلاتر
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(ReceiptVoucher.voucher_date >= date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(ReceiptVoucher.voucher_date <= date_to_obj)
    
    if voucher_number:
        query = query.filter(ReceiptVoucher.voucher_number.like(f'%{voucher_number}%'))
    
    if customer_name:
        query = query.join(Customer).filter(Customer.full_name.like(f'%{customer_name}%'))
    
    # الترتيب والتقسيم إلى صفحات
    query = query.order_by(desc(ReceiptVoucher.voucher_date), desc(ReceiptVoucher.id))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # جلب سجلات الصفحة الحالية
    vouchers = pagination.items
    
    # جلب الحسابات والعملات والعملاء للنموذج
    accounts = Account.query.filter(
        Account.is_active == True,
        or_(Account.is_cash_account == True, Account.is_bank_account == True)
    ).all()
    
    currencies = Currency.query.filter_by(is_active=True).all()
    customers = Customer.query.filter_by(is_active=True).all()
    
    return render_template('receipt-vouchers.html',
                          vouchers=vouchers,
                          accounts=accounts,
                          currencies=currencies,
                          customers=customers,
                          page=page,
                          has_next=pagination.has_next,
                          has_prev=pagination.has_prev)

@app.route('/financial-reports', methods=['GET'])
@login_required
def financial_reports():
    """صفحة التقارير المالية"""
    # نوع التقرير
    report_type = request.args.get('report_type', 'account_statement')
    
    # معلمات التقرير
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    account_id = request.args.get('account_id')
    
    # تحويل التواريخ
    date_from_obj = None
    date_to_obj = None
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # نتائج التقرير
    report_data = None
    
    # جلب بيانات التقرير حسب النوع
    if report_type == 'account_statement' and account_id:
        # كشف حساب
        report_data = get_account_statement(account_id, date_from_obj, date_to_obj)
    
    elif report_type == 'trial_balance':
        # ميزان المراجعة
        report_data = get_trial_balance(date_from_obj, date_to_obj)
    
    elif report_type == 'income_statement':
        # قائمة الدخل
        report_data = get_income_statement(date_from_obj, date_to_obj)
    
    elif report_type == 'balance_sheet':
        # الميزانية العمومية
        report_data = get_balance_sheet(date_to_obj)
    
    # جلب الحسابات للنموذج
    accounts = Account.query.filter_by(is_active=True).all()
    
    return render_template('financial-reports.html',
                          report_type=report_type,
                          report_data=report_data,
                          accounts=accounts,
                          date_from=date_from,
                          date_to=date_to,
                          account_id=account_id)

def get_account_statement(account_id, date_from=None, date_to=None):
    """جلب كشف حساب"""
    # التحقق من وجود الحساب
    account = Account.query.get(account_id)
    if not account:
        return None
    
    # بناء الاستعلام
    query = AccountTransaction.query.filter(AccountTransaction.account_id == account_id)
    
    # تطبيق فلاتر التاريخ
    if date_from:
        query = query.filter(AccountTransaction.transaction_date >= date_from)
    
    if date_to:
        query = query.filter(AccountTransaction.transaction_date <= date_to)
    
    # ترتيب الحركات
    query = query.order_by(AccountTransaction.transaction_date, AccountTransaction.id)
    
    # جلب الحركات
    transactions = query.all()
    
    # حساب الرصيد الافتتاحي
    opening_balance = 0
    
    if date_from:
        # جلب مجموع المدين والدائن قبل تاريخ البداية
        prev_debit = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account_id,
            AccountTransaction.transaction_type == 'debit',
            AccountTransaction.transaction_date < date_from
        ).scalar() or 0
        
        prev_credit = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account_id,
            AccountTransaction.transaction_type == 'credit',
            AccountTransaction.transaction_date < date_from
        ).scalar() or 0
        
        # حساب الرصيد الافتتاحي حسب نوع الحساب
        if account.account_type in ['asset', 'expense']:
            opening_balance = prev_debit - prev_credit
        else:
            opening_balance = prev_credit - prev_debit
    
    # تجهيز بيانات كشف الحساب
    statement = {
        'account': account,
        'opening_balance': opening_balance,
        'closing_balance': opening_balance,
        'transactions': []
    }
    
    # إضافة الحركات وحساب الأرصدة التراكمية
    running_balance = opening_balance
    
    for transaction in transactions:
        # حساب الرصيد الجديد
        if transaction.transaction_type == 'debit':
            if account.account_type in ['asset', 'expense']:
                running_balance += transaction.amount
            else:
                running_balance -= transaction.amount
            
            amount = transaction.amount
            debit = transaction.amount
            credit = 0
        else:
            if account.account_type in ['liability', 'equity', 'revenue']:
                running_balance += transaction.amount
            else:
                running_balance -= transaction.amount
            
            amount = transaction.amount
            debit = 0
            credit = transaction.amount
        
        # إضافة الحركة مع الرصيد المتراكم
        statement['transactions'].append({
            'transaction': transaction,
            'debit': debit,
            'credit': credit,
            'balance': running_balance,
            'journal': JournalEntry.query.get(transaction.journal_id) if transaction.journal_id else None
        })
    
    # تحديث الرصيد الختامي
    statement['closing_balance'] = running_balance
    
    return statement

def get_trial_balance(date_from=None, date_to=None):
    """جلب ميزان المراجعة"""
    # بناء الاستعلام
    query = Account.query.filter(Account.is_active == True)
    
    # جلب الحسابات
    accounts = query.all()
    
    # تجهيز بيانات ميزان المراجعة
    trial_balance = {
        'accounts': [],
        'total_debit': 0,
        'total_credit': 0
    }
    
    # حساب أرصدة الحسابات
    for account in accounts:
        # جلب مجموع المدين والدائن ضمن فترة التقرير
        debit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit'
        )
        
        credit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit'
        )
        
        # تطبيق فلاتر التاريخ
        if date_from:
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
        
        if date_to:
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
        
        # استرجاع الإحصائيات
        debit_sum = debit_sum_query.scalar() or 0
        credit_sum = credit_sum_query.scalar() or 0
        
        # حساب الرصيد حسب نوع الحساب
        if account.account_type in ['asset', 'expense']:
            balance = debit_sum - credit_sum
            debit_balance = balance if balance > 0 else 0
            credit_balance = -balance if balance < 0 else 0
        else:
            balance = credit_sum - debit_sum
            credit_balance = balance if balance > 0 else 0
            debit_balance = -balance if balance < 0 else 0
        
        # إضافة الحساب إلى ميزان المراجعة إذا كان له رصيد
        if debit_balance > 0 or credit_balance > 0:
            trial_balance['accounts'].append({
                'account': account,
                'debit': debit_balance,
                'credit': credit_balance
            })
            
            trial_balance['total_debit'] += debit_balance
            trial_balance['total_credit'] += credit_balance
    
    return trial_balance

def get_income_statement(date_from=None, date_to=None):
    """جلب قائمة الدخل"""
    # بناء استعلام الإيرادات
    revenue_query = Account.query.filter(
        Account.is_active == True,
        Account.account_type == 'revenue'
    )
    
    # بناء استعلام المصروفات
    expense_query = Account.query.filter(
        Account.is_active == True,
        Account.account_type == 'expense'
    )
    
    # جلب الحسابات
    revenue_accounts = revenue_query.all()
    expense_accounts = expense_query.all()
    
    # تجهيز بيانات قائمة الدخل
    income_statement = {
        'revenues': [],
        'expenses': [],
        'total_revenue': 0,
        'total_expense': 0,
        'net_income': 0
    }
    
    # حساب الإيرادات
    for account in revenue_accounts:
        # جلب مجموع الحركات الدائنة والمدينة ضمن فترة التقرير
        credit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit'
        )
        
        debit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit'
        )
        
        # تطبيق فلاتر التاريخ
        if date_from:
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
        
        if date_to:
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
        
        # استرجاع الإحصائيات
        credit_sum = credit_sum_query.scalar() or 0
        debit_sum = debit_sum_query.scalar() or 0
        
        # حساب صافي الإيراد
        revenue_amount = credit_sum - debit_sum
        
        # إضافة الحساب إلى قائمة الدخل إذا كان له قيمة
        if revenue_amount != 0:
            income_statement['revenues'].append({
                'account': account,
                'amount': revenue_amount
            })
            
            income_statement['total_revenue'] += revenue_amount
    
    # حساب المصروفات
    for account in expense_accounts:
        # جلب مجموع الحركات المدينة والدائنة ضمن فترة التقرير
        debit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit'
        )
        
        credit_sum_query = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit'
        )
        
        # تطبيق فلاتر التاريخ
        if date_from:
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date >= date_from)
        
        if date_to:
            debit_sum_query = debit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
            credit_sum_query = credit_sum_query.filter(AccountTransaction.transaction_date <= date_to)
        
        # استرجاع الإحصائيات
        debit_sum = debit_sum_query.scalar() or 0
        credit_sum = credit_sum_query.scalar() or 0
        
        # حساب صافي المصروف
        expense_amount = debit_sum - credit_sum
        
        # إضافة الحساب إلى قائمة الدخل إذا كان له قيمة
        if expense_amount != 0:
            income_statement['expenses'].append({
                'account': account,
                'amount': expense_amount
            })
            
            income_statement['total_expense'] += expense_amount
    
    # حساب صافي الدخل
    income_statement['net_income'] = income_statement['total_revenue'] - income_statement['total_expense']
    
    return income_statement

def get_balance_sheet(date=None):
    """جلب الميزانية العمومية"""
    # إذا لم يتم تحديد تاريخ، استخدم تاريخ اليوم
    if not date:
        date = datetime.now().date()
    
    # بناء استعلام الأصول
    asset_query = Account.query.filter(
        Account.is_active == True,
        Account.account_type == 'asset'
    )
    
    # بناء استعلام الخصوم
    liability_query = Account.query.filter(
        Account.is_active == True,
        Account.account_type == 'liability'
    )
    
    # بناء استعلام حقوق الملكية
    equity_query = Account.query.filter(
        Account.is_active == True,
        Account.account_type == 'equity'
    )
    
    # جلب الحسابات
    asset_accounts = asset_query.all()
    liability_accounts = liability_query.all()
    equity_accounts = equity_query.all()
    
    # تجهيز بيانات الميزانية العمومية
    balance_sheet = {
        'assets': [],
        'liabilities': [],
        'equity': [],
        'total_assets': 0,
        'total_liabilities': 0,
        'total_equity': 0
    }
    
    # حساب الأصول
    for account in asset_accounts:
        # جلب مجموع الحركات المدينة والدائنة حتى التاريخ المحدد
        debit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        credit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        # حساب صافي الأصل
        asset_amount = debit_sum - credit_sum
        
        # إضافة الحساب إلى الميزانية إذا كان له قيمة
        if asset_amount != 0:
            balance_sheet['assets'].append({
                'account': account,
                'amount': asset_amount
            })
            
            balance_sheet['total_assets'] += asset_amount
    
    # حساب الخصوم
    for account in liability_accounts:
        # جلب مجموع الحركات الدائنة والمدينة حتى التاريخ المحدد
        credit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        debit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        # حساب صافي الخصم
        liability_amount = credit_sum - debit_sum
        
        # إضافة الحساب إلى الميزانية إذا كان له قيمة
        if liability_amount != 0:
            balance_sheet['liabilities'].append({
                'account': account,
                'amount': liability_amount
            })
            
            balance_sheet['total_liabilities'] += liability_amount
    
    # حساب حقوق الملكية
    for account in equity_accounts:
        # جلب مجموع الحركات الدائنة والمدينة حتى التاريخ المحدد
        credit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'credit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        debit_sum = db.session.query(func.sum(AccountTransaction.amount)).filter(
            AccountTransaction.account_id == account.id,
            AccountTransaction.transaction_type == 'debit',
            AccountTransaction.transaction_date <= date
        ).scalar() or 0
        
        # حساب صافي حقوق الملكية
        equity_amount = credit_sum - debit_sum
        
        # إضافة الحساب إلى الميزانية إذا كان له قيمة
        if equity_amount != 0:
            balance_sheet['equity'].append({
                'account': account,
                'amount': equity_amount
            })
            
            balance_sheet['total_equity'] += equity_amount
    
    # حساب الأرباح المحتجزة (صافي الدخل)
    income_statement = get_income_statement(None, date)
    retained_earnings = income_statement['net_income']
    
    # إضافة الأرباح المحتجزة إلى حقوق الملكية
    if retained_earnings != 0:
        balance_sheet['equity'].append({
            'account': {'name': 'الأرباح المحتجزة للفترة الحالية'},
            'amount': retained_earnings
        })
        
        balance_sheet['total_equity'] += retained_earnings
    
    return balance_sheet