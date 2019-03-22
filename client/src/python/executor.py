#!/usr/bin/env python3.7

import os
import subprocess


class ExecutionError(Exception):
    """Base Executor Exception Error class."""
    pass


class Executor:

    """Jobs execution class."""

    def __init__(self, logger):
        """Initialize logger.

        :Parameters:
            - `logger`: logging.logger instance.
        """
        self.logger = logger

    def __unique_words(self, file_path):
        """Count unique words in file.

        :Parameters:
            - `file_path`: a string with path to file.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Return:
            Int amount of unique words in file.
        """
        self.logger.info(f'Count unique words in file {file_path}')
        unique_words = set()
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line_words = set(line.split())
                    unique_words.update(line_words)
        except Exception as error:
            self.logger.warning(f'Error occurred {error} when '
                                f'counting unique words in {file_path}')
            raise ExecutionError(error)
        result = f'Unique words: {len(unique_words)}'
        self.logger.info(result)
        return result

    def __create_file(self, file_path):
        """Create file if it not exist.

        :Parameters:
            - `file_path`: a string with path to file.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Returns:
            1) a string f'File {file_path} created' if no errors occurred.
            2) a string with error.
        """
        self.logger.info(f'Creating file {file_path}')
        try:
            fd = os.open(file_path, os.O_CREAT|os.O_EXCL)
            os.close(fd)
        except FileExistsError:
            self.logger.warning(f'File {file_path} already exists')
            raise ExecutionError(f'File {file_path} already exists')
        except Exception as error:
            self.logger.warning(f'Error {error} when creating file {file_path}')
            raise ExecutionError(error)
        result = f'File {file_path} created'
        self.logger.info(result)
        return result

    def __create_dir(self, dir_path):
        """Create directory if it not exist.

        :Parameters:
            - `dir_path`: a string with path to directory.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Returns:
            1) a string f'Directory {dir_path} created' if no errors occurred.
            2) a string with error.
        """
        self.logger.info(f'Creating dir {dir_path}')
        try:
            os.mkdir(dir_path)
        except Exception as error:
            self.logger.warning(f'Error {error} when creating file {dir_path}')
            raise ExecutionError(error)
        result = f'File {dir_path} created'
        self.logger.info(result)
        return result

    def __delete_file(self, file_path):
        """Delete file.

        :Parameters:
            - `file_path`: a string with path to file.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Returns:
            1) a string f'File {file_path} deleted' if no errors occurred.
            2) a string with error.
        """
        try:
            os.remove(file_path)
        except Exception as error:
            self.logger.warning(f"Error {error} when deleting file: {file_path}")
            raise ExecutionError(error)
        result = f'File {file_path} deleted'
        self.logger.info(result)
        return result

    def __delete_dir(self, dir_path):
        """Delete directory.

        :Parameters:
            - `dir_path`: a string with path to directory.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Returns:
            1) a string f'Directory {file_path} deleted' if no errors occurred.
            2) a string with error.
        """
        try:
            os.rmdir(dir_path)
        except Exception as error:
            self.logger.warning(f"Error {error} when deleting dir: {dir_path}")
            raise ExecutionError(error)
        result = f'Directory {dir_path} deleted'
        self.logger.info(result)
        return result

    def __execute_command(self, cmd, dump_dir, job_id):
        """Execute shell command.

        :Parameters:
            - `cmd`: a string with command.
            - `dump_dir`: a string with dump directory path.
            - `job_id`: id of current job.

        :Exceptions:
            - `ExecutionError`: is raised if error occurred.

        :Returns:
            1) a string f'Cmd result saved to {dump_file}' if no errors occurred.
            2) a string with error.
        """
        try:
            cmd_result = subprocess.run(cmd.split(), encoding='utf-8',
                                        stdout=subprocess.PIPE)
            assert cmd_result.returncode == 0, f'{cmd_result.stderr}'
            file_name = 'command_result_' + str(job_id)
            dump_file = os.path.join(dump_dir, file_name)
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
        jobs = {'count': self.__unique_words,
                'create_f': self.__create_file,
                'create_d': self.__create_dir,
                'delete_f': self.__delete_file,
                'delete_d': self.__delete_dir,
                'execute': self.__execute_command}
        return jobs[job_type](*args, **kwargs)
