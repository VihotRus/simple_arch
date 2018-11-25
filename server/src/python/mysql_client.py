#!/usr/bin/env python3.7

""" This module works with database"""

import pymysql

from constants import DB_SECTION
from tools.config_init import config, logger


class MySqlException(Exception):
    pass


class MySqlClient:

    def __init__(self):
        self.__host = config.get(DB_SECTION, 'host')
        self.__name = config.get(DB_SECTION, 'name')
        self.__user = config.get(DB_SECTION, 'user')
        self.__passwd = config.get(DB_SECTION, 'passwd')
        self.__charset = config.get(DB_SECTION, 'charset')

    def connection(func):
        """Database connection decorator"""
        def wrapper(self, *args, **kwargs):
            logger.info('Connecting to database')
            result = False
            try:
                cnx = pymysql.connect(host=self.__host,
                                      db=self.__name,
                                      user=self.__user,
                                      passwd=self.__passwd,
                                      charset=self.__charset)
                logger.info('Connected')
                logger.debug(f'connection object = {cnx}')

                try:
                    logger.debug("Calling func %s " % (func.__name__, ))
                    cursor = cnx.cursor()
                    result = func(self, cursor, *args, **kwargs)
                    logger.info("Commiting changes")
                    cnx.commit()
                except Exception as error:
                    logger.info(f"Error occured: {error}")
                    logger.info("Rollbacking changes")
                    cnx.rollback()
                    raise MySqlException(error)
                finally:
                    logger.debug("Closing connection %s" % (cnx, ))
                    cnx.close()

            except Exception as error:
                logger.info(f'Error occured when connecting to database:{error}')
                raise MySqlException(error)

            return result
        return wrapper

    @connection
    def insert_task(self, cursor, payload):
        """Create new task"""
        required_fields = ('client_host', 'job_type', 'argument')
        data_set = [(column, f"'{value}'") for column, value in payload.items()
                    if column in required_fields]
        columns, values = list(zip(*data_set))
        columns_expression = ','.join(columns)
        values_expression = ','.join(values)
        sql_query = (f"INSERT INTO task ({columns_expression}) "
                     f"VALUES({values_expression})")
        result = cursor.execute(sql_query)
        return result

    @connection
    def update_task(self, cursor, payload, no_include=None):
        """Update task"""
        no_include = no_include if no_include else ('task_id', 'job_timeout')
        task_id = payload.get('task_id')
        data_set = [f"{column} = '{value}'" for column, value in payload.items()
                    if column not in no_include]
        set_expression = ','.join(data_set)
        sql_query = (f"UPDATE task SET {set_expression} WHERE task_id = '{task_id}'")
        logger.info(f'Update task:{task_id} status to {payload}')
        result = cursor.execute(sql_query)
        return result

    @connection
    def get_job(self, cursor):
        """Get new job to process it"""
        status = 'new'
        required_columns = ('task_id', 'client_host', 'job_type',
                            'argument', 'status')
        select_expression = ','.join(required_columns)
        sql_query = (f"SELECT {select_expression} FROM task "
                     f"WHERE status = '{status}' LIMIT 1")
        logger.info('Get new task')
        cursor.execute(sql_query)
        result = cursor.fetchall()
        new_task = {}
        if result:
            new_task = dict(zip(required_columns, result[0]))
        logger.debug(new_task)
        return new_task
