#!/usr/bin/env python3.7

import os
import subprocess

from constants import DUMP_DIR


class ExecutionError(Exception):
    pass


class Executor:
    """Task executor"""

    def __init__(self, logger):
        self.logger = logger

    def __unique_words(self, file_path):
        self.logger.info(f'Count unique words in file {file_path}')
        unique_words = set()
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line_words = set(line.split())
                    unique_words.update(line_words)
        except Exception as error:
            raise ExecutionError(error)
        result = f'Unique words: {len(unique_words)}'
        return result

    def __create_file(self, file_path):
        self.logger.info(f'Creating file {file_path}')
        try:
            os.open(file_path, os.O_CREAT|os.O_EXCL)
            result = 'File created'
        except FileExistsError as error:
            self.logger.warning(f'File {file_path} already exists')
            result = f'File {file_path} already exists'
        except Exception as error:
            self.logger.warning(f'Error {error} when creating file {file_path}')
            self.logger.warning(error)
            self.logger.warning(Exception)
            raise ExecutionError(error)
        self.logger.info(f'Created file {file_path}')
        return result

    def __delete_file(self, file_path):
        try:
            os.remove(file_path)
        except Exception as error:
            self.logger.warning(f"Error {error} when deleting file: {file_path}")
            raise ExecutionError(error)
        self.logger.info(f'File {file_path} deleted')
        result = 'File deleted'
        return result

    def __execute_command(self, cmd):
        try:
            cmd_result = subprocess.run(cmd.split(), encoding='utf-8',
                                        stdout=subprocess.PIPE)
            assert cmd_result.returncode == 0, \
                f'{cmd_result.stderr}'
            dump_file = os.path.join(DUMP_DIR, 'command_result')
            with open(dump_file, 'w') as f:
                output = '\n'.join((cmd, str(cmd_result.stdout)))
                f.write(output)
        except Exception as error:
            self.logger.warning(f'Error <{error}> when executing command: {cmd}')
            raise ExecutionError(error)
        self.logger.info(f'{cmd} result saved to {dump_file}')
        result = f'Cmd result saved to {dump_file}'
        return result

    def execute(self, job_type, *args, **kwargs):
        """Executor interface"""
        jobs  = {'count': self.__unique_words,
                 'create': self.__create_file,
                 'delete': self.__delete_file,
                 'execute': self.__execute_command}
        return jobs[job_type](*args, **kwargs)
