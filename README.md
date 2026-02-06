# Terminal Printout Broadcast

Broadcast your PowerShell terminal output to students/viewers in real-time through a web browser.

## Objective

This tool allows instructors to share their terminal output with students during live coding sessions. Students can view the terminal output in real-time through any web browser - no installation required on their end.

```
[PowerShell Terminal] --> [Log File] --> [Python Server] --> [Tunnel] --> [Students' Browsers]
```

## Features

- Real-time terminal broadcast (0.5 second delay)
- Works with any web browser
- Supports 50+ simultaneous viewers
- No installation required for viewers
- Dark terminal-style interface
- Auto-scrolling to latest output
- **Permanent URL** with Cloudflare Tunnel (recommended)

---

## Tunnel Options

| Option | URL Type | Limits | Setup |
|--------|----------|--------|-------|
| **Cloudflare Tunnel** (recommended) | Permanent (`broadcast.yourdomain.com`) | Unlimited | Requires your own domain |
| ngrok | Changes each restart | Free tier has bandwidth limits | Free account required |
| localtunnel | Stable subdomain | Unlimited but asks for IP password | No signup |

---

## Prerequisites

### On Your Machine (Instructor)

- **Windows 10/11** with WSL2 (Ubuntu)
- **Python 3** (in WSL)
- **One of:** Cloudflare account + domain (recommended), ngrok account, or npm for localtunnel

---

## Installation

### Option A: Cloudflare Tunnel (Recommended - Permanent URL)

#### Step 1: Install cloudflared in WSL

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared && sudo mv /tmp/cloudflared /usr/local/bin/
```

#### Step 2: Login to Cloudflare

```bash
cloudflared tunnel login
```
Open the URL shown and authorize with your Cloudflare account.

#### Step 3: Create a Named Tunnel

```bash
cloudflared tunnel create terminal-broadcast
```

#### Step 4: Add DNS Route (use your domain)

```bash
cloudflared tunnel route dns terminal-broadcast broadcast.yourdomain.com
```

#### Step 5: Create Config File

Create `~/.cloudflared/config.yml`:
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/YOUR_USER/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: broadcast.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

Now you can use `broadcast-start-cloudflare` for a permanent URL!

---

### Option B: ngrok (Easy Setup - URL Changes)

#### Step 1: Install ngrok in WSL

Open WSL terminal and run:

```bash
# Add ngrok repository
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

# Install ngrok
sudo apt update && sudo apt install ngrok -y
```

### Step 2: Configure ngrok

1. Create a free account at: https://dashboard.ngrok.com/signup
2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure ngrok with your token:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 3: Clone This Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/TerminalPrintoutBroadcast.git
cd TerminalPrintoutBroadcast
```

### Step 4: Create Shared Folder

In PowerShell (as Administrator):

```powershell
New-Item -ItemType Directory -Path "C:\terminal_share" -Force
```

### Step 5: Add Scripts to PATH (Optional)

Add to your `~/.bashrc`:

```bash
export PATH="$PATH:$HOME/TerminalPrintoutBroadcast"
```

Then reload:

```bash
source ~/.bashrc
```

---

## Usage

### Quick Start

#### 1. Start the Broadcast (WSL)

```bash
# Using the script (if added to PATH)
broadcast-start-ngrok

# Or manually:
python3 ~/TerminalPrintoutBroadcast/server.py &
ngrok http 8080
```

Copy the ngrok URL shown (e.g., `https://xxxx-xx-xx.ngrok-free.app`)

#### 2. Start Logging (PowerShell)

For commands you type manually:
```powershell
Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append
```

For programs that print output:
```powershell
your-program.exe *>> C:\terminal_share\program_output.txt
```

#### 3. Share URL with Students

Send the ngrok URL to your students. They open it in any browser.

#### 4. Stop the Broadcast

PowerShell:
```powershell
Stop-Transcript
```

WSL:
```bash
broadcast-stop

# Or manually:
pkill -f server.py
pkill ngrok
```

---

## Detailed Usage

### Broadcasting Typed Commands

Use `Start-Transcript` for interactive PowerShell sessions:

```powershell
# Start logging
Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append

# Your commands are now broadcast
dir
Get-Process
# etc...

# Stop logging
Stop-Transcript
```

**Note:** Make sure the server is configured to read `server_output.txt`:
```python
LOG_FILE = "/mnt/c/terminal_share/server_output.txt"
```

### Broadcasting Program Output

For programs that print to stdout/stderr, use file redirection:

```powershell
# Redirect all output to file
your-program.exe *>> C:\terminal_share\program_output.txt

# Example with Python
python your_script.py *>> C:\terminal_share\program_output.txt

# Example with Node.js
node your_app.js *>> C:\terminal_share\program_output.txt
```

**Note:** Make sure the server is configured to read `program_output.txt`:
```python
LOG_FILE = "/mnt/c/terminal_share/program_output.txt"
```

### Switching Between Files

Edit `server.py` line 7 to change which file is broadcast:

```python
# For typed commands:
LOG_FILE = "/mnt/c/terminal_share/server_output.txt"

# For program output:
LOG_FILE = "/mnt/c/terminal_share/program_output.txt"
```

Then restart the server:
```bash
pkill -f server.py
python3 ~/TerminalPrintoutBroadcast/server.py &
```

---

## WSL Commands Reference

| Command | Description |
|---------|-------------|
| `broadcast-start-cloudflare` | Start broadcast with Cloudflare (permanent URL) |
| `broadcast-start-ngrok` | Start broadcast with ngrok |
| `broadcast-start-stable` | Start broadcast with localtunnel |
| `broadcast-stop` | Stop all broadcast services |
| `broadcast-status` | Check broadcast status |

---

## PowerShell Commands Reference

| Command | Description |
|---------|-------------|
| `Start-Transcript -Path "C:\terminal_share\server_output.txt" -Append` | Start logging typed commands |
| `Stop-Transcript` | Stop logging |
| `command *>> C:\terminal_share\program_output.txt` | Redirect program output |

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Server script | `~/TerminalPrintoutBroadcast/server.py` | Python HTTP server |
| Typed commands log | `C:\terminal_share\server_output.txt` | Start-Transcript output |
| Program output log | `C:\terminal_share\program_output.txt` | Redirected program output |
| Student URL | `C:\terminal_share\student_url.txt` | Saved broadcast URL |

---

## Troubleshooting

### "command not found" error
Open a new WSL terminal or run:
```bash
source ~/.bashrc
```

### ngrok authentication error
Make sure you configured your authtoken:
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### File is locked / being used by another process
Stop the transcript or use a different output file:
```powershell
Stop-Transcript
```

### Weird font / spaces between characters
The file encoding is wrong. The server expects UTF-16-LE for PowerShell redirected output. Check `server.py` uses the correct encoding:
```python
encoding='utf-16-le'  # For PowerShell redirected output
encoding='utf-8'      # For Start-Transcript output
```

### Browser shows old content
1. Hard refresh the browser (Ctrl+F5)
2. Check the server is running: `ps aux | grep server.py`
3. Restart the server

### Students can't access the URL
1. Check ngrok is running: `ps aux | grep ngrok`
2. Get the current URL: `curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*'`

---

## Alternative: Using localtunnel

If you prefer not to create an ngrok account, you can use localtunnel (no signup required):

### Install localtunnel
```bash
sudo npm install -g localtunnel
```

### Start with stable URL
```bash
broadcast-start-stable
# URL: https://lgm-monitor.loca.lt
```

**Note:** localtunnel may ask viewers for an IP verification on first visit.

---

## How It Works

1. **PowerShell** writes terminal output to a log file
2. **Python server** reads the log file and serves it as a web page
3. **ngrok** creates a secure tunnel from the internet to your local server
4. **Students** open the ngrok URL in their browser and see live updates

The web page auto-refreshes every 500ms to show new content.

---

## License

MIT License - Feel free to use and modify.

---

## Contributing

Pull requests welcome! Please open an issue first to discuss proposed changes.
