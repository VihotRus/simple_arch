#!/usr/bin/env python3.7

"""This module works with database"""

import pymysql
import time

from constants import DB_SECTION

class MySqlException(Exception):
    """Base MySql Exception Error class"""
    pass


class MySqlClient:

    """Client that works with MySql database"""

    def __init__(self, config, logger):
        """Intiialize db params"""
        self.config = config
        self.logger = logger
        self.__host = self.config.get(DB_SECTION, 'host')
        self.__name = self.config.get(DB_SECTION, 'name')
        self.__user = self.config.get(DB_SECTION, 'user')
        self.__passwd = self.config.get(DB_SECTION, 'passwd')
        self.__charset = self.config.get(DB_SECTION, 'charset')

    @staticmethod
    def retry():
        pass

    def with_connection(func):
        """Database connection decorator"""
        def wrapper(self, *args, **kwargs):
            self.logger.info('Connecting to database')
            result = False
            try:
                cnx = pymysql.connect(host=self.__host,
                                      db=self.__name,
                                      user=self.__user,
                                      passwd=self.__passwd,
                                      charset=self.__charset)
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

            except Exception as error:
                self.logger.error(f'Error occured when connecting to database:{error}')
                raise MySqlException(error)
            return result
        return wrapper

    @with_connection
    def insert_task(self, cursor, job_info):
        """Create new task
        :Args:
            `cursor`: blabla
            `job_info`: job_info dict
        """
        now = int(time.time())
        job_info['ctime'] = now
        job_info['mtime'] = now
        data_set = [(column, f'"{value}"') for column, value in job_info.items()]
        columns, values = list(zip(*data_set))
        columns_expression = ','.join(columns)
        values_expression = ','.join(values)
        sql_query = (f"INSERT INTO job_queue ({columns_expression}) "
                     f"VALUES({values_expression})")
        result = cursor.execute(sql_query)
        return result

    @with_connection
    def update_job(self, cursor, job_info):
        """Update task"""
        not_update = ('id',)
        job_id = job_info.get('id')
        job_info['mtime'] = int(time.time())
        data_set = [f'{column} = "{value}"' for column, value in job_info.items()
                    if column not in not_update]
        set_expression = ','.join(data_set)
        sql_query = (f"UPDATE job_queue SET {set_expression} WHERE id = '{job_id}'")
        self.logger.info(f'Update job with id {job_id} status to {job_info}')
        result = cursor.execute(sql_query)
        return result

    @with_connection
    def get_job(self, cursor):
        """Get new job to process it"""
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
