import re

import portage

#gentoo color scheme
GENTOO_PURPLE = (0.329,0.282,0.478,1)
GENTOO_PURPLE_LIGHT = (0.38,0.325,0.553,1)
GENTOO_PURPLE_LIGHT2 = (0.432,0.337,0.686,1)
GENTOO_PURPLE_LIGHT2_A75 = (0.432,0.337,0.686,0.75)
GENTOO_PURPLE_LIGHT2_A50 = (0.432,0.337,0.686,0.5)
GENTOO_PURPLE_GREY = (0.867,0.855,0.925,1)
GENTOO_PURPLE_GREY_A75 = (0.867,0.855,0.925,0.75)
GENTOO_PURPLE_GREY_A50 = (0.867,0.855,0.925,0.5)
GENTOO_GREEN = (0.451,0.824,0.086,1)
GENTOO_GREEN_A75 = (0.451,0.824,0.086,0.75)
GENTOO_GREEN_A50 = (0.451,0.824,0.086,0.5)

def tree_iterator(g, seed_cp, vertices, dep_dict, sets_property_values, v1=False, stophere=False):
	"""Walk dependency graph given by `dep_dict` starting with `seed_cp`.

	Parameters
	----------
	g : graph_tool.Graph() instance
	The graph to which vertices and edges will be added. It needs to have vlabel, vcolor, vtext_color, egradient, and eorder properties. See definitiona examples at the beginning of functions calling this function.

	seed_cp : str
	Package name from which to start graph.

	dep_dict : dict
	Dictionary containing entire dependency graph.

	v1 : graph_tool Vertex instance , optional
	Vertex to connect to the next generated vertex.

	stophere : boolean, optional
	Stop after adding this node and the corresponding edge. This interrupts the iteration
	"""

	if seed_cp in sum([item[0] for item in sets_property_values],[]):
		vcolor, vtext_color, ecolor, eorder = vertex_and_edge_appearance(seed_cp, sets_property_values, g=g, v1=v1)
		vertices, v1 = add_vertex_and_edge(g, seed_cp, vertices, v1, vcolor=vcolor, vtext_color=vtext_color, ecolor=ecolor, eorder=eorder)
		if not stophere:
			for dep in dep_dict[seed_cp]:
				try:
					_ = vertices[dep]
				except KeyError:
					vertices, _ = tree_iterator(g, dep, vertices, dep_dict, sets_property_values, v1=v1)
				else:
					vertices, _ = tree_iterator(g, dep, vertices, dep_dict, sets_property_values, v1=v1, stophere=True)
	else:
		print("Package \""+seed_cp+"\" was not found in the seed set, or the base and highlight overlays. Where is it coming from?")
	return vertices, v1

def vertex_and_edge_appearance(cp,
	sets_property_values,
	g=False,
	v1=False,
	):
	for set_property_values in sets_property_values:
		if cp in set_property_values[0]:
			vcolor = set_property_values[1][0]
			vtext_color = set_property_values[1][1]
			ecolor = eorder = False
			break
	if v1 and g:
		try:
			cp_for_ecolor_selection = g.vp.vlabel[v1]
		except ValueError:
			pass
		else:
			for set_property_values in sets_property_values:
				if cp_for_ecolor_selection in set_property_values[0]:
					ecolor = set_property_values[1][2]
					eorder = set_property_values[1][3]
					break
	return vcolor, vtext_color, ecolor, eorder

def add_vertex_and_edge(g, cp, vertices,
	v1=False,
	vcolor=GENTOO_PURPLE,
	vtext_color=GENTOO_PURPLE,
	ecolor=GENTOO_PURPLE,
	eorder=1,
	):
	try:
		v2_index = vertices[cp]
	except KeyError:
		v2 = g.add_vertex()
		g.vp.vlabel[v2] = cp
		g.vp.vcolor[v2] = vcolor
		g.vp.vtext_color[v2] = vtext_color
		vertices[cp] = g.vertex_index[v2]
	else:
		v2 = g.vertex(v2_index)
	if v1:
		e = g.add_edge(v1, v2)
		g.ep.egradient[e] = (1,)+ecolor
		g.ep.eorder[e] = eorder
	return vertices, v2

def get_cp_deps(cp, overlay_path, porttree, include_optional_deps=False):
	newest_cpv = cp+"-0_alpha_pre" #nothing should be earlier than this
	ceil_cpv = cp+"-9999" #ideally we would not want live packages
	for cpv in porttree.dbapi.cp_list(cp, mytree=overlay_path):
		if portage.pkgcmp(portage.pkgsplit(cpv), portage.pkgsplit(newest_cpv)) >= 0:
			if portage.pkgcmp(portage.pkgsplit(ceil_cpv), portage.pkgsplit(cpv)) > 0:
				newest_cpv = cpv
			elif newest_cpv == cp+"-0_alpha_pre":
				newest_cpv = cpv
	if newest_cpv != cp+"-0_alpha_pre":
		deps = porttree.dbapi.aux_get(newest_cpv, ["DEPEND","RDEPEND","PDEPEND"])
		deps = ' '.join(deps)
		if not include_optional_deps:
			# optional dep syntax looks like `gdm? ( gnome-base/gdm ) `
			deps = re.sub(r"\? \( .+? \)","",deps)
		# only keep first package from exactly-one-of lists
		deps = re.sub(r"\|\| \( (.+?) .+? \)",r"\1",deps)
		deps = deps.split(" ")
		deps = list(set(deps)) # de-duplicate
	else:
		print("WARNING: skipping "+newest_cpv)
		return False

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
			if deps[ix][:2] in [">=", "<=", "!<", "!>", "!="]:
				deps[ix] = deps[ix][2:]
			if deps[ix][:1] in [">", "<", "~", "="]:
				deps[ix] = deps[ix][1:]
			if deps[ix][-1:] in ["*"]:
				deps[ix] = deps[ix][:-1]
			if deps[ix][:2] in ["!!", "!~"]:
				deps[ix] = None
			elif deps[ix][:1] == "!":
				deps[ix] = None
	deps  = list(filter(None, deps))
	for ix in range(len(deps)):
		if portage.pkgsplit(deps[ix]) != None:
			deps[ix] = portage.pkgsplit(deps[ix])[0]

	return deps
