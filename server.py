#!/usr/bin/env python3
"""Simple HTTP server that serves PowerShell terminal output with auto-refresh"""

import http.server
import os

LOG_FILE = "/mnt/c/terminal_share/program_output.txt"
PORT = 8080

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Terminal Broadcast</title>
    <style>
        body {{
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            padding: 20px;
            margin: 0;
        }}
        #terminal {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        #status {{
            position: fixed;
            top: 10px;
            right: 10px;
            color: #888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="status">Live</div>
    <div id="terminal">{content}</div>
    <script>
        let lastLength = 0;

        async function refresh() {{
            try {{
                const response = await fetch('/content');
                const text = await response.text();
                if (text.length !== lastLength) {{
                    document.getElementById('terminal').textContent = text;
                    lastLength = text.length;
                    window.scrollTo(0, document.body.scrollHeight);
                }}
                document.getElementById('status').textContent = 'Live';
                document.getElementById('status').style.color = '#00ff00';
            }} catch (e) {{
                document.getElementById('status').textContent = 'Reconnecting...';
                document.getElementById('status').style.color = '#ff0000';
            }}
        }}

        // Refresh every 500ms for near real-time updates
        setInterval(refresh, 500);

        // Initial scroll to bottom
        window.scrollTo(0, document.body.scrollHeight);
    </script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/content':
            # Return raw file content
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            try:
                with open(LOG_FILE, 'r', encoding='utf-16-le', errors='ignore') as f:
                    content = f.read()
                self.wfile.write(content.encode('utf-8'))
            except:
                self.wfile.write(b'Waiting for content...')
        else:
            # Return HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            try:
                with open(LOG_FILE, 'r', encoding='utf-16-le', errors='ignore') as f:
                    content = f.read()
            except:
                content = 'Waiting for content...'
            html = HTML_TEMPLATE.format(content=content.replace('<', '&lt;').replace('>', '&gt;'))
            self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress logging

if __name__ == '__main__':
    print(f"Starting server on port {PORT}...")
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    server.serve_forever()
