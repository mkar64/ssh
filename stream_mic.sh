#!/data/data/com.termux/files/usr/bin/bash

# ==========================================
# سكربت بث المايك مباشرة من الهاتف إلى اللابتوب
# ==========================================

if [ -z "$1" ]; then
    echo "=========================================="
    echo "استخدام السكربت (Usage):"
    echo "  ./stream_mic.sh <LAPTOP_IP>"
    echo "=========================================="
    echo "قبل تشغيل هذا السكربت، شغل هذا الأمر على اللابتوب لاستقبال الصوت:"
    echo "  nc -l -p 12345 | ffplay -f s16le -ar 48000 -ch_layout mono -nodisp -"
    echo "=========================================="
    exit 1
fi

LAPTOP_IP="$1"
PORT=12345

# بدء تشغيل PulseAudio في الخلفية إذا لم يكن قيد التشغيل
if ! pulseaudio --check 2>/dev/null; then
    echo "[*] بدء تشغيل PulseAudio..."
    pulseaudio --start --exit-idle-time=-1 2>/dev/null || true
fi

echo "[*] جاري بث صوت المايك إلى اللابتوب ($LAPTOP_IP:$PORT)..."
echo "[*] اضغط Ctrl+C لإيقاف البث."

# تسجيل الصوت من المايك وتمريره عبر الشبكة باستخدام Netcat
sox -d -t raw -r 48000 -c 1 -b 16 -e signed-integer - | nc "$LAPTOP_IP" "$PORT"
