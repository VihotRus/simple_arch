#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import json
import os
import random
import time

from argparse import ArgumentParser, RawTextHelpFormatter
from constants import *
from executor import Executor, ExecutionError
from http import client
from tools.config_init import logger, config


def args_parser():
    # Parsing command line arguments to run API.
    parser = ArgumentParser(description='client options',
                            formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='Client has two purposes:')
    start_parser = subparsers.add_parser('start', help='Start jobs execution')
    start_parser.add_argument(dest='job_executor',
                              choices=['job_executor'],
                              action='store',
                              help='Use `client.py job_executor` to start executing jobs')
    create_task = subparsers.add_parser('create', help='Create new task')
    subsubparsers = create_task.add_subparsers(help='Create random tasks or set type and task argument')
    task = subsubparsers.add_parser('task', help='Create task')
    task.add_argument('-j', '--job_type',
                      choices=['count', 'create', 'delete', 'execute'],
                      required=True,
                      action='store',
                      help="Job type. Select from "
                           "('count', 'create', 'delete', 'execute')\n"
                           "count - count unique words in file\n"
                           "create - create file\n"
                           "delete - delete file\n"
                           "execute - execute shell command")
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

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__tcp = self.__host + ':' + self.__port

    def __enter__(self):
        """Open connection"""
        try:
            self.conn = client.HTTPConnection(self.__tcp)
        except Exception as error:
            logger.error(f"Cannot connect to the server: {error}")
            raise
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection"""
        self.conn.close()
        if exc_val:
            raise


class TaskManager:

    def __init__(self, args):
        self.args = args
        self._executor = Executor(logger)


    def with_connection(func):
        """Connection decorator"""

        def execute_func(self, *args, **kwargs):
            with Connection(HOST, PORT) as conn:
                func(self, conn, *args, **kwargs)

        return execute_func

    @staticmethod
    def get_response(conn, expected_status=200):
        rsp = conn.getresponse()
        print(rsp.status, rsp.reason)
        if rsp.status == expected_status:
            logger.info(rsp.reason)
        else:
            logger.error(rsp.reason)

    def generate_random(self, task_amount):
        job_set = ('count', 'create', 'delete', 'execute')
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
                                    for _ in range(RAND_LEN))
                file_path = os.path.join(DUMP_DIR, file_name)
                self.send_task(job, file_path)
        logger.info(f'Created {task_amount} tasks')

    @with_connection
    def send_task(self, conn, job_type, job_arg):
        # Create a connection
        cmd = 'task'
        data = {'job_type' : job_type, 'job_arg' : job_arg}
        data = json.dumps(data)
        # Request command to server
        conn.request('POST', cmd, body=data)
        logger.debug(f'POST: {data}')
        self.get_response(conn, 201)

    def get_job(self, conn):
        conn.request('GET', 'get_job')
        rsp = conn.getresponse()
        print(rsp.status, rsp.reason)
        data_received = rsp.read()
        try:
            job_info = json.loads(data_received)
        except json.decoder.JSONDecodeError:
            logger.error("Error: Can't receive a job")
            job_info = None
        return job_info

    def update_job(self, conn, job_info, result):
        job_info['result'] = result
        conn.request('PUT', 'job_result', body=json.dumps(job_info))
        self.get_response(conn)

    @with_connection
    def check_job(self, conn):
        """Check if there are any jobs for client"""
        try:
            while True:
                job_info = self.get_job(conn)
                if not job_info:
                    logger.info('No avalaible job')
                    time.sleep(TIMEOUT)
                    continue
                logger.info(f'Received job: {job_info}')
                result = self.execute_job(conn, job_info)
                self.update_job(conn, job_info, result)

        except KeyboardInterrupt:
            print('\nStop checking jobs')

    def execute_job(self, conn, job_info):
        job_type = job_info.get('job_type')
        job_arg = job_info.get('job_arg')
        logger.info(f'Executing task: {job_type} {job_arg}')
        try:
            result = self._executor.execute(job_type, job_arg)
        except ExecutionError as error:
            logger.warning(f'Error in job execution: {error}')
            result = str(error)
        return result


if __name__ == "__main__":
    args = args_parser()
    task_manager = TaskManager(args)
    if args.get('job_executor'):
        logger.info('Starting checking jobs for execution')
        task_manager.check_job()
    elif args.get('task_amount'):
        logger.info('Start generate random tasks')
        task_manager.generate_random(args.get('task_amount'))
    else:
        logger.info('Creating new task')
        job_type = args.get('job_type')
        job_arg = args.get('job_arg')
        task_manager.send_task(job_type, job_arg)
