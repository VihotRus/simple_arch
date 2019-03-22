DROP DATABASE IF EXISTS task_manager;
CREATE DATABASE IF NOT EXISTS task_manager;
USE task_manager;
    source schema/job_queue.sql
    source schema/job_result.sql
