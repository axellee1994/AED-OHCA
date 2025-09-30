-- SELECT *
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = '2019_lines';

-- SELECT inet_server_addr() AS host_addr, inet_server_port() AS port, current_database() AS database, current_user AS user;


DROP TABLE IF EXISTS "2021_COMBINED_grid";
CREATE TABLE "2021_COMBINED_grid" AS
SELECT "address", NULL AS "admin_level", NULL AS "aerialway", NULL AS "aeroway", NULL AS "amenity", "barrier", NULL AS "boundary", NULL AS "building", NULL AS "craft", NULL AS "geological", "geom", "grid_id", "highway", NULL AS "historic", "id", "is_in", NULL AS "land_area", NULL AS "landuse", NULL AS "leisure", "man_made", NULL AS "military", "name", NULL AS "natural", NULL AS "office", "osm_id", NULL AS "osm_way_id", "other_tags", "place", "ref", NULL AS "shop", NULL AS "sport", NULL AS "tourism", NULL AS "type", NULL AS "waterway", NULL AS "z_order", '2021_points_grid' AS src FROM "2021_points_grid"
UNION ALL
SELECT NULL AS "address", NULL AS "admin_level", "aerialway", NULL AS "aeroway", NULL AS "amenity", "barrier", NULL AS "boundary", NULL AS "building", NULL AS "craft", NULL AS "geological", "geom", "grid_id", "highway", NULL AS "historic", "id", NULL AS "is_in", NULL AS "land_area", NULL AS "landuse", NULL AS "leisure", "man_made", NULL AS "military", "name", NULL AS "natural", NULL AS "office", "osm_id", NULL AS "osm_way_id", "other_tags", NULL AS "place", NULL AS "ref", NULL AS "shop", NULL AS "sport", NULL AS "tourism", NULL AS "type", "waterway", "z_order", '2021_lines_grid' AS src FROM "2021_lines_grid"
UNION ALL
SELECT NULL AS "address", NULL AS "admin_level", NULL AS "aerialway", NULL AS "aeroway", NULL AS "amenity", NULL AS "barrier", NULL AS "boundary", NULL AS "building", NULL AS "craft", NULL AS "geological", "geom", "grid_id", NULL AS "highway", NULL AS "historic", "id", NULL AS "is_in", NULL AS "land_area", NULL AS "landuse", NULL AS "leisure", NULL AS "man_made", NULL AS "military", "name", NULL AS "natural", NULL AS "office", "osm_id", NULL AS "osm_way_id", "other_tags", NULL AS "place", NULL AS "ref", NULL AS "shop", NULL AS "sport", NULL AS "tourism", "type", NULL AS "waterway", NULL AS "z_order", '2021_multilinestrings_grid' AS src FROM "2021_multilinestrings_grid"
UNION ALL
SELECT NULL AS "address", "admin_level", NULL AS "aerialway", "aeroway", "amenity", "barrier", "boundary", "building", "craft", "geological", "geom", "grid_id", NULL AS "highway", "historic", "id", NULL AS "is_in", "land_area", "landuse", "leisure", "man_made", "military", "name", "natural", "office", "osm_id", "osm_way_id", "other_tags", "place", NULL AS "ref", "shop", "sport", "tourism", "type", NULL AS "waterway", NULL AS "z_order", '2021_multipolygons_grid' AS src FROM "2021_multipolygons_grid";

