/**
 * إصلاح بسيط لزر القائمة الجانبية في تطبيق وكالة السفر
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف sidebar-fix.js - الإصدار المحسن');
    
    // إضافة مستمع للنقر المباشر على الزر الجديد المضاف
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    if (sidebarToggleBtn) {
        console.log('تم العثور على زر القائمة #sidebarToggleBtn');
        
        sidebarToggleBtn.addEventListener('click', function(event) {
            console.log('تم النقر على زر القائمة الجانبية');
            toggleSidebar();
            event.preventDefault();
            event.stopPropagation();
        });
    } else {
        console.log('لم يتم العثور على زر القائمة، سيتم إضافة زر بديل');
    }
    
    // إضافة معالج عام للصفحة بأكملها لالتقاط النقرات على الأزرار التي قد لا يتم اكتشافها بطريقة مباشرة
    document.body.addEventListener('click', function(event) {
        // التحقق مما إذا كان العنصر المنقور عليه أو أحد آبائه هو زر القائمة
        const clickedElement = event.target;
        
        // التحقق مما إذا كان العنصر المنقور هو زر القائمة أو أحد عناصره الفرعية
        if (clickedElement.closest('#sidebarToggleBtn') || 
            clickedElement.closest('.fa-bars') || 
            (clickedElement.tagName === 'I' && clickedElement.classList.contains('fa-bars'))) {
            
            console.log('تم النقر على زر القائمة من خلال المعالج العام');
            toggleSidebar();
            event.preventDefault();
            event.stopPropagation();
        }
    });
    
    // وسم مخصص للنقر السريع - احتياطي في حالة عدم عمل الزر الأساسي
    const quickFix = document.createElement('div');
    quickFix.id = 'quickFixSidebarBtn';
    quickFix.style.position = 'fixed';
    quickFix.style.top = '60px'; // تعديل الموضع ليكون أسفل الشريط العلوي
    quickFix.style.right = '10px';
    quickFix.style.zIndex = '9999';
    quickFix.style.padding = '5px 10px';
    quickFix.style.background = '#4e73df';
    quickFix.style.color = 'white';
    quickFix.style.border = 'none';
    quickFix.style.borderRadius = '4px';
    quickFix.style.cursor = 'pointer';
    quickFix.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    quickFix.innerHTML = '<span style="font-size: 16px;"><i class="fas fa-bars"></i></span>';
    quickFix.title = 'تبديل القائمة الجانبية (بديل)';
    
    quickFix.addEventListener('click', function(event) {
        console.log('تم النقر على زر الإصلاح السريع البديل');
        toggleSidebar();
        event.stopPropagation();
    });
    
    document.body.appendChild(quickFix);
    
    // مراقبة تغيير حجم النافذة لتطبيق الإعدادات المستجيبة
    window.addEventListener('resize', function() {
        console.log('تم تغيير حجم النافذة');
        applyResponsiveSettings(window.innerWidth);
    });
    
    // استعادة حالة القائمة من التخزين المحلي عند التحميل
    restoreMenuState();
    
    // تطبيق الإعدادات الأولية للتجاوب
    applyResponsiveSettings(window.innerWidth);
    
    // إضافة فئة إلى الجسم للإشارة إلى أن الجافاسكريبت قد تم تحميله
    document.body.classList.add('js-sidebar-fix-loaded');
});

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    console.log('بدء تبديل حالة القائمة');
    
    // الحصول على حجم النافذة الحالي
    const windowWidth = window.innerWidth;
    
    // تبديل الفئات في الجسم
    document.body.classList.toggle('sidebar-collapse');
    
    if (document.body.classList.contains('sidebar-collapse')) {
        // عند إغلاق القائمة
        document.body.classList.remove('sidebar-open');
        
        // تعديل هوامش المحتوى حسب حجم الشاشة
        if (windowWidth >= 992) {
            // سطح المكتب - نظهر القائمة المصغرة
            setContentMargins('4.6rem');
        } else {
            // الأجهزة الصغيرة - نغلق القائمة تمامًا
            setContentMargins('0');
        }
    } else {
        // عند فتح القائمة
        document.body.classList.add('sidebar-open');
        
        // تعديل هوامش المحتوى - للشاشات الكبيرة فقط
        if (windowWidth >= 768) {
            setContentMargins('250px');
        }
    }
    
    // تطبيق التعديلات المناسبة حسب حجم الشاشة
    applyResponsiveSettings(windowWidth);
    
    // تذكر حالة القائمة
    saveMenuState();
}

/**
 * ضبط هوامش المحتوى
 */
function setContentMargins(margin) {
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    // تطبيق الهوامش فقط للشاشات المتوسطة والكبيرة
    if (window.innerWidth >= 768) {
        if (contentWrapper) contentWrapper.style.marginRight = margin;
        if (mainHeader) mainHeader.style.marginRight = margin;
        if (mainFooter) mainFooter.style.marginRight = margin;
    }
}

/**
 * تطبيق الإعدادات المستجيبة حسب حجم الشاشة
 */
function applyResponsiveSettings(windowWidth) {
    const mainSidebar = document.querySelector('.main-sidebar');
    
    if (!mainSidebar) return;
    
    if (windowWidth < 768) {
        // الشاشات الصغيرة (الجوال)
        mainSidebar.style.width = '250px';
        mainSidebar.style.position = 'fixed';
        
        if (document.body.classList.contains('sidebar-open')) {
            mainSidebar.style.right = '0';
        } else {
            mainSidebar.style.right = '-250px';
        }
        
    } else if (windowWidth >= 768 && windowWidth < 992) {
        // الشاشات المتوسطة (تابلت)
        if (document.body.classList.contains('sidebar-collapse')) {
            mainSidebar.style.width = '0';
            mainSidebar.style.overflow = 'hidden';
        } else {
            mainSidebar.style.width = '250px';
            mainSidebar.style.overflow = 'visible';
        }
        
        mainSidebar.style.right = '0';
        
    } else {
        // الشاشات الكبيرة (سطح المكتب)
        mainSidebar.style.right = '0';
        
        if (document.body.classList.contains('sidebar-collapse')) {
            mainSidebar.style.width = '4.6rem';
        } else {
            mainSidebar.style.width = '250px';
        }
    }
}

/**
 * حفظ حالة القائمة في التخزين المحلي
 */
function saveMenuState() {
    const state = document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded';
    localStorage.setItem('sidebar-state', state);
}

/**
 * استعادة حالة القائمة من التخزين المحلي
 */
function restoreMenuState() {
    const savedState = localStorage.getItem('sidebar-state');
    const windowWidth = window.innerWidth;
    
    // لا نستعيد الحالة للشاشات الصغيرة، نجعل القائمة مغلقة دائمًا
    if (windowWidth < 768) {
        document.body.classList.remove('sidebar-open');
        document.body.classList.add('sidebar-collapse');
        return;
    }
    
    if (savedState === 'collapsed') {
        document.body.classList.add('sidebar-collapse');
        document.body.classList.remove('sidebar-open');
        
        // تعديل هوامش المحتوى حسب حجم الشاشة
        if (windowWidth >= 992) {
            setContentMargins('4.6rem');
        } else {
            setContentMargins('0');
        }
    } else if (savedState === 'expanded') {
        document.body.classList.remove('sidebar-collapse');
        document.body.classList.add('sidebar-open');
        
        // تعديل الهوامش - للشاشات الكبيرة فقط
        if (windowWidth >= 768) {
            setContentMargins('250px');
        }
    }
    
    // تطبيق الإعدادات المستجيبة
    applyResponsiveSettings(windowWidth);
}