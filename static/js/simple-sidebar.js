/**
 * الحل الأبسط للقائمة الجانبية - يحل مشكلة القائمة الجانبية في AdminLTE
 */

// عندما يتم تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('تحميل ملف القائمة الجانبية البسيط');
    
    // إعداد زر تبديل القائمة
    setupSidebarToggle();
    
    // إضافة CSS مباشرة للتأكد من أن القائمة الجانبية مرئية
    addRequiredStyles();
});

// إعداد زر القائمة
function setupSidebarToggle() {
    // الحصول على زر القائمة
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    
    if (!toggleBtn) {
        console.error('لم يتم العثور على زر القائمة!');
        return;
    }
    
    // إزالة أي مستمعات سابقة من خلال استبدال الزر
    const newBtn = toggleBtn.cloneNode(true);
    toggleBtn.parentNode.replaceChild(newBtn, toggleBtn);
    
    // إضافة مستمع حدث بسيط
    newBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('تم النقر على زر القائمة');
        
        // إصلاح مباشر للقائمة الجانبية
        document.body.classList.toggle('sidebar-collapse');
        
        // تحديث عرض الشريط الجانبي
        const sidebar = document.querySelector('.main-sidebar');
        
        if (document.body.classList.contains('sidebar-collapse')) {
            sidebar.style.width = '4.6rem';
            sidebar.style.minWidth = '4.6rem';
            // إخفاء النصوص في القائمة
            document.querySelectorAll('.nav-sidebar .nav-link p').forEach(el => {
                el.style.display = 'none';
            });
            console.log('طي القائمة');
        } else {
            sidebar.style.width = '250px';
            sidebar.style.minWidth = '250px';
            // إظهار النصوص في القائمة
            document.querySelectorAll('.nav-sidebar .nav-link p').forEach(el => {
                el.style.display = '';
            });
            console.log('فتح القائمة');
        }
        
        // تحديث هوامش المحتوى
        updateContentMargins();
    });
}

// تحديث هوامش المحتوى
function updateContentMargins() {
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    const margin = isCollapsed ? '4.6rem' : '250px';
    
    // تحديث المحتوى
    document.querySelector('.content-wrapper').style.marginRight = margin;
    document.querySelector('.main-header').style.marginRight = margin;
    document.querySelector('.main-footer').style.marginRight = margin;
    
    console.log('تم تحديث الهوامش إلى', margin);
}

// إضافة الأنماط المطلوبة مباشرة
function addRequiredStyles() {
    // إنشاء عنصر <style>
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        /* تأكيد أن القائمة الجانبية مرئية دائمًا */
        .main-sidebar, .main-sidebar::before {
            display: block !important;
            visibility: visible !important;
            overflow: hidden !important;
        }
        
        /* تصحيح موقع القائمة الجانبية */
        .main-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            transition: width 0.3s ease-in-out;
        }
        
        /* أنماط إضافية للتأكد من الرؤية */
        .sidebar {
            padding-top: 0;
            padding-bottom: 1rem;
            overflow-y: auto;
            height: calc(100% - 4.5rem) !important;
        }
    `;
    
    // إضافة العنصر إلى <head>
    document.head.appendChild(styleElement);
    console.log('تمت إضافة الأنماط المطلوبة');
    
    // التحقق من عرض القائمة الحالي
    updateContentMargins();
}