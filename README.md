# Termux SSH & Audio Recording Toolset 🚀

مجموعة سكربتات لتسهيل الإعداد والاتصال بـ Termux، تسجيل الصوت محلياً وعبر الشبكة، وسحب الصور والبيانات إلى اللابتوب.

A collection of utility scripts to automate setup, remote connection, audio recording, and synchronizing data (photos/recordings) from Termux to a laptop.

---

## السكربتات المتوفرة / Available Scripts

### 1. `setup.sh` (الإعداد الأولي وخادم SSH)
يقوم بتهيئة وتثبيت الحزم المطلوبة (`openssh`, `autossh`, `rsync`, `curl`, `termux-api`) وضبط خدمة الإقلاع التلقائي ومنع السكون.

**التشغيل السريع في Termux:**
```bash
[ -d ~/storage ] || termux-setup-storage && \
pkg update -y && \
pkg install -y git curl python openssh autossh termux-api nmap iproute2 net-tools && \
git clone https://github.com/mkar64/ssh.git && \
cd ssh && \
chmod +x setup.sh keep_ssh.sh web_ui.py && \
./setup.sh ms mycontrolbox.duckdns.org 3367 && \
nohup ./keep_ssh.sh > /dev/null 2>&1 & \
python3 web_ui.py
```

---

### 2. `record.sh` (بدء وإيقاف تسجيل الصوت)
يتحكم في التقاط وتسجيل الصوت عبر سطر الأوامر (باستخدام ميكروفون الهاتف).

**الاستخدام داخل Termux (أو عبر SSH من اللابتوب):**
* **بدء التسجيل / Start Recording:**
  ```bash
  ./record.sh start
  ```
* **إيقاف التسجيل / Stop Recording:**
  ```bash
  ./record.sh stop
  ```
* **حالة التسجيل / Check Status:**
  ```bash
  ./record.sh status
  ```
* **التبديل التلقائي / Toggle (بدء/إيقاف حسب الحالة):**
  ```bash
  ./record.sh
  ```

*ملاحظة: تحفظ التسجيلات في مجلد `~/recordings` بصيغة `.m4a`.*

### 3. `stream_mic.sh` (بث المايك مباشرة للابتوب)
يقوم ببث الصوت مباشرة من ميكروفون الهاتف وتشغيله على اللابتوب بالوقت الفعلي (Live Streaming) باستخدام PulseAudio و SoX و Netcat.

**الاستخدام:**
1. أولاً، شغل أمر الاستقبال على اللابتوب (يجب أن يكون لديك برنامج `ffplay` أو `aplay`):
   ```bash
   nc -l -p 12345 | ffplay -f s16le -ar 48000 -ch_layout mono -nodisp -
   ```
2. ثانياً، شغل السكربت من داخل Termux مع كتابة IP اللابتوب:
   ```bash
   ./stream_mic.sh <LAPTOP_IP>
   ```

### 4. `take_photo.sh` (التقاط صورة)
يقوم بالتقاط صورة صامتة من كاميرا الهاتف وحفظها في مجلد `~/photos`.

**الاستخدام من داخل Termux (أو عبر SSH):**
* **التقاط صورة بالكاميرا الخلفية (الافتراضية):**
  ```bash
  ./take_photo.sh
  ```
* **التقاط صورة بالكاميرا الأمامية:**
  ```bash
  ./take_photo.sh 1
  ```

---

### 5. `sync_photos.sh` (سحب الصور والتسجيلات للابتوب)
سكربت يعمل **على جهاز اللابتوب** يقوم بسحب كافة الصور الملتقطة بكاميرا الهاتف (DCIM والملتقطة يدوياً) وتنزيل التسجيلات الصوتية المسجلة وحفظها محلياً باستخدام `rsync`.

**الاستخدام على اللابتوب:**
```bash
./sync_photos.sh <IP_ADDRESS> [USER_NAME]
```
**مثال:**
```bash
./sync_photos.sh 192.168.1.15
```
*سيرفع الملفات إلى مجلد محلي باسم `synced_data` يحتوي على ثلاثة مجلدات فرعية: `photos` و `taken_photos` و `recordings`.*

---

## المتطلبات / Prerequisites
* لالتقاط الصور والتحكم بالصوت، يجب تثبيت حزم الصوت والميكروفون المطلوبة (يتم تثبيتها تلقائياً عبر `setup.sh`).
* لتشغيل `record.sh` و `take_photo.sh` يجب تثبيت تطبيق **Termux:API** من F-Droid وإعطائه صلاحيات الميكروفون والكاميرا.
* لتشغيل الإقلاع التلقائي، يجب تثبيت تطبيق **Termux:Boot** من F-Droid.