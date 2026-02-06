# Terminal Printout Broadcast

A tool for instructors to broadcast their terminal output to students in real-time through a web browser.

---

## Table of Contents

1. [What Problem Does This Solve?](#what-problem-does-this-solve)
2. [How It Works - The Concept](#how-it-works---the-concept)
3. [Data Flow Diagram](#data-flow-diagram)
4. [Tunnel Options Comparison](#tunnel-options-comparison)
5. [Why We Chose Cloudflare Tunnel](#why-we-chose-cloudflare-tunnel)
6. [Prerequisites - What You Need](#prerequisites---what-you-need)
7. [Free Account Limits](#free-account-limits)
8. [Risks and Considerations](#risks-and-considerations)
9. [Installation Guide](#installation-guide)
10. [Configuration](#configuration)
11. [Usage Guide](#usage-guide)
12. [Status Monitoring](#status-monitoring)
13. [Troubleshooting](#troubleshooting)
14. [File Reference](#file-reference)

---

## What Problem Does This Solve?

### The Problem

During live coding sessions or classes, instructors need to share their terminal output with students. Traditional solutions have limitations:

| Traditional Solution | Problem |
|---------------------|---------|
| Screen sharing (Zoom/Teams) | High bandwidth, lag, requires all students to join call |
| Projector | Only works in physical classroom |
| Copy-paste to chat | Manual, not real-time, loses formatting |
| SSH access for students | Security risk, complex setup |

### The Solution

This tool creates a **live web page** that displays your terminal output. Students simply open a URL in their browser - no installation, no login, no special software required.

**Example:** You run a server on your machine. Students open `https://broadcast.gal-tech.net` and see every log message as it appears, with less than 1 second delay.

---

## How It Works - The Concept

The system has four components:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  Your       │    │  Log File    │    │  Python     │    │  Tunnel     │
│  Program    │───>│  (Windows)   │<───│  Server     │───>│  Service    │
│             │    │              │    │  (WSL)      │    │             │
└─────────────┘    └──────────────┘    └─────────────┘    └──────┬──────┘
                                                                  │
                                                                  │ Internet
                                                                  ▼
                                                         ┌─────────────┐
                                                         │  Student's  │
                                                         │  Browser    │
                                                         └─────────────┘
```

### Component Explanation

| Component | What It Does | Location |
|-----------|--------------|----------|
| **Your Program** | Prints output that you want to share | PowerShell (Windows) |
| **Log File** | Stores the output in a text file | `C:\terminal_share\program_output.txt` |
| **Python Server** | Reads the file and serves it as a web page | WSL (localhost:8080) |
| **Tunnel Service** | Makes your local server accessible from the internet | WSL → Internet |
| **Student's Browser** | Displays the web page with auto-refresh | Any device, anywhere |

### The Magic: Auto-Refresh

The web page contains JavaScript that fetches new content every **500 milliseconds** (0.5 seconds). This creates the illusion of real-time streaming without complex WebSocket setup.

---

## Data Flow Diagram

```
STEP 1: Program Output
========================
PowerShell> uv run my-server.py *>> C:\terminal_share\program_output.txt

    Your program prints: "[INFO] Server started on port 3000"
                              │
                              ▼
STEP 2: File Write
========================
    Windows writes to: C:\terminal_share\program_output.txt
    (File grows with each new line)
                              │
                              ▼
STEP 3: Server Reads
========================
    Python server (WSL) reads: /mnt/c/terminal_share/program_output.txt
    Converts to HTML with terminal styling
    Serves on: http://localhost:8080
                              │
                              ▼
STEP 4: Tunnel Forwards
========================
    Cloudflared creates encrypted tunnel:
    localhost:8080 ←──────→ Cloudflare Edge Servers
                              │
                              ▼
STEP 5: DNS Resolution
========================
    Student types: https://broadcast.gal-tech.net
    DNS resolves to: Cloudflare Edge Server
    Cloudflare routes to: Your tunnel → Your server
                              │
                              ▼
STEP 6: Browser Display
========================
    Browser receives HTML page
    JavaScript fetches /content every 500ms
    New content appears automatically

    ┌────────────────────────────────────┐
    │ Terminal Broadcast           Live  │
    │────────────────────────────────────│
    │ [INFO] Server started on port 3000 │
    │ [INFO] Client connected: 192.168.1 │
    │ [INFO] Processing request...       │
    │ █                                  │
    └────────────────────────────────────┘
```

---

## Tunnel Options Comparison

We evaluated three tunneling services:

| Feature | Cloudflare Tunnel | ngrok | localtunnel |
|---------|-------------------|-------|-------------|
| **URL Type** | Permanent (your domain) | Random, changes each restart | Stable subdomain |
| **Example URL** | `broadcast.gal-tech.net` | `a1b2c3.ngrok-free.app` | `lgm-monitor.loca.lt` |
| **Bandwidth Limit** | Unlimited | 1 GB/month (free) | Unlimited |
| **Requires Account** | Yes (free) | Yes (free) | No |
| **Requires Domain** | Yes | No | No |
| **IP Verification** | No | No | Yes (annoying) |
| **Reliability** | Excellent | Good | Poor |
| **Setup Complexity** | Medium | Easy | Easy |
| **Cost** | Free | Free (limited) / $8/mo | Free |

### Detailed Comparison

#### ngrok
```
Pros:
  + Easy setup (5 minutes)
  + No domain required
  + Good documentation

Cons:
  - URL changes every restart (students need new link each class)
  - 1 GB/month bandwidth limit (can hit this quickly with many students)
  - Free tier shows "Visit Site" interstitial page

Why we stopped using it:
  We hit the bandwidth limit during a class with 30 students.
```

#### localtunnel
```
Pros:
  + No account required
  + Stable subdomain (lgm-monitor.loca.lt)
  + Unlimited bandwidth

Cons:
  - Asks students for IP password on first visit
  - Unreliable (tunnel drops frequently)
  - IP verification often fails even with correct IP

Why we stopped using it:
  Students kept getting "incorrect IP" errors even with the right password.
```

#### Cloudflare Tunnel (Recommended)
```
Pros:
  + Permanent URL that never changes
  + Unlimited bandwidth
  + Highly reliable (enterprise-grade)
  + No interstitial pages
  + Free forever

Cons:
  - Requires owning a domain (~$10/year)
  - More complex initial setup (15-20 minutes)
  - Domain DNS must be on Cloudflare

Why we chose it:
  Once configured, it just works. Students bookmark one URL and use it
  all semester. No bandwidth limits, no IP verification, no surprises.
```

---

## Why We Chose Cloudflare Tunnel

After testing all three options in real classroom settings:

1. **ngrok** failed us when we hit bandwidth limits mid-class
2. **localtunnel** frustrated students with constant IP verification errors
3. **Cloudflare Tunnel** required more setup but has been 100% reliable

**Bottom line:** Spend 20 minutes setting up Cloudflare once, or waste 5 minutes every class dealing with ngrok/localtunnel issues.

---

## Prerequisites - What You Need

### Required

| Requirement | Why Needed | How to Get |
|-------------|------------|------------|
| Windows 10/11 | Your main OS | Already have it |
| WSL2 (Ubuntu) | Run Linux tools | `wsl --install` in PowerShell |
| Python 3 | Run the server | Pre-installed in Ubuntu WSL |
| Domain name | For permanent URL | Purchase from Namecheap, GoDaddy, etc. (~$10/year) |
| Cloudflare account | Manage tunnel | https://dash.cloudflare.com/sign-up (free) |

### Domain Options

You can use:
- **A new domain** purchased for this purpose (~$10/year for `.net`)
- **An existing domain** you already own (add a subdomain like `broadcast.`)
- **A domain connected to other services** (Gmail Workspace, Wix) - just add the subdomain to Cloudflare

**Example:** If you own `myschool.com` for email, you can still use `broadcast.myschool.com` for this tool.

---

## Free Account Limits

### Cloudflare (Our Recommended Solution)

| Resource | Free Limit | Typical Usage |
|----------|------------|---------------|
| Tunnels | Unlimited | You need 1 |
| Bandwidth | Unlimited | Not a concern |
| Requests | Unlimited | Not a concern |
| Concurrent connections | 1000+ | You'll use 1-100 |

**Cloudflare's free tier is genuinely unlimited for this use case.**

### ngrok (Alternative)

| Resource | Free Limit | What Happens When Exceeded |
|----------|------------|---------------------------|
| Bandwidth | 1 GB/month | Tunnel stops working |
| Connections | 40/minute | Requests rejected |
| Tunnels | 1 | Cannot create more |

**Example:** 50 students refreshing every 0.5 seconds for 1 hour = ~180,000 requests. With 10 KB per response, that's 1.8 GB - exceeds free limit.

### localtunnel (Alternative)

| Resource | Free Limit |
|----------|------------|
| Everything | Unlimited |

**Catch:** Reliability is poor and IP verification annoys users.

---

## Risks and Considerations

### Security Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Anyone with URL can view | Medium | URL is not guessable, share only with students |
| Terminal output may contain secrets | High | Never display passwords, API keys, or credentials |
| Students see your file paths | Low | Generally not sensitive |

### Privacy Considerations

- Students can see everything your program outputs
- If you type passwords in the terminal, they will be visible
- Your Windows username and paths are visible

**Best Practice:** Create a dedicated PowerShell window for broadcasting. Don't use it for anything sensitive.

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tunnel disconnects | Students can't view | `broadcast-status` alerts you |
| Server crashes | Students see stale content | Restart with `broadcast-start-cloudflare` |
| File grows too large | Slow loading | Clear file between classes |

---

## Installation Guide

### Step 1: Install WSL (if not already installed)

Open PowerShell as Administrator:
```powershell
wsl --install
```

Restart your computer, then open Ubuntu from Start menu.

### Step 2: Clone the Repository

In WSL terminal:
```bash
cd ~
git clone https://github.com/rmisegal/TerminalPrintoutBroadcast.git
cd TerminalPrintoutBroadcast
```

### Step 3: Add Scripts to PATH

```bash
echo 'export PATH="$PATH:$HOME/TerminalPrintoutBroadcast"' >> ~/.bashrc
source ~/.bashrc
```

**Verify:**
```bash
which broadcast-start-cloudflare
# Should output: /home/yourusername/TerminalPrintoutBroadcast/broadcast-start-cloudflare
```

### Step 4: Create Shared Folder

In PowerShell:
```powershell
New-Item -ItemType Directory -Path "C:\terminal_share" -Force
```

**Verify in WSL:**
```bash
ls /mnt/c/terminal_share
# Should show empty directory (no error)
```

### Step 5: Install cloudflared

In WSL:
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared
sudo mv /tmp/cloudflared /usr/local/bin/
```

**Verify:**
```bash
cloudflared --version
# Should output: cloudflared version 2024.x.x
```

---

## Configuration

### Step 1: Add Domain to Cloudflare

1. Go to https://dash.cloudflare.com
2. Click **"Add a domain"**
3. Enter your domain (e.g., `gal-tech.net`)
4. Select **Free plan**
5. Cloudflare shows you nameservers like:
   ```
   ada.ns.cloudflare.com
   bob.ns.cloudflare.com
   ```

### Step 2: Update Nameservers

Go to where you bought your domain (GoDaddy, Namecheap, etc.) and change nameservers to Cloudflare's.

**Example (Namecheap):**
1. Login to Namecheap
2. Domain List → Manage
3. Nameservers → Custom DNS
4. Enter Cloudflare nameservers
5. Save

**Wait 5-30 minutes for DNS propagation.**

### Step 3: Login to Cloudflare from WSL

```bash
cloudflared tunnel login
```

This opens a browser. Select your domain and click **Authorize**.

**Verify:**
```bash
ls ~/.cloudflared/cert.pem
# Should exist
```

### Step 4: Create the Tunnel

```bash
cloudflared tunnel create terminal-broadcast
```

**Output example:**
```
Tunnel credentials written to /home/user/.cloudflared/abc123-def456.json
Created tunnel terminal-broadcast with id abc123-def456-ghi789
```

**Save the tunnel ID** (e.g., `abc123-def456-ghi789`)

### Step 5: Create DNS Route

```bash
cloudflared tunnel route dns terminal-broadcast broadcast.yourdomain.com
```

**Example:**
```bash
cloudflared tunnel route dns terminal-broadcast broadcast.gal-tech.net
```

### Step 6: Create Configuration File

Create `~/.cloudflared/config.yml`:

```bash
nano ~/.cloudflared/config.yml
```

Enter (replace with your values):
```yaml
tunnel: abc123-def456-ghi789
credentials-file: /home/YOURUSERNAME/.cloudflared/abc123-def456-ghi789.json

ingress:
  - hostname: broadcast.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

**Example for user `rmisegal` with domain `gal-tech.net`:**
```yaml
tunnel: 3177c4d7-75c4-4a49-9de3-1fd78bcc4250
credentials-file: /home/rmisegal/.cloudflared/3177c4d7-75c4-4a49-9de3-1fd78bcc4250.json

ingress:
  - hostname: broadcast.gal-tech.net
    service: http://localhost:8080
  - service: http_status:404
```

Save and exit (Ctrl+X, Y, Enter).

---

## Usage Guide

### Starting a Broadcast Session

#### Step 1: Start the Broadcast (WSL)

```bash
broadcast-start-cloudflare
```

**Expected output:**
```
==========================================
  LGM Terminal Broadcast - CLOUDFLARE
==========================================

[OK] Shared folder exists: /mnt/c/terminal_share
[OK] Log file exists: /mnt/c/terminal_share/program_output.txt
[OK] Web server running on port 8080
[OK] Cloudflare tunnel connected

==========================================
  BROADCAST READY!
==========================================

  PERMANENT STUDENT URL:
  https://broadcast.gal-tech.net

==========================================
```

#### Step 2: Run Your Program (PowerShell)

```powershell
your-program.exe *>> C:\terminal_share\program_output.txt
```

**Examples:**

Python script:
```powershell
python my_server.py *>> C:\terminal_share\program_output.txt
```

Node.js app:
```powershell
node app.js *>> C:\terminal_share\program_output.txt
```

UV/Python project:
```powershell
uv run my-command *>> C:\terminal_share\program_output.txt
```

#### Step 3: Share URL with Students

Send this URL to your students:
```
https://broadcast.yourdomain.com
```

They open it in any browser (phone, tablet, laptop) - no login required.

### Stopping a Broadcast Session

#### Step 1: Stop Your Program (PowerShell)

Press `Ctrl+C` in PowerShell to stop your program.

#### Step 2: Stop the Broadcast (WSL)

```bash
broadcast-stop
```

**Expected output:**
```
Stopping broadcast...
[OK] Broadcast stopped.
```

### Clearing Old Output

Before starting a new session, clear the previous output:

**PowerShell:**
```powershell
Remove-Item C:\terminal_share\program_output.txt -ErrorAction SilentlyContinue
```

Or **WSL:**
```bash
rm /mnt/c/terminal_share/program_output.txt
```

---

## Status Monitoring

### Check Broadcast Status

```bash
broadcast-status
```

**Example output (everything working):**
```
==========================================
  LGM Terminal Broadcast - STATUS
==========================================

[OK] Python server running (PID: 18654)
[OK] Cloudflare tunnel running (PID: 22217)

==========================================
  URL
==========================================
  https://broadcast.gal-tech.net

==========================================
  LOG FILE STATUS
==========================================
  File: C:\terminal_share\program_output.txt
  Last modified: 2026-02-05 14:23:45

  [OK] File updated 3 seconds ago
  Size: 45 KB (46123 bytes)

==========================================
  LAST 5 LINES OF OUTPUT
==========================================

[INFO] Processing request from client 192.168.1.50
[INFO] Query completed in 0.023s
[INFO] Sending response...
[INFO] Request completed successfully
[INFO] Waiting for next request...

==========================================
  BROWSER REFRESH RATE
==========================================

  The browser auto-refreshes every 500ms (0.5 seconds)
  Students see updates within 0.5-1 second of file change
```

**Example output (problem detected):**
```
==========================================
  LOG FILE STATUS
==========================================
  File: C:\terminal_share\program_output.txt
  Last modified: 2026-02-05 14:20:00

  [!] WARNING: No update for 245 seconds!
      (Last update was more than 10 seconds ago)
```

This means your program stopped producing output. Check if it's still running.

---

## Troubleshooting

### Problem: "command not found"

**Symptom:**
```bash
broadcast-start-cloudflare: command not found
```

**Solution:**
```bash
source ~/.bashrc
# Or open a new terminal
```

### Problem: Tunnel won't connect

**Symptom:**
```
[ERROR] Failed to start tunnel
```

**Solution:**
```bash
# Check if already logged in
ls ~/.cloudflared/cert.pem

# If not, login again
cloudflared tunnel login
```

### Problem: Students see old content

**Symptom:** Browser shows content from last class.

**Solution:**
```bash
# Clear the log file
rm /mnt/c/terminal_share/program_output.txt

# Restart broadcast
broadcast-stop
broadcast-start-cloudflare
```

### Problem: Weird characters / spaces between letters

**Symptom:** Output looks like `H e l l o   W o r l d`

**Cause:** PowerShell writes UTF-16, server reads UTF-8.

**Solution:** The server is already configured for UTF-16-LE. If you still see this, restart the server:
```bash
broadcast-stop
broadcast-start-cloudflare
```

### Problem: File locked by another process

**Symptom:**
```
out-file : The process cannot access the file
```

**Solution:** Another program has the file open. Close it:
```powershell
# If using Start-Transcript
Stop-Transcript

# Then use redirection instead
your-program.exe *>> C:\terminal_share\program_output.txt
```

### Problem: WSL DNS not resolving (curl fails but browser works)

**Symptom:**
```bash
curl: (6) Could not resolve host: broadcast.gal-tech.net
```

**Cause:** WSL's auto-generated DNS configuration points to an internal resolver that doesn't work properly.

**Solution:**

Step 1: Disable auto DNS generation
```bash
sudo bash -c 'cat > /etc/wsl.conf << EOF
[network]
generateResolvConf = false
EOF'
```

Step 2: Set public DNS servers
```bash
sudo rm /etc/resolv.conf
sudo bash -c 'cat > /etc/resolv.conf << EOF
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 8.8.4.4
EOF'
```

Step 3: Verify
```bash
curl -s https://broadcast.gal-tech.net | head -5
# Should show HTML content
```

**Note:** After `wsl --shutdown`, the fix persists because of the `/etc/wsl.conf` setting.

---

## File Reference

### Project Files

| File | Purpose |
|------|---------|
| `server.py` | Python HTTP server that serves the log file as HTML |
| `broadcast-start-cloudflare` | Start broadcast with Cloudflare tunnel |
| `broadcast-start-ngrok` | Start broadcast with ngrok (alternative) |
| `broadcast-start-stable` | Start broadcast with localtunnel (alternative) |
| `broadcast-stop` | Stop all broadcast services |
| `broadcast-status` | Check status and show last output |

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `cert.pem` | `~/.cloudflared/` | Cloudflare account credentials |
| `*.json` | `~/.cloudflared/` | Tunnel-specific credentials |
| `config.yml` | `~/.cloudflared/` | Tunnel routing configuration |

### Runtime Files

| File | Location | Purpose |
|------|----------|---------|
| `program_output.txt` | `C:\terminal_share\` | Your program's output |
| `server_output.txt` | `C:\terminal_share\` | Start-Transcript output (alternative) |
| `student_url.txt` | `C:\terminal_share\` | Saved broadcast URL |

---

## Quick Reference Card

### Start Class
```bash
# WSL
broadcast-start-cloudflare
```
```powershell
# PowerShell
your-program.exe *>> C:\terminal_share\program_output.txt
```

### Check Status
```bash
# WSL
broadcast-status
```

### End Class
```powershell
# PowerShell - Stop your program
Ctrl+C
```
```bash
# WSL
broadcast-stop
```

### Student URL
```
https://broadcast.gal-tech.net
```

---

## License

MIT License - Feel free to use and modify.

## Repository

https://github.com/rmisegal/TerminalPrintoutBroadcast
