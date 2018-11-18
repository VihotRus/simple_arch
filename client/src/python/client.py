#!/usr/bin/env python3.7

import http.client
import json

from argparse import ArgumentParser, RawTextHelpFormatter, SUPPRESS
from tools.config_init import logger, config

#get http server ip
HOST = config.get('server', 'host')
PORT = config.get('server', 'port')

def args_parser():
    # Parsing command line arguments to run API
    parser = ArgumentParser(description='client settings',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-t', '--task_type',
                        metavar = 'task type',
                        default='random',
                        help='Determine task to do'
                             'by default random task')
    parser.add_argument('-a', '--argument',
                        metavar = 'argument',
                        default='nothing',
                        help='file_path / shell_command')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help=SUPPRESS)
    return parser.parse_args().__dict__


class TaskCreator():

    def __init__(self, **kwargs):
        self.__server = HOST + ':' + PORT
        self.args = kwargs.get('args') if kwargs.get('args') else {}

    def process_task(self):
        #create a connection
        conn = http.client.HTTPConnection(self.__server)
        cmd = 'task'

        data = json.dumps(self.args)

        #request command to server
        conn.request('GET', cmd, body=data)

        #get response from server
        rsp = conn.getresponse()

        #print server response and data
        print(rsp.status, rsp.reason)
        data_received = rsp.read()
        print(data_received)

        conn.close()


if __name__ == "__main__":
    args = args_parser()
    logger.info("Make a request to server")
    task = TaskCreator(args=args)
    task.process_task()
