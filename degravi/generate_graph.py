import math
import os
from copy import deepcopy

import graph_tool.all as gt
import portage
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from gentoolkit.package import Package

from .utils import get_cp_deps, vertex_and_edge_appearance, tree_iterator, add_vertex_and_edge, populate_from_repository
from .utils import GENTOO_PURPLE, GENTOO_PURPLE_LIGHT, GENTOO_PURPLE_LIGHT2, GENTOO_PURPLE_GREY, GENTOO_GREEN

def repositories_graph(overlay_paths,
	overlay_colors=[GENTOO_PURPLE],
	overlay_text_colors=[GENTOO_PURPLE],
	overlay_edge_colors=[GENTOO_PURPLE],
	extraneous_colors=[GENTOO_PURPLE],
	extraneous_text_colors=[GENTOO_PURPLE],
	extraneous_edge_colors=[GENTOO_PURPLE],
	highlight=[],
	highlight_color=GENTOO_GREEN,
	highlight_edge_color=GENTOO_GREEN,
	highlight_text_color=GENTOO_GREEN,
	only_connected=True,
	only_overlay=True,
	textcolor=False,
	):
	"""Returns all packages from a given overlay path.

	"""

	g = gt.Graph()
	vlabel = g.new_vertex_property('string')
	g.vertex_properties['vlabel'] = vlabel
	vcolor = g.new_vertex_property('vector<double>')
	g.vertex_properties['vcolor'] = vcolor
	vtext_color = g.new_vertex_property('vector<double>')
	g.vertex_properties['vtext_color'] = vtext_color
	egradient = g.new_edge_property('vector<double>')
	g.edge_properties['egradient'] = egradient
	eorder = g.new_edge_property('double')
	g.edge_properties['eorder'] = eorder

	porttree = portage.db[portage.root]['porttree']
	vertices={}
	for ix, overlay_path in enumerate(overlay_paths):
		if overlay_path not in porttree.dbapi.porttrees:
			print('Overlay "{}" is not known to Portage.\n'.format(overlay_path) +
			'Please set it. Learn how at https://wiki.gentoo.org/wiki/Overlay')
			return False
		if not only_overlay:
			try:
				ec = extraneous_colors[ix]
			except IndexError:
				ec = GENTOO_PURPLE
			try:
				etc = extraneous_text_colors[ix]
			except IndexError:
				etc = GENTOO_PURPLE
			try:
				eec = extraneous_edge_colors[ix]
			except IndexError:
				eec = GENTOO_PURPLE
		else:
			ec = etc = eec = GENTOO_PURPLE
		g, vertices = populate_from_repository(g, overlay_path, porttree,
			vertices=vertices,
			only_overlay=only_overlay,
			overlay_color=overlay_colors[ix],
			overlay_text_color=overlay_text_colors[ix],
			overlay_edge_color=overlay_edge_colors[ix],
			overlay_edge_order=ix+2,
			extraneous_color=ec,
			extraneous_text_color=etc,
			extraneous_edge_color=eec,
			extraneous_edge_order=ix+1,
			)

	#set highlight colors
	for v in g.vertices():
		if g.vp.vlabel[v] in highlight:
			g.vp.vcolor[v] = highlight_color
			g.vp.vtext_color[v] = highlight_text_color

	for e in g.edges():
		if g.vp.vlabel[e.source()] in highlight:
			g.ep.egradient[e] = (1,)+highlight_edge_color
			g.ep.eorder[e] = 999 #value which is likely to be larger than all others

	if only_connected:
		g = gt.GraphView(g,vfilt=lambda v: (v.out_degree() > 0) or (v.in_degree() > 0) )
		g.purge_vertices()
	else:
		g = gt.GraphView(g)

	return g

def seeded_graph(base_overlays, seed_set,
	highlight_overlays=[],
	use_match="none",
	seed_color=GENTOO_GREEN,
	seed_text_color=GENTOO_GREEN,
	seed_edge_color=GENTOO_GREEN,
	highlight_color=GENTOO_PURPLE_LIGHT2,
	highlight_text_color=GENTOO_PURPLE,
	highlight_edge_color=GENTOO_PURPLE_LIGHT2,
	base_color=GENTOO_PURPLE_LIGHT2,
	base_text_color=GENTOO_PURPLE,
	base_edge_color=GENTOO_PURPLE_LIGHT2,
	):

	all_overlays = base_overlays + highlight_overlays

	g = gt.Graph()
	vlabel = g.new_vertex_property('string')
	g.vertex_properties['vlabel'] = vlabel
	vcolor = g.new_vertex_property('vector<double>')
	g.vertex_properties['vcolor'] = vcolor
	vtext_color = g.new_vertex_property('vector<double>')
	g.vertex_properties['vtext_color'] = vtext_color
	egradient = g.new_edge_property('vector<double>')
	g.edge_properties['egradient'] = egradient
	eorder = g.new_edge_property('double')
	g.edge_properties['eorder'] = eorder

	porttree = portage.db[portage.root]['porttree']
	vertices={}
	dep_dict={}

	highlight_overlay_cp = porttree.dbapi.cp_all(trees=highlight_overlays)
	all_cp = porttree.dbapi.cp_all(trees=all_overlays)
	for cp in all_cp:
		if use_match == "none":
			deps = get_cp_deps(cp, all_overlays, porttree, matchnone=True, matchall=False)
		elif use_match == "all":
			deps = get_cp_deps(cp, all_overlays, porttree, matchnone=False, matchall=True)
		if deps == False:
			pass
		else:
			dep_dict[cp] = deps

	sets_property_values=[]
	sets_property_values.append([seed_set,[seed_color, seed_text_color, seed_edge_color, 3]])
	sets_property_values.append([highlight_overlay_cp,[highlight_color, highlight_text_color, highlight_edge_color,2]])
	sets_property_values.append([all_cp,[base_color, base_text_color, base_edge_color, 1]])

	for seed_cp in seed_set:
		vertices, _ = tree_iterator(g, seed_cp, vertices, dep_dict,
			sets_property_values=sets_property_values
			)

	return g
