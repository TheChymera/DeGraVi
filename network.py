import portage
from gentoolkit.package import Package

def get_all_packages(overlay_path):
	"""Returns all packages from a given overlay path.
	Originally ftom https://gist.github.com/noisebleed/3194783
	"""
	packages = {}
	porttree = portage.db[portage.root]['porttree']

	if overlay_path not in porttree.dbapi.porttrees:
		print('Overlay "{}" is not known to Portage.\n'.format(overlay_path) +
		'Please set it. Learn how at https://wiki.gentoo.org/wiki/Overlay')
		return False

	for cp in porttree.dbapi.cp_all(trees=[overlay_path]):
		newest_cpv = portage.pkgsplit(cp+"-0")
		for cpv in porttree.dbapi.cp_list(cp, mytree=[overlay_path]):
			cpv_i = portage.pkgsplit(cpv)
			if portage.pkgcmp(cpv_i, newest_cpv) >= 0:
				newest_cpv = cpv_i
		deps = porttree.dbapi.aux_get(cpv, ["DEPEND","RDEPEND","PDEPEND"])
		deps = ' '.join(deps).split() # consolidate deps
		deps = list(set(deps)) # de-duplicate
		for ix, a in enumerate(deps):
			#these are not real atoms, mark for deletion
			if not "/" in a:
				deps[ix] = None
			#remove version indicators
			if a[:2] == ">=" or a[:2] == "<=":
				deps[ix] = a[2:]
		deps  = filter(None, deps)
		for ix, a in enumerate(deps):
			for delimiter in ["[",":"]:
				if delimiter in a:
					deps[ix] = a.split(delimiter)[0]
		for ix, a in enumerate(deps):
			if portage.pkgsplit(a) != None:
				deps[ix] = portage.pkgsplit(a)[0]
		cpv_dependencies = porttree.dbapi.aux_get(cpv, ["DEPEND"])[0].split(" ")
		packages[cp] = deps

	return packages

if __name__ == '__main__':
	packages = get_all_packages('/usr/local/portage/sci')
	for i in packages:
		if "nilearn" in i:
			print i
			print "DEPEND:"
			for a in packages[i]:
				print a
