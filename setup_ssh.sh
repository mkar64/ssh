#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=========================================="
echo "[*] بدء الإعداد التلقائي لـ Termux و SSH..."
echo "=========================================="

# 1. طلب إذن الوصول للذاكرة
echo "[*] إعداد الوصول للذاكرة..."
termux-setup-storage

# 2. تحديث الحزم وتثبيت المتطلبات الأساسية
echo "[*] تحديث وتثبيت الحزم (OpenSSH, AutoSSH, Rsync, Curl)..."
pkg update -y
pkg install -y openssh autossh rsync curl

# 3. إنشاء المجلدات وضبط الأذونات
echo "[*] تجهيز المجلدات الأمنية..."
mkdir -p ~/.ssh
mkdir -p ~/.termux/boot
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 4. إعداد سكربت الإقلاع التلقائي (Termux:Boot)
echo "[*] إعداد الإقلاع التلقائي..."
cat << 'EOF' > ~/.termux/boot/start_services.sh
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sshd
EOF
chmod +x ~/.termux/boot/start_services.sh

# 5. منع السكون وتشغيل خدمة SSH فوراً
echo "[*] تشغيل خادم SSH ومنع السكون..."
termux-wake-lock
sshd

# 6. جلب معلومات الاتصال
USER_NAME=$(whoami)
# محاولة جلب الـ IP النشط بشكل مرن، وإذا فشل نستخدم wlan0 الافتراضي
IP_ADDR=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}')
if [ -z "$IP_ADDR" ]; then
    IP_ADDR=$(ip -4 addr show wlan0 2>/dev/null | awk '/inet / {print $2}' | cut -d/ -f1)
fi

echo "=========================================="
echo "[+] اكتمل الإعداد بنجاح!"
echo "------------------------------------------"
echo "اسم المستخدم (User): $USER_NAME"
echo "عنوان الـ IP المحلي: ${IP_ADDR:-غير متصل بالواي فاي}"
echo "المنفذ الافتراضي (Port): 8022"
echo "------------------------------------------"
echo "أمر الاتصال من اللابتوب:"
echo "ssh -p 8022 $USER_NAME@${IP_ADDR:-<IP_ADDRESS>}"
echo "=========================================="
echo "[!] اضبط كلمة المرور لحسابك الآن:"
passwd
