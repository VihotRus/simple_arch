#!/usr/bin/env python3.7

import json

from constants import HOST, PORT
from http.server import BaseHTTPRequestHandler, HTTPServer
from mysql_client import MySqlClient, MySqlException
from tools.config_init import logger, config


# Create custom HTTPRequestHandler class.
class TaskHandle(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.mysql_client = MySqlClient()
        super().__init__(*args, **kwargs)

    def send_response_with_headers(self, *args, **kwargs):
        self.send_response(*args, **kwargs)
        self.end_headers()

    # Handle GET command.
    def do_GET(self):
        """Get job for client"""
        if self.path == 'get_job':
            try:
                new_job = self.mysql_client.get_job()
                current_job = None
                if new_job:
                    current_job = new_job
                    current_job['status'] = 'open'
                    self.mysql_client.update_task(current_job)
                    self.send_response_with_headers(200, 'Get job')
                else:
                    self.send_response_with_headers(200, 'No Available jobs')
                self.wfile.write(json.dumps(current_job).encode())
            except MySqlException as error:
                logger.warning(f'MySqlError: {error}')
                self.send_error(404, 'Cannot get job')
            return
        else:
            self.send_error(404, 'Not found')

    # Handle POST command.
    def do_POST(self):
        """Create new task"""
        if self.path == 'task':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            try:
                payload = json.loads(post_body)
                host = self.client_address[0]
                payload['client_host'] = host
                self.mysql_client.insert_task(payload)
                self.send_response_with_headers(201, 'POST task')
                # send file content to client
                self.wfile.write(post_body)
            except MySqlException as error:
                logger.error(f"MySqlError: {error}")
                self.send_error(404, 'Failed to POST task')
            except Exception as error:
                logger.error(f"Error occured: {error}")
                self.send_error(400, 'Bad request')
        else:
            self.send_error(404, 'Not found')
        return

    # Handle PUT command.
    def do_PUT(self):
        """Update task"""
        if self.path == 'update':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            try:
                payload = json.loads(post_body)
                self.mysql_client.update_task(payload)
                self.send_response_with_headers(200, 'Task updated')
            except MySqlException as error:
                logger.error(f'MySqlError: {error}')
                self.send_error(404, 'Failed to update task')
            except Exception as error:
                logger.error(f'Error occured: {error}')
                self.send_error(400, 'Bad request')
            return
        else:
            self.send_error(404, 'Not found')


def run():
    with HTTPServer((HOST, PORT), TaskHandle) as httpd:
        print("serving at port", PORT)
        logger.info('Started server')
        httpd.serve_forever()


if __name__ == '__main__':
    run()
