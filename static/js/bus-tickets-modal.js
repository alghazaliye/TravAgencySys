/**
 * ملف JavaScript لإدارة نموذج حجز تذاكر الباص في النافذة المنبثقة (Modal)
 */

$(function () {
    // تهيئة أدوات اختيار التاريخ
    $('#trip-date').datetimepicker({
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

    // تهيئة حقول select2
    $('.select2').select2({
        theme: 'bootstrap4',
        language: 'ar',
        dir: 'rtl'
    });

    // محاكاة البحث عن الرحلات
    $('#search-trips').on('click', function() {
        // التحقق من صحة نموذج البحث
        if (!validateTripSearchForm()) {
            return false;
        }

        // إظهار مؤشر التحميل
        showFormProcessing();

        // محاكاة عملية البحث (ستظهر النتائج بعد ثانية واحدة)
        setTimeout(function() {
            hideFormProcessing();
            
            // إظهار نتائج البحث
            $('#search-results').slideDown();
            
            // إظهار زر متابعة الحجز
            $('#continue-to-booking').hide();
            $('#back-to-search').hide();
            
            // إخفاء نموذج الحجز (في حالة كان ظاهراً)
            $('#booking-form-container').hide();
            $('#seat-map-container').hide();
        }, 1000);
    });

    // عند اختيار رحلة
    $('.select-trip').on('click', function() {
        let row = $(this).closest('tr');
        let company = row.find('td:eq(0)').text();
        let from = row.find('td:eq(1)').text();
        let to = row.find('td:eq(2)').text();
        let departureTime = row.find('td:eq(3)').text();
        let busType = row.find('td:eq(5)').text();
        let price = row.find('td:eq(6)').text().replace(' ر.س', '');
        
        // عرض تفاصيل الرحلة
        $('#trip-details-text').text(`من ${from} إلى ${to} - ${departureTime} - ${company} - ${busType}`);
        $('#ticket-price').val(price);
        
        // إخفاء نتائج البحث
        $('#search-results').hide();
        
        // إظهار نموذج الحجز
        $('#booking-form-container').slideDown();
        
        // تغيير أزرار التنقل في القدم
        $('#continue-to-booking').hide();
        $('#complete-booking').show();
        $('#back-to-search').show();
    });

    // العودة للبحث
    $('#back-to-search').on('click', function() {
        $('#booking-form-container').hide();
        $('#seat-map-container').hide();
        $('#search-results').slideDown();
        
        // تغيير الأزرار
        $('#complete-booking').hide();
        $('#back-to-search').hide();
    });

    // اختيار المقعد
    $('#select-seat').on('click', function() {
        $('#booking-form-container').hide();
        $('#seat-map-container').slideDown();
        
        // تغيير الأزرار
        $('#complete-booking').hide();
        $('#back-to-search').hide();
    });

    // إلغاء اختيار المقعد
    $('#cancel-seat-selection').on('click', function() {
        $('#seat-map-container').hide();
        $('#booking-form-container').slideDown();
        
        // تغيير الأزرار
        $('#complete-booking').show();
        $('#back-to-search').show();
    });

    // تأكيد اختيار المقعد
    $('#confirm-seat').on('click', function() {
        let selectedSeat = $('.seat.selected').data('seat');
        if (selectedSeat) {
            $('#seat-number').val(selectedSeat);
            $('#seat-map-container').hide();
            $('#booking-form-container').slideDown();
            
            // تغيير الأزرار
            $('#complete-booking').show();
            $('#back-to-search').show();
        } else {
            alert('الرجاء اختيار مقعد أولاً');
        }
    });

    // اختيار مقعد
    $('.seat').on('click', function() {
        if ($(this).hasClass('reserved') || $(this).hasClass('aisle')) {
            return false;
        }
        
        $('.seat').removeClass('selected');
        $(this).addClass('selected');
    });

    // تأكيد الحجز
    $('#complete-booking').on('click', function() {
        // التحقق من صحة النموذج
        if (!validateBookingForm()) {
            return false;
        }
        
        // إظهار مؤشر التحميل
        showFormProcessing();
        
        // محاكاة عملية الحجز (ستظهر التأكيد بعد ثانية واحدة)
        setTimeout(function() {
            hideFormProcessing();
            
            // إغلاق المودال
            $('#modal-add-reservation').modal('hide');
            
            // عرض رسالة نجاح
            Swal.fire({
                title: 'تم الحجز بنجاح!',
                text: 'تم تأكيد حجز التذكرة بنجاح. رقم الحجز: BUS-' + Math.floor(Math.random() * 1000000),
                icon: 'success',
                confirmButtonText: 'تم'
            }).then((result) => {
                // إعادة تحميل الصفحة لتحديث قائمة الحجوزات
                // window.location.reload();
                
                // إعادة تعيين النموذج والصفحة
                resetBookingForm();
            });
        }, 1000);
    });

    // إعادة تعيين النموذج
    function resetBookingForm() {
        // إخفاء جميع الأقسام
        $('#search-results').hide();
        $('#booking-form-container').hide();
        $('#seat-map-container').hide();
        
        // إعادة تعيين حقول النموذج
        $('#trip-search-form')[0].reset();
        $('#booking-form')[0].reset();
        
        // إزالة تحديد المقاعد
        $('.seat').removeClass('selected');
        
        // إعادة تعيين أزرار التنقل
        $('#continue-to-booking').hide();
        $('#complete-booking').hide();
        $('#back-to-search').hide();
    }

    // التحقق من صحة نموذج البحث عن الرحلات
    function validateTripSearchForm() {
        let isValid = true;
        
        // التحقق من اختيار مدينة المغادرة
        if ($('#search-from').val() === '') {
            showFieldError('#search-from', 'الرجاء اختيار مدينة المغادرة');
            isValid = false;
        } else {
            clearFieldError('#search-from');
        }
        
        // التحقق من اختيار مدينة الوصول
        if ($('#search-to').val() === '') {
            showFieldError('#search-to', 'الرجاء اختيار مدينة الوصول');
            isValid = false;
        } else {
            clearFieldError('#search-to');
        }
        
        // التحقق من تحديد تاريخ السفر
        if ($('#search-date').val() === '') {
            showFieldError('#search-date', 'الرجاء تحديد تاريخ السفر');
            isValid = false;
        } else {
            clearFieldError('#search-date');
        }
        
        return isValid;
    }

    // التحقق من صحة نموذج الحجز
    function validateBookingForm() {
        let isValid = true;
        
        // التحقق من إدخال اسم المسافر
        if ($('#passenger-name').val() === '') {
            showFieldError('#passenger-name', 'الرجاء إدخال اسم المسافر');
            isValid = false;
        } else {
            clearFieldError('#passenger-name');
        }
        
        // التحقق من إدخال رقم الجوال
        if ($('#mobile').val() === '') {
            showFieldError('#mobile', 'الرجاء إدخال رقم الجوال');
            isValid = false;
        } else {
            clearFieldError('#mobile');
        }
        
        // التحقق من اختيار نوع الهوية
        if ($('#id-type').val() === '') {
            showFieldError('#id-type', 'الرجاء اختيار نوع الهوية');
            isValid = false;
        } else {
            clearFieldError('#id-type');
        }
        
        // التحقق من إدخال رقم الهوية
        if ($('#id-number').val() === '') {
            showFieldError('#id-number', 'الرجاء إدخال رقم الهوية');
            isValid = false;
        } else {
            clearFieldError('#id-number');
        }
        
        // التحقق من اختيار الجنسية
        if ($('#nationality').val() === '') {
            showFieldError('#nationality', 'الرجاء اختيار الجنسية');
            isValid = false;
        } else {
            clearFieldError('#nationality');
        }
        
        // التحقق من اختيار طريقة الدفع
        if ($('#payment-method').val() === '') {
            showFieldError('#payment-method', 'الرجاء اختيار طريقة الدفع');
            isValid = false;
        } else {
            clearFieldError('#payment-method');
            
            // التحقق من إدخال المبلغ المدفوع إذا كانت طريقة الدفع نقداً أو تحويل بنكي
            if ($('#payment-method').val() === 'cash' || $('#payment-method').val() === 'bank-transfer') {
                if ($('#paid-amount').val() === '') {
                    showFieldError('#paid-amount', 'الرجاء إدخال المبلغ المدفوع');
                    isValid = false;
                } else {
                    clearFieldError('#paid-amount');
                }
            }
        }
        
        return isValid;
    }

    // عرض رسالة خطأ على حقل معين
    function showFieldError(fieldSelector, message) {
        $(fieldSelector).addClass('is-invalid');
        if ($(fieldSelector).next('.invalid-feedback').length === 0) {
            $(fieldSelector).after('<div class="invalid-feedback">' + message + '</div>');
        } else {
            $(fieldSelector).next('.invalid-feedback').text(message);
        }
    }

    // إزالة رسالة الخطأ من حقل
    function clearFieldError(fieldSelector) {
        $(fieldSelector).removeClass('is-invalid');
    }

    // عرض مؤشر معالجة النموذج
    function showFormProcessing() {
        // يمكنك إضافة مؤشر تحميل هنا إذا أردت
        $('#modal-add-reservation .modal-footer button').prop('disabled', true);
    }

    // إخفاء مؤشر معالجة النموذج
    function hideFormProcessing() {
        $('#modal-add-reservation .modal-footer button').prop('disabled', false);
    }

    // استدعاء إعادة التعيين عند فتح المودال
    $('#modal-add-reservation').on('show.bs.modal', function (e) {
        resetBookingForm();
    });
});