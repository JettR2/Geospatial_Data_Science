# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 19:59:11 2024

@author: jettr
"""

#%%

import numpy as np
import geopandas as gpd
import osmnx as ox
import networkx as nx
import os
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, MultiLineString
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import folium

# Ensure Pygoes is not used
os.environ['USE_PYGEOS'] = '0'


#%%


# Specifying the type of data
tags = {'building': True}

# Download Building geometries from OSM
gdf = ox.features_from_place('Eugene, Oregon, USA', tags)
print(gdf.shape)  # Output: (59939, number_of_columns)

#%%

# Filter buildings labeled as cafes
cafes = gdf[gdf['amenity'] == 'cafe'].reset_index(drop=True)

# Explicitly construct a new GeoDataFrame
cafes = gpd.GeoDataFrame(cafes, geometry='geometry')

print(cafes.shape)

#%%

# These Cafes are actually polygons, but to simplify, we can plot their centroids
cafes['centroid'] = cafes['geometry'].apply(
    lambda x: x.centroid if isinstance(x, (Polygon, MultiPolygon)) else x)

# Now we'll define the center of the map (Condon Hall)
lat_lon = [44.0751, -123.0781]
m = folium.Map(location=lat_lon, zoom_start=12)

for i in range(cafes.shape[0]):
    my_string = cafes.iloc[i]['name']
    folium.Marker([cafes.iloc[i]['centroid'].y, cafes.iloc[i]['centroid'].x],
                  popup=my_string).add_to(m)

m.save('cafes_map.html')



#%%


# Define coordinates of Condon Hall
lat_lon = (44.0451, -123.0781)

# Define walkable street network 3.2 km around Condon Hall
g = ox.graph_from_point(lat_lon, dist=3200, network_type='walk')

# Plot map
fig, ax = ox.plot_graph(g, bgcolor='white', node_color='black', edge_color='grey', node_size=5)

type(g)

#%%

# Convert to graph
graph_proj = ox.project_graph(g, to_crs=None)

# Get coordinates of Condon Hall
condon_hall = gdf[gdf['name'] == 'Condon Hall'].reset_index()

# Reproject to UTM Zone 10N
condon_hall = condon_hall.to_crs('EPSG:32610')
cafes = cafes.to_crs('EPSG:32610')

condon_hall['centroid'] = condon_hall['geometry'].apply(
  lambda x: x.centroid if type(x) == Polygon else (
  x.centroid if type(x) == MultiPolygon else x))

cafes['centroid'] = cafes['geometry'].apply(
  lambda x: x.centroid if type(x) == Polygon else (
  x.centroid if type(x) == MultiPolygon else x))

#%%

# Get x and y coordinates of Condon Hall
orig_xy = [condon_hall['centroid'].y.values[0], condon_hall['centroid'].x.values[0]]

# Get x and y coordinates of the first cafe
target_xy = [cafes['centroid'].y.values[0], cafes['centroid'].x.values[0]]

#%%

# Find the shortest distance between Condon Hall and any Cafe

# Find the node in the graph that is closest to the origin point
orig_node = ox.distance.nearest_nodes(graph_proj, X=orig_xy[1], Y=orig_xy[0], return_dist=False)

# Find the node in the graph that is closest to the target point
target_node = ox.distance.nearest_nodes(graph_proj, X=target_xy[1], Y=target_xy[0], return_dist=False)

# Calculate the shortest path
route = nx.shortest_path(G=graph_proj, source=orig_node, target=target_node, weight='length')
length = nx.shortest_path_length(G=graph_proj, source=orig_node, target=target_node, weight='length')

print("Shortest path distance = {t:.1f} km.".format(t=length/1000))

# Plot the shortest path using folium
m = ox.plot_route_folium(g, route, weight=5)
m.save('Closes_To_Condon.html')