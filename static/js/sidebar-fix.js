
/**
 * إصلاح محسّن لزر القائمة الجانبية في تطبيق وكالة السفر
 * نسخة 2.0 (تتضمن إصلاح مشكلة "القلب")
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف sidebar-fix.js - الإصدار المحسن');
    
    // تعريف متغير للتحكم في حالة القائمة
    let isProcessing = false;
    
    // إضافة مستمع للنقر المباشر على الزر الرئيسي
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    if (sidebarToggleBtn) {
        console.log('تم العثور على زر القائمة #sidebarToggleBtn');
        
        sidebarToggleBtn.addEventListener('click', function(event) {
            if (!isProcessing) {
                handleSidebarToggle(event);
            }
        });
    }
    
    // إصلاح مشكلة الأيقونات في القائمة الجانبية
    fixSidebarIcons();
    
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
    
    // إضافة زر بديل للتبديل (مخفي افتراضيًا على الشاشات الكبيرة)
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
    quickFix.style.display = window.innerWidth < 768 ? 'block' : 'none';
    quickFix.innerHTML = '<span style="font-size: 16px;"><i class="fas fa-bars"></i></span>';
    quickFix.title = 'تبديل القائمة الجانبية';
    
    quickFix.addEventListener('click', function(event) {
        if (!isProcessing) {
            handleSidebarToggle(event);
        }
    });
    
    document.body.appendChild(quickFix);
    
    // مراقبة تغيير حجم النافذة
    window.addEventListener('resize', function() {
        applyResponsiveSettings(window.innerWidth);
        
        // إظهار/إخفاء الزر البديل حسب حجم الشاشة
        quickFix.style.display = window.innerWidth < 768 ? 'block' : 'none';
    });
    
    // استعادة حالة القائمة عند التحميل
    restoreMenuState();
    
    // تطبيق الإعدادات الأولية للتجاوب
    applyResponsiveSettings(window.innerWidth);
    
    // إصلاح أي أيقونات غير مرئية
    setTimeout(fixMissingIcons, 500);
    
    // إضافة فئة إلى الجسم للإشارة إلى أن الجافاسكريبت قد تم تحميله
    document.body.classList.add('js-sidebar-fix-loaded');
    
    // دالة معالجة تبديل القائمة الجانبية
    function handleSidebarToggle(event) {
        if (isProcessing) return;
        
        isProcessing = true;
        console.log('تم النقر على زر القائمة الجانبية');
        toggleSidebar();
        
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        // إعادة تعيين المتغير بعد 300 مللي ثانية (مدة الانتقال)
        setTimeout(() => {
            isProcessing = false;
            fixSidebarIcons(); // إصلاح مشكلة الأيقونات بعد التبديل
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
    
    // إصلاح أي مشاكل مع عرض الأيقونات
    fixSidebarIcons();
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
    
    // إعادة ضبط الأيقونات بعد تغيير عرض النافذة
    fixSidebarIcons();
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

/**
 * إصلاح مشكلة الأيقونات في القائمة الجانبية - حل مشكلة "القلب"
 */
function fixSidebarIcons() {
    // معالجة جميع روابط القائمة الجانبية
    const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
    
    navLinks.forEach(link => {
        const iconElement = link.querySelector('i.nav-icon, i.fas, i.far, i.fa');
        const textElement = link.querySelector('p');
        
        if (iconElement) {
            // تطبيق الأنماط مباشرة على الأيقونات لضمان ظهورها بشكل صحيح
            iconElement.style.display = 'inline-block';
            iconElement.style.visibility = 'visible';
            iconElement.style.width = '1.6rem';
            iconElement.style.marginLeft = '0.7rem';
            iconElement.style.marginRight = '0';
            iconElement.style.textAlign = 'center';
            
            // التحقق مما إذا كانت الأيقونة تحتوي على font-awesome
            if (iconElement.classList.contains('fa') || 
                iconElement.classList.contains('fas') || 
                iconElement.classList.contains('far') || 
                iconElement.classList.contains('fab')) {
                
                // لا تحتاج إلى إضافة أيقونة أخرى
            } else if (iconElement.innerHTML === '') {
                // إضافة محتوى افتراضي للأيقونة إذا كانت فارغة
                iconElement.innerHTML = '&#xf111;'; // رمز دائرة افتراضي
            }
        } else if (textElement) {
            // إنشاء عنصر أيقونة إذا لم يكن موجودًا
            const newIcon = document.createElement('i');
            newIcon.className = 'nav-icon fas fa-circle';
            newIcon.style.display = 'inline-block';
            newIcon.style.visibility = 'visible';
            newIcon.style.width = '1.6rem';
            newIcon.style.marginLeft = '0.7rem';
            newIcon.style.marginRight = '0';
            newIcon.style.textAlign = 'center';
            
            // إدراج الأيقونة قبل النص
            link.insertBefore(newIcon, textElement);
        }
        
        // تأكد من أن النص ظاهر بوضوح ومنسق بشكل صحيح
        if (textElement) {
            textElement.style.display = 'inline-block';
            textElement.style.margin = '0';
            textElement.style.marginRight = '0.3rem';
        }
        
        // ضبط نمط الارتباط نفسه
        link.style.display = 'flex';
        link.style.alignItems = 'center';
        link.style.padding = '0.8rem 1rem';
    });
    
    // معالجة سهم القوائم الفرعية
    const submenuArrows = document.querySelectorAll('.nav-sidebar .nav-link .right');
    submenuArrows.forEach(arrow => {
        if (arrow) {
            arrow.style.position = 'absolute';
            arrow.style.left = '1rem';
            arrow.style.right = 'auto';
        }
    });
}

/**
 * إصلاح الأيقونات المفقودة
 */
function fixMissingIcons() {
    // معالجة جميع الأيقونات في القائمة الجانبية
    document.querySelectorAll('.nav-sidebar .nav-link i').forEach(icon => {
        if (getComputedStyle(icon).display === 'none' || 
            getComputedStyle(icon).visibility === 'hidden' ||
            icon.offsetWidth === 0 || 
            icon.offsetHeight === 0) {
            
            // إصلاح الأيقونة غير المرئية
            icon.style.display = 'inline-block';
            icon.style.visibility = 'visible';
            icon.style.width = '1.6rem';
            icon.style.marginLeft = '0.7rem';
            icon.style.marginRight = '0';
            icon.style.textAlign = 'center';
            
            // إضافة فئة إضافية للمساعدة في التصحيح
            icon.classList.add('fixed-sidebar-icon');
        }
    });
    
    // معالجة عامة للأيقونات في الأزرار
    document.querySelectorAll('.btn i').forEach(icon => {
        if (getComputedStyle(icon).display === 'none' || 
            getComputedStyle(icon).visibility === 'hidden') {
            
            icon.style.display = 'inline-block';
            icon.style.visibility = 'visible';
            icon.style.marginLeft = '0.5rem';
        }
    });
}
