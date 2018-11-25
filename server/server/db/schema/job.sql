CREATE TABLE IF NOT EXISTS task(
    task_id         INT(10) NOT NULL AUTO_INCREMENT COMMENT 'Unique id for each task',
    client_host     VARCHAR(100) NOT NULL COMMENT 'Hostname of client',
    job_type        VARCHAR(20) NOT NULL COMMENT 'Defines type of job',
    argument        VARCHAR(255) NOT NULL COMMENT 'Job parameter',
    status          VARCHAR(20) NOT NULL DEFAULT 'new' COMMENT 'Task status',
    result          VARCHAR(255) COMMENT 'Job execution result',
    created         INT(11) NOT NULL COMMENT 'Creation timestamp',
    finished        INT(11) COMMENT 'Finish timestamp',
    PRIMARY KEY (task_id)
);
