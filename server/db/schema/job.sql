CREATE TABLE IF NOT EXISTS task(
    task_id         INT(10) NOT NULL AUTO_INCREMENT COMMENT 'unique id for each job',
    client_host     VARCHAR(100) NOT NULL COMMENT 'Hostname of client',
    task_name       VARCHAR(255) NOT NULL COMMENT 'Task description',
    task_parameter  VARCHAR(100) NOT NULL COMMENT 'Task parameter',
    status          VARCHAR(20) NOT NULL COMMENT 'Execution status of task',
    created         TIMESTAMP CURRENT_TIMESTAMP COMMENT 'Date of creation',
    finished        TIMESTAMP COMMENT 'Finish date',
    PRIMARY KEY (job_id)
);
