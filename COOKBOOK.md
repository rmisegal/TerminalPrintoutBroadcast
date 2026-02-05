# Cookbook: Broadcast PowerShell Output to Students

## Overview

```
[PowerShell Terminal] → [Log File] → [Python Server] → [Tunnel] → [Students' Browsers]
```

---

## Tunnel Options

| Option | Pros | Cons |
|--------|------|------|
| **ngrok** (recommended) | Reliable, no IP verification | Requires free account |
| **localtunnel** | No signup needed | Sometimes asks for IP password |

---

## Quick Start Commands

### WSL Commands

| Action | ngrok | localtunnel |
|--------|-------|-------------|
| **Start** | `broadcast-start-ngrok` | `broadcast-start-stable` |
| **Check status** | `broadcast-status` | `broadcast-status` |
| **Stop** | `broadcast-stop` | `broadcast-stop` |

### PowerShell Commands

| Action | Command |
|--------|---------|
| **Start logging** | `Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append` |
| **Stop logging** | `Stop-Transcript` |

---

# NGROK SETUP (One-Time)

## 1. Create Free Account

1. Go to: https://dashboard.ngrok.com/signup
2. Sign up with email or GitHub
3. Verify your email

## 2. Get Your Auth Token

1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your authtoken

## 3. Configure ngrok in WSL

```bash
# Install ngrok (if not installed)
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Add your authtoken
ngrok config add-authtoken YOUR_TOKEN_HERE
```

---

# RUNNING THE BROADCAST

## Step-by-Step (Each Class)

### 1. Start Broadcast (WSL)

**Using ngrok (recommended):**
```bash
broadcast-start-ngrok
```
→ Copy the URL shown (e.g., `https://xxxxx.ngrok-free.app`)

**Using localtunnel (alternative):**
```bash
broadcast-start-stable
```
→ URL is always: `https://lgm-monitor.loca.lt`

### 2. Start Logging (PowerShell)

```powershell
Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append
```

### 3. Run Your Server/Commands (PowerShell)

```powershell
.\your_server.ps1
# or any commands you want students to see
```
→ Students now see all output live!

### 4. End of Class - Stop Everything

**PowerShell:**
```powershell
Stop-Transcript
```

**WSL:**
```bash
broadcast-stop
```

---

## What Students Do

1. Open the URL you share in any browser
2. See your PowerShell terminal output live (read-only)
3. No installation needed

---

## Files Location

| File | Path |
|------|------|
| Student URL | `C:\terminal_share\student_url.txt` |
| Log file | `C:\terminal_share\server_output.txt` |
| Scripts | `~/lgm-broadcast/` |
| Backup | `~/lgm-broadcast/backup/` |

---

## How It Works

1. **Start-Transcript** - PowerShell logs all output to a file
2. **Python Server** - Serves the log file as a web page with auto-refresh (every 0.5 sec)
3. **Tunnel (ngrok/localtunnel)** - Exposes local server to internet

---

## Troubleshooting

**"broadcast-start-ngrok: command not found"**
→ Open a NEW WSL terminal, or run: `source ~/.bashrc`

**ngrok authentication error**
→ Make sure you ran: `ngrok config add-authtoken YOUR_TOKEN`

**localtunnel IP password error**
→ Use ngrok instead, or enter your public IP (run `curl ipv4.icanhazip.com`)

**URL not working**
→ Run `broadcast-status` to verify it's running
→ Run `broadcast-stop` then restart

**PowerShell output not appearing**
→ Make sure you ran `Start-Transcript` in PowerShell
→ Check `C:\terminal_share\server_output.txt` has content

**Need to restart broadcast**
```bash
broadcast-stop
broadcast-start-ngrok
```

---

## Important Notes

- **ngrok URL** (`broadcast-start-ngrok`): URL changes each restart (e.g., `https://xxxxx.ngrok-free.app`)
- **localtunnel URL** (`broadcast-start-stable`): Always `https://lgm-monitor.loca.lt`
- Supports 50+ simultaneous viewers
- Broadcast runs in background
- Students see output with ~0.5 second delay
- Browser auto-refreshes every 0.5 seconds

---

## Quick Reference Card

### Start Class (ngrok)
```bash
# WSL
broadcast-start-ngrok
```
```powershell
# PowerShell
Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append
```

### End Class
```powershell
# PowerShell
Stop-Transcript
```
```bash
# WSL
broadcast-stop
```

---

## Manual Commands (Advanced)

If the shortcut commands don't work, use these manual commands:

### Start Manually (WSL)
```bash
# 1. Start Python server
python3 ~/lgm-broadcast/server.py &

# 2. Start ngrok tunnel
ngrok http 8080

# Or for localtunnel:
lt --port 8080 --subdomain lgm-monitor
```

### Stop Manually (WSL)
```bash
pkill -f server.py
pkill ngrok
pkill lt
```

### Check Status Manually (WSL)
```bash
# Check if processes are running
ps aux | grep -E 'server.py|ngrok|lt' | grep -v grep

# Get ngrok URL
curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*'
```
