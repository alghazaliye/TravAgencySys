/**
 * إصلاح مشكلة التنقل في القائمة الجانبية الشجرية (has-treeview)
 * خاص بمشكلة عدم فتح القوائم الفرعية عند النقر عليها
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('بدء تهيئة إصلاح القائمة الشجرية...');
    
    setupDirectMenuLinks();
    
    function setupDirectMenuLinks() {
        // إضافة مستمعات الأحداث للنقر على عناصر القائمة التي تحتوي على قوائم فرعية
        const treeviewItems = document.querySelectorAll('.nav-item.has-treeview > .nav-link');
        
        // إصلاح خاص لقسم الإعدادات
        const settingsMenu = document.querySelector('.nav-item.has-treeview:has(i.fa-cogs)');
        if (settingsMenu) {
            console.log('تم العثور على قائمة الإعدادات، جارٍ تطبيق الإصلاح...');
            const settingsLink = settingsMenu.querySelector('.nav-link');
            if (settingsLink) {
                // تحديث النص لزيادة قابلية التمييز
                settingsLink.setAttribute('data-section', 'settings');
                settingsLink.style.fontWeight = 'bold';
            }
            
            // التأكد من أن القائمة الفرعية قابلة للنقر
            const submenu = settingsMenu.querySelector('.nav-treeview');
            if (submenu) {
                submenu.style.display = 'block';
                submenu.style.height = 'auto';
                submenu.style.overflow = 'visible';
                submenu.style.opacity = '1';
                
                // تحديث جميع الروابط في القائمة الفرعية للإعدادات
                const subLinks = submenu.querySelectorAll('.nav-link');
                subLinks.forEach(link => {
                    link.style.paddingRight = '2.5rem';
                    link.style.fontWeight = 'normal';
                });
            }
            
            // إضافة فئة menu-open للقائمة
            settingsMenu.classList.add('menu-open');
            
            // بعد تهيئة الصفحة بفترة قصيرة، قم بتطبيق الإصلاح مرة أخرى للتأكد
            setTimeout(() => {
                settingsMenu.classList.add('menu-open');
                if (submenu) {
                    submenu.style.display = 'block';
                    submenu.style.height = 'auto';
                }
            }, 500);
        }
        
        treeviewItems.forEach(function(item) {
            // إزالة أي مستمعات أحداث سابقة
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);
            
            // إضافة خاصية data للتعرف على نوع القائمة
            if (newItem.querySelector('i.fa-cogs')) {
                newItem.setAttribute('data-menu-type', 'settings');
            }
            
            // إضافة مستمع حدث جديد للنقر
            newItem.addEventListener('click', function(event) {
                event.preventDefault();
                
                // الحصول على العنصر الأب (li.has-treeview)
                const parentItem = this.parentNode;
                
                // علاج خاص لقسم الإعدادات
                if (this.getAttribute('data-menu-type') === 'settings' || 
                    this.getAttribute('data-section') === 'settings' ||
                    this.textContent.includes('الإعدادات')) {
                    console.log('تم النقر على قائمة الإعدادات...');
                    parentItem.classList.add('menu-open');
                    
                    const submenu = parentItem.querySelector('.nav-treeview');
                    if (submenu) {
                        submenu.style.display = 'block';
                        submenu.style.height = 'auto';
                        submenu.style.maxHeight = '500px';
                        submenu.style.overflow = 'visible';
                        submenu.style.opacity = '1';
                    }
                    return;
                }
                
                // تبديل فئة menu-open على العنصر الأب
                parentItem.classList.toggle('menu-open');
                
                // التحكم في إظهار/إخفاء القائمة الفرعية
                const submenu = parentItem.querySelector('.nav-treeview');
                if (submenu) {
                    if (parentItem.classList.contains('menu-open')) {
                        // فتح القائمة الفرعية
                        submenu.style.display = 'block';
                        // إذا كان الارتفاع مخفياً، قم بإظهاره تدريجياً
                        if (submenu.style.maxHeight === '0px' || !submenu.style.maxHeight) {
                            submenu.style.transition = 'max-height 0.3s ease-in';
                            submenu.style.maxHeight = submenu.scrollHeight + 'px';
                        }
                    } else {
                        // إغلاق القائمة الفرعية بالتدريج
                        submenu.style.transition = 'max-height 0.3s ease-out';
                        submenu.style.maxHeight = '0px';
                        // بعد انتهاء الانتقال، قم بإخفاء العنصر
                        setTimeout(function() {
                            submenu.style.display = 'none';
                        }, 300);
                    }
                }
                
                console.log('تم النقر على عنصر القائمة الشجرية:', this.textContent.trim());
            });
        });
    }
    
    // التأكد من أن جميع القوائم الفرعية لديها الأنماط المناسبة
    const allTreeViews = document.querySelectorAll('.nav-treeview');
    allTreeViews.forEach(function(treeview) {
        // تهيئة أنماط القوائم الفرعية
        const parentItem = treeview.closest('.has-treeview');
        if (parentItem && parentItem.classList.contains('menu-open')) {
            treeview.style.display = 'block';
            treeview.style.maxHeight = treeview.scrollHeight + 'px';
        } else {
            treeview.style.display = 'none';
            treeview.style.maxHeight = '0px';
        }
    });
    
    // تحديد القوائم المفتوحة حالياً بناءً على الصفحة الحالية
    highlightCurrentPage();
    
    console.log('تم تهيئة إصلاح القائمة الشجرية بنجاح.');
});

/**
 * تحديد الصفحة الحالية في القائمة الجانبية
 */
function highlightCurrentPage() {
    // الحصول على مسار URL الحالي
    const currentPath = window.location.pathname;
    
    // البحث عن الرابط المطابق في القائمة
    const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
    
    // متغير لتخزين الرابط النشط الذي تم العثور عليه
    let activeLink = null;
    
    // البحث عن الرابط المطابق تماماً
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && href === currentPath) {
            activeLink = link;
            // إضافة فئة active للرابط
            link.classList.add('active');
            // البحث عن العنصر الأب has-treeview وفتحه
            const parentTreeview = link.closest('.has-treeview');
            if (parentTreeview) {
                parentTreeview.classList.add('menu-open');
                const submenu = parentTreeview.querySelector('.nav-treeview');
                if (submenu) {
                    submenu.style.display = 'block';
                    submenu.style.maxHeight = submenu.scrollHeight + 'px';
                }
            }
        }
    });
    
    // إذا لم يتم العثور على تطابق تام، ابحث عن تطابق جزئي
    if (!activeLink) {
        navLinks.forEach(function(link) {
            const href = link.getAttribute('href');
            if (href && href !== '#' && currentPath.includes(href) && href !== '/') {
                // إضافة فئة active للرابط
                link.classList.add('active');
                // البحث عن العنصر الأب has-treeview وفتحه
                const parentTreeview = link.closest('.has-treeview');
                if (parentTreeview) {
                    parentTreeview.classList.add('menu-open');
                    const submenu = parentTreeview.querySelector('.nav-treeview');
                    if (submenu) {
                        submenu.style.display = 'block';
                        submenu.style.maxHeight = submenu.scrollHeight + 'px';
                    }
                }
            }
        });
    }
}