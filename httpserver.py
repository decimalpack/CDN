import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import socket
import requests


def main():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-p":
            PORT = int(sys.argv[i+1])
        elif sys.argv[i] == "-o":
            ORIGIN = sys.argv[i+1]
    ORIGIN = "http://cs5700cdnorigin.ccs.neu.edu"
    
    create(PORT)



def create(port:int) -> HTTPServer:
    webServer = HTTPServer((getLocalIp, port), getHandler)
    webServer.serve_forever()


class getHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            re = requests.get("http://cs5700cdnorigin.ccs.neu.edu:8080")
            self.wfile.write(bytes(re.content))
        except Exception:
            self.wfile.write(bytes(b"request to origin failed"))

def getLocalIp():
    # Create epemeral socket to get IP address
    # NOTE: socket.gethostbyname(socket.gethostname()) returns localhost on
    # Ubuntu 22.04
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


if __name__ == "__main__":
    main()