
/**
 * إصلاح بسيط لزر القائمة الجانبية في تطبيق وكالة السفر
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف sidebar-fix.js - الإصدار المحسن');
    
    // تعريف متغير للتحكم في حالة القائمة
    let isProcessing = false;
    
    // إضافة مستمع للنقر المباشر على الزر الجديد المضاف
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    if (sidebarToggleBtn) {
        console.log('تم العثور على زر القائمة #sidebarToggleBtn');
        
        sidebarToggleBtn.addEventListener('click', function(event) {
            if (!isProcessing) {
                handleSidebarToggle(event);
            }
        });
    }
    
    // إضافة معالج عام للصفحة بأكملها لالتقاط النقرات على الأزرار
    document.body.addEventListener('click', function(event) {
        if (!isProcessing) {
            const clickedElement = event.target;
            
            if (clickedElement.closest('#sidebarToggleBtn') || 
                clickedElement.closest('.fa-bars') || 
                (clickedElement.tagName === 'I' && clickedElement.classList.contains('fa-bars'))) {
                
                handleSidebarToggle(event);
            }
        }
    });
    
    // وسم مخصص للنقر السريع
    const quickFix = document.createElement('div');
    quickFix.id = 'quickFixSidebarBtn';
    quickFix.style.position = 'fixed';
    quickFix.style.top = '60px';
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
        if (!isProcessing) {
            handleSidebarToggle(event);
        }
    });
    
    document.body.appendChild(quickFix);
    
    // مراقبة تغيير حجم النافذة
    window.addEventListener('resize', function() {
        applyResponsiveSettings(window.innerWidth);
    });
    
    // استعادة حالة القائمة عند التحميل
    restoreMenuState();
    
    // تطبيق الإعدادات الأولية للتجاوب
    applyResponsiveSettings(window.innerWidth);
    
    // إضافة فئة إلى الجسم للإشارة إلى أن الجافاسكريبت قد تم تحميله
    document.body.classList.add('js-sidebar-fix-loaded');
    
    // دالة معالجة تبديل القائمة الجانبية
    function handleSidebarToggle(event) {
        if (isProcessing) return;
        
        isProcessing = true;
        console.log('تم النقر على زر القائمة الجانبية');
        toggleSidebar();
        event.preventDefault();
        event.stopPropagation();
        
        // إعادة تعيين المتغير بعد 300 مللي ثانية (مدة الانتقال)
        setTimeout(() => {
            isProcessing = false;
        }, 300);
    }
});

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    console.log('بدء تبديل حالة القائمة');
    
    const windowWidth = window.innerWidth;
    document.body.classList.toggle('sidebar-collapse');
    
    if (document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.remove('sidebar-open');
        
        if (windowWidth >= 992) {
            setContentMargins('4.6rem');
        } else {
            setContentMargins('0');
        }
    } else {
        document.body.classList.add('sidebar-open');
        
        if (windowWidth >= 768) {
            setContentMargins('250px');
        }
    }
    
    applyResponsiveSettings(windowWidth);
    saveMenuState();
}

/**
 * ضبط هوامش المحتوى
 */
function setContentMargins(margin) {
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    if (window.innerWidth >= 768) {
        if (contentWrapper) contentWrapper.style.marginRight = margin;
        if (mainHeader) mainHeader.style.marginRight = margin;
        if (mainFooter) mainFooter.style.marginRight = margin;
    }
    
    // تطبيق الإعدادات على متغير CSS لعرض القائمة الجانبية
    document.documentElement.style.setProperty('--sidebar-width', margin);
}

/**
 * تطبيق الإعدادات المستجيبة
 */
function applyResponsiveSettings(windowWidth) {
    const mainSidebar = document.querySelector('.main-sidebar');
    if (!mainSidebar) return;
    
    // الحصول على قيمة إعداد sidebar_mini
    const sidebarMini = document.body.classList.contains('sidebar-mini');
    const collapsedWidth = sidebarMini ? '4.6rem' : '0';
    
    if (windowWidth < 768) {
        mainSidebar.style.width = '250px';
        mainSidebar.style.position = 'fixed';
        
        if (document.body.classList.contains('sidebar-open')) {
            mainSidebar.style.right = '0';
        } else {
            mainSidebar.style.right = '-250px';
        }
    } else if (windowWidth >= 768 && windowWidth < 992) {
        if (document.body.classList.contains('sidebar-collapse')) {
            mainSidebar.style.width = collapsedWidth;
            mainSidebar.style.overflow = 'hidden';
        } else {
            mainSidebar.style.width = '250px';
            mainSidebar.style.overflow = 'visible';
        }
        mainSidebar.style.right = '0';
    } else {
        mainSidebar.style.right = '0';
        
        if (document.body.classList.contains('sidebar-collapse')) {
            mainSidebar.style.width = collapsedWidth;
        } else {
            mainSidebar.style.width = '250px';
        }
    }
    
    // تطبيق الأسلوب على العناصر الموجودة داخل القائمة الجانبية في حالة القائمة المصغرة
    if (sidebarMini) {
        const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
        navLinks.forEach(link => {
            if (document.body.classList.contains('sidebar-collapse')) {
                link.classList.add('sidebar-mini-link');
            } else {
                link.classList.remove('sidebar-mini-link');
            }
        });
    }
}

/**
 * حفظ حالة القائمة
 */
function saveMenuState() {
    const state = document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded';
    localStorage.setItem('sidebar-state', state);
}

/**
 * استعادة حالة القائمة
 */
function restoreMenuState() {
    const savedState = localStorage.getItem('sidebar-state');
    const windowWidth = window.innerWidth;
    
    if (windowWidth < 768) {
        document.body.classList.remove('sidebar-open');
        document.body.classList.add('sidebar-collapse');
        return;
    }
    
    if (savedState === 'collapsed') {
        document.body.classList.add('sidebar-collapse');
        document.body.classList.remove('sidebar-open');
        
        if (windowWidth >= 992) {
            setContentMargins('4.6rem');
        } else {
            setContentMargins('0');
        }
    } else if (savedState === 'expanded') {
        document.body.classList.remove('sidebar-collapse');
        document.body.classList.add('sidebar-open');
        
        if (windowWidth >= 768) {
            setContentMargins('250px');
        }
    }
    
    applyResponsiveSettings(windowWidth);
}
