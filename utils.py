import re

import portage

def add_vertex_and_properties(g, cp, vcolor, vtext_color, ecolor,
	eorder=1,
	v1=False,
	):
	try:
		v2_index = vertices[dep]
	except KeyError:
		v2 = g.add_vertex()
		g.vp.vlabel[v2] = seed_cp
		g.vp.vcolor[v2] = vcolor
		g.vp.vtext_color[v2] = vtext_color
		vertices[dep] = g.vertex_index[v2]
		e = g.add_edge(v1, v2)
		g.ep.egradient[e] = (1,)+ecolor
		g.ep.eorder[e] = eorder
	else:
		v2 = g.vertex(v2_index)
		e = g.add_edge(v1, v2)
		g.ep.egradient[e] = (1,)+ecolor
		g.ep.eorder[e] = eorder

def get_cp_deps(cp, overlay_path, porttree, include_optional_deps=False):
	newest_cpv = cp+"-0_alpha_pre" #nothing should be earlier than this
	for cpv in porttree.dbapi.cp_list(cp, mytree=overlay_path):
		if portage.pkgcmp(portage.pkgsplit(cpv), portage.pkgsplit(newest_cpv)) >= 0:
			newest_cpv = cpv
	if newest_cpv != cp+"-0_alpha_pre":
		deps = porttree.dbapi.aux_get(newest_cpv, ["DEPEND","RDEPEND","PDEPEND"])
		deps = ' '.join(deps)
		if not include_optional_deps:
			# optional dep syntax looks like `gdm? ( gnome-base/gdm ) `
			deps = re.sub(r"\? \( .+? \)","",deps)
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

	return deps
