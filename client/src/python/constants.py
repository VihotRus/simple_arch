#!/usr/bin/env python3.7

from tools.config_init import config

# Get http server tcp.
HOST = config.get('server', 'host')
PORT = config.get('server', 'port')
# Dump directory.
DUMP_DIR = config.get('shared_dir', 'dump_dir')
# Lenth of generated random file names.
RAND_LEN = eval(config.get('shared_dir', 'random_file_lenth'))
# Wait time for checking jobs
TIMEOUT = eval(config.get('job_executor', 'timeout'))
