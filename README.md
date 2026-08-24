# Termux SSH Auto Setup 🚀

سكربت تلقائي لإعداد وتفعيل خادم SSH على تطبيق Termux (أندرويد) مع دعم الإقلاع التلقائي ومنع السكون.

An automated script to configure and enable SSH server on Termux (Android) with auto-boot support and wake-lock to prevent sleep.

---

## التشغيل السريع / Quick Installation

يمكنك تشغيل السكربت مباشرة داخل تطبيق Termux عبر الأمر التالي:
You can run the script directly inside the Termux app using the following command:

```bash
curl -sL https://raw.githubusercontent.com/mkar64/ssh/main/setup_ssh.sh | bash
```

---

## ماذا يفعل هذا السكربت؟ / What does this script do?

1. **صلاحيات الذاكرة / Storage Permission:** يطلب الإذن للوصول إلى ذاكرة الهاتف (`termux-setup-storage`).
2. **تثبيت المتطلبات / Install Dependencies:** يقوم بتحديث الحزم وتثبيت `openssh`, `autossh`, `rsync`, `curl`.
3. **أمان SSH / SSH Security:** ينشئ المجلدات اللازمة ويضبط أذونات الأمان للمفاتيح (`chmod 700` و `chmod 600`).
4. **الإقلاع التلقائي / Auto-Boot:** ينشئ سكربت التشغيل التلقائي متوافق مع إضافة **Termux:Boot** ليعمل خادم SSH بمجرد تشغيل الهاتف.
5. **منع السكون / Wake Lock:** يقوم بتشغيل `termux-wake-lock` لضمان عدم توقف الخدمة عند إغلاق الشاشة.
6. **الاتصال وسرية الحساب / Connection & Password:** يعرض معلومات الاتصال بالخادم ويطلب تعيين كلمة مرور جديدة لجهازك.

---

## طريقة الاتصال / Connection Info

بعد اكتمال تشغيل السكربت، يمكنك الاتصال من الحاسوب الشخصي عبر المنفذ `8022`:
After execution, connect from your computer using port `8022`:

```bash
ssh -p 8022 <username>@<ip_address>
```

> [!NOTE]
> تأكد من تثبيت تطبيق [Termux:Boot](https://github.com/termux/termux-boot) من F-Droid إذا كنت تريد تفعيل ميزة الإقلاع التلقائي عند تشغيل الهاتف.