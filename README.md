# 🚀 SSH Remote Management & Connection Suite
### نظام إدارة واتصال SSH المتكامل لأجهزة Android (Termux) وأنظمة Linux

نظام شمولـي خفيف ومُحدث لإدارة اتصالات SSH والتشغيل الدائم مع واجهة تحكم ويب تفاعلية واكتشاف للشبكات المحلية.

---

## 📌 الميزات الرئيسية (Key Features)

- 📱 **دليل Termux المخصص (Termux Guide):**
  يحتوي المستودع على دليل تفصيلي شامل مخصص لتطبيق Termux بملف [TERMUX_GUIDE.md](file:///home/ms/.gemini/antigravity-ide/scratch/anydesk-termux-web/TERMUX_GUIDE.md) يشرح الصلاحيات والأوامر والحزم المطلوبة.
- ⚡ **القيم الافتراضية (Default Parameters):**
  - **المنفذ الافتراضي (Port):** `3367`
  - **الخادم الافتراضي (Host):** `mycontrolbox.duckdns.org`
  - **المستخدم الافتراضي (User):** `ms`
- 📱 **اكتشاف تلقائي لبيئة التشغيل (OS Auto-Detection):**
  - **Android Termux:** تثبيت الحزم تلقائياً عبر `pkg install`.
  - **Linux / Ubuntu / Debian:** تثبيت الحزم تلقائياً عبر `apt-get install`.
- 📦 **تثبيت حزم دفعة واحدة (Batch Package Setup):**
  `openssh`, `autossh`, `termux-api`, `curl`, `rsync`, `git`, `python3`, `nmap`, `iproute2`, `net-tools`, `fail2ban`.
- 🔑 **توليد مفاتيح ed25519 وتصديرها:**
  توليد تلقائي للمفتاح ونسخه للهدف بضغطة زر أو أمر واحد.
- 🔄 **سكربت الاتصال المستمر (`keep_ssh.sh`):**
  حلقة مراقبة بـ `autossh` لمنع انقطاع الجلسة وتفعيل `termux-wake-lock` لمنع سكون المعالج بالأندرويد.
- 🌐 **واجهة تحكم ويب تفاعلية (`web_ui.py`):**
  تدرج على المنفذ **8080** بدون أي مكتبات خارجية (Standard Python Library)، وتتضمن:
  - أزرار التحكم السريع (Quick Action Buttons).
  - اكتشاف عناوين الـ IP النشطة في الشبكة المحلية (LAN Network Discovery) واختيارها من قائمة منسدلة.
  - تنفيذ الأوامر المباشرة وشاشة متابعة المخرجات (Live Terminal Log).

---

## 🚀 أمر النسخ واللصق الشامل (All-in-One Termux Command)

يمكنك نسخ البلوك الكامل التالي ولصقه في **Termux** دفعة واحدة لتنفيذ كافة خطوات التثبيت والتشغيل بالتسلسل:

```bash
termux-setup-storage && \
pkg update -y && \
pkg install -y git curl python && \
git clone https://github.com/mkar64/ssh.git && \
cd ssh && \
chmod +x setup.sh keep_ssh.sh web_ui.py && \
./setup.sh ms mycontrolbox.duckdns.org 3367 && \
nohup ./keep_ssh.sh > /dev/null 2>&1 & \
python3 web_ui.py
```

---

## 🛠 التثبيت والتشغيل السريع (Quick Start)

### 1. تشغيل السكربت الشامل (Setup Script):

يمكنك تشغيل السكربت بالقيم الافتراضية:

```bash
chmod +x setup.sh
./setup.sh
```

أو تمرير متغيرات ديناميكية من التيرمينال:
`./setup.sh <اسم_المستخدم> <الهوست/الدومين> <المنفذ>`

**مثال:**
```bash
./setup.sh ms mycontrolbox.duckdns.org 3367
```

أو عن طريق `curl` مباشرة:
```bash
curl -sL https://raw.githubusercontent.com/mkar64/ssh/main/setup.sh | bash -s -- ms mycontrolbox.duckdns.org 3367
```

---

## 🔄 2. تشغيل خدمة الاتصال المستمر (Keep SSH)

يقوم السكربت بإنشاء وتجهيز `keep_ssh.sh` تلقائياً. للتشغيل في الخلفية:

```bash
nohup ./keep_ssh.sh > /dev/null 2>&1 &
```

لإيقاف الجلسة أو إعادة تشغيلها:
```bash
pkill -f autossh
```

---

## 🌐 3. واجهة التحكم بالويب (Web UI)

لتشغيل سيرفر الويب على المنفذ `8080`:

```bash
python3 web_ui.py
```

افتح المتصفح على العنوان:
👉 **`http://localhost:8080`** أو **`http://<IP_الجهاز>:8080`**

### الأزرار المتاحة بواجهة الويب:
- 🔌 **فحص اتصال SSH:** تجربة الاتصال المباشر بالهدف المختار وتأكيد الاستجابة.
- 📊 **حالة الخدمة:** عرض العمليات النشطة حالياً لجلسات `autossh`.
- 🔄 **إعادة تشغيل autoSSH:** إعادة تشغيل جلسة الاتصال بالخلفية.
- 🔒 **منع سكون الهاتف:** تفعيل `termux-wake-lock` على أندرويد.
- 🔎 **فحص واكتشاف الأجهزة:** عمل Scan للشبكة المحلية وحصر الآيبيات النشطة بقائمة منسدلة اختيارية.
- 🖥 **شاشة التنفيذ المباشر:** إدخال أي أمر SSH أو نظام وتشغيله مباشرة وعرض مخرجاته.

---

## 📁 هيكلة المشروع (Project Structure)

```text
.
├── setup.sh       # السكربت الرئيسي لتجهيز النظام والحزم والمفاتيح
├── keep_ssh.sh    # سكربت المراقبة والاتصال المستمر بـ AutoSSH
├── web_ui.py      # خادم الويب التفاعلي بـ Python (Port 8080)
└── README.md      # دليل الاستخدام والتأثيث
```

---

## 🔒 الأمان والاستخدام (Security & Permissions)

- يُنشئ السكربت مفتاح `ed25519` محمي بالتصاريح `600` والمجلد `700`.
- يتم استخدام الخيار `StrictHostKeyChecking=accept-new` لقبول البصمة الأولى بأمان عند الاتصال بالأجهزة الجديدة.
