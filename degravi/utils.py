import re

import portage

#gentoo color scheme
GENTOO_PURPLE = (0.329,0.282,0.478,1)
GENTOO_PURPLE_A75 = (0.329,0.282,0.478,0.75)
GENTOO_PURPLE_A50 = (0.329,0.282,0.478,0.5)
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

def get_cp_deps(cp, overlay_path, porttree, matchnone=True, matchall=True):
	"""Get cp formatted deps for given cp.

	Parameters
	----------
	cp : str
	Category and package formatted according to the Portage cp syntax (category/package)

	overlay_path : str
	Path to the overlay in which to check for package versions

	porttree : porttree object
	Porttree object obtained via e.g. `porttree = portage.db[portage.root]['porttree']`

	matchnone : boolean , optional
	Whether to only match mandatory dependencies.

	matcall : boolean , optional
	Whether to match all mandatory dependencies.
	"""

	# This list always comes pre-sorted, should this no longer be the case at some point, it can be *explicitly* sorted via:
	# https://dev.gentoo.org/~zmedico/portage/doc/api/portage.dbapi.porttree.html#portage.dbapi.porttree.portdbapi._cpv_sort_ascending
	all_cpvs = porttree.dbapi.cp_list(cp, mytree=overlay_path)
	if len(all_cpvs) >= 1:
		# Ideally we avoid live (`*-9999`) packages if possible, they are in spite of appearances often poorly maintained.
		newest_cpv = all_cpvs[-1] if all_cpvs[0].endswith("-9999") else all_cpvs[0]
	elif len(all_cpvs) == 1:
		newest_cpv = all_cpvs[0]
	else:
		print(f"WARNING: Portage cannot find any versions for the `{cp}` package.")
		return False

	deps = porttree.dbapi.aux_get(newest_cpv, ["DEPEND","RDEPEND","PDEPEND"])
	deps = portage.dep.use_reduce(depstr=deps, matchnone=matchnone, matchall=matchall, flat=True)
	deps = ' '.join(deps)
	# only keep first package from exactly-one-of lists
	deps = re.sub(r"\|\| \( (.+?) .+? \)",r"\1",deps)
	deps = deps.split(" ")
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
			if deps[ix][:2] in [">=", "<="]:
				deps[ix] = deps[ix][2:]
			if deps[ix][:1] in [">", "<", "~", "="]:
				deps[ix] = deps[ix][1:]
			if deps[ix][-1:] in ["*"]:
				deps[ix] = deps[ix][:-1]
			if deps[ix][:2] in ["!!", "!~", "!<", "!>", "!="]:
				deps[ix] = None
			elif deps[ix][:1] == "!":
				deps[ix] = None
	deps  = list(filter(None, deps))
	for ix in range(len(deps)):
		if portage.pkgsplit(deps[ix]) != None:
			deps[ix] = portage.pkgsplit(deps[ix])[0]

	return deps

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
	extraneous_edge_order=1,
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
			if only_overlay:
				if dep in all_cp or dep in vertices:
					vertices, _ = add_vertex_and_edge(g, dep, vertices, v1,
						vcolor=overlay_color,
						vtext_color=overlay_text_color,
						ecolor=overlay_edge_color,
						eorder=overlay_edge_order,
						)
				else:
					break
			sets_property_values=[]
			sets_property_values.append([all_cp,[overlay_color,overlay_text_color,overlay_edge_color,overlay_edge_order]])
			sets_property_values.append([all_cp+deps,[extraneous_color,extraneous_text_color,extraneous_edge_color,extraneous_edge_order]])
			vcolor, vtext_color, ecolor, eorder = vertex_and_edge_appearance(dep, sets_property_values, g, v1)
			vertices, _ = add_vertex_and_edge(g, dep, vertices, v1, vcolor=vcolor, vtext_color=vtext_color, ecolor=ecolor, eorder=eorder)

	return g, vertices
