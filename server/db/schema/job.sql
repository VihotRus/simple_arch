CREATE TABLE IF NOT EXISTS task(
    task_id         INT(10) NOT NULL AUTO_INCREMENT COMMENT 'unique id for each job',
    client_host     VARCHAR(100) NOT NULL COMMENT 'Hostname of client',
    task_name       VARCHAR(255) NOT NULL COMMENT 'Task description',
    task_parameter  VARCHAR(100) NOT NULL COMMENT 'Task parameter',
    job_status      VARCHAR(20) NOT NULL DEFAULT 'new' COMMENT 'Execution status of task',
    job_result     VARCHAR(20) COMMENT 'Job execution result',
    created         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date of creation',
    finished        TIMESTAMP COMMENT 'Finish date',
    PRIMARY KEY (task_id)
);
