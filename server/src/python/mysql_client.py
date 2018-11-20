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
    def insert_task(self, cursor, task_type, host):
        result = False
        status = 'open'
        sql_query = (f"INSERT INTO job (task_name, client_host, status) " \
                     f"VALUES('{task_type}', '{host}', '{status}')")
        insert_result = cursor.execute(sql_query)
        if insert_result:
            result = True
        return result


    @connection
    def job_list(self, cursor, hostname):
        """Get job list for client host"""
        sql_query = (f"SELECT * FROM job WHERE client_host='{hostname}' "
                     f"AND status != 'finished'")
        logger.info(f'Selecting jobs for client {hostname}')
        cursor.execute(sql_query)
        result = cursor.fetchall()
        job_list = []
        for job in result:
            task_id, name, host, status = job
            job = {'task_id' : task_id,
                   'name' : name,
                   'host' : host,
                   'status' : status}
            job_list.append(job)
        return job_list


    @connection
    def update_task(self, cursor, task_id, status):
        """Update task status and result"""
        result = False
        sql_query = (f"UPDATE job SET status = '{status}' WHERE job_id = {task_id}")
        logger.info(f'Update task:{task_id} status to {status}')
        update_result = cursor.execute(sql_query)
        if update_result:
            result = True
        return result
