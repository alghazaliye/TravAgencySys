/**
 * إصلاح بسيط لزر القائمة الجانبية في تطبيق وكالة السفر
 */

document.addEventListener('DOMContentLoaded', function() {
    // إضافة معالج نقر على زر القائمة الجانبية
    document.body.addEventListener('click', function(event) {
        // البحث عن الزر بناءً على الخصائص
        if (event.target.closest('[data-widget="pushmenu"]')) {
            console.log('تم النقر على زر القائمة الجانبية');
            
            // تبديل حالة القائمة
            toggleSidebar();
            
            // منع السلوك الافتراضي
            event.preventDefault();
            event.stopPropagation();
        }
    });
    
    // إضافة مستمع للنقر المباشر على الزر أيضًا
    const pushmenuButton = document.querySelector('[data-widget="pushmenu"]');
    if (pushmenuButton) {
        pushmenuButton.onclick = function(event) {
            console.log('تم النقر على زر القائمة الجانبية - المعالج المباشر');
            toggleSidebar();
            event.preventDefault();
            event.stopPropagation();
            return false;
        };
    }
    
    // وسم مخصص للنقر السريع
    const quickFix = document.createElement('div');
    quickFix.style.position = 'fixed';
    quickFix.style.top = '10px';
    quickFix.style.right = '10px';
    quickFix.style.zIndex = '9999';
    quickFix.style.padding = '5px 10px';
    quickFix.style.background = '#f8f9fa';
    quickFix.style.border = '1px solid #ddd';
    quickFix.style.borderRadius = '4px';
    quickFix.style.cursor = 'pointer';
    quickFix.innerHTML = '<span style="font-size: 16px;"><i class="fas fa-bars"></i></span>';
    quickFix.title = 'تبديل القائمة الجانبية';
    
    quickFix.addEventListener('click', function() {
        console.log('تم النقر على زر الإصلاح السريع');
        toggleSidebar();
    });
    
    document.body.appendChild(quickFix);
});

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    // تبديل الفئات في الجسم
    document.body.classList.toggle('sidebar-collapse');
    
    if (document.body.classList.contains('sidebar-collapse')) {
        // عند إغلاق القائمة
        document.body.classList.remove('sidebar-open');
        
        // تعديل هوامش المحتوى
        setContentMargins('0');
    } else {
        // عند فتح القائمة
        document.body.classList.add('sidebar-open');
        
        // تعديل هوامش المحتوى
        setContentMargins('250px');
    }
}

/**
 * ضبط هوامش المحتوى
 */
function setContentMargins(margin) {
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    if (contentWrapper) contentWrapper.style.marginRight = margin;
    if (mainHeader) mainHeader.style.marginRight = margin;
    if (mainFooter) mainFooter.style.marginRight = margin;
}