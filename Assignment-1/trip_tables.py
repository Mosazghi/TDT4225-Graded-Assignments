DB_NAME = 'A1_db'

TABLES = {}
TABLES['trip'] = (
    "CREATE TABLE IF NOT EXISTS `trip` ("
    "  `id` BIGINT PRIMARY KEY,"
    "  `call_type` CHAR(1),"
    "  `origin_call_id` BIGINT NULL,"
    "  `origin_stand_id` INT NULL,"
    "  `taxi_id` INT NOT NULL,"
    "  `timestamp` DATETIME NOT NULL,"
    "  `day_type` CHAR(1),"
    "  `missing_data` BOOLEAN NOT NULL"
    ")")

TABLES['gps_point'] = (
    "CREATE TABLE IF NOT EXISTS `gps_point` ("
    "  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,"
    "  `trip_id` BIGINT NOT NULL,"
    "  `point_index` INT NOT NULL,"
    "  `longitude` DOUBLE NOT NULL,"
    "  `latitude` DOUBLE NOT NULL,"
    "  FOREIGN KEY (`trip_id`)"
    "    REFERENCES `trip`(`id`)"
    "    ON DELETE CASCADE"
    ")")
