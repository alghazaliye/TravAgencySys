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
    
    // التعامل مع حدث تغيير حجم النافذة
    window.addEventListener('resize', handleWindowResize);
    
    // تصحيح أي مشاكل في واجهة المستخدم
    fixUIIssues();
});

/**
 * تصحيح مشكلة القائمة الجانبية في الاتجاه من اليمين إلى اليسار
 */
function fixRtlSidebar() {
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
    const sidebar = document.querySelector('.main-sidebar');
    if (sidebar) {
        sidebar.style.overflow = 'auto';
        sidebar.style.height = '100%';
    }
    
    // إصلاح مشكلة رأس الشاشة على الأجهزة المحمولة
    const header = document.querySelector('.main-header');
    if (header) {
        header.style.position = 'fixed';
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