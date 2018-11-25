#!/usr/bin/env python3.7

from tools.config_init import config

# TCP configuration
HOST = config.get('server', 'host')
PORT = eval(config.get('server', 'port'))
# Db config section.
DB_SECTION = 'db'