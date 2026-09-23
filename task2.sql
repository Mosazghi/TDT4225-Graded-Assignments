CREATE TABLE trip (
    id INT AUTO_INCREMENT PRIMARY KEY,
    taxi_id INT NOT NULL,
    call_type CHAR(1),
    origin_call_id INT,
    origin_stand_id INT,
    start_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    day_type CHAR(1)
);

CREATE TABLE gps_point (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    point_index INT,
    longitude DOUBLE,
    latitude DOUBLE,

    FOREIGN KEY (trip_id) REFERENCES Trip(id),
    UNIQUE (trip_id, point_index)
);


#1
SELECT
    (SELECT COUNT(DISTINCT taxi_id) FROM trip) AS tot_taxis,
    (SELECT COUNT(*) FROM trip) AS tot_trip,
    (SELECT COUNT(*) FROM gps_point) AS tot_gps_points;

#2
SELECT avg(trip_count) AS avg_trip_count
FROM (
    SELECT count(id) AS trip_count
    FROM trip
    GROUP BY taxi_id
) AS trip_counts;

#3
SELECT taxi_id, count(id) AS trip_count
FROM trip
GROUP BY taxi_id
ORDER BY trip_count DESC
LIMIT 20;

#4
SELECT DISTINCT taxi_id,
CASE WHEN count_A = GREATEST(count_A, count_B, count_C) THEN 'A'
WHEN count_B = GREATEST(count_A, count_B, count_C) THEN 'B'
WHEN count_C = GREATEST(count_A, count_B, count_C) THEN 'C'
END AS most_used_call_type
FROM (
SELECT
    taxi_id,
    SUM(CASE WHEN call_type = 'A' THEN 1 ELSE 0 END) AS count_A,
    SUM(CASE WHEN call_type = 'B' THEN 1 ELSE 0 END) AS count_B,
    SUM(CASE WHEN call_type = 'C' THEN 1 ELSE 0 END) AS count_C
FROM trip
GROUP BY taxi_id) AS counts;

#4b) #This is not complete yet i think, we have to use python
SELECT avg(nr_gps_points)*15
FROM(
    SELECT count(*) AS nr_gps_points
    FROM trip
    JOIN gps_point ON trip.id = gps_point.trip_id
    GROUP BY trip_id
)
