/**
 * ملف JavaScript لإدارة صفحة حجز تذاكر الباص
 */

$(function () {
    'use strict';
    
    // تهيئة أدوات اختيار التاريخ والوقت
    initializeDateTimePickers();
    
    // تهيئة أدوات Select2
    initializeSelect2();
    
    // مراقبة تغيير نوع الرحلة (ذهاب / ذهاب وعودة)
    $('input[name="tripType"]').on('change', function() {
        if ($(this).val() === 'round-trip') {
            $('.return-date-section').slideDown();
            $('#returnDate').prop('required', true);
        } else {
            $('.return-date-section').slideUp();
            $('#returnDate').prop('required', false);
        }
    });
    
    // البحث عن الرحلات المتاحة
    $('#searchAvailableTrips').on('click', function() {
        // التحقق من صحة البيانات
        if (!validateTripSearchForm()) {
            return;
        }
        
        // عرض قسم الرحلات المتاحة
        $('#availableTripsSection').slideDown();
        $('#seatSelectionSection').hide();
        $('#selectedTripDetails').hide();
        
        // محاكاة البحث عن الرحلات (في حالة التطبيق الحقيقي سيتم استبدالها بطلب AJAX)
        simulateTripsSearch();
    });
    
    // اختيار رحلة من الجدول
    $(document).on('click', '.select-trip', function() {
        // استرجاع بيانات الرحلة المحددة
        const tripId = $(this).data('trip-id');
        const departureTime = $(this).data('departure-time');
        const tripRow = $(this).closest('tr');
        const busType = tripRow.find('td:eq(1)').text();
        const tripDuration = tripRow.find('td:eq(2)').text();
        const price = tripRow.find('td:eq(4)').text();
        
        // تحديث المعلومات لاستخدامها لاحقاً
        $('#ticketPrice').val(price.replace(' ر.س', ''));
        
        // عرض قسم اختيار المقاعد
        $('#seatSelectionSection').slideDown();
        
        // تحديث بيانات الرحلة المحددة
        const fromCity = $('#fromCity option:selected').text();
        const toCity = $('#toCity option:selected').text();
        const tripDate = $('#departureDate').val();
        
        $('#tripFrom').text(fromCity);
        $('#tripTo').text(toCity);
        $('#tripDate').text(tripDate);
        $('#tripTime').text(departureTime);
        $('#tripPrice').text(price);
        
        // إظهار قسم تفاصيل الرحلة المحددة
        $('#selectedTripDetails').slideDown();
        
        // التمرير إلى قسم اختيار المقاعد
        $('html, body').animate({
            scrollTop: $('#seatSelectionSection').offset().top - 100
        }, 500);
    });
    
    // نقر على مقعد في خريطة المقاعد
    $(document).on('click', '.seat:not(.reserved):not(.aisle)', function() {
        const seatId = $(this).data('seat-id');
        
        // تبديل حالة المقعد
        $(this).toggleClass('selected');
        
        // تحديث حقل المقاعد المحددة
        updateSelectedSeats();
    });
    
    // زر الانتقال بين الخطوات
    $('.next-step').on('click', function() {
        const nextSection = $(this).data('next');
        $(`.section:visible`).hide();
        $(`#${nextSection}`).show();
        
        // التمرير إلى الخطوة الجديدة
        $('html, body').animate({
            scrollTop: $(`#${nextSection}`).offset().top - 100
        }, 500);
    });
    
    $('.prev-step').on('click', function() {
        const prevSection = $(this).data('prev');
        $(`.section:visible`).hide();
        $(`#${prevSection}`).show();
        
        // التمرير إلى الخطوة السابقة
        $('html, body').animate({
            scrollTop: $(`#${prevSection}`).offset().top - 100
        }, 500);
    });
    
    // تحديث قائمة الحسابات بناءً على نوع التوصيل
    $('#paymentType').on('change', function() {
        // إعادة تعيين الحقول
        $('#cash-fields').hide();
        $('#cashAmount, #receiptNumber').prop('required', false);
        
        // تحديث قائمة الحسابات المالية حسب نوع التوصيل
        var accountSelect = $('#account');
        accountSelect.empty(); // مسح الخيارات السابقة
        accountSelect.append('<option value="">اختر الحساب المالي</option>');
        
        // إظهار الحقول المناسبة حسب نوع التوصيل
        switch ($(this).val()) {
            case 'cash':
                // إظهار حقول الصندوق
                $('#cash-fields').show();
                $('#cashAmount, #receiptNumber').prop('required', true);
                
                // إضافة حسابات الصندوق
                accountSelect.append('<option value="101">الصندوق الرئيسي</option>');
                accountSelect.append('<option value="102">صندوق المبيعات</option>');
                accountSelect.append('<option value="103">الصندوق النثري</option>');
                break;
                
            case 'credit':
                // إضافة حسابات العملاء
                accountSelect.append('<option value="201">محمد أحمد عبدالله</option>');
                accountSelect.append('<option value="202">خالد محمد السيد</option>');
                accountSelect.append('<option value="203">عبدالله ناصر العتيبي</option>');
                accountSelect.append('<option value="204">فهد سعد الغامدي</option>');
                accountSelect.append('<option value="205">علي حسن الشمري</option>');
                break;
                
            case 'transfer':
            case 'bank':
                // إضافة حسابات البنوك
                accountSelect.append('<option value="301">بنك الراجحي</option>');
                accountSelect.append('<option value="302">البنك الأهلي السعودي</option>');
                accountSelect.append('<option value="303">بنك الإنماء</option>');
                accountSelect.append('<option value="304">بنك سامبا</option>');
                accountSelect.append('<option value="305">بنك الرياض</option>');
                break;
        }
        
        // تحديث قائمة Select2
        accountSelect.trigger('change');
    });
    
    // تنفيذ التغيير الأولي لتحديث القائمة حسب القيمة الافتراضية عند تحميل الصفحة
    $('#paymentType').trigger('change');
    
    // إكمال الحجز
    $('#complete-reservation').on('click', function() {
        // التحقق من صحة النموذج بالكامل
        if (!validateCompleteForm()) {
            return;
        }
        
        // بدء العملية
        showFormProcessing();
        
        // جمع البيانات من النموذج
        var formData = {
            passengerName: $('#passengerName').val(),
            mobileNumber: $('#mobileNumber').val(),
            birthPlace: $('#birthPlace').val(),
            birthDate: $('#birthDate').val(),
            gender: $('#gender').val(),
            idType: $('#idType').val(),
            idNumber: $('#idNumber').val(),
            nationality: $('#nationality').val(),
            issueDate: $('#issueDate').val(),
            issuePlace: $('#issuePlace').val(),
            busType: $('input[name="busType"]:checked').val(),
            departureCity: $('#departureCity').val(),
            destinationCity: $('#destinationCity').val(),
            transportCompany: $('#transportCompany').val(),
            tripType: $('#tripType').val(),
            reservationDate: $('#reservationDate').val(),
            purpose: $('#purpose').val(),
            notes: $('#notes').val(),
            transactionDate: $('#transactionDate').val(),
            paymentType: $('#paymentType').val(),
            sellPrice: $('#sellPrice').val(),
            receivedAmount: $('#receivedAmount').val(),
            remainingAmount: $('#remainingAmount').val(),
            accountId: $('#accountId').val(),
            statement: $('#statement').val(),
            supplierId: $('#supplierId').val(),
            purchasePrice: $('#purchasePrice').val()
        };
        
        // إرسال البيانات إلى الخادم باستخدام AJAX
        $.ajax({
            type: 'POST',
            url: '/api/create-bus-booking',
            data: formData,
            success: function(response) {
                hideFormProcessing();
                if (response.success) {
                    // نجاح عملية الحفظ
                    showBookingConfirmation(response.booking_number);
                    
                    // إعادة تحميل الصفحة بعد 2 ثانية لتحديث قائمة الحجوزات
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                } else {
                    // فشل عملية الحفظ
                    Swal.fire({
                        icon: 'error',
                        title: 'خطأ!',
                        text: 'حدث خطأ أثناء حفظ الحجز: ' + response.error,
                        confirmButtonText: 'حسناً'
                    });
                }
            },
            error: function(xhr, status, error) {
                hideFormProcessing();
                Swal.fire({
                    icon: 'error',
                    title: 'خطأ!',
                    text: 'حدث خطأ في الاتصال بالخادم. يرجى المحاولة مرة أخرى.',
                    confirmButtonText: 'حسناً'
                });
                console.error(error);
            }
        });
    });
});

/**
 * تهيئة أدوات اختيار التاريخ والوقت
 */
function initializeDateTimePickers() {
    // تاريخ السفر
    $('#departureDatePicker').datetimepicker({
        format: 'DD/MM/YYYY',
        useCurrent: false,
        locale: 'ar',
        minDate: moment().startOf('day'),
        icons: {
            time: 'far fa-clock',
            date: 'far fa-calendar',
            up: 'fas fa-arrow-up',
            down: 'fas fa-arrow-down',
            previous: 'fas fa-chevron-right',
            next: 'fas fa-chevron-left',
            today: 'fas fa-calendar-check',
            clear: 'far fa-trash-alt',
            close: 'far fa-times-circle'
        }
    });
    
    // تاريخ العودة
    $('#returnDatePicker').datetimepicker({
        format: 'DD/MM/YYYY',
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
            close: 'far fa-times-circle'
        }
    });
    
    // ضمان أن تاريخ العودة لا يكون قبل تاريخ السفر
    $("#departureDatePicker").on("change.datetimepicker", function (e) {
        $('#returnDatePicker').datetimepicker('minDate', e.date);
    });
    
    $("#returnDatePicker").on("change.datetimepicker", function (e) {
        $('#departureDatePicker').datetimepicker('maxDate', e.date);
    });
    
    // وقت السفر وباقي حقول التاريخ والوقت
    $('#departureTimePicker').datetimepicker({
        format: 'HH:mm',
        stepping: 15,
        locale: 'ar',
        icons: {
            time: 'far fa-clock',
            up: 'fas fa-arrow-up',
            down: 'fas fa-arrow-down',
            previous: 'fas fa-chevron-right',
            next: 'fas fa-chevron-left'
        }
    });
    
    // محدد التاريخ والوقت للعمليات
    $('#transactionDateTimePicker').datetimepicker({
        format: 'DD/MM/YYYY HH:mm',
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
            close: 'far fa-times-circle'
        }
    });
    
    // تواريخ الهوية
    $('#idIssueDatePicker, #idExpiryDatePicker, #birthDatePicker').datetimepicker({
        format: 'DD/MM/YYYY',
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
            close: 'far fa-times-circle'
        }
    });
}

/**
 * تهيئة أدوات Select2
 */
function initializeSelect2() {
    $('#fromCity, #toCity, #nationality, #idType, #currency, #paymentType, #supplierId, #account').select2({
        dir: "rtl",
        language: "ar",
        width: '100%'
    });
}

/**
 * التحقق من صحة نموذج البحث عن الرحلات
 */
function validateTripSearchForm() {
    let valid = true;
    const fromCity = $('#fromCity').val();
    const toCity = $('#toCity').val();
    const departureDate = $('#departureDate').val();
    const returnDate = $('#returnDate').val();
    const tripType = $('input[name="tripType"]:checked').val();
    
    // التحقق من المدينة المنطلق منها
    if (!fromCity) {
        showFieldError('#fromCity', 'يرجى اختيار مدينة المغادرة');
        valid = false;
    } else {
        clearFieldError('#fromCity');
    }
    
    // التحقق من المدينة المقصودة
    if (!toCity) {
        showFieldError('#toCity', 'يرجى اختيار مدينة الوصول');
        valid = false;
    } else if (fromCity === toCity) {
        showFieldError('#toCity', 'يجب أن تكون مدينة الوصول مختلفة عن مدينة المغادرة');
        valid = false;
    } else {
        clearFieldError('#toCity');
    }
    
    // التحقق من تاريخ السفر
    if (!departureDate) {
        showFieldError('#departureDate', 'يرجى اختيار تاريخ السفر');
        valid = false;
    } else {
        clearFieldError('#departureDate');
    }
    
    // التحقق من تاريخ العودة (في حالة الذهاب والعودة)
    if (tripType === 'round-trip' && !returnDate) {
        showFieldError('#returnDate', 'يرجى اختيار تاريخ العودة');
        valid = false;
    } else {
        clearFieldError('#returnDate');
    }
    
    return valid;
}

/**
 * التحقق من صحة النموذج الكامل
 */
function validateCompleteForm() {
    // هنا يتم التحقق من كافة حقول النموذج
    // لتبسيط الشيفرة تم استبعاد التحقق التفصيلي
    
    const requiredFields = [
        '#passengerName',
        '#phoneNumber',
        '#idType',
        '#idNumber',
        '#nationality',
        '#ticketPrice',
        '#paymentType',
        '#transactionDateTime',
        '#supplierId',
        '#purchasePrice'
    ];
    
    let valid = true;
    
    // التحقق من الحقول المطلوبة
    requiredFields.forEach(field => {
        if (!$(field).val()) {
            showFieldError(field, 'هذا الحقل مطلوب');
            valid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // التحقق من المقاعد المحددة
    if ($('.seat.selected').length === 0) {
        alert('يرجى اختيار مقعد واحد على الأقل');
        valid = false;
    }
    
    return valid;
}

/**
 * عرض رسالة خطأ على حقل معين
 */
function showFieldError(fieldSelector, message) {
    const field = $(fieldSelector);
    field.addClass('is-invalid');
    
    // التحقق من وجود رسالة خطأ سابقة
    if (field.next('.invalid-feedback').length === 0) {
        field.after(`<div class="invalid-feedback">${message}</div>`);
    } else {
        field.next('.invalid-feedback').text(message);
    }
}

/**
 * إزالة رسالة الخطأ من حقل
 */
function clearFieldError(fieldSelector) {
    const field = $(fieldSelector);
    field.removeClass('is-invalid');
}

/**
 * محاكاة البحث عن الرحلات المتاحة
 */
function simulateTripsSearch() {
    // محاكاة بسيطة للبحث
    // في التطبيق الحقيقي سيتم استبدال هذا بطلب AJAX لاسترجاع الرحلات المتاحة
    
    // عرض رسالة التحميل
    $('#availableTripsSection').html('<div class="text-center my-4"><i class="fas fa-spinner fa-spin fa-3x"></i><p class="mt-2">جاري البحث عن الرحلات المتاحة...</p></div>');
    
    // محاكاة تأخير الشبكة
    setTimeout(function() {
        // إعادة عرض قسم الرحلات المتاحة
        $('#availableTripsSection').html(`
            <hr>
            <h5 class="text-primary mb-3">
                <i class="fas fa-list ml-1"></i>
                الرحلات المتاحة
            </h5>
            
            <div class="table-responsive">
                <table class="table table-hover table-bordered" id="availableTripsTable">
                    <thead class="thead-light">
                        <tr>
                            <th>وقت المغادرة</th>
                            <th>نوع الباص</th>
                            <th>مدة الرحلة</th>
                            <th>المقاعد المتاحة</th>
                            <th>السعر</th>
                            <th>اختيار</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>08:30 صباحاً</td>
                            <td>سياحي (VIP)</td>
                            <td>5 ساعات</td>
                            <td>23 مقعد</td>
                            <td>200 ر.س</td>
                            <td>
                                <button type="button" class="btn btn-primary btn-sm select-trip" data-trip-id="1" data-departure-time="08:30 صباحاً">
                                    <i class="fas fa-check"></i> اختيار
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td>10:00 صباحاً</td>
                            <td>عادي</td>
                            <td>5.5 ساعات</td>
                            <td>12 مقعد</td>
                            <td>150 ر.س</td>
                            <td>
                                <button type="button" class="btn btn-primary btn-sm select-trip" data-trip-id="2" data-departure-time="10:00 صباحاً">
                                    <i class="fas fa-check"></i> اختيار
                                </button>
                            </td>
                        </tr>
                        <tr>
                            <td>12:30 ظهراً</td>
                            <td>سياحي (VIP)</td>
                            <td>5 ساعات</td>
                            <td>32 مقعد</td>
                            <td>200 ر.س</td>
                            <td>
                                <button type="button" class="btn btn-primary btn-sm select-trip" data-trip-id="3" data-departure-time="12:30 ظهراً">
                                    <i class="fas fa-check"></i> اختيار
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `);
    }, 1000);
}

/**
 * تحديث قائمة المقاعد المحددة
 */
function updateSelectedSeats() {
    const selectedSeats = [];
    $('.seat.selected').each(function() {
        selectedSeats.push($(this).data('seat-id'));
    });
    
    if (selectedSeats.length > 0) {
        $('#selectedSeats').val(selectedSeats.join(', '));
        $('#tripSeat').text(selectedSeats.join(', '));
    } else {
        $('#selectedSeats').val('');
        $('#tripSeat').text('لم يتم الاختيار');
    }
}

/**
 * عرض مؤشر معالجة النموذج
 */
function showFormProcessing() {
    $('button').prop('disabled', true);
    $('#complete-reservation').html('<i class="fas fa-spinner fa-spin ml-2"></i> جاري الحفظ...');
}

/**
 * إخفاء مؤشر معالجة النموذج
 */
function hideFormProcessing() {
    $('button').prop('disabled', false);
    $('#complete-reservation').html('حفظ الحجز');
}

/**
 * عرض تأكيد الحجز
 */
function showBookingConfirmation() {
    // إغلاق النافذة المنبثقة
    $('#modal-add-reservation').modal('hide');
    
    // إظهار رسالة التأكيد
    Swal.fire({
        title: 'تم الحجز بنجاح!',
        text: 'تم حفظ حجز تذكرة الباص بنجاح',
        icon: 'success',
        confirmButtonText: 'تم'
    }).then((result) => {
        // إعادة تحميل الصفحة بعد التأكيد
        location.reload();
    });
}