#!/usr/bin/env python3.7

"""Server module"""

import json

from constants import HOST, PORT
from http.server import BaseHTTPRequestHandler, HTTPServer
from mysql_client import MySqlClient, MySqlException
from tools.config_init import logger, config


class TaskHandler(BaseHTTPRequestHandler):

    """Class handler of client requests"""
    def __init__(self, *args, **kwargs):
        """Initialaze MySql client."""
        self._mysql_client = MySqlClient(config, logger)
        super().__init__(*args, **kwargs)

    def send_response_with_headers(self, *args, **kwargs):
        self.send_response(*args, **kwargs)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        """Handle GET command."""
        # Get job for client.
        if self.path == 'get_job':
            try:
                new_job = self._mysql_client.get_job()
                if new_job:
                    self.send_response_with_headers(200, 'Get job')
                else:
                    self.send_response_with_headers(200, 'No Available jobs')
                self.wfile.write(json.dumps(new_job).encode())
            except MySqlException as error:
                logger.error(f'MySqlError: {error}')
                self.send_error(404, "MySqlError: can't get job")
                self.wfile.write(json.dumps({}).encode())
        else:
            self.send_error(404, 'Not found')

    def do_POST(self):
        """Handle POST command."""
        # Create new task.
        if self.path == 'task':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            try:
                job_info = json.loads(post_body)
                host = self.client_address[0]
                job_info['client_host'] = host
                self._mysql_client.insert_task(job_info)
                self.send_response_with_headers(201, 'POST task')
                # Send file content to client.
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

    def do_PUT(self):
        """Handle PUT command."""
        # Update task.
        if self.path == 'job_result':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            job_info = json.loads(post_body)
            job_info['status'] = 'finished'
            try:
                self._mysql_client.update_job(job_info)
                self.send_response_with_headers(200, 'Task updated')
            except MySqlException as error:
                logger.error(f'MySqlError: {error}')
                self.send_error(404, 'Failed to update task')
        else:
            self.send_error(404, 'Not found')

    def handle_http(self, status_code, path):
        paths = {'get_job' : {'status' : 200},
                'task' : {'status' : 201},
                'update' : {'status' : 200}}
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            content = json.loads(path)
        except Exception:
            self.logger.error(Exception)

    def respond(self, status):
        response = self.handle_http(status, self.path)
        self.wfile.write(response)


def run():
    with HTTPServer((HOST, PORT), TaskHandler) as httpd:
        print("serving at port", PORT)
        logger.info('Started server')
        httpd.serve_forever()


if __name__ == '__main__':
    run()
