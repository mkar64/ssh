#!/data/data/com.termux/files/usr/bin/bash

# ==========================================
# سكربت التقاط صورة من كاميرا الهاتف
# ==========================================

# مجلد حفظ الصور
PHOTOS_DIR="$HOME/photos"
mkdir -p "$PHOTOS_DIR"

# الكاميرا الافتراضية (0 هي الخلفية، 1 هي الأمامية)
CAMERA_ID="${1:-0}"
FILE="$PHOTOS_DIR/photo_$(date +%Y%m%d_%H%M%S).jpg"

# التقاط الصورة
termux-camera-photo -c "$CAMERA_ID" "$FILE" 2>/dev/null
