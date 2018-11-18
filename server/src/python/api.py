#!/usr/bin/env python3.7

import json
import os
import socketserver

from http.server import BaseHTTPRequestHandler, HTTPServer

from tools.config_init import logger, config


HOST = config.get('server', 'host')
PORT = eval(config.get('server', 'port'))

#Create custom HTTPRequestHandler class
class TaskHandle(BaseHTTPRequestHandler):

    #handle GET command
    def do_GET(self):
        self.send_response(200)

        #send header first
        self.send_header('Content-type','text-html')
        self.end_headers()

        #send file content to client
        self.wfile.write('Task manager server is running'.encode())
        return

    def do_POST(self):
        try:
            if self.path == 'task':
                self.send_response(200)

                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                loaded_data = json.loads(post_body)

                #send header first
                self.send_header('Content-type','text-html')
                self.end_headers()

                #send file content to client
                self.wfile.write(post_body)
                return

        except:
            self.do_send_error(404, 'file not found')

def run():
    with socketserver.TCPServer((HOST, PORT), TaskHandle) as httpd:
        try:
            print("serving at port", PORT)
            logger.info('Started server')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('^C received, shutting down the web server')
            httpd.socket.close()

if __name__ == '__main__':
    run()
