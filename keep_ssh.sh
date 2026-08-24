#!/usr/bin/env bash

# ==============================================================================
# Persistent SSH & AutoSSH Keeper Script
# ==============================================================================

# Target Configuration
SSH_USER="ms"
SSH_HOST="mycontrolbox.duckdns.org"
SSH_PORT="3367"
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
