#!/usr/bin/env python3.7

import json

from http.server import BaseHTTPRequestHandler, HTTPServer

from tools.config_init import logger, config
from mysql_client import MySqlClient


HOST = config.get('server', 'host')
PORT = eval(config.get('server', 'port'))

#Create custom HTTPRequestHandler class
class TaskHandle(BaseHTTPRequestHandler):


    def __init__(self, *args, **kwargs):
        self.mysql_client = MySqlClient()
        super().__init__(*args, **kwargs)


    def send_response(self, *args, **kwargs):
        super().send_response(*args, **kwargs)
        #send header
        # self.send_header('Content-type','text-html')
        self.end_headers()


    #handle GET command
    def do_GET(self):
        try:
            if self.path == 'get_job':

                self.send_response(200)

                open_job = self.mysql_client.get_job()
                print(open_job)
                response = open_job

                response = json.dumps(response).encode()
                self.wfile.write(response)
                return
            else:
                raise

        except Exception as e:
            print(e)
            self.send_error(404, 'file not found')


    #handle POST command
    def do_POST(self):

        if self.path == 'task':
            self.send_response(201, 'POST task')

            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            payload = json.loads(post_body)
            host = self.client_address[0]

            self.mysql_client.insert_task(payload, host)

            #send file content to client
            self.wfile.write(post_body)
            return

    def do_PUT(self):
        """Change task status"""
        if self.path == 'update':

            self.send_response(200, 'Update task')

            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            payload = json.loads(post_body)

            result = self.mysql_client.update_task(payload)
            if result:
                self.send_response(200, 'Task updated')
            else:
                self.send_response(404, 'Error occured')


def run():
    with HTTPServer((HOST, PORT), TaskHandle) as httpd:
        print("serving at port", PORT)
        logger.info('Started server')
        httpd.serve_forever()

if __name__ == '__main__':
    run()
