import math
import os
from copy import deepcopy

import graph_tool.all as gt
import portage
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from gentoolkit.package import Package

#gentoo color scheme
GENTOO_PURPLE = (0.329,0.282,0.478,1)
GENTOO_PURPLE_LIGHT = (0.38,0.325,0.553,1)
GENTOO_PURPLE_LIGHT2 = (0.432,0.337,0.686,1)
GENTOO_PURPLE_GREY = (0.867,0.855,0.925,1)
GENTOO_GREEN = (0.451,0.824,0.086,1)

def populate_from_repository(g, overlay_path, porttree,
	vertices={},
	only_overlay=True,
	overlay_color=GENTOO_PURPLE_LIGHT2,
	overlay_text_color=GENTOO_PURPLE,
	overlay_edge_color=GENTOO_PURPLE_LIGHT2,
	overlay_eorder=2,
	extraneous_color=GENTOO_PURPLE_GREY,
	extraneous_text_color=GENTOO_PURPLE,
	extraneous_edge_color=GENTOO_PURPLE_GREY,
	extraneous_eorder=1,
	):

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
			vlabel[v1] = cp
			vcolor[v1] = overlay_color
			vtext_color[v1] = overlay_text_color
			vertices[cp] = g.vertex_index[v1]
		else:
			v1 = g.vertex(cp_index)
		for dep in deps:
			try:
				dep_index = vertices[dep]
			except KeyError:
				if dep in all_cp:
					v2 = g.add_vertex()
					vlabel[v2] = dep
					vcolor[v2] = overlay_color
					vtext_color[v2] = overlay_text_color
					vertices[dep] = g.vertex_index[v2]
					e = g.add_edge(v1, v2)
					egradient[e] = (1,)+overlay_edge_color
					eorder[e] = overlay_eorder
				elif not only_overlay:
					v2 = g.add_vertex()
					vlabel[v2] = dep
					vcolor[v2] = extraneous_color
					vtext_color[v2] = extraneous_text_color
					vertices[dep] = g.vertex_index[v2]
					e = g.add_edge(v1, v2)
					egradient[e] = (1,)+extraneous_edge_color
					eorder[e] = extraneous_eorder
			else:
				v2 = g.vertex(dep_index)
				e = g.add_edge(v1, v2)
				egradient[e] = (1,)+overlay_edge_color
				eorder[e] = overlay_eorder

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
			overlay_eorder=ix+2,
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
