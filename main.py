from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import json
import threading
from datetime import datetime

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        print(f"Handling GET request for {pr_url.path}")
        try:
            if pr_url.path == '/':
                self.send_file('index.html')
            elif pr_url.path == '/message.html':
                self.send_file('message.html')
            elif pr_url.path.endswith('.css'):
                self.send_file(pr_url.path[1:], 'text/css')
            elif pr_url.path.endswith('.png'):
                self.send_file(pr_url.path[1:], 'image/png')
            else:
                self.send_file('error.html', 404)
        except Exception as e:
            print(f"Error handling GET request: {e}")

    def do_POST(self):
        print(f"Handling POST request for {self.path}")
        try:
            if self.path == '/message':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = urllib.parse.parse_qs(post_data.decode())
                send_to_socket(data)
                self.send_file('message.html')
            else:
                self.send_file('error.html', 404)
        except Exception as e:
            print(f"Error handling POST request: {e}")

    def send_file(self, filename, content_type='text/html', status=200):
        print(f"Sending file {filename}")
        try:
            self.send_response(status)
            self.send_header('Content-type', content_type)
            self.end_headers()
            with open(filename, 'rb') as fd:
                self.wfile.write(fd.read())
        except Exception as e:
            print(f"Error sending file {filename}: {e}")

def send_to_socket(data):
    print(f"Sending data to socket: {data}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(data).encode(), ('localhost', 5000))
    except Exception as e:
        print(f"Error sending data to socket: {e}")

def run_socket_server():
    print("Running socket server")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 5000))
        while True:
            data, addr = sock.recvfrom(1024)
            data = json.loads(data.decode())
            with open('storage/data.json', 'a') as f:
                f.write(json.dumps({str(datetime.now()): data}) + '\n')
    except Exception as e:
        print(f"Error in socket server: {e}")

def run(server_class=HTTPServer, handler_class=HttpHandler):
    print("Running HTTP server")
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        print("Server closed")
        http.server_close()

if __name__ == '__main__':
    threading.Thread(target=run_socket_server).start()
    run()
