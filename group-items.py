#! /usr/bin/env python
"""
Reads in the geometric_contains.csv file and groups by logainm_id and produces
a convex hull of the shape.
"""

import shapely.geometry
import sys, os
import csv
from collections import defaultdict
import fiona, fiona.crs

def find_convex_hulls(input_dir):
    contains_filename = os.path.join(input_dir, 'geometric_contains.csv')
    outer_points = defaultdict(set)
    with open(contains_filename) as input_fp:
        csv_reader = csv.DictReader(input_fp)
        for row in csv_reader:
            outer_points[row['outer_obj_id']].add((row['inner_lat'], row['inner_lon']))

    geom_filename = os.path.join(input_dir, 'geometries.csv')
    # There might be nothign in there, so just add a general point
    with open(geom_filename) as input_fp:
        csv_reader = csv.DictReader(input_fp)
        for row in csv_reader:
            outer_points[row['logainm_id']].add((row['lat'], row['lon']))
    

    convex_hulls = {}
    for outer_obj_id in outer_points:
        points = outer_points[outer_obj_id]
        # Note: flipped lat/lon to make it XY
        points = [(float(x[1]), float(x[0])) for x in points]
        shape = shapely.geometry.MultiPoint(points).convex_hull

        if shape.geom_type != 'Polygon':
            # only one point, so put a tiny buffer around it so we have a polygon
            #print shape.geom_type
            shape = shape.buffer(0.00001)
        else:
            #print "Is polygon"
            pass


        convex_hulls[outer_obj_id] = shape
    
    return convex_hulls

def add_convex_hulls_to_all_logainm(convex_hulls, all_of_logainm_filename):
    all_of_logainm = {}
    with open(all_of_logainm_filename) as input_fp:
        csv_reader = csv.DictReader(input_fp)
        for row in csv_reader:
            if row['logainm_id'] in convex_hulls:
                row['polygon'] = convex_hulls[row['logainm_id']]
                row['polygon_wkt'] = row['polygon'].wkt
                all_of_logainm[row['logainm_id']] = row

    return all_of_logainm

if __name__ == '__main__':
    csv_dir = sys.argv[1]
    convex_hulls = find_convex_hulls(csv_dir)

    all_of_logainm = add_convex_hulls_to_all_logainm(convex_hulls, os.path.join(csv_dir, 'logainm_names.csv'))

    keys = ['logainm_id', 'logainm_category_code', 'name_en', 'name_ga', 'polygon_wkt']

    

    #with open(sys.argv[2], 'w') as output_fp:
    #    writer = csv.DictWriter(output_fp, keys, lineterminator="\n")
    #    writer.writeheader()
    #    for logainm_id in sorted(all_of_logainm.keys()):
    #        writer.writerow(all_of_logainm[logainm_id])

    schema = {
        'geometry': 'Polygon',
        'properties': {'lid': 'int', 'code': 'str', 'name_en': 'str', 'name_ga': 'str'},
    }

    crs = fiona.crs.from_epsg(4326)

    # Write a new Shapefile
    with fiona.open('logainm.shp', 'w', driver='ESRI Shapefile', crs=crs, schema=schema) as c:
        ## If there are multiple geometries, put the "for" loop here
        for logainm_id in sorted(all_of_logainm.keys()):
            row = all_of_logainm[logainm_id]
            print "writing ", logainm_id
            c.write({
                'geometry': shapely.geometry.mapping(row['polygon']),
                'properties': {'lid': row['logainm_id'], 'code': row['logainm_category_code'],
                               'name_en': row['name_en'], 'name_ga': row['name_ga']},
            })

