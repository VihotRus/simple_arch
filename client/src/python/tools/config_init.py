#!/usr/bin/env python3.7

import configparser
import logging.config
import os

#Variables from enviroment
ENV_DIR = 'C:\\Users\\Ruslan\\PycharmProjects\\task_manager\simple_arch\\client'
CONF_ROOT = f'{ENV_DIR}/etc'

#Logging initialization
logger_file = os.path.join(CONF_ROOT, "logger.conf")
logging.config.fileConfig(logger_file)
logger = logging.getLogger('task_manager')

#Config initialization
config_file = os.path.join(CONF_ROOT, "client.conf")
config = configparser.RawConfigParser()
config.read(config_file)
