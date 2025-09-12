SELECT *
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = '2019_lines';

-- SELECT inet_server_addr() AS host_addr, inet_server_port() AS port, current_database() AS database, current_user AS user;



-- Stacking all tables (NEED TO MAKE CHOOSING THE COLUMN NAMES DYNAMIC!)
-- Then you must align the column list (choose a standard set and NULL out missing ones):
-- SELECT grid_id, id, osm_id, name, highway, waterway, aerialway, barrier, man_made, z_order, other_tags, NULL, geom AS src
-- FROM "2019_lines_grid"
-- UNION ALL
-- SELECT grid_id, id, osm_id, name, NULL AS highway, NULL AS waterway, NULL AS aerialway, NULL AS barrier, NULL AS man_made, NULL AS z_order, other_tags, type, geom AS src
-- FROM "2019_multilinestrings_grid";

