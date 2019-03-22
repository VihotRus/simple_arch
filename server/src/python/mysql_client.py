#!/usr/bin/env python3.7

"""This module works with database."""

import pymysql
import time


class MySqlException(Exception):
    """Base MySqlClient Exception Error class."""
    pass


class MySqlClient:

    """Class that works with MySql database."""

    def __init__(self, config, logger):
        """Initialize db params, config and logger.

        :Parameters:
            - `config`: configparser instance.
            - `logger': logging.logger instance.
        """
        self.config = config
        self.logger = logger
        self.__host = self.config.get('db', 'host')
        self.__name = self.config.get('db', 'name')
        self.__user = self.config.get('db', 'user')
        self.__passwd = self.config.get('db', 'passwd')
        # Retries connect to db.
        self.__retries = 5
        # Delay connect after retry
        self.__delay = 3

    def with_connection(func):
        """Database connection decorator."""
        def wrapper(self, *args, **kwargs):
            self.logger.info('Connecting to database')
            retries = self.__retries
            result = 'no connection to db'
            while retries >1:
                try:
                    cnx = pymysql.connect(host=self.__host,
                                        db=self.__name,
                                        user=self.__user,
                                        passwd=self.__passwd)
                    self.logger.info('Connected')
                    self.logger.debug("Calling func %s " % (func.__name__, ))
                    try:
                        cursor = cnx.cursor()
                        result = func(self, cursor, *args, **kwargs)
                        self.logger.info("Commiting changes")
                        cnx.commit()
                    except Exception as error:
                        self.logger.error(error)
                        self.logger.info("Rollbacking changes")
                        cnx.rollback()
                        raise MySqlException(error)
                    finally:
                        self.logger.debug("Closing connection %s" % (cnx, ))
                        cnx.close()
                        break

                except Exception as error:
                    self.logger.error(f'Error occured when connecting '
                                      f'to database:{error}')
                    time.sleep(self.__delay)
                    retries -= 1
            if result == 'no connection to db':
                msg = f'Connection to database failed after ' \
                      f'{self.__retries} retries'
                self.logger.error(msg)
                raise MySqlException(msg)
            return result
        return wrapper

    def insert_dict(self, cursor, table, data):
        """Insert items from dictionary.

        :Parameters:
            - `cursor`: connection cursor object.
            - `table`: a string with mysql table name.
            - `data`: dictionary with data to insert.
        """
        data_set = [(column, f'"{value}"') for column, value in data.items()]
        columns, values = list(zip(*data_set))
        columns_expression = ','.join(columns)
        values_expression = ','.join(values)
        sql_query = (f"INSERT INTO {table} ({columns_expression}) "
                     f"VALUES({values_expression})")
        self.logger.debug(f'Executing query: {sql_query}')
        cursor.execute(sql_query)

    @with_connection
    def create_job(self, cursor, job_info):
        """Create new job.

        :Parameters:
            - `cursor`: connection cursor object. It comes from decorator.
            - `job_info`: dictionary with job type and job argument. for e.g.:
                           {'job_type': 'create', 'job_arg': '/tmp/text.txt'}
        """
        now = int(time.time())
        job_info['ctime'] = now
        job_info['mtime'] = now
        self.insert_dict(cursor, 'job_queue', job_info)

    @with_connection
    def update_job(self, cursor, job_info, result_info=None):
        """Update job.

        :Parameters:
            - `cursor`: connection cursor object. It comes from decorator.
            - `job_info: dictionary with job_info to update. for e.g.:
                         {'id': 1, 'status': 'finished'}
            - `result_info`: dictionary with job result info.
                            by default None. for e.g.:
                            {'job_id': 1, 'result': 'PASS',
                             'result_info: 'File test.txt created',
                             'run_time': 1}
        """
        not_update = ('id',)
        job_id = job_info['id']
        job_info['mtime'] = int(time.time())
        data_set = [f'{column} = "{value}"' for column, value in job_info.items()
                    if column not in not_update]
        set_expression = ','.join(data_set)
        sql_query = (f"UPDATE job_queue SET {set_expression} WHERE id = '{job_id}'")
        self.logger.info(f'Update job with id {job_id} status to {job_info}')
        cursor.execute(sql_query)
        if result_info:
            result_info['job_id'] = job_info['id']
            result_info['run_time'] = int(time.time()) - job_info['stime']
            self.insert_dict(cursor, 'job_result', result_info)

    @with_connection
    def get_job(self, cursor):
        """Get new job to process it.

        :Parameters:
            - `cursor`: connection cursor object. It comes from decorator.

        :Returns:
            1) Empty dict if no jobs in queue with status 'new'.
            2) Dictionary with job information that contains all values
               from `required_columns` variable. for e.g.:
               {'id': 1, 'client_host: 'localhost',
                'job_type': 'create', 'job_arg': 'test.txt'}
        """
        status = 'new'
        required_columns = ('id', 'client_host', 'job_type', 'job_arg')
        select_expression = ','.join(required_columns)
        sql_query = (f"SELECT {select_expression} FROM job_queue "
                     f"WHERE status = '{status}' ORDER BY ctime LIMIT 1")
        cursor.execute(sql_query)
        result = cursor.fetchall()
        new_job = {}
        if result:
            new_job = dict(zip(required_columns, result[0]))
            new_job['status'] = 'in_progress'
            new_job['stime'] = int(time.time())
            self.update_job(new_job)
        self.logger.info(f'Get new task: {new_job}')
        return new_job
