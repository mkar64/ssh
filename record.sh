#!/data/data/com.termux/files/usr/bin/bash

RECORDINGS_DIR="$HOME/recordings"
mkdir -p "$RECORDINGS_DIR"

# التحقق من حالة التسجيل
is_recording() {
    # الأداة ترجع بيانات بصيغة JSON
    # إذا كان التسجيل نشطاً، ستحتوي على "isRecording": true
    INFO=$(termux-microphone-record -i 2>/dev/null)
    if echo "$INFO" | grep -q '"isRecording": true'; then
        return 0 # نعم، يسجل
    else
        return 1 # لا، متوقف
    fi
}

start_rec() {
    if is_recording; then
        termux-microphone-record -i
    else
        FILE="$RECORDINGS_DIR/recording_$(date +%Y%m%d_%H%M%S).m4a"
        termux-microphone-record -f "$FILE"
    fi
}

stop_rec() {
    if is_recording; then
        termux-microphone-record -q
    fi
}

show_status() {
    echo "[*] حالة التسجيل الحالية:"
    termux-microphone-record -i
}

case "$1" in
    start)
        start_rec
        ;;
    stop)
        stop_rec
        ;;
    status)
        show_status
        ;;
    *)
        # التبديل التلقائي في حال عدم تمرير وسيط (Toggle)
        if is_recording; then
            stop_rec
        else
            start_rec
        fi
        ;;
esac
