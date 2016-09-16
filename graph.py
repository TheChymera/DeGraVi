import math
import os
from copy import deepcopy

import portage
import matplotlib.pyplot as plt
import graph_tool.all as gt
from gentoolkit.package import Package

#relative paths
thisscriptspath = os.path.dirname(os.path.realpath(__file__))
neurogentoo_file = os.path.join(thisscriptspath,"neurogentoo.txt")
NEUROGENTOO = [line.strip() for line in open(neurogentoo_file, 'r')]

gentoo_purple = (0.329,0.282,0.478,1)
gentoo_purple_light = (0.38,0.325,0.553,1)
gentoo_purple_grey = (0.867,0.855,0.925,1)
gentoo_green = (0.451,0.824,0.86,1)

def repository_graph(overlay_paths, overlay_colors=[], highlight=[], highlight_color=(0.8,0,0.8,1)):
	"""Returns all packages from a given overlay path.

	"""
	porttree = portage.db[portage.root]['porttree']

	for overlay_path in overlay_paths:
		if overlay_path not in porttree.dbapi.porttrees:
			print('Overlay "{}" is not known to Portage.\n'.format(overlay_path) +
			'Please set it. Learn how at https://wiki.gentoo.org/wiki/Overlay')
			return False

	g = gt.Graph()

	vertices = {}
	#CREATE PROPERTIES
	##label
	label = g.new_vertex_property('string')
	g.vertex_properties['label'] = label
	##vertex_color
	vcolor = g.new_vertex_property('vector<double>')
	g.vertex_properties['vcolor'] = vcolor


	all_cp = porttree.dbapi.cp_all(trees=overlay_paths)
	for cp in all_cp:
		newest_cpv = cp+"-0_beta" #nothing should be earlier than this
		for cpv in porttree.dbapi.cp_list(cp, mytree=overlay_paths):
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
			label[v1] = cp
			if cp in highlight:
				vcolor[v1] = highlight_color
			else:
				vcolor[v1] = [0.2,0.2,0.2,1]
			vertices[cp] = g.vertex_index[v1]
		else:
			v1 = g.vertex(cp_index)
		for dep in deps:
			try:
				dep_index = vertices[dep]
			except KeyError:
				if dep in all_cp:
					v2 = g.add_vertex()
					label[v2] = dep
					if dep in highlight:
						vcolor[v2] = highlight_color
					else:
						vcolor[v2] = [0.2,0.2,0.2,1]
					vertices[dep] = g.vertex_index[v2]
					e = g.add_edge(v1, v2)
			else:
				v2 = g.vertex(dep_index)
				e = g.add_edge(v1, v2)

	g = gt.GraphView(g,vfilt=lambda v: (v.out_degree() > 0) or (v.in_degree() > 0) )
	g.purge_vertices()

	return g

def draw_degraph(g, plot_type="graph"):
	state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True)
	t = gt.get_hierarchy_tree(state)[0]
	tpos = pos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() - 1), weighted=True)
	cts = gt.get_hierarchy_control_points(g, t, tpos)
	pos = g.own_property(tpos)

	text_rotation = g.new_vertex_property('double')
	g.vertex_properties['text_rotation'] = text_rotation
	for v in g.vertices():
		if pos[v][0] >= 0:
			try:
				text_rotation[v] = math.atan(pos[v][1]/pos[v][0])
			except ZeroDivisionError:
				text_rotation[v] = 0
		else:
			text_rotation[v] = math.pi + math.atan(pos[v][1]/pos[v][0])

	#more readable (up-side-up) labels:
	# for v in g.vertices():
	# 	try:
	# 		text_rotation[v] = math.atan(pos[v][1]/pos[v][0])
	# 	except ZeroDivisionError:
	# 		text_rotation[v] = 0

	if plot_type == "graph":
		gt.graph_draw(g, pos=pos,
				edge_control_points=cts,
				vertex_anchor=0,
				vertex_color=g.vertex_properties['vcolor'],
				vertex_fill_color=g.vertex_properties['vcolor'],
				vertex_font_size=14,
				vertex_text=g.vertex_properties['label'],
				vertex_text_position=0,
				vertex_text_rotation=g.vertex_properties['text_rotation'],
				vertex_size=10,
				edge_start_marker="none",
				edge_mid_marker="none",
				edge_end_marker="none",
				bg_color=[1,1,1,1],
				output_size=[8000,8000],
				output='/home/chymera/degra.png',
				)
	elif plot_type == "state":
		gt.draw_hierarchy(state,
			vertex_text_position=1,
			vertex_font_size=12,
			vertex_text=g.vertex_properties['label'],
			vertex_text_rotation=g.vertex_properties['text_rotation'],
			vertex_anchor=0,
			bg_color=[1,1,1,1],
			output_size=[6000,6000],
			output='/home/chymera/degra.png',
			)

if __name__ == '__main__':
	# packages = get_all_packages('/usr/portage')
	g = repository_graph(['/usr/local/portage/sci'], highlight=NEUROGENTOO)
	draw_degraph(g)
	# gt.graph_draw(g)
	# packages = get_all_packages(['/usr/local/portage/sci','/usr/portage'])
