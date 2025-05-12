/**
 * إصلاح خاص بالقائمة الجانبية بدعم RTL لـ AdminLTE
 * يعمل بشكل متوافق مع مكتبة AdminLTE
 */

// تهيئة عند تحميل الصفحة
$(document).ready(function() {
    console.log('تهيئة إصلاح القائمة الجانبية RTL');
    
    // ضمان وجود أنماط RTL
    ensureRtlStyles();
    
    // معالجة الأزرار الخاصة بالقائمة
    setupSidebarToggle();
    
    // استعادة حالة القائمة من التخزين المحلي (إذا كانت مخزنة)
    restoreSidebarState();
});

// إضافة الأنماط الخاصة بـ RTL
function ensureRtlStyles() {
    // التأكد من أن القائمة الجانبية على اليمين
    $('.main-sidebar').css({
        'right': '0',
        'left': 'auto'
    });
    
    // ضبط هوامش المحتوى
    $('.content-wrapper, .main-header, .main-footer').css({
        'margin-right': '250px',
        'margin-left': '0'
    });
    
    // ضبط هوامش المحتوى عند طي القائمة
    if ($('body').hasClass('sidebar-collapse')) {
        $('.content-wrapper, .main-header, .main-footer').css({
            'margin-right': '4.6rem'
        });
        
        // إخفاء النص في القائمة المطوية
        $('.nav-sidebar .nav-link p').css('display', 'none');
    }
}

// إعداد زر تبديل القائمة
function setupSidebarToggle() {
    // استخدام زر القائمة الأصلي
    $('#sidebarToggleBtn').off('click').on('click', function(e) {
        // منع السلوك الافتراضي
        e.preventDefault();
        
        console.log('تم النقر على زر القائمة الجانبية');
        
        // تبديل القائمة الجانبية
        $('body').toggleClass('sidebar-collapse');
        
        // حفظ الحالة
        localStorage.setItem('sidebar-collapsed', $('body').hasClass('sidebar-collapse') ? 'true' : 'false');
        
        // تحديث الأنماط
        updateSidebarStyles();
    });
}

// تحديث أنماط القائمة الجانبية
function updateSidebarStyles() {
    const isCollapsed = $('body').hasClass('sidebar-collapse');
    
    if (isCollapsed) {
        // عند طي القائمة
        $('.content-wrapper, .main-header, .main-footer').css({
            'margin-right': '4.6rem'
        });
        
        // إخفاء النص في روابط القائمة
        $('.nav-sidebar .nav-link p').css('display', 'none');
    } else {
        // عند فتح القائمة
        $('.content-wrapper, .main-header, .main-footer').css({
            'margin-right': '250px'
        });
        
        // إظهار النص في روابط القائمة
        $('.nav-sidebar .nav-link p').css('display', '');
    }
}

// استعادة حالة القائمة من التخزين المحلي
function restoreSidebarState() {
    const savedState = localStorage.getItem('sidebar-collapsed');
    
    if (savedState === 'true' && !$('body').hasClass('sidebar-collapse')) {
        $('body').addClass('sidebar-collapse');
        updateSidebarStyles();
    } else if (savedState === 'false' && $('body').hasClass('sidebar-collapse')) {
        $('body').removeClass('sidebar-collapse');
        updateSidebarStyles();
    }
}