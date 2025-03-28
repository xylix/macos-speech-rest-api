#!/usr/bin/env python3
import http.server
import socketserver
import json
import subprocess
import shlex
import os
from urllib.parse import urlparse

PORT = int(os.environ.get('PORT', 3000))

class CommandHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def execute_command(self, command):
        try:
            # Use shlex.split to safely handle command arguments
            process = subprocess.run(command, shell=True, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True, 
                                    check=True)
            return {
                'success': True,
                'command': command,
                'stdout': process.stdout,
                'stderr': process.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'command': command,
                'error': 'Command execution failed',
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode
            }

    def do_POST(self):
        path = urlparse(self.path).path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            
            if path == '/say':
                if 'voice' not in data or 'text' not in data:
                    self._set_headers(400)
                    response = {'error': 'Missing required parameters: voice, text'}
                else:
                    # Sanitize inputs to prevent command injection
                    voice = shlex.quote(data['voice'])
                    text = shlex.quote(data['text'])
                    
                    # Execute the say command
                    command = f"say -v {voice} {text}"
                    result = self.execute_command(command)
                    
                    self._set_headers(200 if result['success'] else 500)
                    response = result
                    
            elif path == '/hear':
                if 'locale' not in data or 'timeout' not in data or 'exitWord' not in data:
                    self._set_headers(400)
                    response = {'error': 'Missing required parameters: locale, timeout, exitWord'}
                else:
                    # Sanitize inputs to prevent command injection
                    locale = shlex.quote(data['locale'])
                    timeout = shlex.quote(str(data['timeout']))
                    exit_word = shlex.quote(data['exitWord'])
                    
                    # Execute the hear command
                    command = f"hear -p -l {locale} -t {timeout} -x {exit_word}"
                    result = self.execute_command(command)
                    
                    self._set_headers(200 if result['success'] else 500)
                    response = result
            else:
                self._set_headers(404)
                response = {'error': 'Endpoint not found'}
                
        except json.JSONDecodeError:
            self._set_headers(400)
            response = {'error': 'Invalid JSON in request body'}
        except Exception as e:
            self._set_headers(500)
            response = {'error': f'Server error: {str(e)}'}
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server():
    handler = CommandHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print("Endpoints available:")
        print(f"- POST /say - Execute 'say -v <voice> <text>'")
        print(f"- POST /hear - Execute 'hear -p -l <locale> -t <timeout> -x <exitWord>'")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
