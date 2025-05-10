/**
 * ملف JavaScript محسن لإدارة حجوزات الباص
 * يتضمن تحسينات للتفاعل بين الحقول والتحقق من البيانات وإنشاء القيود المحاسبية
 */

$(function () {
    'use strict';
    
    // ===== 1. تحسين التفاعل بين الحقول =====
    
    // تحديث قائمة الحسابات عند تغيير طريقة الدفع
    $('#paymentType').on('change', function() {
        updateAccountOptions();
    });
    
    // تغيير حقول القيم المالية عند تغيير سعر البيع أو سعر التكلفة
    $('#sellPrice, #purchasePrice').on('input', function() {
        validatePrices();
        calculateProfit();
    });
    
    // تحديث المبلغ المتبقي عند تغيير المبلغ المستلم
    $('#receivedAmount').on('input', function() {
        validateReceivedAmount();
        calculateRemainingAmount();
    });
    
    // تحديث البيان عند تغيير البيانات المتعلقة
    $('#departureCity, #destinationCity, #passengerName, #supplierId').on('change', function() {
        updateStatement();
    });
    
    // تفعيل التحقق من البيانات عند محاولة الحفظ
    $('#complete-reservation').on('click', function(e) {
        e.preventDefault();
        
        if (validateAllFields()) {
            createTransactionAndSave();
        }
    });
    
    // ===== 2. وظائف التحقق من البيانات =====
    
    // التحقق من جميع الحقول
    function validateAllFields() {
        // مسح جميع الأخطاء السابقة
        clearAllErrors();
        
        let isValid = true;
        
        // التحقق من الحقول المطلوبة
        const requiredFields = [
            { id: 'passengerName', message: 'يرجى إدخال اسم المسافر' },
            { id: 'mobileNumber', message: 'يرجى إدخال رقم الجوال' },
            { id: 'departureCity', message: 'يرجى اختيار مدينة المغادرة' },
            { id: 'destinationCity', message: 'يرجى اختيار مدينة الوصول' },
            { id: 'reservationDate', message: 'يرجى تحديد تاريخ الحجز' },
            { id: 'supplierId', message: 'يرجى اختيار مزود الخدمة' },
            { id: 'sellPrice', message: 'يرجى إدخال سعر البيع' },
            { id: 'purchasePrice', message: 'يرجى إدخال سعر التكلفة' },
            { id: 'paymentType', message: 'يرجى اختيار طريقة الدفع' },
            { id: 'accountId', message: 'يرجى اختيار الحساب' }
        ];
        
        // التحقق من كل حقل مطلوب
        requiredFields.forEach(field => {
            if (!$('#' + field.id).val()) {
                showFieldError('#' + field.id, field.message);
                isValid = false;
            }
        });
        
        // التحقق من الحقول الإضافية حسب نوع الرحلة
        if ($('#journeyTypeRoundTrip').is(':checked') && !$('#returnDate').val()) {
            showFieldError('#returnDate', 'يرجى تحديد تاريخ العودة للرحلة ذهاب وعودة');
            isValid = false;
        }
        
        // التحقق من الأسعار
        if (!validatePrices()) {
            isValid = false;
        }
        
        // التحقق من المبلغ المستلم
        if ($('#paymentType').val() === 'cash' && !validateReceivedAmount()) {
            isValid = false;
        }
        
        return isValid;
    }
    
    // التحقق من الأسعار
    function validatePrices() {
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;
        const purchasePrice = parseFloat($('#purchasePrice').val()) || 0;
        let isValid = true;
        
        // التحقق من سعر البيع
        if (sellPrice <= 0) {
            showFieldError('#sellPrice', 'يجب أن يكون سعر البيع أكبر من صفر');
            isValid = false;
        } else {
            clearFieldError('#sellPrice');
        }
        
        // التحقق من العلاقة بين سعر التكلفة وسعر البيع
        if (purchasePrice > sellPrice) {
            showFieldError('#purchasePrice', 'سعر التكلفة أكبر من سعر البيع! تأكد من صحة الأسعار');
            isValid = false;
        } else {
            clearFieldError('#purchasePrice');
        }
        
        return isValid;
    }
    
    // التحقق من المبلغ المستلم
    function validateReceivedAmount() {
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;
        const receivedAmount = parseFloat($('#receivedAmount').val()) || 0;
        let isValid = true;
        
        // التحقق من أن المبلغ المستلم لا يتجاوز المبلغ المتبقي
        if (receivedAmount > sellPrice) {
            showFieldError('#receivedAmount', 'المبلغ المستلم أكبر من سعر البيع! تأكد من صحة القيمة');
            isValid = false;
        } else {
            clearFieldError('#receivedAmount');
        }
        
        return isValid;
    }
    
    // عرض رسالة خطأ على حقل معين
    function showFieldError(selector, message) {
        $(selector).addClass('is-invalid');
        
        // التحقق من وجود رسالة خطأ سابقة
        if ($(selector).next('.invalid-feedback').length === 0) {
            $(selector).after('<div class="invalid-feedback">' + message + '</div>');
        } else {
            $(selector).next('.invalid-feedback').text(message);
        }
    }
    
    // إزالة رسالة الخطأ من حقل
    function clearFieldError(selector) {
        $(selector).removeClass('is-invalid');
    }
    
    // مسح جميع رسائل الخطأ
    function clearAllErrors() {
        $('.is-invalid').removeClass('is-invalid');
    }
    
    // ===== 3. وظائف الحسابات المالية =====
    
    // حساب هامش الربح
    function calculateProfit() {
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;
        const purchasePrice = parseFloat($('#purchasePrice').val()) || 0;
        const profitAmount = sellPrice - purchasePrice;
        
        // تحديث قيمة الربح
        if (!isNaN(profitAmount)) {
            const profitPercentage = sellPrice > 0 ? ((profitAmount / sellPrice) * 100).toFixed(1) : 0;
            
            // عرض معلومات هامش الربح
            if ($('#profitInfo').length === 0) {
                $('#sellPrice').after('<div id="profitInfo" class="small text-muted mt-1"></div>');
            }
            
            // تحديث نص معلومات الربح
            if (profitAmount >= 0) {
                $('#profitInfo').html(`هامش الربح: <span class="text-success">${profitAmount.toFixed(2)} (${profitPercentage}%)</span>`);
            } else {
                $('#profitInfo').html(`خسارة: <span class="text-danger">${Math.abs(profitAmount).toFixed(2)} (${profitPercentage}%)</span>`);
            }
        }
    }
    
    // حساب المبلغ المتبقي
    function calculateRemainingAmount() {
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;
        const receivedAmount = parseFloat($('#receivedAmount').val()) || 0;
        const remainingAmount = sellPrice - receivedAmount;
        
        // تحديث حقل المبلغ المتبقي
        $('#remainingAmount').val(remainingAmount >= 0 ? remainingAmount.toFixed(2) : 0);
        
        // تحديث المبلغ بالكلمات
        if ($('#remainingAmountInWords').length === 0) {
            $('#remainingAmount').after('<div id="remainingAmountInWords" class="amount-in-words"></div>');
        }
        
        const currencyText = getCurrencyText();
        $('#remainingAmountInWords').text(convertNumberToArabicWords(remainingAmount) + ' ' + currencyText);
    }
    
    // ===== 4. وظائف التحديث الديناميكي للحقول =====
    
    // تحديث خيارات الحسابات بناءً على طريقة الدفع
    function updateAccountOptions() {
        const paymentType = $('#paymentType').val();
        const accountSelect = $('#accountId');
        
        // حذف الخيارات الحالية
        accountSelect.empty().append('<option value="">اختر الحساب المالي</option>');
        
        // إضافة خيارات جديدة حسب نوع الدفع
        if (paymentType === 'cash') {
            accountSelect.append('<option value="cash_1">صندوق الشركة الرئيسي</option>');
            accountSelect.append('<option value="cash_2">صندوق الفرع 1</option>');
            accountSelect.append('<option value="cash_3">صندوق الفرع 2</option>');
            $('#receivedAmountContainer').slideDown();
            $('#remainingAmountContainer').show();
        } 
        else if (paymentType === 'credit') {
            accountSelect.append('<option value="client_1">حساب العملاء العام</option>');
            accountSelect.append('<option value="client_2">عملاء الشركات</option>');
            accountSelect.append('<option value="client_3">عملاء VIP</option>');
            $('#receivedAmountContainer').slideUp();
            $('#receivedAmount').val('0');
            $('#remainingAmountContainer').show();
            // تحديث المبلغ المتبقي ليساوي كامل سعر البيع
            const sellPrice = parseFloat($('#sellPrice').val()) || 0;
            $('#remainingAmount').val(sellPrice.toFixed(2));
        } 
        else if (paymentType === 'bank_transfer') {
            accountSelect.append('<option value="bank_1">بنك الراجحي</option>');
            accountSelect.append('<option value="bank_2">البنك الأهلي</option>');
            accountSelect.append('<option value="bank_3">بنك الإنماء</option>');
            $('#receivedAmountContainer').slideDown();
            $('#remainingAmountContainer').show();
        }
        
        // تحديث قائمة Select2
        accountSelect.trigger('change');
        
        // تحديث المبلغ المتبقي بعد التغيير
        calculateRemainingAmount();
    }
    
    // توليد البيان التلقائي
    function updateStatement() {
        const departureCity = $('#departureCity option:selected').text() || $('#departureCity').val();
        const destinationCity = $('#destinationCity option:selected').text() || $('#destinationCity').val();
        const passengerName = $('#passengerName').val();
        const supplier = $('#supplierId option:selected').text() || 'المورد';
        
        if (departureCity && destinationCity && passengerName) {
            const statement = `حجز تذكرة باص من ${departureCity} إلى ${destinationCity} للمسافر ${passengerName} مع ${supplier}`;
            $('#statement').val(statement);
        }
    }
    
    // ===== 5. وظائف إنشاء القيود المحاسبية والحفظ =====
    
    // إنشاء القيود المحاسبية وحفظ الحجز
    function createTransactionAndSave() {
        // عرض مؤشر التحميل
        $('#complete-reservation').prop('disabled', true).html('<i class="fas fa-spinner fa-spin ml-1"></i> جاري الحفظ...');
        
        // جمع البيانات من النموذج
        const formData = new FormData($('#bus-booking-form')[0]);
        
        // إضافة معلومات القيد المحاسبي
        const journalEntryData = prepareJournalEntryData();
        for (const key in journalEntryData) {
            formData.append(key, journalEntryData[key]);
        }
        
        // إرسال البيانات للخادم
        $.ajax({
            type: 'POST',
            url: '/api/create-bus-booking',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    // نجاح الحفظ
                    Swal.fire({
                        icon: 'success',
                        title: 'تم الحفظ بنجاح',
                        text: 'تم حفظ الحجز وإنشاء القيود المحاسبية المرتبطة به',
                        confirmButtonText: 'تم'
                    }).then(function() {
                        // مسح البيانات المحفوظة بعد نجاح الحجز
                        sessionStorage.removeItem('busBookingSellPrice');
                        sessionStorage.removeItem('busBookingPurchasePrice');
                        sessionStorage.removeItem('busBookingReceivedAmount');
                        sessionStorage.removeItem('busBookingCurrency');
                        
                        window.location.href = '/bus-tickets';
                    });
                } else {
                    // فشل الحفظ
                    Swal.fire({
                        icon: 'error',
                        title: 'خطأ!',
                        text: response.error || 'حدث خطأ أثناء حفظ الحجز',
                        confirmButtonText: 'حسناً'
                    });
                    $('#complete-reservation').prop('disabled', false).html('<i class="fas fa-save ml-1"></i> حفظ الحجز');
                }
            },
            error: function(xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'خطأ!',
                    text: 'حدث خطأ في الاتصال بالخادم. يرجى المحاولة مرة أخرى.',
                    confirmButtonText: 'حسناً'
                });
                $('#complete-reservation').prop('disabled', false).html('<i class="fas fa-save ml-1"></i> حفظ الحجز');
                console.error(error);
            }
        });
    }
    
    // تحضير بيانات القيد المحاسبي
    function prepareJournalEntryData() {
        const paymentType = $('#paymentType').val();
        const sellPrice = parseFloat($('#sellPrice').val()) || 0;
        const purchasePrice = parseFloat($('#purchasePrice').val()) || 0;
        const receivedAmount = parseFloat($('#receivedAmount').val()) || 0;
        const remainingAmount = parseFloat($('#remainingAmount').val()) || 0;
        const statement = $('#statement').val();
        const accountId = $('#accountId').val();
        const supplierId = $('#supplierId').val();
        
        // معلومات القيد
        const journalData = {
            'journal_entry_description': statement,
            'journal_entry_type': 'bus_booking'
        };
        
        // إضافة بنود القيد حسب نوع الدفع
        if (paymentType === 'cash') {
            // 1. قيد لتسجيل المبيعات
            if (receivedAmount > 0) {
                journalData['journal_accounts'] = JSON.stringify([
                    { account_id: accountId, description: 'استلام قيمة حجز تذكرة باص', debit_amount: receivedAmount, credit_amount: 0 },
                    { account_id: 'revenue_account', description: 'إيراد حجز تذكرة باص', debit_amount: 0, credit_amount: receivedAmount }
                ]);
            }
            
            // 2. قيد إضافي إذا كان المبلغ المتبقي أكبر من الصفر
            if (remainingAmount > 0) {
                journalData['journal_accounts_remaining'] = JSON.stringify([
                    { account_id: 'receivables_account', description: 'ذمم مدينة - قيمة متبقية لحجز تذكرة باص', debit_amount: remainingAmount, credit_amount: 0 },
                    { account_id: 'revenue_account', description: 'إيراد حجز تذكرة باص - رصيد متبقي', debit_amount: 0, credit_amount: remainingAmount }
                ]);
            }
        } 
        else if (paymentType === 'credit') {
            // قيد مبلغ آجل على الحساب
            journalData['journal_accounts'] = JSON.stringify([
                { account_id: accountId, description: 'ذمم مدينة - حجز تذكرة باص', debit_amount: sellPrice, credit_amount: 0 },
                { account_id: 'revenue_account', description: 'إيراد حجز تذكرة باص', debit_amount: 0, credit_amount: sellPrice }
            ]);
        } 
        else if (paymentType === 'bank_transfer') {
            // 1. قيد لتسجيل المبيعات عبر التحويل البنكي
            if (receivedAmount > 0) {
                journalData['journal_accounts'] = JSON.stringify([
                    { account_id: accountId, description: 'استلام قيمة حجز تذكرة باص عبر تحويل بنكي', debit_amount: receivedAmount, credit_amount: 0 },
                    { account_id: 'revenue_account', description: 'إيراد حجز تذكرة باص', debit_amount: 0, credit_amount: receivedAmount }
                ]);
            }
            
            // 2. قيد إضافي إذا كان المبلغ المتبقي أكبر من الصفر
            if (remainingAmount > 0) {
                journalData['journal_accounts_remaining'] = JSON.stringify([
                    { account_id: 'receivables_account', description: 'ذمم مدينة - قيمة متبقية لحجز تذكرة باص', debit_amount: remainingAmount, credit_amount: 0 },
                    { account_id: 'revenue_account', description: 'إيراد حجز تذكرة باص - رصيد متبقي', debit_amount: 0, credit_amount: remainingAmount }
                ]);
            }
        }
        
        // 3. قيد لتسجيل تكلفة بضاعة مباعة إذا كان هناك سعر تكلفة
        if (purchasePrice > 0) {
            journalData['journal_accounts_cost'] = JSON.stringify([
                { account_id: 'cogs_account', description: 'تكلفة خدمات حجز تذكرة باص', debit_amount: purchasePrice, credit_amount: 0 },
                { account_id: supplierId, description: 'ذمم دائنة - مزود خدمة حجز باص', debit_amount: 0, credit_amount: purchasePrice }
            ]);
        }
        
        return journalData;
    }
    
    // ===== 6. وظائف مساعدة =====
    
    // الحصول على نص العملة
    function getCurrencyText() {
        const currencyCode = $('#currency').val() || 'SAR';
        let currencyText = 'ريال سعودي';
        
        if (currencyCode === 'USD') currencyText = 'دولار أمريكي';
        else if (currencyCode === 'EUR') currencyText = 'يورو';
        else if (currencyCode === 'YER') currencyText = 'ريال يمني';
        
        return currencyText;
    }
    
    // ===== 7. تهيئة الصفحة =====
    
    // تنفيذ العمليات المطلوبة عند تحميل الصفحة
    function initPage() {
        // التأكد من تحديث خيارات الحساب بناءً على طريقة الدفع الابتدائية
        updateAccountOptions();
        
        // تحديث المبالغ المالية والعبارات الوصفية
        validatePrices();
        calculateProfit();
        calculateRemainingAmount();
        updateStatement();
        
        console.log('تم تهيئة الصفحة بنجاح مع التحسينات المطلوبة');
    }
    
    // بدء تهيئة الصفحة
    initPage();
});

// وظيفة تحويل الرقم إلى كلمات عربية
function convertNumberToArabicWords(number) {
    // هذه وظيفة مبسطة للتحويل، يمكن استبدالها بمكتبة أكثر تطورًا
    if (number == 0) return "صفر";
    
    const arabicOnes = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة"];
    const arabicTens = ["", "عشر", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"];
    const arabicHundreds = ["", "مائة", "مئتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"];
    const arabicThousands = ["", "ألف", "ألفان", "ثلاثة آلاف", "أربعة آلاف", "خمسة آلاف", "ستة آلاف", "سبعة آلاف", "ثمانية آلاف", "تسعة آلاف"];
    
    // تقريب الرقم لأقرب رقمين عشريين
    number = Math.round(number * 100) / 100;
    
    // فصل الجزء الصحيح والعشري
    const parts = number.toString().split('.');
    const integerPart = parseInt(parts[0]);
    const decimalPart = parts.length > 1 ? parseInt(parts[1].padEnd(2, '0').substring(0, 2)) : 0;
    
    // تحويل الجزء الصحيح
    let result = "";
    if (integerPart < 11) {
        result = arabicOnes[integerPart];
    } else if (integerPart < 100) {
        const ones = integerPart % 10;
        const tens = Math.floor(integerPart / 10);
        if (ones === 0) {
            result = arabicTens[tens];
        } else {
            result = arabicOnes[ones] + " و" + arabicTens[tens];
        }
    } else if (integerPart < 1000) {
        const hundreds = Math.floor(integerPart / 100);
        const remainder = integerPart % 100;
        if (remainder === 0) {
            result = arabicHundreds[hundreds];
        } else if (remainder < 11) {
            result = arabicHundreds[hundreds] + " و" + arabicOnes[remainder];
        } else {
            const ones = remainder % 10;
            const tens = Math.floor(remainder / 10);
            if (ones === 0) {
                result = arabicHundreds[hundreds] + " و" + arabicTens[tens];
            } else {
                result = arabicHundreds[hundreds] + " و" + arabicOnes[ones] + " و" + arabicTens[tens];
            }
        }
    } else if (integerPart < 10000) {
        const thousands = Math.floor(integerPart / 1000);
        const remainder = integerPart % 1000;
        if (remainder === 0) {
            result = arabicThousands[thousands];
        } else {
            let remainderText = "";
            if (remainder < 11) {
                remainderText = arabicOnes[remainder];
            } else if (remainder < 100) {
                const ones = remainder % 10;
                const tens = Math.floor(remainder / 10);
                if (ones === 0) {
                    remainderText = arabicTens[tens];
                } else {
                    remainderText = arabicOnes[ones] + " و" + arabicTens[tens];
                }
            } else {
                const hundreds = Math.floor(remainder / 100);
                const subRemainder = remainder % 100;
                if (subRemainder === 0) {
                    remainderText = arabicHundreds[hundreds];
                } else if (subRemainder < 11) {
                    remainderText = arabicHundreds[hundreds] + " و" + arabicOnes[subRemainder];
                } else {
                    const ones = subRemainder % 10;
                    const tens = Math.floor(subRemainder / 10);
                    if (ones === 0) {
                        remainderText = arabicHundreds[hundreds] + " و" + arabicTens[tens];
                    } else {
                        remainderText = arabicHundreds[hundreds] + " و" + arabicOnes[ones] + " و" + arabicTens[tens];
                    }
                }
            }
            result = arabicThousands[thousands] + " و" + remainderText;
        }
    } else {
        result = "أكثر من عشرة آلاف";
    }
    
    // إضافة الجزء العشري إذا وجد
    if (decimalPart > 0) {
        let decimalText = "";
        if (decimalPart < 11) {
            decimalText = arabicOnes[decimalPart];
        } else if (decimalPart < 100) {
            const ones = decimalPart % 10;
            const tens = Math.floor(decimalPart / 10);
            if (ones === 0) {
                decimalText = arabicTens[tens];
            } else {
                decimalText = arabicOnes[ones] + " و" + arabicTens[tens];
            }
        }
        result += " و" + decimalText + " هللة";
    }
    
    return result || "صفر";
}