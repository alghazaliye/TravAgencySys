/**
 * ملف JavaScript لإدارة صفحة حجز تذاكر الباص
 * ويتضمن التعامل مع العلاقات بين الحقول وتحديث واجهة المستخدم
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل صفحة حجز تذاكر الباص');
    
    // تهيئة أدوات اختيار التاريخ
    initializeDateTimePickers();
    
    // تهيئة أدوات select2
    initializeSelect2();
    
    // تهيئة وظائف حساب المبلغ المتبقي
    initializePaymentCalculations();
    
    // تهيئة العلاقة بين طريقة الدفع وخيارات الحساب
    initializePaymentMethodAccountRelation();
    
    // تهيئة تحديث رموز العملة
    initializeCurrencySymbols();
    
    // أحداث النقر على الأزرار
    setupButtonEvents();
});

/**
 * تهيئة أدوات اختيار التاريخ والوقت
 */
function initializeDateTimePickers() {
    if ($.fn.datetimepicker) {
        // تهيئة أداة اختيار التاريخ للميلاد
        $('#birth-date-picker').datetimepicker({
            format: 'YYYY-MM-DD',
            useCurrent: false,
            locale: 'ar',
            icons: {
                time: 'far fa-clock',
                date: 'far fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-right',
                next: 'fas fa-chevron-left',
                today: 'fas fa-calendar-check',
                clear: 'far fa-trash-alt',
                close: 'fas fa-times'
            }
        });
        
        // تهيئة أداة اختيار التاريخ للإصدار
        $('#issue-date-picker').datetimepicker({
            format: 'YYYY-MM-DD',
            useCurrent: false,
            locale: 'ar',
            icons: {
                time: 'far fa-clock',
                date: 'far fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-right',
                next: 'fas fa-chevron-left',
                today: 'fas fa-calendar-check',
                clear: 'far fa-trash-alt',
                close: 'fas fa-times'
            }
        });
        
        // تهيئة أداة اختيار التاريخ للحجز
        $('#reservation-date-picker').datetimepicker({
            format: 'YYYY-MM-DD',
            useCurrent: true,
            locale: 'ar',
            icons: {
                time: 'far fa-clock',
                date: 'far fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-right',
                next: 'fas fa-chevron-left',
                today: 'fas fa-calendar-check',
                clear: 'far fa-trash-alt',
                close: 'fas fa-times'
            }
        });
        
        // تهيئة أداة اختيار التاريخ للعودة
        $('#return-date-picker').datetimepicker({
            format: 'YYYY-MM-DD',
            useCurrent: false,
            locale: 'ar',
            icons: {
                time: 'far fa-clock',
                date: 'far fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-right',
                next: 'fas fa-chevron-left',
                today: 'fas fa-calendar-check',
                clear: 'far fa-trash-alt',
                close: 'fas fa-times'
            }
        });
        
        // تهيئة أداة اختيار التاريخ والوقت للمعاملة
        $('#transaction-date-picker').datetimepicker({
            format: 'DD MMMM, YYYY',
            useCurrent: true,
            locale: 'ar',
            icons: {
                time: 'far fa-clock',
                date: 'far fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-right',
                next: 'fas fa-chevron-left',
                today: 'fas fa-calendar-check',
                clear: 'far fa-trash-alt',
                close: 'fas fa-times'
            }
        });
        
        // إضافة حدث تغيير نوع الرحلة لتفعيل/تعطيل حقل تاريخ العودة
        $('#journey-type').on('change', function() {
            var journeyType = $(this).val();
            if (journeyType === 'round-trip') {
                $('#return-date').prop('disabled', false);
            } else {
                $('#return-date').prop('disabled', true);
                $('#return-date').val('');
            }
        });
    }
}

/**
 * تهيئة أدوات Select2
 */
function initializeSelect2() {
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap',
            dir: 'rtl',
            language: 'ar',
            width: '100%'
        });
    }
}

/**
 * تهيئة حساب المبلغ المتبقي
 */
function initializePaymentCalculations() {
    // تحديث المبلغ المتبقي عند تغيير سعر البيع أو المبلغ الواصل
    $('#selling-price, #received-amount').on('input', function() {
        updateRemainingAmount();
    });
    
    // حساب المبلغ المتبقي أول مرة
    updateRemainingAmount();
}

/**
 * تحديث المبلغ المتبقي
 */
function updateRemainingAmount() {
    var sellingPrice = parseFloat($('#selling-price').val() || 0);
    var receivedAmount = parseFloat($('#received-amount').val() || 0);
    var remainingAmount = Math.max(0, sellingPrice - receivedAmount);
    
    $('#remaining-amount').val(remainingAmount.toFixed(2));
}

/**
 * تهيئة الحقول حسب طريقة الدفع المختارة
 */
function initializePaymentMethodAccountRelation() {
    // تحديث خيارات الحساب عند تغيير طريقة الدفع
    $('#payment-method').on('change', function() {
        updateAccountOptions();
    });
    
    // تحديث خيارات الحساب عند تحميل الصفحة
    updateAccountOptions();
}

/**
 * تحديث خيارات الحساب بناءً على طريقة الدفع المختارة
 */
function updateAccountOptions() {
    var paymentMethod = $('#payment-method').val();
    var accountSelect = $('#account');
    
    // حفظ القيمة الحالية للحساب
    var currentAccount = accountSelect.val();
    
    // تفريغ القائمة
    accountSelect.empty();
    accountSelect.append('<option value="">اختر الحساب</option>');
    
    // إضافة الخيارات المناسبة حسب طريقة الدفع
    if (paymentMethod === 'cash') {
        // إذا كانت طريقة الدفع نقدية، أظهر فقط خيار الصندوق
        accountSelect.append('<option value="cash_1">الصندوق</option>');
    } else if (paymentMethod === 'bank-transfer') {
        // إذا كانت تحويل بنكي، أظهر فقط البنوك
        accountSelect.append('<option value="bank_1">بنك الراجحي</option>');
        accountSelect.append('<option value="bank_2">البنك الأهلي</option>');
        accountSelect.append('<option value="bank_3">بنك البلاد</option>');
    } else if (paymentMethod === 'credit') {
        // إذا كانت دفع آجل، أظهر فقط العملاء
        accountSelect.append('<option value="client_1">العميل - محمد أحمد</option>');
        accountSelect.append('<option value="client_2">العميل - علي سعيد</option>');
        accountSelect.append('<option value="client_3">العميل - خالد عبدالله</option>');
    }
    
    // إعادة تهيئة select2
    accountSelect.trigger('change');
    
    // محاولة استعادة القيمة المحددة سابقاً إذا كانت متوافقة مع الخيارات الجديدة
    if (currentAccount) {
        accountSelect.find('option[value="' + currentAccount + '"]').prop('selected', true).trigger('change');
    }
}

/**
 * تهيئة تحديث رموز العملة
 */
function initializeCurrencySymbols() {
    // تحديث رموز العملة عند تغيير العملة
    $('#currency-type').on('change', function() {
        updateCurrencySymbols($(this).val());
    });
    
    // تحديث رموز العملة عند تحميل الصفحة
    updateCurrencySymbols($('#currency-type').val() || 'SAR');
}

/**
 * تحديث رموز العملة في جميع الحقول المالية
 */
function updateCurrencySymbols(currencyCode) {
    var symbol = getCurrencySymbol(currencyCode);
    $('.currency-symbol').text(symbol);
}

/**
 * الحصول على رمز العملة المناسب
 */
function getCurrencySymbol(currencyCode) {
    switch (currencyCode) {
        case 'USD':
            return '$';
        case 'EUR':
            return '€';
        case 'YER':
            return 'ر.ي';
        case 'SAR':
        default:
            return 'ر.س';
    }
}

/**
 * تهيئة أحداث النقر على الأزرار
 */
function setupButtonEvents() {
    // زر إظهار نموذج الحجز الجديد
    $('#show-booking-form').on('click', function() {
        console.log('عرض نموذج الحجز');
        $('#booking-form-container').fadeIn();
        // تحديث حقل تاريخ ووقت العملية بالتاريخ والوقت الحالي
        setCurrentDateTimeToTransactionDate();
    });
    
    // زر إلغاء/إخفاء نموذج الحجز
    $('#hide-booking-form').on('click', function() {
        console.log('إخفاء نموذج الحجز');
        $('#booking-form-container').fadeOut();
    });
    
    // زر البحث عن الرحلات
    $('#search-trips').on('click', function() {
        console.log('بحث عن الرحلات');
        // في المستقبل: إرسال طلب AJAX للبحث عن الرحلات
        $('#search-results').fadeIn();
    });
    
    // زر اختيار رحلة
    $('.select-trip').on('click', function() {
        console.log('تم اختيار رحلة');
        // في المستقبل: تعبئة بيانات الرحلة تلقائياً
        $('#search-results').hide();
        toastr.success('تم اختيار الرحلة بنجاح');
    });
}

/**
 * تحديث حقل تاريخ ووقت العملية بالتاريخ والوقت الحالي
 */
function setCurrentDateTimeToTransactionDate() {
    // الحصول على تاريخ ووقت اليوم
    var now = moment();
    
    // تنسيق التاريخ حسب التنسيق المطلوب
    var formattedDateTime = now.format('DD MMMM, YYYY');
    
    // تعيين القيمة في حقل تاريخ ووقت العملية
    $('#transaction-date').val(formattedDateTime);
    
    // تحديث datetimepicker لعكس القيمة الجديدة
    $('#transaction-date-picker').datetimepicker('date', now);
}