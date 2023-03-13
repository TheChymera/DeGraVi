import os

from .generate_graph import repositories_graph, seeded_graph
from .plotting import circular_depgraph
from .utils import (
	GENTOO_PURPLE,
	GENTOO_PURPLE_A75,
	GENTOO_PURPLE_A50,
	GENTOO_PURPLE_LIGHT,
	GENTOO_PURPLE_LIGHT2,
	GENTOO_PURPLE_LIGHT2_A75,
	GENTOO_PURPLE_GREY,
	GENTOO_PURPLE_GREY_A75,
	GENTOO_PURPLE_GREY_A50,
	GENTOO_GREEN,
	GENTOO_GREEN_A75,
	)


def package_deps(cp, save_as='/tmp/{package_name}_mindeps.pdf'):
	"""
	Seeded graph for an arbitrary package, highlighting the science overlay.

	Parameters
	----------
	cp : str
		String containing the category and the package name, separated by a slash, e.g. `sci-biology/samri`.
	save_as : str, optional
		Path under which to save the dependency graph.
		If the string contains the substring `{package_name}`, this will be expanded to the package name given previously.
		The default value is `/tmp/{package_name}_mindeps.pdf`.


	Examples
	--------

	run e.g. `python -c "import examples; examples.one_sci_package('dev-python/heudiconv')"` from the shell.

	"""
	if isinstance(cp, str):
		package_name = cp.split("/")[1]
		cp = [cp]
	else:
		package_name = "PACKAGE_LIST"
	g = seeded_graph(['/var/db/repos/gentoo'], cp,
		highlight_overlays=["/home/chymera/src/sci"],
		use_match="none",
		seed_color=GENTOO_GREEN,
		seed_text_color=GENTOO_GREEN,
		seed_edge_color=GENTOO_GREEN_A75,
		highlight_color=GENTOO_PURPLE_LIGHT2,
		highlight_text_color=GENTOO_PURPLE,
		highlight_edge_color=GENTOO_PURPLE_LIGHT2_A75,
		base_color=GENTOO_PURPLE_GREY,
		base_text_color=GENTOO_PURPLE,
		base_edge_color=GENTOO_PURPLE_GREY_A50,
		)
	circular_depgraph(g,
		save_as=save_as.format(package_name=package_name)
		)
