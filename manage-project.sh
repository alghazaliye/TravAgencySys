#!/bin/bash

# ------ إعدادات قابلة للتخصيص ------
PROJECT_DIR="$HOME/TravAgencySys"  # مسار قابل للكتابة بدون صلاحيات root
GIT_REPO="https://github.com/alghazaliye/TravAgencySys.git"
BACKUP_DIR="$HOME/backups"         # مسار النسخ الاحتياطي
DEPLOY_DIR="$HOME/public_html"     # مسار النشر النهائي
DEPLOY_BRANCH="main"

# ------ الألوان للعرض ------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ------ التحقق من المتطلبات الأساسية ------
function check_requirements() {
    local missing=()
    
    # التحقق من وجود الأدوات الأساسية
    command -v git >/dev/null 2>&1 || missing+=("git")
    command -v tar >/dev/null 2>&1 || missing+=("tar")
    command -v rsync >/dev/null 2>&1 || missing+=("rsync")
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}الأدوات التالية مفقودة:${NC} ${missing[*]}"
        echo -e "${YELLOW}جاري التثبيت التلقائي...${NC}"
        sudo apt-get update && sudo apt-get install -y "${missing[@]}"
    fi
}

# ------ إعداد المشروع ------
function setup_project() {
    echo -e "${YELLOW}جاري إعداد المشروع في: $PROJECT_DIR${NC}"
    
    if [ -d "$PROJECT_DIR" ]; then
        echo -e "${YELLOW}المجلد موجود مسبقًا، جاري التحديث...${NC}"
        cd "$PROJECT_DIR" || exit 1
        if [ -d .git ]; then
            git pull origin "$DEPLOY_BRANCH"
        else
            echo -e "${RED}المجلد ليس مستودع git!${NC}"
            exit 1
        fi
    else
        git clone "$GIT_REPO" "$PROJECT_DIR" || {
            echo -e "${RED}فشل في استنساخ المستودع!${NC}"
            exit 1
        }
    fi
    
    echo -e "${GREEN}تم الإعداد/التحديث بنجاح!${NC}"
}

# ------ عمليات Git ------
function git_operations() {
    echo -e "${YELLOW}جاري مزامنة المستودع...${NC}"
    
    cd "$PROJECT_DIR" || exit 1
    
    if [ ! -d .git ]; then
        echo -e "${RED}هذا المسار ليس مستودع git!${NC}"
        exit 1
    fi
    
    # جلب أحدث التغييرات
    git fetch origin
    
    # المزامنة مع الفرع الرئيسي
    git checkout "$DEPLOY_BRANCH"
    git merge "origin/$DEPLOY_BRANCH"
    
    # إضافة التغييرات
    git add -A
    
    if git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}لا يوجد تغييرات جديدة.${NC}"
    else
        git commit -m "تحديث تلقائي: $(date +'%Y-%m-%d %H:%M')"
        git push origin "$DEPLOY_BRANCH"
        echo -e "${GREEN}تمت المزامنة مع GitHub!${NC}"
    fi
}

# ------ النشر ------
function deploy() {
    echo -e "${YELLOW}جاري النشر إلى: $DEPLOY_DIR${NC}"
    
    # إنشاء مجلد النشر إذا لم يكن موجودًا
    mkdir -p "$DEPLOY_DIR"
    
    # نسخ الملفات مع الحفاظ على الصلاحيات
    rsync -av --delete \
        --exclude='.git' \
        --exclude='.env' \
        "$PROJECT_DIR"/ "$DEPLOY_DIR"/
    
    echo -e "${GREEN}تم النشر بنجاح!${NC}"
}

# ------ النسخ الاحتياطي ------
function backup() {
    local timestamp=$(date +'%Y%m%d-%H%M%S')
    local backup_file="$BACKUP_DIR/TravAgencySys-$timestamp.tar.gz"
    
    echo -e "${YELLOW}جاري إنشاء نسخة احتياطية...${NC}"
    
    # إنشاء مجلد النسخ الاحتياطي
    mkdir -p "$BACKUP_DIR"
    
    # نسخ احتياطي للكود
    tar -czf "$backup_file" -C "$PROJECT_DIR" .
    
    echo -e "${GREEN}تم إنشاء النسخة الاحتياطية في:${NC}"
    echo "→ $backup_file"
}

# ------ القائمة الرئيسية ------
function main_menu() {
    while true; do
        echo -e "\n${GREEN}=== إدارة نظام وكالة السفر ===${NC}"
        echo "1) الإعداد الأولي/التحديث"
        echo "2) مزامنة مع GitHub"
        echo "3) النشر إلى المسار النهائي"
        echo "4) نسخة احتياطية"
        echo "5) الخروج"
        
        read -rp "اختر الإجراء [1-5]: " choice
        
        case "$choice" in
            1) setup_project ;;
            2) git_operations ;;
            3) deploy ;;
            4) backup ;;
            5) exit 0 ;;
            *) echo -e "${RED}اختيار غير صحيح! الرجاء المحاولة مرة أخرى.${NC}" ;;
        esac
    done
}

# ------ التنفيذ الرئيسي ------
check_requirements
main_menu
