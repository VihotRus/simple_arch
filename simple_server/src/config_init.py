#!/usr/bin/env python3.7

import ConfigParser
import logging.config
import os

#Variables from enviroment
ENV_DIR = os.environ['PROD_ROOT']
CONF_ROOT = os.environ['CONF_ROOT']

#Logging initialization
logger_file = os.path.join(CONF_ROOT, "logger.conf")
logging.config.fileConfig(logger_file)
logger = logging.getLogger('task_manager')

#Config initialization
config_file = os.path.join(CONF_ROOT, "db.conf")
config = ConfigParser.RawConfigParser()
config.read(config_file)
