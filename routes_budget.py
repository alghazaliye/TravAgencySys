"""
مسارات خاصة بإدارة الميزانيات
"""
import os
import json
import uuid
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, or_, func

from app import app, db
from models import Account, AccountCategory, Budget

import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/budget/management', methods=['GET'])
@login_required
def budget_management():
    """صفحة إدارة الميزانيات"""
    # استلام المعلمات من الاستعلام
    selected_year = int(request.args.get('year', datetime.now().year))
    selected_category = request.args.get('category_id', '')
    selected_status = request.args.get('status', '')
    
    # جلب فئات الحسابات
    account_categories = AccountCategory.query.all()
    
    # إنشاء استعلام أساسي
    query = Budget.query.join(Account)
    
    # تطبيق المرشحات
    query = query.filter(Budget.year == selected_year)
    
    if selected_category:
        query = query.filter(Account.category_id == selected_category)
    
    # جلب الميزانيات السنوية والربع سنوية والشهرية
    annual_budgets = query.filter(and_(Budget.month == None, Budget.quarter == None)).all()
    quarterly_budgets = query.filter(and_(Budget.month == None, Budget.quarter != None)).all()
    monthly_budgets = query.filter(Budget.month != None).all()
    
    # تطبيق مرشح الحالة
    if selected_status:
        # سنقوم بفلترة النتائج بعد جلبها حسب الحالة (جيدة، تحذير، متجاوزة)
        # نظرًا لأن الحالة هي خاصية محسوبة وليست عمودًا في قاعدة البيانات
        if selected_status == 'good':
            annual_budgets = [b for b in annual_budgets if b.status == 'success']
            quarterly_budgets = [b for b in quarterly_budgets if b.status == 'success']
            monthly_budgets = [b for b in monthly_budgets if b.status == 'success']
        elif selected_status == 'warning':
            annual_budgets = [b for b in annual_budgets if b.status == 'warning']
            quarterly_budgets = [b for b in quarterly_budgets if b.status == 'warning']
            monthly_budgets = [b for b in monthly_budgets if b.status == 'warning']
        elif selected_status == 'danger':
            annual_budgets = [b for b in annual_budgets if b.status == 'danger']
            quarterly_budgets = [b for b in quarterly_budgets if b.status == 'danger']
            monthly_budgets = [b for b in monthly_budgets if b.status == 'danger']
    
    # حساب إجمالي الميزانية والميزانية المتبقية
    total_budget = sum(float(budget.amount) for budget in annual_budgets)
    total_spent = sum(float(budget.actual_amount) for budget in annual_budgets)
    remaining_budget = total_budget - total_spent
    
    # حساب نسبة الاستهلاك والانحراف
    usage_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
    budget_variance = total_budget - total_spent
    
    # إعداد بيانات الرسوم البيانية
    annual_chart_data = {
        'labels': [],
        'budget_data': [],
        'actual_data': []
    }
    
    # بيانات الرسم البياني السنوي
    for budget in annual_budgets:
        annual_chart_data['labels'].append(budget.account.name)
        annual_chart_data['budget_data'].append(float(budget.amount))
        annual_chart_data['actual_data'].append(float(budget.actual_amount))
    
    # بيانات الرسم البياني ربع السنوي
    quarterly_chart_data = {
        'labels': [],
        'budget_data': [],
        'actual_data': []
    }
    
    quarters = {}
    for budget in quarterly_budgets:
        quarter_key = f'Q{budget.quarter}'
        if quarter_key not in quarters:
            quarters[quarter_key] = {'budget': 0, 'actual': 0}
        
        quarters[quarter_key]['budget'] += float(budget.amount)
        quarters[quarter_key]['actual'] += float(budget.actual_amount)
    
    for quarter, data in sorted(quarters.items()):
        quarterly_chart_data['labels'].append(quarter)
        quarterly_chart_data['budget_data'].append(data['budget'])
        quarterly_chart_data['actual_data'].append(data['actual'])
    
    # بيانات الرسم البياني الشهري
    monthly_chart_data = {
        'labels': [],
        'budget_data': [],
        'actual_data': []
    }
    
    months = {}
    for budget in monthly_budgets:
        if budget.month_name not in months:
            months[budget.month_name] = {'budget': 0, 'actual': 0}
        
        months[budget.month_name] += float(budget.amount)
        months[budget.month_name] += float(budget.actual_amount)
    
    month_order = {'يناير': 1, 'فبراير': 2, 'مارس': 3, 'إبريل': 4, 'مايو': 5, 'يونيو': 6, 
                  'يوليو': 7, 'أغسطس': 8, 'سبتمبر': 9, 'أكتوبر': 10, 'نوفمبر': 11, 'ديسمبر': 12}
    
    for month, data in sorted(months.items(), key=lambda x: month_order.get(x[0], 13)):
        monthly_chart_data['labels'].append(month)
        monthly_chart_data['budget_data'].append(data['budget'])
        monthly_chart_data['actual_data'].append(data['actual'])
    
    # بيانات توزيع الميزانية
    budget_distribution = {
        'labels': [],
        'data': []
    }
    
    categories = {}
    for budget in annual_budgets:
        category_name = budget.account.category.name
        if category_name not in categories:
            categories[category_name] = 0
        
        categories[category_name] += float(budget.amount)
    
    for category, amount in categories.items():
        budget_distribution['labels'].append(category)
        budget_distribution['data'].append(amount)
    
    return render_template('budget-management.html',
                           current_year=datetime.now().year,
                           selected_year=selected_year,
                           selected_category=selected_category,
                           selected_status=selected_status,
                           account_categories=account_categories,
                           annual_budgets=annual_budgets,
                           quarterly_budgets=quarterly_budgets,
                           monthly_budgets=monthly_budgets,
                           total_budget=total_budget,
                           remaining_budget=remaining_budget,
                           usage_percentage=usage_percentage,
                           budget_variance=budget_variance,
                           annual_chart_data=annual_chart_data,
                           quarterly_chart_data=quarterly_chart_data,
                           monthly_chart_data=monthly_chart_data,
                           budget_distribution=budget_distribution)


@app.route('/budget/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    """إنشاء ميزانية جديدة"""
    if request.method == 'POST':
        # جلب البيانات من النموذج
        account_id = request.form.get('account_id')
        budget_type = request.form.get('budget_type')
        year = int(request.form.get('year'))
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes')
        
        # تحديد الشهر أو الربع حسب نوع الميزانية
        month = None
        quarter = None
        
        if budget_type == 'monthly':
            month = int(request.form.get('month'))
        elif budget_type == 'quarterly':
            quarter = int(request.form.get('quarter'))
        
        # التحقق من وجود ميزانية مشابهة
        existing_budget = Budget.query.filter_by(
            account_id=account_id,
            year=year,
            month=month,
            quarter=quarter
        ).first()
        
        if existing_budget:
            flash('توجد ميزانية مشابهة لهذا الحساب في نفس الفترة!', 'warning')
            return redirect(url_for('create_budget'))
        
        # إنشاء ميزانية جديدة
        new_budget = Budget(
            account_id=account_id,
            year=year,
            month=month,
            quarter=quarter,
            amount=amount,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(new_budget)
        db.session.commit()
        
        flash('تم إنشاء الميزانية بنجاح!', 'success')
        return redirect(url_for('budget_management'))
    
    # جلب الحسابات لعرضها في القائمة المنسدلة
    accounts = Account.query.filter(Account.account_type.in_(['expense', 'asset'])).all()
    
    return render_template('budget-form.html',
                           accounts=accounts,
                           current_year=datetime.now().year,
                           budget=None,
                           title='إنشاء ميزانية جديدة',
                           action='create')


@app.route('/budget/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    """تعديل ميزانية موجودة"""
    budget = Budget.query.get_or_404(budget_id)
    
    if request.method == 'POST':
        # جلب البيانات من النموذج
        account_id = request.form.get('account_id')
        budget_type = request.form.get('budget_type')
        year = int(request.form.get('year'))
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes')
        
        # تحديد الشهر أو الربع حسب نوع الميزانية
        month = None
        quarter = None
        
        if budget_type == 'monthly':
            month = int(request.form.get('month'))
        elif budget_type == 'quarterly':
            quarter = int(request.form.get('quarter'))
        
        # التحقق من وجود ميزانية مشابهة (غير الميزانية الحالية)
        existing_budget = Budget.query.filter(
            Budget.account_id == account_id,
            Budget.year == year,
            Budget.month == month,
            Budget.quarter == quarter,
            Budget.id != budget_id
        ).first()
        
        if existing_budget:
            flash('توجد ميزانية مشابهة لهذا الحساب في نفس الفترة!', 'warning')
            return redirect(url_for('edit_budget', budget_id=budget_id))
        
        # تحديث الميزانية
        budget.account_id = account_id
        budget.year = year
        budget.month = month
        budget.quarter = quarter
        budget.amount = amount
        budget.notes = notes
        
        db.session.commit()
        
        flash('تم تحديث الميزانية بنجاح!', 'success')
        return redirect(url_for('budget_management'))
    
    # جلب الحسابات لعرضها في القائمة المنسدلة
    accounts = Account.query.filter(Account.account_type.in_(['expense', 'asset'])).all()
    
    return render_template('budget-form.html',
                           accounts=accounts,
                           current_year=datetime.now().year,
                           budget=budget,
                           title='تعديل الميزانية',
                           action='edit')


@app.route('/budget/view/<int:budget_id>')
@login_required
def view_budget_details(budget_id):
    """عرض تفاصيل الميزانية"""
    budget = Budget.query.get_or_404(budget_id)
    
    # جلب المعاملات المالية المرتبطة بالحساب خلال فترة الميزانية
    from datetime import date, timedelta
    
    # تحديد فترة الميزانية
    start_date = None
    end_date = None
    
    if budget.month is not None:
        # ميزانية شهرية
        start_date = date(budget.year, budget.month, 1)
        if budget.month == 12:
            end_date = date(budget.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(budget.year, budget.month + 1, 1) - timedelta(days=1)
    elif budget.quarter is not None:
        # ميزانية ربع سنوية
        month_start = (budget.quarter - 1) * 3 + 1
        start_date = date(budget.year, month_start, 1)
        if month_start + 2 >= 12:
            end_date = date(budget.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(budget.year, month_start + 3, 1) - timedelta(days=1)
    else:
        # ميزانية سنوية
        start_date = date(budget.year, 1, 1)
        end_date = date(budget.year, 12, 31)
    
    # جلب المعاملات المالية
    from models import AccountTransaction
    transactions = AccountTransaction.query.filter(
        AccountTransaction.account_id == budget.account_id,
        AccountTransaction.transaction_date >= start_date,
        AccountTransaction.transaction_date <= end_date
    ).order_by(AccountTransaction.transaction_date.desc()).all()
    
    # إعداد بيانات التخطيط
    chart_data = {
        'dates': [],
        'amounts': []
    }
    
    # تجميع المعاملات حسب التاريخ
    daily_transactions = {}
    for transaction in transactions:
        date_str = transaction.transaction_date.strftime('%Y-%m-%d')
        if date_str not in daily_transactions:
            daily_transactions[date_str] = 0
        
        amount = float(transaction.amount)
        if transaction.transaction_type == 'debit':
            daily_transactions[date_str] += amount
        else:
            daily_transactions[date_str] -= amount
    
    # ترتيب المعاملات حسب التاريخ
    sorted_dates = sorted(daily_transactions.keys())
    cumulative_amount = 0
    for date_str in sorted_dates:
        chart_data['dates'].append(date_str)
        cumulative_amount += daily_transactions[date_str]
        chart_data['amounts'].append(cumulative_amount)
    
    return render_template('budget-details.html',
                           budget=budget,
                           transactions=transactions,
                           chart_data=chart_data,
                           start_date=start_date,
                           end_date=end_date)


@app.route('/budget/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    """حذف ميزانية"""
    budget = Budget.query.get_or_404(budget_id)
    
    db.session.delete(budget)
    db.session.commit()
    
    flash('تم حذف الميزانية بنجاح!', 'success')
    return redirect(url_for('budget_management'))