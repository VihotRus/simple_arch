#!/usr/bin/env python3.7

"""Server module."""

import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from mysql_client import MySqlClient, MySqlException
from tools.config_init import logger, config

HOST = config.get('server', 'host')
PORT = eval(config.get('server', 'port'))


class TaskHandler(BaseHTTPRequestHandler):

    """Class handler of client requests."""

    def __init__(self, *args, **kwargs):
        """Initialize MySql client."""
        self._mysql_client = MySqlClient(config, logger)
        super().__init__(*args, **kwargs)

    def response(self, status, message):
        """Send response with headers.

        :Parameters:
            - `status`: http status code.
            - `message`: a string with custom message.
        """
        self.send_response(status, message)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        """Handle GET command."""
        if self.path == 'get_job':
            # Get job for client.
            try:
                new_job = self._mysql_client.get_job()
                if new_job:
                    self.response(200, 'Get job')
                else:
                    self.response(200, 'No Available jobs')
                # Send job info to client.
                self.wfile.write(json.dumps(new_job).encode())
            except MySqlException:
                self.send_error(404, "Failed to GET job")
        else:
            self.send_error(404, 'Not found')

    def do_POST(self):
        """Handle POST command."""
        if self.path == 'task':
            # Create new task.
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            try:
                job_info = json.loads(post_body)
                host = self.client_address[0]
                job_info['client_host'] = host
                self._mysql_client.create_job(job_info)
                self.response(201, 'POST task')
                # Send file content to client.
                self.wfile.write(post_body)
            except MySqlException:
                self.send_error(404, 'Failed to POST job')
            except ValueError as error:
                logger.error(f"Error when loading json {post_body}:\n{error}")
                self.send_error(400, 'Bad request')
        else:
            self.send_error(404, 'Not found')
        return

    def do_PUT(self):
        """Handle PUT command."""
        if self.path == 'job_result':
            # Update task
            content_len = int(self.headers.get('Content-Length'))
            put_body = self.rfile.read(content_len)
            job_info, result_info = json.loads(put_body)
            job_info['status'] = 'finished'
            try:
                self._mysql_client.update_job(job_info, result_info)
                self.response(200, 'Task updated')
            except MySqlException as error:
                logger.error(f'MySqlError: {error}')
                self.send_error(404, 'Failed to update task')
        else:
            self.send_error(404, 'Not found')


def run():
    with HTTPServer((HOST, PORT), TaskHandler) as httpd:
        print("serving at port", PORT)
        logger.info('Started server')
        httpd.serve_forever()


if __name__ == '__main__':
    run()
