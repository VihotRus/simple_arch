#!/usr/bin/env python3.7

from http.server import BaseHTTPRequestHandler, HTTPServer

from tools.config_init import logger, config

import socketserver
import os

HOST = config.get('server', 'host')
PORT = eval(config.get('server', 'port'))

#Create custom HTTPRequestHandler class
class TaskHandle(BaseHTTPRequestHandler):

    #handle GET command
    def do_GET(self):
        rootdir = '/tmp' #file location
        try:
            if self.path == 'task':
                #send code 200 response
                # read = self.raw_requestline()
                self.send_response(200)

                #send header first
                self.send_header('Content-type','text-html')
                self.end_headers()

                #send file content to client
                self.wfile.write('HELLO'.encode())
                return

        except IOError:
            self.send_error(404, 'file not found')

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
