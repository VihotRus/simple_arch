#!/usr/bin/env python3.7

import json
import http.client
import time

from argparse import ArgumentParser, RawTextHelpFormatter
from tools.config_init import logger, config

#get http server ip
HOST = config.get('server', 'host')
PORT = config.get('server', 'port')

# def args_parser():
#     # Parsing command line arguments to run API
#     parser = ArgumentParser(description='client settings',
#                             formatter_class=RawTextHelpFormatter)
#     parser.add_argument('-t', '--task_type',
#                         choices = ['count', 'create', 'delete', 'execute', 'random'],
#                         metavar = 'task type',
#                         default='random',
#                         # required=True,
#                         help='Determine task to do'
#                              'by default random task')
#     parser.add_argument('-a', '--argument',
#                         metavar = 'argument',
#                         default='nothing',
#                         # required=True,
#                         help='file_path / shell_command')
#     parser.add_argument('-r', '--run',
#                         choices = ['start', 'stop'],
#                         metavar = 'run',
#                         help = 'run/stop job checker')
#     return parser.parse_args().__dict__

def args_parser():
    # Parsing command line arguments to run API
    parser = ArgumentParser(description='client options',
                            formatter_class=RawTextHelpFormatter)
    # parser.add_argument(dest='purpose',
    #                     choices=['start', 'create_task'],
    #                     metavar='start/create_task',
    #                     action='store',
    #                     help='client purpose')
    subparsers = parser.add_subparsers(help='Client has two purposes:')
    start_parser = subparsers.add_parser('start', help='Start checking jobs')
    start_parser.add_argument(dest='start',
                              action='store',
                              help='Use client.py start to begin checking jobs')
    # start_parser.add_argument(dest='purpose', action='store_const', const='start', help='start checking jobs')
    task_parser = subparsers.add_parser('create_task', help='Create a new task')


    return parser.parse_args().__dict__

class Connection:

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__tcp = self.__host + ':' + self.__port

    def __enter__(self):
        """Open connection"""

        self.conn = http.client.HTTPConnection(self.__tcp)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection"""

        self.conn.close()
        if exc_val:
            raise


class TaskManager:

    def __init__(self, args):
        self.args = args


    def with_connection(func):
        """Connection decorator"""

        def execute_func(self, *args):
            with Connection(HOST, PORT) as conn:
                func(self, conn, *args)

        return execute_func


    @with_connection
    def send_task(self, conn):
        #create a connection
        cmd = 'task'

        data = json.dumps(self.args)
        test_dataset = {'task_name' : 'create', 'task_parameter' : '/tmp'}
        data = json.dumps(test_dataset)

        #request command to server
        conn.request('POST', cmd, body=data)

        #get response from server
        rsp = conn.getresponse()

        #print server response and data
        print(rsp.status, rsp.reason)
        data_received = rsp.read()
        print(data_received)


    @with_connection
    def check_job(self, conn):
        """Check if there are any jobs for client"""
        try:
            while(True):

                conn.request('GET', 'get_job')
                rsp = conn.getresponse()

                print(rsp.status, rsp.reason)
                data_received = rsp.read()

                job = json.loads(data_received)
                logger.info(f'Received job: {job}')
                if job:
                    task_id = job.get('task_id')
                    status = 'in_progress'
                    update_task = {'task_id' : task_id, 'job_status' : status}
                    conn.request('PUT', 'update', body = json.dumps(update_task))
                    rsp = conn.getresponse()
                    assert rsp.status == 200, 'Error occured'
                    print(rsp.status, rsp.reason)
                    try:
                        print('Doing job')
                        print('1.')
                        print('2..')
                        print('3...')
                        time.sleep(20)
                        result = 'passed'
                    except:
                        result = 'errored'
                    finally:
                        status = 'finished'
                        update_task = {'task_id' : task_id, 'job_status' : status, 'job_result' : result}
                        conn.request('PUT', 'update', body = json.dumps(update_task))
                        rsp = conn.getresponse()
                        print(rsp.status, rsp.reason)
                        time.sleep(30)

                time.sleep(30)

        except KeyboardInterrupt:
            print('\nStop checking jobs')


if __name__ == "__main__":
    #args = args_parser()
    #print(args)
    # logger.info('Make a request to server')
    # logger.debug(f"Make a request to server with data:{args}")
    args = {}
    task = TaskManager(args=args)
    # # if args.get('run') == 'start':
    # #     task.check_job()
    # # else:
    # #     task.send_task()
    task.check_job()
    #task.send_task()
