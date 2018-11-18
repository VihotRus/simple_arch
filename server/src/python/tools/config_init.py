#!/usr/bin/env python3.7

from argparse import ArgumentParser, RawTextHelpFormatter
import configparser
import logging.config
import os

#Variables from enviroment
ENV_DIR = os.environ['SERVER_PRODROOT']
CONF_ROOT = os.environ['SERVER_CONFROOT']

#Logging initialization
logger_file = os.path.join(CONF_ROOT, "logger.conf")
logging.config.fileConfig(logger_file)
logger = logging.getLogger('task_manager')

#Config initialization
config_file = os.path.join(CONF_ROOT, "general.conf")
config = configparser.RawConfigParser()
config.read(config_file)
