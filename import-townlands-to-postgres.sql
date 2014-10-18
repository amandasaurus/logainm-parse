drop table logainm_townlands;
create table logainm_townlands ( gid serial, logainm_id integer, name_en text, name_ga text, lat float, lon float, geom geometry(Point, 4326) );
copy logainm_townlands (logainm_id, name_en, name_ga, lat, lon) from '/tmp/townlands.csv' WITH CSV HEADER;
update logainm_townlands set geom = St_SetSRID(ST_MakePoint(lat, lon), 4326);
SELECT UpdateGeometrySRID('logainm_townlands','geom',4326);

create table logosm as select osm_id, logainm_id, name as osm_name, "name:ga" as osm_name_ga, name_en as logainm_name_en, name_ga as logainm_name_ga, way as osm_polygon, geom as logainm_point  from planet_osm_polygon JOIN logainm_townlands ON (admin_level = '10' and st_contains(planet_osm_polygon.way, logainm_townlands.geom) and planet_osm_polygon.name = logainm_townlands.name_en) where ("name:ga" IS NULL) OR ("name:ga" IS NOT NULL AND name_ga = "name:ga");
