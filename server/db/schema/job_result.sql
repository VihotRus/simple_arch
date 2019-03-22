DROP TABLE IF EXISTS job_result;
CREATE TABLE IF NOT EXISTS job_result(
    id              INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Unique id for each result',
    job_id          INT(11) NOT NULL COMMENT 'Job id from job_queue table',
    result          VARCHAR(5) NOT NULL COMMENT 'Job  genetral result PASS or ERROR',
    result_info     VARCHAR(255) NOT NULL COMMENT 'Execution result of jub',
    run_time        INT(11) NOT NULL COMMENT 'Job run time',
    PRIMARY KEY (id),
    FOREIGN KEY(job_id) REFERENCES job_queue(id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
