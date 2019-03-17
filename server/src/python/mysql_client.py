#!/usr/bin/env python3.7

""" This module works with database"""

import pymysql
from tools.config_init import config, logger

#db config section
DB_SECTION = 'db'


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
            try:
                cnx = pymysql.connect(host = self.__host,
                                      db = self.__name,
                                      user = self.__user,
                                      passwd = self.__passwd,
                                      charset = self.__charset)
                logger.info('Connected')
                logger.debug(f'connection object = {cnx}')
                cursor = cnx.cursor()

                try:
                    logger.debug("Calling func %s " % (func.__name__, ))
                    result = func(self, cursor, *args, **kwargs)
                    logger.info("Commiting changes")
                    cnx.commit()
                except Exception as error:
                    logger.info("Error occured")
                    logger.error(error)
                    logger.info("Rollbacking changes")
                    cnx.rollback()
                    result = error.args[-1]
                finally:
                    logger.debug("Closing connection %s" % (cnx, ))
                    cnx.close()

            except Exception as error:
                logger.info(f'Error occured when connecting to database:{error}')
                result = error.args[-1]

            return result
        return wrapper

    @connection
    def insert_task(self, cursor, payload, host):
        result = False
        task_name = payload.get('task_name')
        task_parameter = payload.get('task_parameter')
        sql_query = (f"INSERT INTO task (client_host, task_name, task_parameter) "
                     f"VALUES('{host}', '{task_name}', '{task_parameter}')")
        insert_result = cursor.execute(sql_query)
        if insert_result:
            result = True
        return result


    @connection
    def update_task(self, cursor, payload):
        """Update task status and result"""
        result = False
        task_id = payload.get('task_id')
        job_status = payload.get('job_status')
        job_result = payload.get('job_result')
        sql_query = (f"UPDATE task SET job_status = '{job_status}', job_result = '{job_result}' "
                     f"WHERE task_id = '{task_id}'")
        logger.info(f'Update task:{task_id} status to {job_status}')
        update_result = cursor.execute(sql_query)
        if update_result:
            result = True
        return result

    @connection
    def get_job(self, cursor):
        """Get new job to process it"""
        status = 'new'
        sql_query = (f"SELECT task_id, client_host, task_name, task_parameter, job_status "
                     f"FROM task WHERE job_status = '{status}' LIMIT 1")
        logger.info('Get new task')
        cursor.execute(sql_query)
        result = cursor.fetchall()[0]
        new_task = {}
        if result:
            task_id, client_host, task_name, task_parameter, job_status = result
            new_task = {'task_id' : task_id,
                        'client_host' : client_host,
                        'task_name' : task_name,
                        'task_parameter' : task_parameter,
                        'job_status' : job_status}
        return new_task