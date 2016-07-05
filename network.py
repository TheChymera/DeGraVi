import portage
from gentoolkit.package import Package

def get_all_packages(overlay_path):
	"""Returns all packages from a given overlay path.
	Originally ftom https://gist.github.com/noisebleed/3194783
	"""
	packages = {}
	porttree = portage.db[portage.root]['porttree']
	vartree = portage.db[portage.root]['vartree']

	if overlay_path not in porttree.dbapi.porttrees:
		print('Overlay "{}" is not known to Portage.\n'.format(overlay_path) +
		'Please set it. Learn how at https://wiki.gentoo.org/wiki/Overlay')
		return False

	for cp in porttree.dbapi.cp_all(trees=[overlay_path]):
		for cpv in porttree.dbapi.cp_list(cp, mytree=[overlay_path]):
			packages[cpv] = Package(cpv)
		for cpv in vartree.dbapi.cp_list(cp):
			# Insert only a new entry if not overriding an existing one.
			packages.setdefault(cpv, Package(cpv))

	return packages

if __name__ == '__main__':
	packages = get_all_packages('/usr/local/portage/sci')
	# for i in packages:
	# 	if "nilearn" in i:
	# 		print i
	# 		print ">>>", packages[i]
