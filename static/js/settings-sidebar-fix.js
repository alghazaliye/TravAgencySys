/**
 * إصلاح خاص لقائمة الإعدادات في القائمة الجانبية
 * 
 * هذا الملف هو حل بديل مبسط لمشكلة عدم فتح قائمة الإعدادات
 * الجانبية عند النقر عليها.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('جارٍ تطبيق إصلاح خاص لقائمة الإعدادات...');

    // تنفيذ الإصلاح بعد فترة قصيرة من تحميل الصفحة
    setTimeout(function() {
        // البحث عن رابط قائمة الإعدادات
        const settingsLinks = Array.from(document.querySelectorAll('.nav-link')).filter(
            link => link.textContent.includes('الإعدادات')
        );

        if (settingsLinks.length > 0) {
            console.log('تم العثور على رابط الإعدادات، جارٍ فتح القائمة الفرعية...');
            const settingsLink = settingsLinks[0];
            const parentLi = settingsLink.closest('.has-treeview');
            
            if (parentLi) {
                // تعيين الفئات المناسبة لفتح القائمة
                parentLi.classList.add('menu-open');
                
                // العثور على القائمة الفرعية وإظهارها
                const submenu = parentLi.querySelector('.nav-treeview');
                if (submenu) {
                    submenu.style.display = 'block';
                    
                    // تحسين مظهر روابط القائمة الفرعية
                    const subLinks = submenu.querySelectorAll('.nav-link');
                    subLinks.forEach(link => {
                        link.style.paddingRight = '2.5rem';
                        
                        // تحديد الرابط النشط
                        if (link.getAttribute('href') === window.location.pathname) {
                            link.classList.add('active');
                        }
                    });
                }
            }
        }
        
        // معالجة النقر على رابط الإعدادات
        document.body.addEventListener('click', function(e) {
            // البحث عن العنصر الذي تم النقر عليه
            const clickedElement = e.target;
            
            // التحقق مما إذا كان العنصر المنقور هو رابط الإعدادات أو أحد العناصر داخله
            const settingsLink = clickedElement.closest('.nav-link');
            if (settingsLink && settingsLink.textContent.includes('الإعدادات')) {
                e.preventDefault();
                
                const parentLi = settingsLink.closest('.has-treeview');
                if (parentLi) {
                    parentLi.classList.add('menu-open');
                    
                    const submenu = parentLi.querySelector('.nav-treeview');
                    if (submenu) {
                        submenu.style.display = 'block';
                    }
                }
            }
        });
        
    }, 500);
});