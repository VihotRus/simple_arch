#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Client module."""

import configparser
import json
import logging.config
import os
import random
import time

from argparse import ArgumentParser, RawTextHelpFormatter
from executor import Executor, ExecutionError
from http import client

ENV_DIR = '/home/ruslan/git/task_manager/client'
CONF_ROOT = f'{ENV_DIR}/etc'

def args_parser():
    # Parsing command line arguments to run API.
    parser = ArgumentParser(description='client options',
                            formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='Client has two purposes:')
    start_parser = subparsers.add_parser('start', help='Start jobs execution')
    start_parser.add_argument(dest='job_executor',
                              choices=['job_executor'],
                              action='store',
                              help='Use `client.py job_executor` to '
                                   'start executing jobs')
    create_task = subparsers.add_parser('create', help='Create new task')
    subsubparsers = create_task.add_subparsers(help='Create random tasks or set'
                                                    ' type and task argument')
    task = subsubparsers.add_parser('task', help='Create task')
    task.add_argument('-j', '--job_type',
                      choices=['count', 'create_f', 'create_d',
                               'delete_f', 'delete_d', 'execute'],
                      required=True,
                      action='store',
                      help="Job type.\nSelect from "
                           "('count', 'create', 'delete', 'execute')\n"
                           "count - count unique words in file;\n"
                           "create_f - create file;\n"
                           "create_d - create directory;\n"
                           "delete_f - delete file;\n"
                           "delete_d - delete directory;\n"
                           "execute - execute shell command.")
    task.add_argument('-a', '--job_arg',
                      required=True,
                      metavar='task parameter',
                      action='store',
                      help='Task paramater:\n'
                           'For (`count`, `create`, `delete`) '
                           'task types - file path\n'
                           'For `execute` task_type - command')
    random_task = subsubparsers.add_parser('random', help='Create random tasks')
    random_task.add_argument(dest='task_amount',
                             type=int,
                             action='store',
                             help='Amount of random tasks that will be generated')
    return parser.parse_args().__dict__


class Connection:

    """Connection context manager."""

    def __init__(self, host, port):
        """Initialize tcp server"""
        self.__host = host
        self.__port = port
        self.__tcp = self.__host + ':' + self.__port

    def __enter__(self):
        """Open connection."""
        try:
            self.conn = client.HTTPConnection(self.__tcp)
        except Exception as error:
            self.logger.error(f"Cannot connect to the server: {error}")
            raise
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        self.conn.close()
        if exc_val:
            raise


class TaskManager:

    """Client main class that making requests
       and getting responses."""

    def __init__(self, arguments):
        """Initialize client.

        :Parameters:
            - `arguments`: shell arguments.
        """
        self.args = arguments
        # Logger initialization.
        logger_file = os.path.join(CONF_ROOT, "logger.conf")
        logging.config.fileConfig(logger_file)
        self.logger = logging.getLogger('task_manager')
        # Config initialization.
        config_file = os.path.join(CONF_ROOT, "client.conf")
        self.config = configparser.RawConfigParser()
        self.config.read(config_file)
        # Executor initialization.
        self._executor = Executor(self.logger)
        self.__host = self.config.get('server', 'host')
        self.__port = self.config.get('server', 'port')
        # Directory to save shell commands output.
        self.dump_dir = self.config.get('shared_dir', 'dump_dir')
        # Length of generated random file names.
        self.rand_len = eval(self.config.get('shared_dir', 'random_file_length'))
        # Wait time for checking jobs
        self.timeout = eval(self.config.get('job_executor', 'timeout'))

    def with_connection(func):
        """Connection decorator."""
        def execute_func(self, *args, **kwargs):
            with Connection(self.__host, self.__port) as conn:
                func(self, conn, *args, **kwargs)
        return execute_func

    def generate_random(self, task_amount):
        """Generate random jobs.

        :Parameters:
            - `task_amount`: and int with amount of jobs to generate.
        """
        job_set = ('count', 'create_f', 'delete_f', 'execute')
        execute_args = ('ps -aux',
                        'ls -la /home/ruslan',
                        'df -ah',
                        'sudo -l')
        name_letters = 'abc'
        for _ in range(task_amount):
            job = random.choice(job_set)
            if job == 'execute':
                exec_arg = random.choice(execute_args)
                self.send_task(job, exec_arg)
            else:
                file_name = ''.join(random.choice(name_letters)
                                    for _ in range(self.rand_len))
                file_path = os.path.join(self.dump_dir, file_name)
                self.send_task(job, file_path)
        self.logger.info(f'Created {task_amount} tasks')

    def get_response(self, conn, expected_status=200):
        """Get response.

        :Parameters:
            - `conn`: connection object to server.
            - `expected_status`: expected status of received response.
                                by default 200.
        """
        rsp = conn.getresponse()
        print(rsp.status, rsp.reason)
        if rsp.status == expected_status:
            self.logger.info(rsp.reason)
        else:
            self.logger.error(rsp.reason)

    @with_connection
    def send_task(self, conn, job_type, job_arg):
        """Send created job to server.

         :Parameters:
            - `conn`: connection object to server. It comes from decorator.
            - `job_type`: a string with type of job.
            - `job_arg`: a string with job argument(file path or shell command).
        """
        cmd = 'task'
        data = {'job_type' : job_type, 'job_arg' : job_arg}
        data = json.dumps(data)
        conn.request('POST', cmd, body=data)
        self.logger.debug(f'POST: {data}')
        self.get_response(conn, 201)

    def get_job(self, conn):
        """Get job.

        :Parameters:
            - `conn`: connection object to server.

        :Exceptions:
            - `json.decoder.JSONDecodeError`: is raised when
                                              failed to get a job.

        :Returns:
            1) dictionary with job info. for e.g.:
               {'id': 1, 'client_host': 'localhost',
                'job_type': 'command', 'job_arg': 'ls -la'}
            2) empty dictionary if no jobs to do.
            3) None if error occurred
        """
        conn.request('GET', 'get_job')
        rsp = conn.getresponse()
        print(rsp.status, rsp.reason)
        data_received = rsp.read()
        try:
            job_info = json.loads(data_received)
        except json.decoder.JSONDecodeError:
            self.logger.error("Error: Can't receive a job")
            job_info = None
        return job_info

    def update_result(self, conn, job_info, result_info):
        """Send a request with job result update.

        :Parameters:
            - `conn`: connection object to server.
            - `job_info`: a dictionary with job information.
            - `result_info`: a dictionary with job result information. for e.g.:
                             {'result_info': 'File test.txt created',
                              'result': 'PASS'}
        """
        to_update = (job_info, result_info)
        conn.request('PUT', 'job_result', body=json.dumps(to_update))
        self.get_response(conn)

    @with_connection
    def check_job(self, conn):
        """Checking for jobs to do.

        :Parameters:
            - `conn`: connection object to server.

        :Exceptions:
            - `KeyboardInterrupt`: is raised when press Ctrl+C
                                   to stop checking jobs.
        """
        try:
            while True:
                job_info = self.get_job(conn)
                if not job_info:
                    self.logger.info('No avalaible job')
                    time.sleep(self.timeout)
                    continue
                self.logger.info(f'Received job: {job_info}')
                result_info = self.execute_job(job_info)
                self.update_result(conn, job_info, result_info)

        except KeyboardInterrupt:
            print('\nStop checking jobs')

    def execute_job(self, job_info):
        """Execute job.

        :Parameters:
            - `job_info`: a dictionary with job information.

        :Exceptions:
            - `ExecutionError`: is raise if error occurred.

        :Return:
            - a dictionary with result and result_info. for e.g.:
              {'result': 'PASS", 'result_info': 'File deleted'}
        """
        job_type = job_info['job_type']
        job_arg = job_info['job_arg']
        self.logger.info(f'Executing task: {job_type} {job_arg}')
        try:
            if job_type == 'execute':
                result_info = self._executor.execute(job_type,
                                                     job_arg,
                                                     self.dump_dir,
                                                     job_info['id'])
            else:
                result_info = self._executor.execute(job_type, job_arg)
            result = 'PASS'
        except ExecutionError as error:
            result_info = str(error)
            result = 'ERROR'
        return {'result_info': result_info, 'result': result}


if __name__ == "__main__":
    args = args_parser()
    task_manager = TaskManager(args)
    if args.get('job_executor'):
        task_manager.logger.info('Starting checking jobs for execution')
        task_manager.check_job()
    elif args.get('task_amount'):
        task_manager.logger.info('Start generate random tasks')
        task_manager.generate_random(args.get('task_amount'))
    else:
        task_manager.logger.info('Creating new task')
        job_type = args.get('job_type')
        job_arg = args.get('job_arg')
        task_manager.send_task(job_type, job_arg)
