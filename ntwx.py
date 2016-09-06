import portage
import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy
from gentoolkit.package import Package
from networkx.drawing.nx_agraph import graphviz_layout, pygraphviz_layout


def get_all_packages(overlay_paths):
	"""Returns all packages from a given overlay path.
	Originally ftom https://gist.github.com/noisebleed/3194783
	"""
	packages = {}
	porttree = portage.db[portage.root]['porttree']

	for overlay_path in overlay_paths:
		if overlay_path not in porttree.dbapi.porttrees:
			print('Overlay "{}" is not known to Portage.\n'.format(overlay_path) +
			'Please set it. Learn how at https://wiki.gentoo.org/wiki/Overlay')
			return False

	for cp in porttree.dbapi.cp_all(trees=overlay_paths):
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
		packages[cp] = deps


	G = nx.Graph(packages)

	options = {
		'with_labels': False,
		'node_color': 'red',
		'node_size': 5,
		'linewidths': 0,
		'width': 0.5,
	}


	plt.figure(figsize=(14,14), tight_layout=True)
	plt.axis('equal')
	# print(packages["sci-mathematics/yoricks"])
	# nx.draw_shell(G, nlist=[range(0,10), range(10,1000)], **options)
	# nx.draw(G, shell_layout(G, nlist=[range(0,10), range(10,2000)]), **options)
	# nx.draw_spring(G, iterations=500000, **options)

	# pos=pygraphviz_layout(G,prog='neato',args='')
	# pos=nx.spring_layout(G,dim=3,iterations=10000)
	pos=nx.spring_layout(G,k=0.05,iterations=1000)
	nx.draw(G, pos, **options)

	plt.show()

	return G

if __name__ == '__main__':
	# packages = get_all_packages('/usr/portage')
	packages = get_all_packages(['/usr/local/portage/sci'])
	# packages = get_all_packages(['/usr/local/portage/sci','/usr/portage'])
