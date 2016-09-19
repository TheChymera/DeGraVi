import math
import os
from copy import deepcopy

import graph_tool.all as gt
import portage
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from gentoolkit.package import Package

from utils import get_cp_deps, tree_add_vertex_and_properties, tree_iterator
from utils import GENTOO_PURPLE, GENTOO_PURPLE_LIGHT, GENTOO_PURPLE_LIGHT2, GENTOO_PURPLE_GREY, GENTOO_GREEN

def populate_from_repository(g, overlay_path, porttree,
	vertices={},
	only_overlay=True,
	overlay_color=GENTOO_PURPLE_LIGHT2,
	overlay_text_color=GENTOO_PURPLE,
	overlay_edge_color=GENTOO_PURPLE_LIGHT2,
	overlay_edge_order=2,
	extraneous_color=GENTOO_PURPLE_GREY,
	extraneous_text_color=GENTOO_PURPLE,
	extraneous_edge_color=GENTOO_PURPLE_GREY,
	extraneous_eorder=1,
	):


	all_cp = porttree.dbapi.cp_all(trees=[overlay_path])
	for cp in all_cp:
		newest_cpv = cp+"-0_beta" #nothing should be earlier than this
		for cpv in porttree.dbapi.cp_list(cp, mytree=overlay_path):
			if portage.pkgcmp(portage.pkgsplit(cpv), portage.pkgsplit(newest_cpv)) >= 0:
				newest_cpv = cpv
		if newest_cpv != cp+"-0_beta":
			deps = porttree.dbapi.aux_get(newest_cpv, ["DEPEND","RDEPEND","PDEPEND"])
			deps = ' '.join(deps).split() # consolidate deps
			deps = list(set(deps)) # de-duplicate

		#correct dependency list formatting
		for ix in range(len(deps)):
			#remove non-package entries from deps list
			if not "/" in deps[ix]:
				deps[ix] = None
			else:
				#remove all syntax that does not match cpv
				for delimiter in ["[",":"]:
					if delimiter in deps[ix]:
						deps[ix] = deps[ix].split(delimiter)[0]
				if deps[ix][:2] in [">=", "<=", "!<", "!>"]:
					deps[ix] = deps[ix][2:]
				if deps[ix][:1] in [">", "<", "~", "=", "!"]:
					deps[ix] = deps[ix][1:]
				if deps[ix][-1:] in ["*"]:
					deps[ix] = deps[ix][:-1]
		deps  = list(filter(None, deps))
		for ix, a in enumerate(deps):
			if portage.pkgsplit(a) != None:
				deps[ix] = portage.pkgsplit(a)[0]

		#Populate graph
		try:
			cp_index = vertices[cp]
		except KeyError:
			v1 = g.add_vertex()
			g.vp.vlabel[v1] = cp
			g.vp.vcolor[v1] = overlay_color
			g.vp.vtext_color[v1] = overlay_text_color
			vertices[cp] = g.vertex_index[v1]
		else:
			v1 = g.vertex(cp_index)
		for dep in deps:
			try:
				dep_index = vertices[dep]
			except KeyError:
				if dep in all_cp:
					v2 = g.add_vertex()
					g.vp.vlabel[v2] = dep
					g.vp.vcolor[v2] = overlay_color
					g.vp.vtext_color[v2] = overlay_text_color
					vertices[dep] = g.vertex_index[v2]
					e = g.add_edge(v1, v2)
					g.ep.egradient[e] = (1,)+overlay_edge_color
					g.ep.eorder[e] = overlay_edge_order
				elif not only_overlay:
					v2 = g.add_vertex()
					g.vp.vlabel[v2] = dep
					g.vp.vcolor[v2] = extraneous_color
					g.vp.vtext_color[v2] = extraneous_text_color
					vertices[dep] = g.vertex_index[v2]
					e = g.add_edge(v1, v2)
					g.ep.egradient[e] = (1,)+extraneous_edge_color
					g.ep.eorder[e] = extraneous_eorder
			else:
				v2 = g.vertex(dep_index)
				e = g.add_edge(v1, v2)
				g.ep.egradient[e] = (1,)+overlay_edge_color
				g.ep.eorder[e] = overlay_edge_order

	return g, vertices

def dependency_graph(overlay_paths,
	overlay_colors=[GENTOO_PURPLE],
	overlay_text_colors=[GENTOO_PURPLE],
	overlay_edge_colors=[GENTOO_PURPLE],
	extraneous_colors=[GENTOO_PURPLE],
	extraneous_text_colors=[GENTOO_PURPLE],
	extraneous_edge_colors=[GENTOO_PURPLE],
	highlight=[],
	highlight_color=GENTOO_GREEN,
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
			extraneous_eorder=ix+1,
			)

	#set highlight colors
	for v in g.vertices():
		if g.vp.vlabel[v] in highlight:
			g.vp.vcolor[v] = highlight_color
			g.vp.vtext_color[v] = highlight_text_color

	for e in g.edges():
		if g.vp.vlabel[e.source()] in highlight:
			g.ep.egradient[e] = (1,)+highlight_text_color
			g.ep.eorder[e] = 999 #value which is likely to be larger than all others

	if only_connected:
		g = gt.GraphView(g,vfilt=lambda v: (v.out_degree() > 0) or (v.in_degree() > 0) )
		g.purge_vertices()
	else:
		g = gt.GraphView(g)

	return g

def tree_graph(base_overlays, seed_set,
	highlight_overlays=[],
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
		deps = get_cp_deps(cp, all_overlays, porttree)
		if deps == False:
			pass
		else:
			dep_dict[cp] = deps

	for seed_cp in seed_set:
		vertices, _ = tree_iterator(g, seed_cp, vertices, dep_dict,
			seed_set=seed_set,
			highlight_overlay_cp=highlight_overlay_cp,
			all_cp=all_cp,
			seed_property_values=[seed_color, seed_text_color, seed_edge_color, 3],
			highlight_property_values=[highlight_color, highlight_text_color, highlight_edge_color,2],
			base_property_values=[base_color, base_text_color, base_edge_color, 1],
			)

	print(g.num_vertices())
