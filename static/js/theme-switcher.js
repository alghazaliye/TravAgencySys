/**
 * ملف JavaScript للتحكم في تبديل الوضع الليلي والنهاري
 */

// تهيئة متغيرات إدارة الوضع المظلم/الفاتح
let currentTheme = localStorage.getItem('theme') || 'auto';
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const htmlElement = document.documentElement;

// دالة وضع نمط معين
function setTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    htmlElement.setAttribute('data-theme', theme);
    
    // تحديث أيقونة الزر
    if (themeToggleBtn) {
        if (getEffectiveTheme() === 'dark') {
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggleBtn.title = 'تبديل إلى الوضع النهاري';
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggleBtn.title = 'تبديل إلى الوضع الليلي';
        }
    }
}

// دالة للحصول على الوضع الفعلي بناءً على الإعدادات وتفضيلات النظام
function getEffectiveTheme() {
    if (currentTheme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return currentTheme;
}

// تهيئة الوضع عند تحميل الصفحة
function initTheme() {
    // تحميل القيمة المخزنة محلياً (إن وجدت)
    setTheme(currentTheme);
    
    // إضافة استماع لتفضيلات النظام
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (currentTheme === 'auto') {
            setTheme('auto'); // سيقوم بتحديث الأيقونة بناءً على القيمة الجديدة
        }
    });
    
    // استماع لنقرات زر تبديل الوضع
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // تبديل بين الأوضاع الثلاثة: النهاري، الليلي، التلقائي
            if (currentTheme === 'light') {
                setTheme('dark');
            } else if (currentTheme === 'dark') {
                setTheme('auto');
            } else {
                setTheme('light');
            }
        });
    }
}

// تهيئة عند تحميل المستند
document.addEventListener('DOMContentLoaded', initTheme);