#!/usr/bin/env python3.7

import json
import os
import socketserver

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
            if self.path == 'check_job':

                self.send_response(200)

                #send header first
                # self.send_header('Content-type','text-html')
                # self.end_headers()

                host = self.client_address[0]
                job_list = self.mysql_client.job_list(host)
                response = job_list

                response = json.dumps(response).encode()
                self.wfile.write(response)
                return
            else:
                raise

        except:
            self.send_error(404, 'file not found')


    #handle POST command
    def do_POST(self):

        if self.path == 'task':
            self.send_response(201, 'POST task')

            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            loaded_task = json.loads(post_body)

            host = self.client_address[0]
            task_type = loaded_task.get('task_type')
            self.mysql_client.insert_task(task_type, host)

            #send header first
            # self.send_header('Content-type','text-html')
            # self.end_headers()

            #send file content to client
            self.wfile.write(post_body)
            return

    def do_PUT(self):
        """Change task status"""
        if self.path == 'update':

            self.send_response(200, 'Update task')

            #send header first
            # self.send_header('Content-type','text-html')
            # self.end_headers()

            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            loaded_task = json.loads(post_body)
            task_id = loaded_task.get('task_id')
            status = loaded_task.get('status')

            result = self.mysql_client.update_task(task_id, status)
            if result:
                self.send_response(200, 'Task updated')
                #send header first
                self.send_header('Content-type','text-html')
                self.end_headers()
            else:
                self.send_response(404, 'Error occured')
                #send header first
                self.send_header('Content-type','text-html')
                self.end_headers()

def run():
    with HTTPServer((HOST, PORT), TaskHandle) as httpd:
        print("serving at port", PORT)
        logger.info('Started server')
        httpd.serve_forever()

if __name__ == '__main__':
    run()
