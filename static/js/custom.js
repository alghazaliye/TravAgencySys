/**
 * ملف JavaScript المخصص لتحسين تجربة المستخدم في نظام وكالة السفر
 */

document.addEventListener("DOMContentLoaded", function() {
    // تصحيح مشكلة القائمة الجانبية في الاتجاه من اليمين إلى اليسار
    fixRtlSidebar();
    
    // تهيئة جداول البيانات
    initializeDataTables();
    
    // تهيئة أداة اختيار التاريخ
    initializeDatepickers();
    
    // تهيئة select2
    initializeSelect2();
    
    // تفعيل المخططات في لوحة التحكم
    initializeCharts();
    
    // تفعيل عناصر التحقق من صحة النماذج في Bootstrap
    initializeFormValidation();
    
    // تهيئة أزرار التنقل في النماذج متعددة الخطوات
    initializeFormNavigation();
    
    // تهيئة عرض المبالغ المالية كتابة بالحروف العربية
    initializeAmountToWords();
    
    // تهيئة دعم العملات المتعددة
    initializeMultiCurrencySupport();
    
    // التعامل مع حدث تغيير حجم النافذة
    window.addEventListener('resize', handleWindowResize);
    
    // تصحيح أي مشاكل في واجهة المستخدم
    fixUIIssues();
});

/**
 * تصحيح مشكلة القائمة الجانبية في الاتجاه من اليمين إلى اليسار
 */
function fixRtlSidebar() {
    // التأكد من أن الشريط الجانبي يملأ ارتفاع الصفحة
    const mainSidebar = document.querySelector('.main-sidebar');
    if (mainSidebar) {
        mainSidebar.style.minHeight = '100vh';
        mainSidebar.style.height = '100%';
        
        // التأكد من ضبط وضع position بشكل صحيح
        mainSidebar.style.position = 'fixed';
    }
    
    // إصلاح مشكلة التمرير في الشريط الجانبي
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.style.height = 'calc(100% - 4.5rem)';
        sidebar.style.overflowY = 'auto';
        sidebar.style.paddingBottom = '0';
        sidebar.style.paddingRight = '0.5rem';
        sidebar.style.paddingLeft = '0.5rem';
    }
    
    // إعادة تعيين علامات التبويب في القائمة الجانبية
    const navItems = document.querySelectorAll('.nav-sidebar .nav-item');
    
    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link && link.getAttribute('href') === window.location.pathname) {
            link.classList.add('active');
            
            // إذا كان العنصر داخل قائمة فرعية، افتح القائمة الأم
            let parent = item.parentElement;
            while (parent) {
                if (parent.classList.contains('nav-treeview')) {
                    const parentItem = parent.parentElement;
                    if (parentItem) {
                        const parentLink = parentItem.querySelector('.nav-link');
                        if (parentLink) {
                            parentLink.classList.add('active');
                        }
                        parentItem.classList.add('menu-open');
                    }
                }
                parent = parent.parentElement;
            }
        }
    });
    
    // إصلاح مشكلة الأيقونات في القائمة للـ RTL
    document.querySelectorAll('.nav-sidebar .nav-link').forEach(link => {
        const icon = link.querySelector('.nav-icon');
        if (icon) {
            link.classList.add('d-flex');
            icon.style.marginLeft = '10px';
            icon.style.marginRight = '0';
        }
    });
    
    // إصلاح مشكلة تبديل القائمة الجانبية في وضع الجوال
    const pushMenuButton = document.querySelector('[data-widget="pushmenu"]');
    if (pushMenuButton) {
        // نزيل المستمع السابق إذا كان موجودًا
        pushMenuButton.replaceWith(pushMenuButton.cloneNode(true));
        
        // نعيد تعريف الزر بعد استبداله
        const newPushMenuButton = document.querySelector('[data-widget="pushmenu"]');
        // لا نضيف مستمعًا خاصًا، ونترك AdminLTE يتعامل مع الأمر
    }
    
    // معالجة مشكلة القائمة المنسدلة في الهاتف المحمول
    if (window.innerWidth <= 767.98) {
        fixMobileSidebar();
    }
}

/**
 * إصلاح مشكلات الشريط الجانبي في الأجهزة المحمولة
 */
function fixMobileSidebar() {
    // تأكد من عدم ظهور الشريط الجانبي عند التحميل على الجوال
    document.body.classList.remove('sidebar-open');
    document.body.classList.add('sidebar-closed', 'sidebar-collapse');
    
    // تعديل أسلوب العرض لمنع مشكلة التمرير في الأجهزة المحمولة
    const mainSidebar = document.querySelector('.main-sidebar');
    if (mainSidebar) {
        mainSidebar.style.overflow = 'hidden';
        mainSidebar.style.height = '100%';
        mainSidebar.style.minHeight = '100vh';
        mainSidebar.style.position = 'fixed';
        mainSidebar.style.top = '0';
        mainSidebar.style.zIndex = '1100';
    }
    
    // تعديل .sidebar للتمرير
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.style.height = 'calc(100% - 3.5rem)';
        sidebar.style.overflowY = 'auto';
        sidebar.style.paddingBottom = '1rem';
    }
    
    // إصلاح مشكلة رأس الشاشة على الأجهزة المحمولة
    const header = document.querySelector('.main-header');
    if (header) {
        header.style.position = 'fixed';
        header.style.top = '0';
        header.style.width = '100%';
        header.style.zIndex = '1001';
    }
    
    // إضافة هامش للمحتوى الرئيسي لتجنب تداخله مع الرأس الثابت
    const contentWrapper = document.querySelector('.content-wrapper');
    if (contentWrapper && header) {
        contentWrapper.style.marginTop = (header.offsetHeight) + 'px';
    }
}

/**
 * معالجة تغيير حجم النافذة
 */
function handleWindowResize() {
    if (window.innerWidth <= 767.98) {
        fixMobileSidebar();
    } else {
        // إعادة تعيين أنماط المحتوى عند العرض على الشاشات الكبيرة
        const contentWrapper = document.querySelector('.content-wrapper');
        if (contentWrapper) {
            contentWrapper.style.marginTop = '';
        }
    }
}

/**
 * تهيئة جداول البيانات
 */
function initializeDataTables() {
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            "paging": true,
            "lengthChange": true,
            "searching": true,
            "ordering": true,
            "info": true,
            "autoWidth": false,
            "responsive": true,
            "language": {
                "sProcessing": "جارٍ التحميل...",
                "sLengthMenu": "أظهر _MENU_ مدخلات",
                "sZeroRecords": "لم يعثر على أية سجلات",
                "sInfo": "إظهار _START_ إلى _END_ من أصل _TOTAL_ مدخل",
                "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
                "sInfoFiltered": "(منتقاة من مجموع _MAX_ مدخل)",
                "sInfoPostFix": "",
                "sSearch": "ابحث:",
                "sUrl": "",
                "oPaginate": {
                    "sFirst": "الأول",
                    "sPrevious": "السابق",
                    "sNext": "التالي",
                    "sLast": "الأخير"
                }
            }
        });
    }
}

/**
 * تهيئة أداة اختيار التاريخ
 */
function initializeDatepickers() {
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'dd-mm-yyyy',
            autoclose: true,
            rtl: true,
            language: 'ar',
            todayHighlight: true,
            orientation: "bottom"
        });
    }
}

/**
 * تهيئة select2
 */
function initializeSelect2() {
    if ($.fn.select2) {
        $('.select2').select2({
            dir: "rtl",
            language: "ar"
        });
    }
}

/**
 * تهيئة المخططات
 */
function initializeCharts() {
    // مراجعة إذا كان Chart.js متاحًا وعنصر canvas موجود
    if (typeof Chart !== 'undefined' && document.getElementById('visasChart')) {
        initializeVisasChart();
    }
    
    if (typeof Chart !== 'undefined' && document.getElementById('salesChart')) {
        initializeSalesChart();
    }
}

/**
 * مخطط التأشيرات
 */
function initializeVisasChart() {
    const ctx = document.getElementById('visasChart').getContext('2d');
    
    // خيارات المخطط المشتركة
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0
            }
        },
        scales: {
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    font: {
                        family: "Tajawal"
                    },
                    maxTicksLimit: 12
                }
            },
            y: {
                ticks: {
                    font: {
                        family: "Tajawal"
                    },
                    beginAtZero: true,
                    maxTicksLimit: 5,
                    padding: 10
                },
                grid: {
                    color: "rgb(234, 236, 244)",
                    borderColor: "rgb(234, 236, 244)",
                    drawBorder: false,
                    borderDash: [2],
                    borderDashOffset: [2]
                }
            },
        },
        legend: {
            display: true,
            position: 'top',
            rtl: true,
            labels: {
                fontFamily: "Tajawal"
            }
        },
        tooltips: {
            rtl: true,
            bodyFontFamily: "Tajawal",
            titleFontFamily: "Tajawal",
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleFontColor: '#6e707e',
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10
        }
    };
    
    // بيانات المخطط
    const data = {
        labels: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
        datasets: [
            {
                label: "تأشيرات العمرة",
                backgroundColor: "#4e73df",
                borderColor: "#4e73df",
                data: [45, 50, 38, 41, 35, 28, 32, 35, 50, 65, 75, 80],
                fill: false
            },
            {
                label: "تأشيرات العمل",
                backgroundColor: "#1cc88a",
                borderColor: "#1cc88a",
                data: [20, 25, 30, 35, 40, 45, 40, 35, 30, 25, 20, 15],
                fill: false
            },
            {
                label: "تأشيرات الزيارة",
                backgroundColor: "#f6c23e",
                borderColor: "#f6c23e",
                data: [30, 32, 28, 30, 35, 25, 22, 20, 25, 30, 35, 40],
                fill: false
            }
        ]
    };
    
    // إنشاء المخطط
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}

/**
 * مخطط المبيعات
 */
function initializeSalesChart() {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    // خيارات المخطط المشتركة
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0
            }
        },
        scales: {
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    font: {
                        family: "Tajawal"
                    },
                    maxTicksLimit: 12
                }
            },
            y: {
                ticks: {
                    font: {
                        family: "Tajawal"
                    },
                    beginAtZero: true,
                    maxTicksLimit: 5,
                    padding: 10
                },
                grid: {
                    color: "rgb(234, 236, 244)",
                    borderColor: "rgb(234, 236, 244)",
                    drawBorder: false,
                    borderDash: [2],
                    borderDashOffset: [2]
                }
            },
        },
        legend: {
            display: true,
            position: 'top',
            rtl: true,
            labels: {
                fontFamily: "Tajawal"
            }
        },
        tooltips: {
            rtl: true,
            bodyFontFamily: "Tajawal",
            titleFontFamily: "Tajawal",
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleFontColor: '#6e707e',
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10
        }
    };
    
    // بيانات المخطط
    const data = {
        labels: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
        datasets: [
            {
                label: "الإيرادات (بالريال)",
                backgroundColor: "rgba(78, 115, 223, 0.3)",
                borderColor: "#4e73df",
                pointBackgroundColor: "#4e73df",
                pointBorderColor: "#4e73df",
                pointHoverBackgroundColor: "#4e73df",
                pointHoverBorderColor: "#4e73df",
                data: [25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000],
                fill: true
            }
        ]
    };
    
    // إنشاء المخطط
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}

/**
 * تفعيل التحقق من صحة النماذج في Bootstrap
 */
function initializeFormValidation() {
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * إصلاح مشكلات واجهة المستخدم
 */
function fixUIIssues() {
    // إصلاح مشكلة في الشريط العلوي على الأجهزة المحمولة
    const header = document.querySelector('.main-header');
    if (header && window.innerWidth <= 767.98) {
        header.style.position = 'fixed';
        header.style.top = '0';
        header.style.width = '100%';
        header.style.zIndex = '1001';
        
        // إضافة هامش للمحتوى الرئيسي لتجنب تداخله مع الرأس الثابت
        const contentWrapper = document.querySelector('.content-wrapper');
        if (contentWrapper) {
            contentWrapper.style.marginTop = (header.offsetHeight) + 'px';
        }
    }
    
    // إصلاح عرض المحتوى عند فتح الشريط الجانبي
    const pushMenuButton = document.querySelector('[data-widget="pushmenu"]');
    if (pushMenuButton) {
        pushMenuButton.addEventListener('click', function() {
            const contentWrapper = document.querySelector('.content-wrapper');
            const mainHeader = document.querySelector('.main-header');
            const mainFooter = document.querySelector('.main-footer');
            
            // إذا كان الشريط الجانبي مفتوحًا، تأكد من الحفاظ على عرض المحتوى كاملًا
            if (document.body.classList.contains('sidebar-open') || 
                !document.body.classList.contains('sidebar-collapse')) {
                if (contentWrapper) contentWrapper.style.width = 'calc(100% - 250px)';
                if (mainHeader) mainHeader.style.width = 'calc(100% - 250px)';
                if (mainFooter) mainFooter.style.width = 'calc(100% - 250px)';
            } else {
                if (contentWrapper) contentWrapper.style.width = '100%';
                if (mainHeader) mainHeader.style.width = '100%';
                if (mainFooter) mainFooter.style.width = '100%';
            }
        });
    }
    
    // إصلاح مشكلة أيقونات الأزرار
    document.querySelectorAll('.btn i').forEach(icon => {
        if (getComputedStyle(icon).marginLeft === '0px') {
            icon.style.marginLeft = '5px';
        }
    });
    
    // إصلاح مشكلة حجم النص في الجداول على الشاشات الصغيرة
    if (window.innerWidth <= 576) {
        document.querySelectorAll('table').forEach(table => {
            table.classList.add('small');
        });
    }
}

/**
 * تهيئة أزرار التنقل في النماذج متعددة الخطوات
 */
function initializeFormNavigation() {
    // أزرار الانتقال للقسم التالي
    const nextButtons = document.querySelectorAll('.next-step');
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const nextSectionId = this.getAttribute('data-next');
            const currentSection = this.closest('.section');
            
            // التحقق من صحة الحقول الإلزامية في القسم الحالي
            const requiredFields = currentSection.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (isValid) {
                // إخفاء القسم الحالي
                currentSection.style.display = 'none';
                
                // إظهار القسم التالي
                const nextSection = document.getElementById(nextSectionId);
                if (nextSection) {
                    nextSection.style.display = 'block';
                    
                    // تحديث شريط التقدم إذا كان موجودًا
                    updateProgressBar(nextSectionId);
                    
                    // تمرير إلى أعلى القسم الجديد
                    window.scrollTo({ top: nextSection.offsetTop - 100, behavior: 'smooth' });
                }
            }
        });
    });
    
    // أزرار الرجوع للقسم السابق
    const prevButtons = document.querySelectorAll('.prev-step');
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const prevSectionId = this.getAttribute('data-prev');
            const currentSection = this.closest('.section');
            
            // إخفاء القسم الحالي
            currentSection.style.display = 'none';
            
            // إظهار القسم السابق
            const prevSection = document.getElementById(prevSectionId);
            if (prevSection) {
                prevSection.style.display = 'block';
                
                // تحديث شريط التقدم إذا كان موجودًا
                updateProgressBar(prevSectionId);
                
                // تمرير إلى أعلى القسم الجديد
                window.scrollTo({ top: prevSection.offsetTop - 100, behavior: 'smooth' });
            }
        });
    });
    
    // تهيئة تبديل نوع الرحلة (ذهاب/ذهاب وعودة) في نموذج حجز الطيران
    const tripTypeInputs = document.querySelectorAll('input[name="tripType"]');
    tripTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const returnDateSection = document.querySelector('.return-date-section');
            if (returnDateSection) {
                if (this.value === 'round-trip') {
                    returnDateSection.style.display = 'block';
                } else {
                    returnDateSection.style.display = 'none';
                }
            }
        });
    });
}

/**
 * تحديث شريط التقدم (إذا كان موجودًا)
 */
function updateProgressBar(sectionId) {
    // الحصول على رقم الخطوة من معرّف القسم
    const stepMatch = sectionId.match(/section-(\w+)/);
    if (!stepMatch) return;
    
    // تحديد كل الأقسام
    const sections = document.querySelectorAll('.section');
    const totalSteps = sections.length;
    
    // معرفة الخطوة الحالية
    let currentStepIndex = 0;
    sections.forEach((section, index) => {
        if (section.id === sectionId) {
            currentStepIndex = index;
        }
    });
    
    // تحديث شريط التقدم إذا وجد
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const progressPercentage = ((currentStepIndex + 1) / totalSteps) * 100;
        progressBar.style.width = progressPercentage + '%';
        progressBar.setAttribute('aria-valuenow', progressPercentage);
    }
    
    // تحديث مؤشرات الخطوات إذا وجدت
    const stepIndicators = document.querySelectorAll('.step-indicator');
    if (stepIndicators.length > 0) {
        stepIndicators.forEach((indicator, index) => {
            if (index <= currentStepIndex) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }
}

/**
 * تهيئة عرض المبالغ المالية كتابة بالحروف العربية
 */
function initializeAmountToWords() {
    // الاستماع لأحداث تغيير القيمة في حقول المبالغ المالية
    document.querySelectorAll('input[type="number"]').forEach(input => {
        // تحقق مما إذا كان حقل مالي (له علامة عملة في العنصر الأب)
        const hasAmountIndicator = input.closest('.input-group')?.querySelector('.input-group-text')?.textContent.includes('ر.س') || false;
        
        if (hasAmountIndicator || input.id.includes('price') || input.id.includes('amount') || input.id.includes('cost')) {
            // تسجيل الحقل كحقل مالي
            input.classList.add('amount-field');
            
            // إضافة عنصر لعرض المبلغ كتابة
            const amountInWordsId = input.id + '-text';
            
            if (!document.getElementById(amountInWordsId)) {
                const container = input.closest('.form-group');
                const amountInWordsElement = document.createElement('small');
                amountInWordsElement.id = amountInWordsId;
                amountInWordsElement.className = 'form-text text-muted amount-in-words';
                amountInWordsElement.style.fontStyle = 'italic';
                container.appendChild(amountInWordsElement);
            }
            
            // إضافة معالج الحدث للعنصر
            input.addEventListener('input', function() {
                updateAmountInWords(this);
            });
            
            // تحديث القيمة الأولية
            updateAmountInWords(input);
        }
    });
}

/**
 * تحديث عرض المبلغ كتابة
 */
function updateAmountInWords(input) {
    const value = parseFloat(input.value);
    let amountInWordsElement;
    
    // محاولة العثور على العنصر الذي يعرض المبلغ كتابةً
    if (input.id === 'receipt-amount') {
        amountInWordsElement = document.getElementById('receipt-amount-in-words');
    } else if (input.id === 'amount') {
        amountInWordsElement = document.getElementById('amount-in-words');
    } else {
        amountInWordsElement = document.getElementById(input.id + '-text') || 
                             document.getElementById(input.id + '-in-words');
    }
    
    if (amountInWordsElement) {
        if (!isNaN(value) && value > 0) {
            const currencyText = getCurrencyText(input);
            amountInWordsElement.textContent = convertNumberToArabicWords(value) + ' ' + currencyText;
        } else {
            amountInWordsElement.textContent = '';
        }
    }
}

/**
 * الحصول على نص العملة المناسب للحقل
 */
function getCurrencyText(input) {
    // التحقق من وجود حقل اختيار العملة في النموذج
    const form = input.closest('form') || input.closest('.card-body');
    let currencySelect;
    
    // محاولة العثور على حقل العملة لسند الصرف أو سند القبض أو أي نموذج آخر
    if (form) {
        currencySelect = form.querySelector('#currency-type') || 
                        form.querySelector('#receipt-currency-type') || 
                        form.querySelector('[name="currency"]') ||
                        form.querySelector('[name="currency-type"]') ||
                        form.querySelector('[name="receipt-currency-type"]');
    }
    
    if (currencySelect) {
        const currencyValue = currencySelect.value;
        
        // استخدام كائن العملات العالمي إذا كان متاحاً
        if (window.multiCurrency && window.multiCurrency.currencyNames) {
            const currencyName = window.multiCurrency.currencyNames[currencyValue];
            if (currencyName) {
                return currencyName + ' فقط لا غير';
            }
        }
        
        switch (currencyValue) {
            case 'USD':
                return 'دولار أمريكي فقط لا غير';
            case 'EUR':
                return 'يورو فقط لا غير';
            case 'GBP':
                return 'جنيه إسترليني فقط لا غير';
            case 'AED':
                return 'درهم إماراتي فقط لا غير';
            case 'KWD':
                return 'دينار كويتي فقط لا غير';
            case 'EGP':
                return 'جنيه مصري فقط لا غير';
            default:
                return 'ريال سعودي فقط لا غير';
        }
    }
    
    // القيمة الافتراضية هي الريال السعودي
    return 'ريال سعودي فقط لا غير';
}

/**
 * تحويل الرقم إلى كلمات عربية
 */
function convertNumberToArabicWords(number) {
    // الأرقام من صفر إلى تسعة عشر
    const ones = [
        'صفر', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة',
        'عشرة', 'أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر', 'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر'
    ];
    
    // العشرات
    const tens = [
        '', '', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون'
    ];
    
    // المئات
    const hundreds = [
        '', 'مائة', 'مائتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة', 'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة'
    ];
    
    // تدرجات الأعداد الكبيرة
    const scales = [
        '', 'ألف', 'مليون', 'مليار', 'تريليون'
    ];
    
    // التعامل مع الكسور
    const truncated = Math.floor(number);
    const decimal = Math.round((number - truncated) * 100);
    
    if (truncated === 0) {
        if (decimal === 0) {
            return ones[0]; // صفر
        }
        return convertLessThanOneThousand(decimal) + ' هللة';
    }
    
    let words = '';
    
    let scaleIndex = 0;
    let num = truncated;
    
    while (num > 0) {
        const hundreds = num % 1000;
        if (hundreds > 0) {
            const scaleWord = scales[scaleIndex];
            if (words.length > 0) {
                words = convertLessThanOneThousand(hundreds) + ' ' + scaleWord + ' و ' + words;
            } else {
                words = convertLessThanOneThousand(hundreds) + ' ' + scaleWord;
            }
        }
        
        num = Math.floor(num / 1000);
        scaleIndex++;
    }
    
    // إضافة الكسور
    if (decimal > 0) {
        words += ' و ' + convertLessThanOneThousand(decimal) + ' هللة';
    }
    
    return words;
    
    // دالة مساعدة لتحويل الأرقام أقل من 1000
    function convertLessThanOneThousand(n) {
        if (n < 20) {
            return ones[n];
        }
        
        const digit = n % 10;
        const ten = Math.floor(n / 10) % 10;
        const hundred = Math.floor(n / 100) % 10;
        
        let result = '';
        
        if (hundred > 0) {
            result += hundreds[hundred];
            if (n % 100 > 0) {
                result += ' و ';
            }
        }
        
        if (n % 100 < 20 && n % 100 > 0) {
            result += ones[n % 100];
        } else if (n % 100 > 0) {
            if (digit > 0) {
                result += ones[digit] + ' و ' + tens[ten];
            } else {
                result += tens[ten];
            }
        }
        
        return result;
    }
}

/**
 * تهيئة إدارة العملات المتعددة
 */
function initializeMultiCurrencySupport() {
    // أسعار صرف العملات مقابل الريال السعودي (للأغراض التوضيحية فقط)
    const exchangeRates = {
        'SAR': 1.0,      // ريال سعودي (عملة الأساس)
        'USD': 0.27,     // دولار أمريكي
        'EUR': 0.24,     // يورو
        'GBP': 0.21,     // جنيه إسترليني
        'AED': 0.98      // درهم إماراتي
    };
    
    // أسماء العملات بالعربي مع رموزها
    const currencyNames = {
        'SAR': 'ريال سعودي',
        'USD': 'دولار أمريكي',
        'EUR': 'يورو',
        'GBP': 'جنيه إسترليني',
        'AED': 'درهم إماراتي'
    };
    
    // رموز العملات
    const currencySymbols = {
        'SAR': 'ر.س',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'AED': 'د.إ'
    };
    
    // تحديث معلومات سعر الصرف في سند القبض
    function updateReceiptExchangeRateInfo() {
        const currencySelect = document.getElementById('receipt-currency-type');
        const exchangeRateInfoElem = document.getElementById('exchange-rate-info');
        
        if (!currencySelect || !exchangeRateInfoElem) {
            return;
        }
        
        const selectedCurrency = currencySelect.value;
        const currencyName = currencyNames[selectedCurrency] || selectedCurrency;
        const rate = exchangeRates[selectedCurrency] || 1.0;
        
        if (selectedCurrency === 'SAR') {
            exchangeRateInfoElem.textContent = `١ ${currencyName} = ١ ريال سعودي`;
        } else {
            const sarEquivalent = (1 / rate).toFixed(2);
            exchangeRateInfoElem.textContent = `١ ${currencyName} = ${sarEquivalent} ريال سعودي`;
        }
    }
    
    // تحديث معلومات سعر الصرف في سند الصرف
    function updatePaymentExchangeRateInfo() {
        const currencySelect = document.getElementById('currency-type');
        const exchangeRateInfoElem = document.getElementById('payment-exchange-rate-info');
        
        if (!currencySelect || !exchangeRateInfoElem) {
            return;
        }
        
        const selectedCurrency = currencySelect.value;
        const currencyName = currencyNames[selectedCurrency] || selectedCurrency;
        const rate = exchangeRates[selectedCurrency] || 1.0;
        
        if (selectedCurrency === 'SAR') {
            exchangeRateInfoElem.textContent = `١ ${currencyName} = ١ ريال سعودي`;
        } else {
            const sarEquivalent = (1 / rate).toFixed(2);
            exchangeRateInfoElem.textContent = `١ ${currencyName} = ${sarEquivalent} ريال سعودي`;
        }
    }
    
    // تحويل مبلغ بين العملات
    function convertAmountBetweenCurrencies(amount, fromCurrency, toCurrency) {
        if (!amount || isNaN(amount) || amount <= 0) {
            return 0;
        }
        
        const fromRate = exchangeRates[fromCurrency] || 1.0;
        const toRate = exchangeRates[toCurrency] || 1.0;
        
        // تحويل من العملة المصدر إلى الريال السعودي، ثم إلى العملة الهدف
        const amountInSAR = amount / fromRate;
        const amountInTargetCurrency = amountInSAR * toRate;
        
        return amountInTargetCurrency.toFixed(2);
    }
    
    // تسجيل مستمعي الأحداث
    function registerCurrencyEventListeners() {
        // سند القبض
        const receiptCurrencySelect = document.getElementById('receipt-currency-type');
        if (receiptCurrencySelect) {
            receiptCurrencySelect.addEventListener('change', function() {
                updateReceiptExchangeRateInfo();
                
                // تحديث رمز العملة
                const currencySymbol = document.getElementById('receipt-currency-symbol');
                if (currencySymbol) {
                    currencySymbol.textContent = currencySymbols[this.value] || this.value;
                }
                
                // إعادة حساب المبلغ بالكلمات
                const amountInput = document.getElementById('receipt-amount');
                if (amountInput) {
                    const event = new Event('input', { bubbles: true });
                    amountInput.dispatchEvent(event);
                }
            });
            
            // تهيئة أولية
            updateReceiptExchangeRateInfo();
        }
        
        // سند الصرف
        const paymentCurrencySelect = document.getElementById('currency-type');
        if (paymentCurrencySelect) {
            paymentCurrencySelect.addEventListener('change', function() {
                updatePaymentExchangeRateInfo();
                
                // تحديث رمز العملة
                const currencySymbol = document.getElementById('currency-symbol');
                if (currencySymbol) {
                    currencySymbol.textContent = currencySymbols[this.value] || this.value;
                }
                
                // إعادة حساب المبلغ بالكلمات
                const amountInput = document.getElementById('amount');
                if (amountInput) {
                    const event = new Event('input', { bubbles: true });
                    amountInput.dispatchEvent(event);
                }
            });
            
            // تهيئة أولية
            updatePaymentExchangeRateInfo();
        }
        
        // أزرار تحديث أسعار الصرف
        const updateExchangeRateButtons = document.querySelectorAll('button[title="تحديث أسعار الصرف"]');
        updateExchangeRateButtons.forEach(button => {
            button.addEventListener('click', function() {
                Swal.fire({
                    title: 'جاري التحديث...',
                    text: 'يتم الآن تحديث أسعار الصرف من المصادر الرسمية',
                    icon: 'info',
                    showConfirmButton: false,
                    allowOutsideClick: false,
                    willOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                // محاكاة عملية التحديث (في التطبيق الحقيقي، سيتم استدعاء API)
                setTimeout(function() {
                    // تحديث افتراضي للقيم بغرض العرض
                    exchangeRates['USD'] = 0.266;
                    exchangeRates['EUR'] = 0.245;
                    exchangeRates['GBP'] = 0.208;
                    exchangeRates['AED'] = 0.979;
                    
                    // تحديث معلومات سعر الصرف
                    updateReceiptExchangeRateInfo();
                    updatePaymentExchangeRateInfo();
                    
                    Swal.fire({
                        title: 'تم التحديث!',
                        text: 'تم تحديث أسعار الصرف بنجاح',
                        icon: 'success',
                        confirmButtonText: 'حسناً'
                    });
                }, 1500);
            });
        });
    }
    
    // تصدير الدوال للاستخدام العام
    window.multiCurrency = {
        exchangeRates: exchangeRates,
        currencyNames: currencyNames,
        currencySymbols: currencySymbols,
        convert: convertAmountBetweenCurrencies,
        updateReceiptExchangeRateInfo: updateReceiptExchangeRateInfo,
        updatePaymentExchangeRateInfo: updatePaymentExchangeRateInfo
    };
    
    // تسجيل مستمعي الأحداث عند تهيئة الصفحة
    registerCurrencyEventListeners();
}