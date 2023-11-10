#!/usr/bin/env python3
# Simple Server / Parser for JSON sent through HTTP Post
import http.server
import socketserver
import json
import os
from datetime import datetime

def convert_date(input_date):
    # Parse input date string
    input_datetime = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S.%f")
    # Format the date as "YYYYMMDD_HHMMSS"
    output_date = input_datetime.strftime("%Y%m%d_%H%M%S")
    return output_date

def extract_event_clips(json_data):
    event_clips_list = []

    # Check if the required keys exist in the JSON data
    if "events" in json_data:
        events = json_data["events"]

        for event in events:
            if "eventClips" in event:
                event_clips = event["eventClips"]

                for clip in event_clips:
                    if all(key in clip for key in ("id", "tCin", "tCout")):
                        clip_info = f"{clip['id']}.ts {convert_date(clip['tCin'])} {convert_date(clip['tCout'])}"
                        event_clips_list.append(clip_info)

    for clip in event_clips_list:
        print (clip)
        os.system ("./cut_clip.sh "+clip+" &")


class JSONHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            if isinstance(json_data, dict):
                current_datetime = datetime.now().strftime('%Y%m%d-%H%M%S')
                extract_event_clips(json_data)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'JSON command processed')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid JSON structure')
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Invalid JSON format')

if __name__ == '__main__':
    PORT = 9999
    with socketserver.TCPServer(("", PORT), JSONHandler) as httpd:
        print(f"Listening to port {PORT}")
        httpd.serve_forever()

