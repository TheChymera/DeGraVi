import math
import os

import matplotlib.pyplot as plt
from matplotlib import transforms

import graph_tool.all as gt

def circular_depgraph(g,
	plot_type="graph",
	save_as="~/depgraph.png",
	):

	save_as = os.path.abspath(os.path.expanduser(save_as))

	state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True)
	t = gt.get_hierarchy_tree(state)[0]
	tpos = pos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() - 1), weighted=True)
	cts = gt.get_hierarchy_control_points(g, t, tpos)
	pos = g.own_property(tpos)

	vtext_rotation = g.new_vertex_property('double')
	g.vertex_properties['vtext_rotation'] = vtext_rotation

	for v in g.vertices():
		#set vtext_rotation
		if pos[v][0] >= 0:
			try:
				vtext_rotation[v] = math.atan(pos[v][1]/pos[v][0])
			except ZeroDivisionError:
				vtext_rotation[v] = 0
		else:
			vtext_rotation[v] = math.pi + math.atan(pos[v][1]/pos[v][0])

	#here we do black magic to get proper output size (controls vertex spacing) and scaling
	vertex_number = g.num_vertices()
	view_zoom = (vertex_number*36.0485)**(-10.068/vertex_number)+0.017037
	output_size = vertex_number*6+70
	title_size = vertex_number/47
	dpi=300
	character_offset = title_size/output_size
	if output_size >= 18000:
		print("WARNING: You are exceding the maximal printable size - 150cm in one dimension at 300dpi")
	print("Plotting dependency graph containing {0} packages, at a resolution of {1} pixels by {1} pixels".format(vertex_number, output_size))

	if plot_type == "graph":
		gt.graph_draw(g, pos=pos,
				edge_control_points=cts,
				vertex_anchor=0,
				vertex_color=g.vertex_properties['vcolor'],
				vertex_fill_color=g.vertex_properties['vcolor'],
				vertex_font_size=14,
				vertex_text=g.vertex_properties['vlabel'],
				vertex_text_position=6.2,
				vertex_text_rotation=g.vertex_properties['vtext_rotation'],
				vertex_text_color=g.vertex_properties['vtext_color'],
				vertex_size=16,
				edge_start_marker="none",
				edge_mid_marker="none",
				edge_end_marker="none",
				edge_gradient=g.edge_properties["egradient"],
				eorder=g.edge_properties["eorder"],
				bg_color=[1,1,1,1],
				output_size=[output_size,output_size],
				output=save_as,
				fit_view=view_zoom,
				)
	elif plot_type == "state":
		gt.draw_hierarchy(state,
			vertex_text_position=1,
			vertex_font_size=12,
			vertex_text=g.vertex_properties['label'],
			vertex_text_rotation=g.vertex_properties['text_rotation'],
			vertex_anchor=0,
			bg_color=[1,1,1,1],
			output_size=[output_size,output_size],
			output=save_as,
			)
