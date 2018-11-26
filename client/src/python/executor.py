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
        unique_words = set()
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line_words = set(line.split())
                    unique_words.update(line_words)
        except Exception as error:
            raise ExecutionError(error)
        result = f'Unique words: {uniq_words}'
        return result

    @staticmethod
    def create_file(file_path):
        logger.info(f'Creating file {file_path}')
        if os.path.exists(file_path):
            logger.warning(f'File {file_path} already exists')
            raise ExecutionError(f'File {file_path} already exists')
        else:
            try:
                os.open(file_path, os.O_WRONLY)
            except Exception as error:
                logger.warning(f'Error {error} when creating file {file_path}')
                raise ExecutionError(error)
            logger.info(f'Created file {file_path}')
            result = 'File created'
        return result

    @staticmethod
    def delete_file(file_path):
        try:
            os.remove(file_path)
        except Exception as error:
            logger.warning(f"Error {error} when deleting file: {file_path}")
            raise ExecutionError(error)
        logger.info(f'File {file_path} deleted')
        result = 'File deleted'
        return result

    @staticmethod
    def execute_command(cmd):
        try:
            cmd_result = subprocess.run(cmd.split(), encoding='utf-8',
                                        stdout=subprocess.PIPE)
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
        result = f'Cmd result saved to {dump_file}'
        return result

    def execute(self, task_type, *args, **kwargs):
        execution = {'count': self.unique_words,
                     'create': self.create_file,
                     'delete': self.delete_file,
                     'execute': self.execute_command}
        try:
            result = execution.get(task_type)(*args, **kwargs)
        except TypeError as error:
            logger.error(f'Incorect task type: {task_type}i\n'
                         f'must be in {execution.keys()}')
            raise
        except Exception as error:
            logger.warning(f'Error {error} in job execution: ({task_type}, {args})')
            raise ExecutionError(error)
        return result
