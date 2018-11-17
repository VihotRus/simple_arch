CREATE TABLE IF NOT EXISTS job(
    job_id          INT(10) NOT NULL AUTO_INCREMENT COMMENT 'unique id for each job',
    task_name       VARCHAR(255) NOT NULL COMMENT 'Task description',
    client_host     VARCHAR(100) NOT NULL COMMENT 'Hostname of client',
    status          VARCHAR(20) NOT NULL COMMENT 'Execution status of task',
    PRIMARY KEY (job_id)
);
