#!/usr/bin/env bash

# ==============================================================================
# Comprehensive SSH & Remote Management Setup Script
# السكربت الشامل لإعداد وإدارة اتصالات SSH لنظام أندرويد (تيرموكس) ولينكس
# ==============================================================================

set -e

# Default values / القيم الافتراضية
DEFAULT_USER="ms"
DEFAULT_HOST="mycontrolbox.duckdns.org"
DEFAULT_PORT="3367"

# Dynamic arguments from terminal / الأرجومنتات الديناميكية
SSH_USER="${1:-$DEFAULT_USER}"
SSH_HOST="${2:-$DEFAULT_HOST}"
SSH_PORT="${3:-$DEFAULT_PORT}"

# ANSI Color Codes / الألوان للتنسيق
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================${NC}"
echo -e "${PURPLE}   🚀 SSH Management System Setup & Installer 🚀   ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo -e "${YELLOW}Target User:${NC} ${SSH_USER}"
echo -e "${YELLOW}Target Host:${NC} ${SSH_HOST}"
echo -e "${YELLOW}Target Port:${NC} ${SSH_PORT}"
echo -e "${CYAN}------------------------------------------------------${NC}"

# 1. Environment Detection / اكتشاف بيئة التشغيل
echo -e "\n${BLUE}[1/5] Detecting Operating Environment... / فحص بيئة التشغيل...${NC}"

IS_TERMUX=false
IS_DEBIAN_LIKE=false

if command -v pkg &> /dev/null || [ -d "/data/data/com.termux" ] || [[ "$(uname -o 2>/dev/null)" == *"Android"* ]]; then
    IS_TERMUX=true
    echo -e "${GREEN}✓ Environment Detected: Termux on Android${NC}"
elif command -v apt-get &> /dev/null || command -v apt &> /dev/null; then
    IS_DEBIAN_LIKE=true
    echo -e "${GREEN}✓ Environment Detected: Linux (Debian/Ubuntu based)${NC}"
else
    echo -e "${YELLOW}⚠ Environment: Standard Linux/Unix (non-Debian/Termux)${NC}"
fi

# 2. Package Batch Installation / تحديث وتركيب الحزم دفعة واحدة
echo -e "\n${BLUE}[2/5] Updating packages & installing dependencies... / تثبيت الحزم والمكتبات المطلوبة...${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -e "${CYAN}Running termux pkg update & batch install...${NC}"
    pkg update -y || true
    # Packages for Termux
    TERMUX_PKGS="openssh autossh termux-api curl rsync git python nmap iproute2 net-tools"
    pkg install -y $TERMUX_PKGS
    
    # Request storage access and wake-lock if termux-api installed
    if command -v termux-wake-lock &> /dev/null; then
        termux-wake-lock || true
        echo -e "${GREEN}✓ Termux Wake-Lock enabled (CPU sleep prevented).${NC}"
    fi
elif [ "$IS_DEBIAN_LIKE" = true ]; then
    echo -e "${CYAN}Running apt-get update & batch install...${NC}"
    if [ "$EUID" -ne 0 ] && command -v sudo &> /dev/null; then
        SUDO="sudo -n"
    else
        SUDO=""
    fi
    
    LINUX_PKGS="openssh-client openssh-server autossh curl rsync git python3 python3-pip nmap iproute2 net-tools fail2ban"
    $SUDO apt-get update -y 2>/dev/null || true
    $SUDO apt-get install -y $LINUX_PKGS 2>/dev/null || echo -e "${YELLOW}⚠ Package installation via sudo skipped or requires manual apt install.${NC}"
else
    echo -e "${YELLOW}⚠ Custom package manager detected. Please ensure openssh, autossh, nmap, python3 are installed.${NC}"
fi

# 3. SSH Key Generation & Copy / توليد ونسخ مفتاح ed25519
echo -e "\n${BLUE}[3/5] Checking & Generating SSH ed25519 Key Pair... / إنشاء مفتاح SSH...${NC}"

mkdir -p ~/.ssh
chmod 700 ~/.ssh

KEY_FILE="$HOME/.ssh/id_ed25519"
if [ ! -f "$KEY_FILE" ]; then
    echo -e "${CYAN}Generating new ed25519 key pair without passphrase...${NC}"
    ssh-keygen -t ed25519 -N "" -f "$KEY_FILE" -C "ssh-manager-$(date +%Y%m%d)"
    echo -e "${GREEN}✓ Key successfully generated at $KEY_FILE${NC}"
else
    echo -e "${GREEN}✓ Key ed25519 already exists at $KEY_FILE${NC}"
fi

chmod 600 "$KEY_FILE"
chmod 644 "${KEY_FILE}.pub"

echo -e "\n${YELLOW}Public Key Content (${KEY_FILE}.pub):${NC}"
cat "${KEY_FILE}.pub"
echo ""

# Attempt SSH key copy if interactive or requested
echo -e "${CYAN}Would you like to deploy/copy this SSH key to target server [${SSH_USER}@${SSH_HOST}:${SSH_PORT}] now?${NC}"
echo -e "${YELLOW}Notice: You will need to input the password once during copy.${NC}"

if command -v ssh-copy-id &> /dev/null; then
    # Try non-blocking check or prompt
    read -t 10 -p "Copy key now? (y/N): " COPY_CHOICE || COPY_CHOICE="n"
    if [[ "$COPY_CHOICE" =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}Executing: ssh-copy-id -p $SSH_PORT -i ${KEY_FILE}.pub ${SSH_USER}@${SSH_HOST}${NC}"
        ssh-copy-id -p "$SSH_PORT" -i "${KEY_FILE}.pub" "${SSH_USER}@${SSH_HOST}" || echo -e "${RED}✘ Key copy skipped or failed. You can run ssh-copy-id manually later.${NC}"
    else
        echo -e "${YELLOW}Skipped key copying. You can deploy it manually using:${NC}"
        echo -e "${CYAN}ssh-copy-id -p $SSH_PORT -i ${KEY_FILE}.pub ${SSH_USER}@${SSH_HOST}${NC}"
    fi
fi

# 4. Generate persistent runner script keep_ssh.sh / إنشاء سكربت التشغيل الدائم
echo -e "\n${BLUE}[4/5] Generating persistent execution script keep_ssh.sh... / إنشاء سكربت keep_ssh.sh...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEEP_SSH_PATH="$SCRIPT_DIR/keep_ssh.sh"

cat << 'EOF' > "$KEEP_SSH_PATH"
#!/usr/bin/env bash

# ==============================================================================
# Persistent SSH & AutoSSH Keeper Script
# ==============================================================================

# Target Configuration
SSH_USER="__SSH_USER__"
SSH_HOST="__SSH_HOST__"
SSH_PORT="__SSH_PORT__"
REVERSE_PORT="${REVERSE_PORT:-2222}" # Remote reverse tunnel port to access this machine

# AutoSSH Settings
export AUTOSSH_GATETIME=0
export AUTOSSH_POLL=30
export AUTOSSH_PORT=0
export AUTOSSH_LOGFILE="$HOME/.ssh/autossh.log"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}  Starting Continuous SSH Keep-Alive Monitor...     ${NC}"
echo -e "${GREEN}====================================================${NC}"

# Prevent device sleep on Termux
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock || true
    echo -e "${GREEN}✓ Termux Wake-Lock activated.${NC}"
fi

# Function to check connection state
check_connection() {
    nc -z -w 5 "$SSH_HOST" "$SSH_PORT" &>/dev/null
    return $?
}

# Main Monitoring Loop
while true; do
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${YELLOW}Initiating connection to ${SSH_USER}@${SSH_HOST}:${SSH_PORT}...${NC}"
    
    # AutoSSH Command with keepalive, strict host checking auto-accept, and reverse port forward option
    autossh -M 0 \
        -o "ServerAliveInterval=15" \
        -o "ServerAliveCountMax=3" \
        -o "ExitOnForwardFailure=yes" \
        -o "StrictHostKeyChecking=accept-new" \
        -o "UserKnownHostsFile=/dev/null" \
        -N -T \
        -p "$SSH_PORT" \
        -R "${REVERSE_PORT}:localhost:22" \
        "${SSH_USER}@${SSH_HOST}" || true

    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}Connection dropped or failed. Retrying in 10 seconds...${NC}"
    sleep 10
done
EOF

# Substitute parameters into keep_ssh.sh
sed -i "s/__SSH_USER__/$SSH_USER/g" "$KEEP_SSH_PATH"
sed -i "s/__SSH_HOST__/$SSH_HOST/g" "$KEEP_SSH_PATH"
sed -i "s/__SSH_PORT__/$SSH_PORT/g" "$KEEP_SSH_PATH"

chmod +x "$KEEP_SSH_PATH"
echo -e "${GREEN}✓ Generated keep_ssh.sh successfully at: $KEEP_SSH_PATH${NC}"

# 5. Summary & Web UI Launcher Setup / تلخيص وإيقاد النظام
echo -e "\n${BLUE}[5/5] Finalizing Setup & Web UI Ready... / إنهاء الإعداد وتجهيز واجهة الويب...${NC}"

WEB_UI_PATH="$SCRIPT_DIR/web_ui.py"
chmod +x "$WEB_UI_PATH" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/setup.sh"

echo -e "\n${CYAN}======================================================${NC}"
echo -e "${GREEN}  ✔ SSH System Setup Complete Successfully!           ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo -e "${YELLOW}To start persistent SSH monitor:${NC}"
echo -e "   ${CYAN}./keep_ssh.sh &${NC}"
echo -e ""
echo -e "${YELLOW}To start the Lightweight Web Control Panel (Port 8080):${NC}"
echo -e "   ${CYAN}python3 web_ui.py${NC}"
echo -e ""
echo -e "${YELLOW}Quick Command to run both in background:${NC}"
echo -e "   ${CYAN}nohup ./keep_ssh.sh > /dev/null 2>&1 & python3 web_ui.py${NC}"
echo -e "${CYAN}======================================================${NC}"
