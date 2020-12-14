#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jensforsgard
"""


import matplotlib.pyplot as plt

from shapely.geometry import Polygon




def color_dcnry(game):
    """ Retrieves the dictionary of colors of supply center provinces
    describing the current position of the game.

    """
    # Neutrals are snow colored
    dcnry = {prov.name: 'snow' for prov in game.variant.map.supply_centers}

    # Non-neutral are colored by power
    for power in game.powers:
        colors = {prov.name: game.variant.province_colors[power.name]
                  for prov in game.supply_centers[power]}
        dcnry.update(colors)
    
    return dcnry




def plot_polygon(geom, color, edgecolor='black'):
    """ Plots one polygon with the given colors.
    
    """
    if type(geom) == Polygon:
        geom = [geom]

    for poly in geom:
        plt.fill(*poly.exterior.xy, facecolor=color,
                     edgecolor=edgecolor, linewidth=.3)




def plot_provinces(game, gdf):
    """ Returns a plt.fill of province of the given index of the
    geodataframe.

    """
    dcnry = color_dcnry(game)
        
    for k in gdf.index:
        if not gdf.loc[k, 'land']:
            plot_polygon(gdf.loc[k, 'geometry'], 'azure', 'cornflowerblue')
            
        elif gdf.loc[k, 'static']:
            plot_polygon(gdf.loc[k, 'geometry'], 'lightgray')               

        else:
            try:
                plot_polygon(gdf.loc[k, 'geometry'], dcnry[gdf.loc[k, 'name']])

            except KeyError:  # Not a supply center
                plot_polygon(gdf.loc[k, 'geometry'], 'oldlace')




def plot_unit(unit, point, size, color, shift, retreat=False):
    """ Returns a plt.plot of the units current location.

    """
    markers = {'Army': 'o', 'Fleet': '^'}

    if retreat:
        plt.plot([point.x + shift], [point.y - shift], 
                 marker=markers[unit.force.name],
                 color=color, markersize=.75*size,
                 markeredgewidth=.3, markeredgecolor='red')

    else:
        plt.plot([point.x], [point.y],
                 marker=markers[unit.force.name],
                 color=color, markersize=size,
                 markeredgewidth=.3, markeredgecolor='black')




def plot_units(game, gdf):
    """ Plots the units of the game at locations stored in the geodataframe.
    
    """
    retreat = False
    if game.season.phase == 'Retreats':
        retreat = True
        ordered = [order.unit for order in game.orders]
    
    size = game.variant.marker_size
    shift = game.shift
    
    for unit in game.units:
        point = gdf[gdf.name == unit.location.name].iloc[0].geometry
        color = game.__unit_color__(unit.owner)
        if retreat and unit in ordered:
            plot_unit(unit, point, size, color, shift, retreat)
        else:
            plot_unit(unit, point, size, color, shift)




def plot_names(gdf):
    """ Plots the names of the provinces in the board.
    
    """
    for k in gdf.index:
        point = gdf.loc[k, 'geometry']
        plt.annotate(gdf.loc[k, 'name'], xy=(point.x, point.y))




def show(game):
    """ Plots the current position. 

    """
    if game.graphics is None:
        game.__load_graphics__()

    gdf = game.graphics

    plt.figure(dpi=150)
    plt.axis('off')
    plt.margins(0)

    # Plot the provinces; with sea provinces are plotted first.
    sea = gdf[(gdf.point == False) & (gdf.land == False)]
    plot_provinces(game, sea)
    land = gdf[(gdf.point == False) & (gdf.land == True)]
    plot_provinces(game, land)

    # Plot the units
    points = gdf[(gdf.point == True) & (gdf.text == False)]
    plot_units(game, points)

    # Plot names of provinces
    names = gdf[(gdf.point == True) & (gdf.text == True)]
    plot_names(names)

    plt.show()

