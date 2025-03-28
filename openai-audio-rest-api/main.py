import os
import json
import uuid
import tempfile
import subprocess
import http.server
import socketserver
from typing import Dict, Any

# List of available macOS voices (can be extended)
VOICE_MAPPING = {
    "alloy": "Alex",     # Default OpenAI -> Default macOS
    "echo": "Samantha",
    "fable": "Daniel",
    "onyx": "Fred",
    "nova": "Victoria",
    "shimmer": "Karen"
}

class OpenAICompatibleTTSHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OpenAI-compatible TTS API"""
    
    def _set_headers(self, status_code=200, content_type="application/json"):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _handle_options(self):
        """Handle OPTIONS requests for CORS preflight"""
        self._set_headers()
        
    def do_OPTIONS(self):
        """Handle OPTIONS method for CORS support"""
        self._handle_options()
        
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/v1/audio/voices":
            self._handle_list_voices()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": {
                    "message": "Not found",
                    "type": "invalid_request_error",
                    "code": "not_found"
                }
            }).encode("utf-8"))
    
    def _handle_list_voices(self):
        """List available voices endpoint"""
        voices = [
            {"voice": openai_voice, "name": macos_voice} 
            for openai_voice, macos_voice in VOICE_MAPPING.items()
        ]
        
        response = {
            "object": "list",
            "data": voices
        }
        
        self._set_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/v1/audio/speech":
            self._handle_speech()
        elif self.path == "/v1/audio/transcriptions":
            self._handle_transcription()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                "error": {
                    "message": "Not found",
                    "type": "invalid_request_error",
                    "code": "not_found"
                }
            }).encode("utf-8"))
    
    def _parse_json_body(self) -> Dict[str, Any]:
        """Parse JSON request body"""
        content_length = int(self.headers.get("Content-Length", 0))
        request_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(request_body)
    
    def _handle_speech(self):
        """Handle text-to-speech conversion request"""
        try:
            # Parse request body
            request = self._parse_json_body()
            
            # Extract parameters
            text_input = request.get("input", "")
            voice = request.get("voice", "alloy")
            response_format = request.get("response_format", "mp3")
            speed = request.get("speed", 1.0)
            
            # Validate response format
            if response_format not in ["mp3", "opus", "aac", "flac"]:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": f"Unsupported format: {response_format}. Only mp3, opus, aac, and flac are supported.",
                        "type": "invalid_request_error",
                        "code": "invalid_format"
                    }
                }).encode("utf-8"))
                return
            
            # Map OpenAI voice to macOS voice
            macos_voice = VOICE_MAPPING.get(voice, "Alex")
            
            # Create temporary files for the audio output
            temp_dir = tempfile.gettempdir()
            temp_aiff_file = f"{temp_dir}/{uuid.uuid4()}.aiff"  # 'say' only outputs AIFF
            output_filename = f"{temp_dir}/{uuid.uuid4()}.{response_format}"
            
            try:
                # Set the rate parameter (speed adjustment)
                rate_param = ""
                if speed and speed != 1.0:
                    # macOS 'say' rate is words per minute, 
                    # so we'll approximate the conversion
                    # Normal rate is around 180 wpm
                    base_rate = 180
                    adjusted_rate = int(base_rate * speed)
                    rate_param = f"-r {adjusted_rate}"
                    
                # Execute the say command with specified voice and output to AIFF file
                say_command = f'say -v "{macos_voice}" {rate_param} -o "{temp_aiff_file}" "{text_input}"'
                
                # Use subprocess for better control and security
                process = subprocess.run(
                    say_command, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                if process.returncode != 0:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({
                        "error": {
                            "message": f"Text-to-speech conversion failed: {process.stderr}",
                            "type": "server_error"
                        }
                    }).encode("utf-8"))
                    return
                
                # Use ffmpeg to convert AIFF to requested format
                codec_mapping = {
                    "mp3": "libmp3lame",
                    "opus": "libopus",
                    "aac": "aac",
                    "flac": "flac"
                }
                
                codec = codec_mapping[response_format]
                
                # Set appropriate ffmpeg parameters based on format
                extra_params = []
                if response_format == "opus":
                    extra_params = ["-b:a", "64k"]  # Set bitrate for opus
                elif response_format == "aac":
                    extra_params = ["-b:a", "192k"]  # Set bitrate for aac
                
                # Build ffmpeg command
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-i", temp_aiff_file,
                    "-c:a", codec
                ]
                ffmpeg_cmd.extend(extra_params)
                ffmpeg_cmd.append(output_filename)
                
                # Execute ffmpeg conversion
                convert_process = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True
                )
                
                if convert_process.returncode != 0:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({
                        "error": {
                            "message": f"Audio format conversion failed: {convert_process.stderr}",
                            "type": "server_error"
                        }
                    }).encode("utf-8"))
                    return
                
                # Read the audio file
                with open(output_filename, "rb") as audio_file:
                    audio_content = audio_file.read()
                
                # Set the correct content type based on response_format
                content_type_mapping = {
                    "mp3": "audio/mpeg",
                    "opus": "audio/opus",
                    "aac": "audio/aac",
                    "flac": "audio/flac"
                }
                
                # Return audio data
                self._set_headers(200, content_type_mapping[response_format])
                self.wfile.write(audio_content)
                
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "error": {
                        "message": f"Error generating audio: {str(e)}",
                        "type": "server_error"
                    }
                }).encode("utf-8"))
            finally:
                # Clean up temporary files in the finally block
                if os.path.exists(temp_aiff_file):
                    os.remove(temp_aiff_file)
                if os.path.exists(output_filename):
                    os.remove(output_filename)
        
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({
                "error": {
                    "message": "Invalid JSON in request body",
                    "type": "invalid_request_error"
                }
            }).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": {
                    "message": f"Server error: {str(e)}",
                    "type": "server_error"
                }
            }).encode("utf-8"))
    
    def _handle_transcription(self):
        """Placeholder for transcription endpoint - removed implementation"""
        self._set_headers(501)  # Not Implemented
        self.wfile.write(json.dumps({
            "error": {
                "message": "Speech-to-text functionality is not implemented",
                "type": "not_implemented"
            }
        }).encode("utf-8"))


def run_server(host="0.0.0.0", port=8003):
    """Run the HTTP server"""
    server_address = (host, port)
    httpd = socketserver.ThreadingTCPServer(server_address, OpenAICompatibleTTSHandler)
    print(f"Starting OpenAI-compatible TTS server on http://{host}:{port}")
    
    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("WARNING: ffmpeg not found. Please install ffmpeg for audio format conversion.")
        print("The server will start, but audio conversion will likely fail.")
    
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
