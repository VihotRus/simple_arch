#!/usr/bin/env python3.7

import os
import subprocess

from constants import DUMP_DIR
from tools.config_init import logger


class ExecutionError(Exception):
    pass


class Executor:
    """Task executor"""

    @staticmethod
    def unique_words(file_path):
        logger.info(f'Count unique words in file {file_path}')
        words = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line_words = line.split()
                    words.extend(line_words)
            uniq_words = len(set(words))
        except Exception as error:
            raise ExecutionError(error)
        result = f'Unique words: {uniq_words}'
        return result

    @staticmethod
    def create_file(file_path):
        logger.info(f'Creating file {file_path}')
        if os.path.exists(file_path):
            logger.info('File already exists')
        else:
            try:
                open(file_path, 'w+')
            except Exception as error:
                logger.warning(f'Error when creating file {file_path}')
                raise ExecutionError(error)
            logger.info(f'Created file {file_path}')
            result = 'File created'
        return result

    @staticmethod
    def delete_file(file_path):
        try:
            os.remove(file_path)
        except Exception as error:
            logger.warning(f"Error when deleting file: {file_path}")
            raise ExecutionError(error)
        logger.info(f'File {file_path} deleted')
        result = 'File deleted'
        return result

    @staticmethod
    def execute_command(cmd):
        try:
            cmd_result = subprocess.run(cmd.split(), encoding='utf-8',
                                        stdout=subprocess.PIPE)
            logger.debug(cmd_result)
            dump_file = os.path.join(DUMP_DIR, 'command_result')
            assert cmd_result.returncode == 0, \
                f'{cmd_result.stderr}'
            with open(dump_file, 'w') as f:
                output = '\n'.join((cmd, str(cmd_result.stdout)))
                f.write(output)
        except Exception as error:
            logger.warning(f'Error <{error}> when executing command: {cmd}')
            raise ExecutionError(error)
        logger.info(f'{cmd} result saved to {dump_file}')
        result = 'Cmd result saved'
        return result

    def execute(self, task_type, *args, **kwargs):
        execution = {'count': self.unique_words,
                     'create': self.create_file,
                     'delete': self.delete_file,
                     'execute': self.execute_command}
        return execution.get(task_type)(*args, **kwargs)
