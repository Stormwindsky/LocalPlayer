#!/usr/bin/env python3
"""
Local Video Player with Absolute Path Support
- Videos stored in /home/(username)/Bureau/LocalPlayer/
- Uses absolute file paths for video sources
- Press '0' to import videos
- Works completely offline
"""

import os
import sys
import json
import shutil
import threading
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from tkinter import Tk, filedialog, messagebox

# Configuration
PORT = 8000
DATA_FILE = "videos.json"
HTML_FILE = "LocalPlayer.html"
SUPPORTED_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm', '.ogv')

def get_video_directory():
    """Get the absolute path to the video directory"""
    username = os.getenv('USER')
    return f"/home/{username}/Bureau/LocalPlayer"

def create_html_file():
    """Create the HTML player file if it doesn't exist"""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalVideoPlayer</title>
    <style>
        /* All previous CSS styles */
        /* ... */
    </style>
</head>
<body>
    <!-- All previous HTML structure -->
    <!-- ... -->
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Previous JavaScript code with modifications:
            
            // Modified playVideo function to use absolute paths
            function playVideo(video) {{
                const videoPlayer = document.getElementById('video-player');
                videoPlayer.src = video.absolutePath;
                // Rest of the function remains the same
                // ...
            }}
            
            // Modified refresh function to check file existence
            function refreshLibrary() {{
                // Use fetch API to check file existence
                // ...
            }}
            
            // Rest of your JavaScript code
            // ...
        }});
    </script>
</body>
</html>"""
    
    with open(HTML_FILE, 'w') as f:
        f.write(html_content)

class RequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler to serve files from video directory"""
    def translate_path(self, path):
        # Redirect video requests to the video directory
        if path.startswith('/videos/'):
            video_path = path[8:]  # Remove '/videos/' prefix
            return os.path.join(get_video_directory(), video_path)
        return super().translate_path(path)

def start_server():
    """Start the HTTP server"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('', PORT), RequestHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()

def import_videos():
    """Import videos from selected directory"""
    root = Tk()
    root.withdraw()
    source_dir = filedialog.askdirectory(title="Select folder with videos")
    
    if not source_dir:
        return
        
    video_dir = get_video_directory()
    os.makedirs(video_dir, exist_ok=True)
    
    videos = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            videos = json.load(f)
    
    imported = 0
    for root_dir, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                src = os.path.join(root_dir, file)
                dest = os.path.join(video_dir, file)
                
                # Handle filename conflicts
                counter = 1
                base, ext = os.path.splitext(file)
                while os.path.exists(dest):
                    new_name = f"{base}_{counter}{ext}"
                    dest = os.path.join(video_dir, new_name)
                    counter += 1
                
                # Copy file
                shutil.copy2(src, dest)
                imported += 1
                
                # Add to video list
                videos.append({
                    "name": os.path.splitext(os.path.basename(dest))[0],
                    "fileName": os.path.basename(dest),
                    "absolutePath": f"/videos/{os.path.basename(dest)}",
                    "size": os.path.getsize(dest),
                    "type": f"video/{ext[1:]}",
                    "addedDate": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "isFavorite": False
                })
    
    # Save metadata
    with open(DATA_FILE, 'w') as f:
        json.dump(videos, f, indent=2)
    
    messagebox.showinfo("Import Complete", f"Imported {imported} videos")

def main():
    """Main application function"""
    print("Starting Local Video Player...")
    print(f"Video directory: {get_video_directory()}")
    
    # Create necessary files
    if not os.path.exists(HTML_FILE):
        create_html_file()
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}/{HTML_FILE}')
    
    # Command loop
    while True:
        cmd = input("\nCommands:\n0 - Import videos\nq - Quit\n> ").strip().lower()
        if cmd == '0':
            import_videos()
        elif cmd == 'q':
            break

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        print("This application is designed for Linux systems.")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")