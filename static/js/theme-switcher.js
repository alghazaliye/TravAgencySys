/**
 * إدارة السمة للواجهة العربية (ضوء/ظلام)
 * النسخة 1.0
 */

// انتظار تحميل DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    createThemeToggle();
});

/**
 * تهيئة السمة عند التحميل
 */
function initializeTheme() {
    // التحقق من وجود تفضيل مخزن
    const savedTheme = localStorage.getItem('travel-theme');
    
    // تطبيق السمة المحفوظة أو الافتراضية
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        console.log('تم تحميل السمة المحفوظة:', savedTheme);
    } else {
        // التحقق من تفضيل الوضع الداكن في النظام
        const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (prefersDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            console.log('تم تطبيق الوضع الداكن استنادًا إلى تفضيل المتصفح');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            console.log('تم تطبيق الوضع الفاتح افتراضيًا');
        }
    }
}

/**
 * إنشاء زر تبديل السمة
 */
function createThemeToggle() {
    // إنشاء زر تبديل السمة
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle-container';
    themeToggle.setAttribute('aria-label', 'تبديل بين السمة الفاتحة والداكنة');
    themeToggle.innerHTML = '<i class="fas fa-sun theme-toggle-icon"></i><i class="fas fa-moon theme-toggle-icon"></i>';
    themeToggle.title = 'تبديل السمة';
    
    // إضافة الزر للصفحة
    document.body.appendChild(themeToggle);
    
    // معالج حدث النقر
    themeToggle.addEventListener('click', toggleTheme);
    
    // تحديث أيقونة الزر الأولية
    updateToggleIcon();
}

/**
 * تبديل السمة
 */
function toggleTheme() {
    // الحصول على السمة الحالية
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    // تبديل السمة
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // تحديث السمة
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // حفظ التفضيل
    localStorage.setItem('travel-theme', newTheme);
    
    // تحديث المظهر المرئي
    updateToggleIcon();
    
    // سجل التغيير
    console.log('تم التبديل إلى السمة:', newTheme);
    
    // إضافة تأثير تحول على مستوى الصفحة
    addPageTransitionEffect();
}

/**
 * تحديث أيقونة الزر
 */
function updateToggleIcon() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themeToggle = document.querySelector('.theme-toggle-container');
    
    if (!themeToggle) return;
    
    // تحديث نص التلميح
    themeToggle.title = currentTheme === 'dark' 
        ? 'التبديل إلى الوضع الفاتح' 
        : 'التبديل إلى الوضع الداكن';
}

/**
 * إضافة تأثير انتقالي للصفحة عند تغيير السمة
 */
function addPageTransitionEffect() {
    // إنشاء عنصر التأثير
    const transitionEl = document.createElement('div');
    transitionEl.style.position = 'fixed';
    transitionEl.style.top = '0';
    transitionEl.style.left = '0';
    transitionEl.style.width = '100%';
    transitionEl.style.height = '100%';
    transitionEl.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    transitionEl.style.opacity = '0';
    transitionEl.style.transition = 'opacity 0.3s ease';
    transitionEl.style.pointerEvents = 'none';
    transitionEl.style.zIndex = '9999';
    
    // إضافة العنصر للصفحة
    document.body.appendChild(transitionEl);
    
    // تطبيق التأثير
    setTimeout(() => {
        transitionEl.style.opacity = '1';
        
        setTimeout(() => {
            transitionEl.style.opacity = '0';
            
            setTimeout(() => {
                document.body.removeChild(transitionEl);
            }, 300);
        }, 200);
    }, 0);
}

/**
 * الاستماع لتغيرات في تفضيل الوضع الداكن على مستوى النظام
 */
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        const newTheme = e.matches ? 'dark' : 'light';
        
        // تحديث السمة فقط إذا لم يضبط المستخدم تفضيله بشكل مباشر
        if (!localStorage.getItem('travel-theme')) {
            document.documentElement.setAttribute('data-theme', newTheme);
            updateToggleIcon();
            console.log('تم تغيير السمة تلقائيًا استنادًا إلى تفضيلات النظام:', newTheme);
        }
    });
}