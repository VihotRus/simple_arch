DROP TABLE IF EXISTS job_queue;
CREATE TABLE IF NOT EXISTS job_queue(
    id         INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Unique id for each job',
    client_host     VARCHAR(100) NOT NULL COMMENT 'Client hostname',
    job_type        VARCHAR(10) NOT NULL COMMENT 'Defines type of job',
    job_arg         VARCHAR(255) NOT NULL COMMENT 'Job argument',
    status          VARCHAR(20) NOT NULL DEFAULT 'new' COMMENT 'Task status',
    ctime           INT(11) NOT NULL COMMENT 'Creation time',
    stime           INT(11) COMMENT 'Start time',
    mtime           INT(11) NOT NULL COMMENT 'Modification time',
    PRIMARY KEY (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
