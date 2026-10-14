#1
SELECT
    (SELECT COUNT(DISTINCT taxi_id) FROM trip) AS taxis,
    (SELECT COUNT(*) FROM trip) AS trips,
    (SELECT COUNT(*) FROM gps_point) AS gps_points;

#2
SELECT AVG(trip_count) AS avg_trip_count
FROM (
    SELECT COUNT(id) AS trip_count
    FROM trip
    GROUP BY taxi_id
) AS trip_counts;

#3
SELECT taxi_id, COUNT(id) AS trip_count
FROM trip
GROUP BY taxi_id
ORDER BY trip_count DESC
LIMIT 20;

#4a)
WITH ct_counts AS (
    SELECT taxi_id, call_type, COUNT(*) AS frequency
    FROM trip
    GROUP BY taxi_id, call_type
),
ranked_cts AS (
    SELECT
        taxi_id,
        call_type AS most_frequenct_call_type,
        frequency AS count,
        ROW_NUMBER() OVER (
            PARTITION BY taxi_id
            ORDER BY frequency DESC
        ) AS rank_id
    FROM ct_counts
)
SELECT taxi_id, most_frequenct_call_type, count
FROM ranked_cts
WHERE rank_id = 1;

#7
SELECT COUNT(*) AS invalid_trips
FROM trip t
WHERE NOT EXISTS (
    SELECT 1
    FROM gps_point g
    WHERE g.trip_id = t.id
      AND g.point_index = 2
);
