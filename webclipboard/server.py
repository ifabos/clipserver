"""
Web Clipboard Server - A web-based clipboard sharing server

This module provides a simple HTTP server that allows viewing and
modifying the system clipboard through a web interface.
"""

import os
import random
import string
import http.server
import socketserver
import base64
import json
import pyperclip
from urllib.parse import parse_qs
import threading
import webbrowser

# Default configuration
DEFAULT_PORT = 8080
USERNAME = "clipboard"
TOKEN_LENGTH = 8

class WebClipboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the Web Clipboard server."""
    
    def __init__(self, *args, auth_token=None, **kwargs):
        self.auth_token = auth_token
        self.authenticated_sessions = kwargs.pop('authenticated_sessions', set())
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # Check if this is the root path
        if self.path == '/':
            # Check authentication
            if self.is_authenticated():
                self.send_main_page()
            else:
                self.send_auth_page()
            return
        
        # API endpoint to get clipboard content
        elif self.path == '/api/get-clipboard':
            if not self.is_authenticated():
                self.send_error(401, "Unauthorized")
                return
            
            try:
                clipboard_content = pyperclip.paste()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"content": clipboard_content}).encode())
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
            return
        
        # Serve favicon
        elif self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
            
        self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests."""
        # Handle login form submission
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)
            
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if username == USERNAME and password == self.auth_token:
                # Generate session token
                session_token = base64.b64encode(os.urandom(16)).decode('utf-8')
                self.authenticated_sessions.add(session_token)
                
                # Redirect to main page with session token
                self.send_response(302)
                self.send_header('Set-Cookie', f'session={session_token}; Path=/')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                # Authentication failed
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authentication Failed</h1><p>Invalid username or password.</p><a href="/">Try again</a></body></html>')
            return
        
        # API endpoint to set clipboard content
        elif self.path == '/api/set-clipboard':
            if not self.is_authenticated():
                self.send_error(401, "Unauthorized")
                return
            
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                json_data = json.loads(post_data)
                
                clipboard_content = json_data.get('content', '')
                pyperclip.copy(clipboard_content)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
            return
        
        self.send_error(404, "Not Found")
    
    def is_authenticated(self):
        """Check if the request has a valid session cookie."""
        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            for cookie in cookies.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('session='):
                    session_token = cookie[8:]  # Remove 'session=' prefix
                    if session_token in self.authenticated_sessions:
                        return True
        return False
    
    def send_auth_page(self):
        """Send the authentication page."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        auth_page = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Web Clipboard - Login</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }}
                .login-container {{
                    background-color: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    width: 300px;
                }}
                h1 {{
                    margin-top: 0;
                    text-align: center;
                }}
                form {{
                    display: flex;
                    flex-direction: column;
                }}
                label {{
                    margin-bottom: 0.5rem;
                }}
                input {{
                    padding: 0.5rem;
                    margin-bottom: 1rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }}
                button {{
                    padding: 0.5rem;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>Web Clipboard</h1>
                <form action="/login" method="post">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" value="clipboard" readonly>
                    
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                    
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        '''
        
        self.wfile.write(auth_page.encode())
    
    def send_main_page(self):
        """Send the main clipboard page."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        main_page = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Web Clipboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                .header {
                    background-color: #f5f5f5;
                    padding: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                .title {
                    margin: 0;
                    font-size: 1.5rem;
                }
                .button-container {
                    display: flex;
                    gap: 1rem;
                }
                .button {
                    padding: 0.5rem 1rem;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .button:hover {
                    background-color: #0056b3;
                }
                .content {
                    flex: 1;
                    padding: 1rem;
                    #display: flex;
                    justify-content: center;
                    align-items: center;
                }
                #clipboardText {
                    width: 100%;
                    height: 75vh;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    resize: vertical;
                }
                .status {
                    padding: 0.5rem 1rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    display: none;
                }
                .success {
                    background-color: #d4edda;
                    color: #155724;
                }
                .error {
                    background-color: #f8d7da;
                    color: #721c24;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="title">Web Clipboard</h1>
                <div class="button-container">
                    <button id="refreshButton" class="button">Refresh</button>
                    <button id="pasteButton" class="button">Paste</button>
                </div>
            </div>
            
            <div id="statusMessage" class="status"></div>
            
            <div class="content">
                <textarea id="clipboardText" placeholder="Clipboard content will appear here..."></textarea>
            </div>
            
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const clipboardText = document.getElementById('clipboardText');
                    const refreshButton = document.getElementById('refreshButton');
                    const pasteButton = document.getElementById('pasteButton');
                    const statusMessage = document.getElementById('statusMessage');
                    
                    // Function to show status message
                    function showStatus(message, isSuccess) {
                        statusMessage.textContent = message;
                        statusMessage.className = isSuccess ? 'status success' : 'status error';
                        statusMessage.style.display = 'block';
                        
                        setTimeout(() => {
                            statusMessage.style.display = 'none';
                        }, 3000);
                    }
                    
                    // Function to get clipboard content from server
                    function getClipboardContent() {
                        fetch('/api/get-clipboard')
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Failed to fetch clipboard content');
                                }
                                return response.json();
                            })
                            .then(data => {
                                clipboardText.value = data.content;
                                showStatus('Clipboard content refreshed', true);
                            })
                            .catch(error => {
                                showStatus(error.message, false);
                            });
                    }
                    
                    // Function to set clipboard content on server
                    function setClipboardContent() {
                        fetch('/api/set-clipboard', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ content: clipboardText.value })
                        })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Failed to update clipboard content');
                                }
                                return response.json();
                            })
                            .then(data => {
                                if (data.success) {
                                    showStatus('Clipboard updated successfully', true);
                                }
                            })
                            .catch(error => {
                                showStatus(error.message, false);
                            });
                    }
                    
                    // Event listeners
                    refreshButton.addEventListener('click', getClipboardContent);
                    pasteButton.addEventListener('click', setClipboardContent);
                    
                    // Load clipboard content on page load
                    getClipboardContent();
                });
            </script>
        </body>
        </html>
        '''
        
        self.wfile.write(main_page.encode())


def create_handler_class(auth_token, authenticated_sessions):
    """Create a handler class with the specified auth token and session store."""
    return type('CustomWebClipboardHandler', (WebClipboardHandler,), {
        '__init__': lambda self, *args, **kwargs: WebClipboardHandler.__init__(
            self, *args, auth_token=auth_token, authenticated_sessions=authenticated_sessions, **kwargs
        )
    })


def start_server(port=DEFAULT_PORT, open_browser=True):
    """
    Start the Web Clipboard server.
    
    Args:
        port (int): The port to run the server on (default: 8080)
        open_browser (bool): Whether to automatically open a browser (default: True)
    
    Returns:
        None
    """
    # Generate random token
    auth_token = ''.join(random.choices(string.ascii_letters + string.digits, k=TOKEN_LENGTH))
    authenticated_sessions = set()
    
    # Create custom handler class with auth token
    handler_class = create_handler_class(auth_token, authenticated_sessions)
    
    try:
        # Create and configure the server
        httpd = socketserver.TCPServer(("", port), handler_class)
        
        print(f"Web Clipboard Server started at http://localhost:{port}")
        print(f"Username: {USERNAME}")
        print(f"Password: {auth_token}")
        
        # Open browser after a short delay
        if open_browser:
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}', new=2)).start()
        
        # Start the server
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        print("Server shut down successfully")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    start_server()
