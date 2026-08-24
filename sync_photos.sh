#!/bin/bash

# ==========================================
# سكربت سحب الصور والتسجيلات من الهاتف إلى اللابتوب
# ==========================================

# الإعدادات الافتراضية
PORT=8022
LOCAL_DIR="./synced_data"

# التحقق من المدخلات
if [ -z "$1" ]; then
    echo "=========================================="
    echo "استخدام السكربت (Usage):"
    echo "  ./sync_photos.sh <IP_ADDRESS> [USER_NAME]"
    echo "=========================================="
    echo "مثال: ./sync_photos.sh 192.168.1.5"
    exit 1
fi

IP="$1"
USER="${2:-$(whoami 2>/dev/null || echo "u0_a243")}"

echo "=========================================="
echo "[*] بدء سحب البيانات من الهاتف ($IP)..."
echo "=========================================="

# 1. إنشاء المجلدات المحلية
mkdir -p "$LOCAL_DIR/photos"
mkdir -p "$LOCAL_DIR/recordings"

# 2. سحب الصور (DCIM Camera)
echo "[*] سحب الصور (DCIM Camera)..."
if rsync -avz --progress -e "ssh -p $PORT" "$USER@$IP:/sdcard/DCIM/Camera/" "$LOCAL_DIR/photos/"; then
    echo "[+] تم سحب الصور بنجاح."
else
    echo "[!] تنبيه: فشل سحب الصور أو المجلد فارغ."
fi

# 3. سحب التسجيلات الصوتية
echo "[*] سحب التسجيلات الصوتية..."
if rsync -avz --progress -e "ssh -p $PORT" "$USER@$IP:~/recordings/" "$LOCAL_DIR/recordings/"; then
    echo "[+] تم سحب التسجيلات الصوتية بنجاح."
else
    echo "[!] تنبيه: فشل سحب التسجيلات أو المجلد فارغ."
fi

echo "=========================================="
echo "[+] اكتملت عملية المزامنة بنجاح!"
echo "[+] الملفات محفوظة في المجلد المحلي: $LOCAL_DIR"
echo "=========================================="
