#!/usr/bin/env python3.7

from argparse import ArgumentParser, RawTextHelpFormatter
import configparser
import logging.config
import os

#Variables from enviroment
ENV_DIR = '/home/ruslan/git/task_manager/server'
CONF_ROOT = f'{ENV_DIR}/etc'

#Logging initialization
logger_file = os.path.join(CONF_ROOT, "logger.conf")
logging.config.fileConfig(logger_file)
logger = logging.getLogger('task_manager')

#Config initialization
config_file = os.path.join(CONF_ROOT, "server.conf")
config = configparser.RawConfigParser()
config.read(config_file)
