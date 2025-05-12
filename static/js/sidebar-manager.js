/**
 * مدير القائمة الجانبية الموحّد - لحل مشكلة تكرار الأيقونات
 * الإصدار 1.0
 */

// إنشاء متغير عام للإشارة إلى أن الأيقونات قد تمت معالجتها
window.sidebarIconsFixed = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل مدير القائمة الجانبية الموحد');

    // التأكد من أن هذا الملف هو فقط من سيقوم بمعالجة الأيقونات
    document.body.setAttribute('data-sidebar-manager-active', 'true');

    // إزالة الأيقونات المكررة من جميع روابط القائمة
    cleanupSidebarIcons();

    // إضافة المستمعات للنقر على زر تبديل القائمة
    setupSidebarToggle();

    // تطبيق حالة التصغير استنادًا إلى التخزين المحلي
    restoreSidebarState();
});

/**
 * تنظيف أيقونات القائمة الجانبية وإزالة التكرار
 */
function cleanupSidebarIcons() {
    // إذا كانت هناك عملية إصلاح جارية، نتجاهلها
    if (window.sidebarIconsFixed) {
        return;
    }

    // تحديد أننا بدأنا عملية إصلاح الأيقونات
    window.sidebarIconsFixed = true;

    console.log('بدء تنظيف أيقونات القائمة الجانبية...');

    // الحصول على جميع عناصر القائمة
    const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');

    // عداد للإحصائيات
    let iconsRemoved = 0;
    let linksProcessed = 0;

    navLinks.forEach(link => {
        // التعامل مع كل رابط على حدة
        linksProcessed++;

        // إيجاد جميع الأيقونات في الرابط
        const icons = link.querySelectorAll('i.nav-icon, i.fas, i.far, i.fa, i.fab');

        // إذا كان هناك أكثر من أيقونة واحدة، نحتفظ فقط بالأولى
        if (icons.length > 1) {
            // الاحتفاظ بالأيقونة الأولى وإزالة الباقي
            const firstIcon = icons[0];
            
            // وضع علامة على الأيقونة الأولى للإشارة إلى أنها الأصلية
            firstIcon.setAttribute('data-original-icon', 'true');
            
            // إزالة باقي الأيقونات
            for (let i = 1; i < icons.length; i++) {
                icons[i].remove();
                iconsRemoved++;
            }
        }

        // تنسيق الأيقونة المتبقية (إن وجدت)
        const remainingIcon = link.querySelector('i.nav-icon, i.fas, i.far, i.fa, i.fab');
        if (remainingIcon) {
            // تطبيق الأنماط الموحدة على الأيقونة
            remainingIcon.style.display = 'inline-flex';
            remainingIcon.style.alignItems = 'center';
            remainingIcon.style.justifyContent = 'center';
            remainingIcon.style.visibility = 'visible';
            remainingIcon.style.width = '2rem';
            remainingIcon.style.height = '2rem';
            remainingIcon.style.marginLeft = '0.7rem';
            remainingIcon.style.marginRight = '0';
            remainingIcon.style.textAlign = 'center';
            remainingIcon.style.fontSize = '1.25rem';
            remainingIcon.style.color = 'inherit';
        }

        // وضع علامة على الرابط للإشارة إلى أنه تم معالجته
        link.setAttribute('data-icons-cleaned', 'true');
    });

    console.log(`تم معالجة ${linksProcessed} رابط وإزالة ${iconsRemoved} أيقونة مكررة`);
}

/**
 * إعداد زر تبديل القائمة الجانبية
 */
function setupSidebarToggle() {
    // البحث عن كافة أزرار تبديل القائمة في الصفحة
    const toggleButtons = document.querySelectorAll('[data-widget="pushmenu"], .sidebar-toggle, #sidebarToggleBtn, #mainMenuToggleBtn');
    
    console.log('تم العثور على', toggleButtons.length, 'زر تبديل');
    
    // إضافة مستمع حدث لزر تبديل القائمة الرئيسي مباشرة
    const mainToggleBtn = document.getElementById('sidebarToggleBtn');
    if (mainToggleBtn) {
        console.log('إضافة مستمع أحداث لزر التبديل الرئيسي');
        
        // إزالة أي مستمعات أحداث سابقة
        const newBtn = mainToggleBtn.cloneNode(true);
        mainToggleBtn.parentNode.replaceChild(newBtn, mainToggleBtn);
        
        // إضافة مستمع أحداث جديد
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // منع انتشار الحدث
            console.log('تم النقر على زر تبديل القائمة');
            toggleSidebar();
        });
    }
    
    // إضافة مستمعات أحداث لجميع الأزرار الأخرى
    toggleButtons.forEach(button => {
        // تجاهل الزر الرئيسي لأننا تعاملنا معه بالفعل
        if (button.id === 'sidebarToggleBtn') {
            return;
        }
        
        // التحقق مما إذا كان الزر قد تم معالجته مسبقًا
        if (button.hasAttribute('data-toggle-listener-added')) {
            return;
        }
        
        console.log('إضافة مستمع أحداث لزر تبديل إضافي');
        
        // إزالة أي مستمعات أحداث سابقة
        const newBtn = button.cloneNode(true);
        button.parentNode.replaceChild(newBtn, button);
        
        // إضافة مستمع للنقر على الزر
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // منع انتشار الحدث
            console.log('تم النقر على زر تبديل إضافي');
            toggleSidebar();
        });
        
        // وضع علامة على الزر للإشارة إلى أنه تم معالجته
        newBtn.setAttribute('data-toggle-listener-added', 'true');
    });
    
    // إزالة كلاس sidebar-closed عند بدء التشغيل إذا لم تكن مطوية
    if (!document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.remove('sidebar-closed');
    }
}

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    console.log('تبديل القائمة الجانبية');
    
    // حل مشكلة الهاتف المحمول - إضافة فئة sidebar-open للأجهزة الصغيرة
    const windowWidth = window.innerWidth;
    
    if (windowWidth < 768) {
        // للأجهزة المحمولة، نتبدل بين فتح وإغلاق القائمة
        if (document.body.classList.contains('sidebar-open')) {
            // إغلاق القائمة
            document.body.classList.remove('sidebar-open');
            document.body.classList.add('sidebar-collapse', 'sidebar-closed');
            console.log('إغلاق القائمة على الجوال');
        } else {
            // فتح القائمة
            document.body.classList.add('sidebar-open');
            document.body.classList.remove('sidebar-collapse', 'sidebar-closed');
            console.log('فتح القائمة على الجوال');
        }
    } else {
        // للأجهزة الكبيرة، نتبدل بين فتح وطي القائمة
        document.body.classList.toggle('sidebar-collapse');
        
        if (document.body.classList.contains('sidebar-collapse')) {
            document.body.classList.add('sidebar-closed');
            console.log('طي القائمة على الشاشة الكبيرة');
        } else {
            document.body.classList.remove('sidebar-closed');
            console.log('فتح القائمة على الشاشة الكبيرة');
        }
    }
    
    // تحديد حالة القائمة الحالية
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    
    // تحديث العناصر المرتبطة بحالة القائمة
    updateSidebarElements(isCollapsed);
    
    // حفظ الحالة في التخزين المحلي
    localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
}

/**
 * تحديث عناصر القائمة الجانبية بناءً على حالة التصغير
 */
function updateSidebarElements(isCollapsed) {
    console.log('تحديث عناصر القائمة الجانبية', isCollapsed ? 'مطوية' : 'مفتوحة');
    
    const windowWidth = window.innerWidth;
    const sidebar = document.querySelector('.main-sidebar');
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    // لا نقوم بتعيين أنماط CSS مباشرة على العناصر
    // بدلاً من ذلك، نستخدم فئات CSS ونترك AdminLTE
    // يتعامل مع الأنماط
    
    // إذا كان على الهاتف المحمول، لا نقوم بتغيير الهوامش
    if (windowWidth < 768) {
        if (sidebar) {
            // تنظيف الأنماط المضافة سابقاً
            sidebar.style.width = '';
            sidebar.style.transform = '';
            sidebar.style.marginRight = '';
            sidebar.style.transition = '';
        }
        
        if (contentWrapper) contentWrapper.style.marginRight = '';
        if (mainHeader) mainHeader.style.marginRight = '';
        if (mainFooter) mainFooter.style.marginRight = '';
        
        console.log('تمت معالجة القائمة للهاتف المحمول');
    } else {
        // على الشاشات الكبيرة
        if (isCollapsed) {
            // القائمة مطوية
            console.log('تطبيق أنماط القائمة المطوية للشاشات الكبيرة');
            
            // تنظيف أنماط CSS المضافة مباشرة
            if (sidebar) {
                sidebar.removeAttribute('style');
            }
            
            // إخفاء النص على الفور لتحسين الأداء الظاهري
            const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
            navTexts.forEach(text => {
                text.style.display = 'none';
                text.style.visibility = 'hidden';
            });
        } else {
            // القائمة مفتوحة
            console.log('تطبيق أنماط القائمة المفتوحة للشاشات الكبيرة');
            
            // تنظيف أنماط CSS المضافة مباشرة
            if (sidebar) {
                sidebar.removeAttribute('style');
            }
            
            // إظهار النص
            const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
            navTexts.forEach(text => {
                text.style.display = '';
                text.style.visibility = '';
            });
        }
    }
    
    // تنظيف دالي الحالة والأنماط المضافة
    setTimeout(() => {
        cleanupStyles();
    }, 500);
}

/**
 * تنظيف الأنماط المضافة مباشرة للعناصر
 */
function cleanupStyles() {
    // إزالة أي أنماط قد تكون تسببت في مشاكل
    const sidebar = document.querySelector('.main-sidebar');
    if (sidebar) {
        // إعادة الأنماط الافتراضية فقط
        sidebar.style.position = 'fixed';
        sidebar.style.top = '0';
        sidebar.style.bottom = '0';
        sidebar.style.overflowY = 'hidden';
    }
}

/**
 * استعادة حالة القائمة الجانبية من التخزين المحلي
 */
function restoreSidebarState() {
    const savedState = localStorage.getItem('sidebar-collapsed');
    
    if (savedState === 'true' && !document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.add('sidebar-collapse');
        updateSidebarElements(true);
    } else if (savedState === 'false' && document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.remove('sidebar-collapse');
        updateSidebarElements(false);
    }
}

// استدعاء تنظيف الأيقونات عند تغيير حجم النافذة
window.addEventListener('resize', function() {
    updateSidebarElements(document.body.classList.contains('sidebar-collapse'));
});

// تعطيل الوظائف المشابهة في ملفات JavaScript الأخرى لمنع التكرار
window.disableConflictingFunctions = function() {
    console.log('منع تكرار وظائف القائمة الجانبية');
    
    // تعطيل الوظائف في sidebar-fix.js
    if (window.fixSidebarIcons && window.fixSidebarIcons !== cleanupSidebarIcons) {
        window.fixSidebarIcons = function() {
            console.log('تم تجاهل fixSidebarIcons من ملف آخر');
            return;
        };
    }
    
    // تعطيل وظائف في mini-sidebar.js
    if (window.setupMiniSidebar) {
        window.setupMiniSidebar = function() {
            console.log('تم تجاهل setupMiniSidebar من ملف آخر');
            return;
        };
    }
    
    if (window.enhanceSidebarIcons) {
        window.enhanceSidebarIcons = function() {
            console.log('تم تجاهل enhanceSidebarIcons من ملف آخر');
            return;
        };
    }
    
    // تعطيل الوظائف في custom.js
    if (window.fixRtlSidebar) {
        const originalFixRtlSidebar = window.fixRtlSidebar;
        
        window.fixRtlSidebar = function() {
            console.log('تعديل سلوك fixRtlSidebar لمنع التكرار');
            
            // نطلب الوظيفة الأصلية ولكن نتجاهل جزء الأيقونات
            // تطبيق إصلاحات الأنماط فقط دون إضافة أو تعديل الأيقونات
            const mainSidebar = document.querySelector('.main-sidebar');
            if (mainSidebar) {
                mainSidebar.style.minHeight = '100vh';
                mainSidebar.style.height = '100%';
                mainSidebar.style.position = 'fixed';
            }
            
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.height = 'calc(100% - 4.5rem)';
                sidebar.style.overflowY = 'auto';
                sidebar.style.paddingBottom = '0';
                sidebar.style.paddingRight = '0.5rem';
                sidebar.style.paddingLeft = '0.5rem';
            }
            
            // لا نقوم بتطبيق تعديلات الأيقونات
            
            // استدعاء fixMobileSidebar إذا كان حجم النافذة صغيرًا
            if (window.innerWidth <= 767.98 && window.fixMobileSidebar) {
                window.fixMobileSidebar();
            }
        };
    }
};

// تنفيذ دالة تعطيل الوظائف المتضاربة فورًا
window.disableConflictingFunctions();

// إزالة أي أزرار قائمة إضافية تم إنشاؤها
function removeExtraToggleButtons() {
    // نحن نعرف أن الزر الأصلي هو #sidebarToggleBtn
    // نبحث عن الأزرار الأخرى مثل mainMenuToggleBtn وما إلى ذلك
    setTimeout(() => {
        const mainMenuBtn = document.getElementById('mainMenuToggleBtn');
        if (mainMenuBtn && mainMenuBtn !== document.getElementById('sidebarToggleBtn')) {
            console.log('إزالة زر قائمة إضافي: mainMenuToggleBtn');
            mainMenuBtn.remove();
        }
        
        // تجميع الأزرار الزائدة من السمات المحددة
        const extraButtons = document.querySelectorAll('[data-widget="pushmenu"]:not(#sidebarToggleBtn)');
        extraButtons.forEach(btn => {
            if (btn && btn !== document.getElementById('sidebarToggleBtn')) {
                console.log('إزالة زر قائمة إضافي بسمة data-widget="pushmenu"');
                btn.remove();
            }
        });
        
        const quickFixBtn = document.getElementById('quickFixSidebarBtn');
        if (quickFixBtn) {
            console.log('إزالة زر إصلاح سريع: quickFixSidebarBtn');
            quickFixBtn.remove();
        }
    }, 100);
}

// تنفيذ دالة إزالة الأزرار الإضافية
removeExtraToggleButtons();