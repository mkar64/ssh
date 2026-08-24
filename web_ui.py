#!/usr/bin/env python3
"""
Lightweight SSH & Remote Device Control Web UI
واجهة تحكم خفيفة لتدارك وتتبع اتصالات SSH واكتشاف الشبكة
Runs on http://localhost:8080 using Python 3 Standard Library
"""

import http.server
import socketserver
import json
import subprocess
import urllib.parse
import os
import re
import socket
import sys
from datetime import datetime

PORT = 8080
DEFAULT_USER = "ms"
DEFAULT_HOST = "mycontrolbox.duckdns.org"
DEFAULT_PORT = 3367

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة واتصال SSH المتكامل</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-card: rgba(22, 30, 46, 0.7);
            --bg-card-hover: rgba(30, 42, 66, 0.8);
            --accent-cyan: #00f2fe;
            --accent-blue: #4facfe;
            --accent-green: #00e676;
            --accent-red: #ff5252;
            --accent-purple: #7928ca;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Tajawal', sans-serif;
        }

        body {
            background: var(--bg-primary);
            background-image: 
                radial-gradient(at 10% 10%, rgba(79, 172, 254, 0.15) 0px, transparent 50%),
                radial-gradient(at 90% 90%, rgba(121, 40, 202, 0.15) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
        }

        h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-red);
            box-shadow: 0 0 10px var(--accent-red);
        }

        .status-dot.active {
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }

        .card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .card:hover {
            border-color: rgba(0, 242, 254, 0.3);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--accent-cyan);
        }

        .form-group {
            margin-bottom: 16px;
        }

        label {
            display: block;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-weight: 500;
        }

        input, select {
            width: 100%;
            padding: 12px 14px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }

        input:focus, select:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
        }

        .btn-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .btn {
            padding: 12px 18px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            color: #000;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
        }

        .btn-primary:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: var(--accent-cyan);
        }

        .btn-warning {
            background: linear-gradient(135deg, #ff9900, #ff5500);
            color: #fff;
        }

        .btn-danger {
            background: linear-gradient(135deg, #ff5252, #d32f2f);
            color: #fff;
        }

        .btn-full {
            grid-column: span 2;
        }

        .terminal-card {
            grid-column: 1 / -1;
        }

        .terminal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .terminal-window {
            background: #050811;
            border-radius: 12px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            color: #00ff66;
            min-height: 240px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            white-space: pre-wrap;
            direction: ltr;
            text-align: left;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.9rem;
        }

        .info-label {
            color: var(--text-secondary);
        }

        .info-value {
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            direction: ltr;
        }

        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: inline-block;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="logo-group">
            <div class="logo-icon">⚡</div>
            <div>
                <h1>لوحة التحكم لنظام SSH المتكامل</h1>
                <div class="subtitle">إدارة الأجهزة، فحص الشبكة المحلية والاتصال المستمر</div>
            </div>
        </div>
        <div class="status-badge" id="systemStatusBadge">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">جاري فحص الاتصال...</span>
        </div>
    </header>

    <div class="grid">
        <!-- Quick Action Buttons -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">⚡ الأزرار السريعة (Quick Actions)</div>
            </div>
            <div class="btn-grid">
                <button class="btn btn-primary" onclick="execPreset('test_ssh')">
                    🔌 فحص اتصال SSH
                </button>
                <button class="btn btn-secondary" onclick="execPreset('status')">
                    📊 حالة الخدمة
                </button>
                <button class="btn btn-warning" onclick="execPreset('restart')">
                    🔄 إعادة تشغيل autoSSH
                </button>
                <button class="btn btn-secondary" onclick="execPreset('wake_lock')">
                    🔒 منع سكون الهاتف
                </button>
                <button class="btn btn-secondary btn-full" onclick="execPreset('view_logs')">
                    📜 عرض سجّلات الاتصال (Autossh Logs)
                </button>
            </div>
        </div>

        <!-- Network Discovery & Scan -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">🔍 اكتشاف الشبكة المحلية (LAN Scan)</div>
            </div>
            <div class="form-group">
                <label>العناوين النشطة المكتشفة بالشبكة:</label>
                <select id="lanIpSelect">
                    <option value="">اضغط "فحص الشبكة" لاكتشاف الأجهزة...</option>
                </select>
            </div>
            <div class="btn-grid">
                <button class="btn btn-primary btn-full" id="scanBtn" onclick="scanNetwork()">
                    🔎 فحص واكتشاف الأجهزة النشطة
                </button>
            </div>
            <div style="margin-top: 15px;">
                <div class="info-row">
                    <span class="info-label">الآيبي المحلي (LAN):</span>
                    <span class="info-value" id="localIpVal">...</span>
                </div>
                <div class="info-row">
                    <span class="info-label">الخادم الافتراضي:</span>
                    <span class="info-value" id="defaultHostVal">...</span>
                </div>
            </div>
        </div>

        <!-- Target & Command Execution Config -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">🛠 إعدادات الاتصال والأوامر</div>
            </div>
            <div class="form-group">
                <label>اسم المستخدم (User):</label>
                <input type="text" id="sshUser" value="ms">
            </div>
            <div class="form-group">
                <label>الهدف (Host / IP):</label>
                <input type="text" id="sshHost" value="mycontrolbox.duckdns.org">
            </div>
            <div class="form-group">
                <label>المنفذ (Port):</label>
                <input type="number" id="sshPort" value="3367">
            </div>
        </div>
    </div>

    <!-- Custom Command Execution Terminal -->
    <div class="card terminal-card">
        <div class="terminal-header">
            <div class="card-title">🖥 شاشة تنفيذ الأوامر المباشرة (Command Terminal)</div>
            <button class="btn btn-secondary" onclick="clearTerminal()" style="padding: 4px 12px; font-size: 0.8rem;">مسح الشاشة</button>
        </div>
        <div class="form-group" style="display: flex; gap: 10px;">
            <input type="text" id="customCmd" placeholder="أدخل أمر SSH أو أمر نظام لتنفيذه (مثلاً: uptime, ls -la, reboot)..." onkeydown="if(event.key==='Enter') runCustomCmd()">
            <button class="btn btn-primary" onclick="runCustomCmd()" style="min-width: 120px;">تشغيل الأمر</button>
        </div>
        <div class="terminal-window" id="terminalLog">> النظام جاهز واستجابة خادم بايثون 8080 نشطة.</div>
    </div>
</div>

<script>
    function appendLog(msg, clear = false) {
        const term = document.getElementById('terminalLog');
        const time = new Date().toLocaleTimeString('ar-EG');
        if (clear) {
            term.textContent = `[${time}] ${msg}`;
        } else {
            term.textContent += `\n[${time}] ${msg}`;
        }
        term.scrollTop = term.scrollHeight;
    }

    function clearTerminal() {
        document.getElementById('terminalLog').textContent = '> تم مسح الشاشة.';
    }

    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.getElementById('localIpVal').textContent = data.local_ip || 'غير معروف';
            document.getElementById('defaultHostVal').textContent = `${data.default_user}@${data.default_host}:${data.default_port}`;
            
            const dot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (data.autossh_running) {
                dot.classList.add('active');
                statusText.textContent = `متصل بنجاح (AutoSSH PID: ${data.autossh_pid})`;
            } else {
                dot.classList.remove('active');
                statusText.textContent = 'خادم SSH المحلي نشط (AutoSSH متوقف)';
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function execPreset(action) {
        appendLog(`جاري تنفيذ الإجراء السريع: ${action}...`);
        const user = document.getElementById('sshUser').value;
        const host = document.getElementById('sshHost').value;
        const port = document.getElementById('sshPort').value;

        try {
            const res = await fetch('/api/exec', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, user, host, port })
            });
            const data = await res.json();
            appendLog(`=== النتيجة (${action}) ===\n` + (data.output || data.error));
            fetchStatus();
        } catch (e) {
            appendLog(`خطأ في الاتصال بالخادم: ${e}`);
        }
    }

    async function scanNetwork() {
        const btn = document.getElementById('scanBtn');
        const select = document.getElementById('lanIpSelect');
        btn.innerHTML = '<span class="spinner"></span> جاري فحص الشبكة...';
        btn.disabled = true;
        appendLog("بدء عملية اكتشاف الأجهزة المتصلة بالشبكة المحلية...");

        try {
            const res = await fetch('/api/scan-network', { method: 'POST' });
            const data = await res.json();
            select.innerHTML = '';

            if (data.hosts && data.hosts.length > 0) {
                data.hosts.forEach(h => {
                    const opt = document.createElement('option');
                    opt.value = h.ip;
                    opt.textContent = `${h.ip} ${h.mac ? '('+h.mac+')' : ''} ${h.hostname ? '['+h.hostname+']' : ''}`;
                    select.appendChild(opt);
                });
                appendLog(`تم العثور على ${data.hosts.length} جهاز نشط في الشبكة المحلية.`);
            } else {
                const opt = document.createElement('option');
                opt.textContent = 'لم يتم العثور على أجهزة نشطة أخرى';
                select.appendChild(opt);
                appendLog("لم يتم العثور على أجهزة أخرى عبر ARP/Nmap.");
            }
        } catch (e) {
            appendLog(`خطأ أثناء فحص الشبكة: ${e}`);
        } finally {
            btn.innerHTML = '🔎 فحص واكتشاف الأجهزة النشطة';
            btn.disabled = false;
        }
    }

    // Select IP from dropdown updates Target Host input
    document.getElementById('lanIpSelect').addEventListener('change', function() {
        if (this.value) {
            document.getElementById('sshHost').value = this.value;
            appendLog(`تم اختيار الهدف المطلوب: ${this.value}`);
        }
    });

    async function runCustomCmd() {
        const cmdInput = document.getElementById('customCmd');
        const cmd = cmdInput.value.trim();
        if (!cmd) return;

        const user = document.getElementById('sshUser').value;
        const host = document.getElementById('sshHost').value;
        const port = document.getElementById('sshPort').value;

        appendLog(`جاري تنفيذ الأمر عبر SSH على [${user}@${host}:${port}]: ${cmd}`);
        cmdInput.value = '';

        try {
            const res = await fetch('/api/exec', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'custom', cmd, user, host, port })
            });
            const data = await res.json();
            appendLog(`=== مخرجات الأمر ===\n` + (data.output || data.error));
        } catch (e) {
            appendLog(`خطأ أثناء التشغيل: ${e}`);
        }
    }

    fetchStatus();
    setInterval(fetchStatus, 10000);
</script>
</body>
</html>
"""

class SSHWebHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress standard HTTP noise in terminal
        pass

    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif parsed.path == '/api/status':
            self.handle_status()
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            payload = json.loads(body_data) if body_data else {}
        except Exception:
            payload = {}

        if parsed.path == '/api/scan-network':
            self.handle_network_scan()
        elif parsed.path == '/api/exec':
            self.handle_exec(payload)
        else:
            self.send_error(404, "Endpoint Not Found")

    def handle_status(self):
        local_ip = self.get_local_ip()
        autossh_pid = self.get_process_pid('autossh')
        
        response = {
            "status": "online",
            "local_ip": local_ip,
            "default_user": DEFAULT_USER,
            "default_host": DEFAULT_HOST,
            "default_port": DEFAULT_PORT,
            "autossh_running": bool(autossh_pid),
            "autossh_pid": autossh_pid or ""
        }
        self._set_json_headers(200)
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_process_pid(self, proc_name):
        try:
            out = subprocess.check_output(["pgrep", "-f", proc_name]).decode('utf-8').strip()
            if out:
                return out.split('\n')[0]
        except Exception:
            pass
        return None

    def handle_network_scan(self):
        hosts = []
        # Method 1: Check arp / ip neighbor
        try:
            out = subprocess.check_output(["ip", "neighbor"]).decode('utf-8', errors='ignore')
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and "REACHABLE" in line or "STALE" in line or "DELAY" in line:
                    ip = parts[0]
                    mac = parts[4] if len(parts) > 4 else ""
                    if not ip.startswith("127.") and not ip.startswith("fe80"):
                        hosts.append({"ip": ip, "mac": mac, "hostname": "LAN Device"})
        except Exception:
            pass

        # Fallback Method 2: arp -a
        if not hosts:
            try:
                out = subprocess.check_output(["arp", "-a"]).decode('utf-8', errors='ignore')
                for line in out.splitlines():
                    match = re.search(r'\(([\d\.]+)\) at ([0-9a-fA-F:]+)', line)
                    if match:
                        hosts.append({"ip": match.group(1), "mac": match.group(2), "hostname": "LAN Device"})
            except Exception:
                pass

        # Method 3: nmap fallback if available and no hosts found
        if not hosts and subprocess.call(["which", "nmap"], stdout=subprocess.DEVNULL) == 0:
            try:
                local_ip = self.get_local_ip()
                subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"
                out = subprocess.check_output(["nmap", "-sn", subnet, "--max-rtt-timeout", "500ms"]).decode('utf-8', errors='ignore')
                current_ip = None
                for line in out.splitlines():
                    if "Nmap scan report for" in line:
                        parts = line.split()
                        current_ip = parts[-1].strip("()")
                        hosts.append({"ip": current_ip, "mac": "", "hostname": "Scanned Device"})
            except Exception:
                pass

        self._set_json_headers(200)
        self.wfile.write(json.dumps({"hosts": hosts}, ensure_ascii=False).encode('utf-8'))

    def handle_exec(self, payload):
        action = payload.get('action', '')
        user = payload.get('user', DEFAULT_USER)
        host = payload.get('host', DEFAULT_HOST)
        port = payload.get('port', DEFAULT_PORT)
        cmd = payload.get('cmd', '')

        output = ""
        error = ""

        try:
            if action == 'test_ssh':
                ssh_cmd = [
                    "ssh", "-p", str(port),
                    "-o", "ConnectTimeout=5",
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", "BatchMode=yes",
                    f"{user}@{host}",
                    "echo 'SSH connection successful! Host details:'; uname -a; uptime"
                ]
                proc = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                output = proc.stdout if proc.returncode == 0 else f"Failed (Exit Code {proc.returncode}):\n{proc.stderr}\n{proc.stdout}"
            
            elif action == 'status':
                proc = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                lines = [l for l in proc.stdout.splitlines() if 'ssh' in l or 'autossh' in l]
                output = "Active SSH Processes:\n" + ("\n".join(lines) if lines else "No autossh/ssh process active.")

            elif action == 'restart':
                subprocess.run(["pkill", "-f", "autossh"], stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "keep_ssh.sh"], stderr=subprocess.DEVNULL)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                keep_script = os.path.join(script_dir, "keep_ssh.sh")
                if os.path.exists(keep_script):
                    subprocess.Popen(["nohup", keep_script, user, host, str(port), "&"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    output = f"Restarted keep_ssh.sh for target {user}@{host}:{port} in background."
                else:
                    output = "keep_ssh.sh script not found. Please run setup.sh first."

            elif action == 'wake_lock':
                if subprocess.call(["which", "termux-wake-lock"], stdout=subprocess.DEVNULL) == 0:
                    subprocess.run(["termux-wake-lock"])
                    output = "Termux Wake-Lock enabled successfully."
                else:
                    output = "Termux wake-lock not available on non-Android Linux system."

            elif action == 'view_logs':
                log_path = os.path.expanduser("~/.ssh/autossh.log")
                if os.path.exists(log_path):
                    with open(log_path, 'r', errors='ignore') as f:
                        output = "".join(f.readlines()[-30:])
                else:
                    output = "Log file ~/.ssh/autossh.log does not exist yet."

            elif action == 'custom':
                if not cmd:
                    output = "No command provided."
                else:
                    # Execute SSH command against target host
                    ssh_cmd = [
                        "ssh", "-p", str(port),
                        "-o", "ConnectTimeout=10",
                        "-o", "StrictHostKeyChecking=accept-new",
                        f"{user}@{host}",
                        cmd
                    ]
                    proc = subprocess.run(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
                    output = proc.stdout if proc.returncode == 0 else f"Exit Code {proc.returncode}:\n{proc.stderr}\n{proc.stdout}"
            else:
                output = f"Unknown action: {action}"

        except subprocess.TimeoutExpired:
            error = "Execution timed out (Limit: 15s)."
        except Exception as e:
            error = f"Error during execution: {str(e)}"

        self._set_json_headers(200)
        self.wfile.write(json.dumps({"output": output, "error": error}, ensure_ascii=False).encode('utf-8'))

def run_server():
    server_address = ('', PORT)
    httpd = socketserver.TCPServer(server_address, SSHWebHandler)
    print(f"==================================================")
    print(f" 🚀 SSH Web Control UI active on http://0.0.0.0:{PORT}")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Web Server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
