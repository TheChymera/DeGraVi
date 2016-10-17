

import os

from generate_graph import repositories_graph, seeded_graph
from plotting import circular_depgraph
from utils import (
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

#relative paths
thisscriptspath = os.path.dirname(os.path.realpath(__file__))
neurogentoo_file = os.path.join(thisscriptspath,"neurogentoo.txt")
NEUROGENTOO = [line.strip() for line in open(neurogentoo_file, 'r')]

def gentoo_science():
	g = repositories_graph(['/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_LIGHT],
		overlay_text_colors=[GENTOO_PURPLE],
		overlay_edge_colors=[GENTOO_PURPLE_A50],
		extraneous_colors=[GENTOO_PURPLE_GREY],
		extraneous_text_colors=[GENTOO_PURPLE_GREY],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		highlight_edge_color=GENTOO_GREEN_A75,
		textcolor=GENTOO_PURPLE,
		only_overlay=False,
		)
	circular_depgraph(g,
		save_as="~/gentoo_science.pdf"
		)

def neuro_gentoo_science():
	g = repositories_graph(['/usr/portage','/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE_LIGHT2],
		overlay_text_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE],
		overlay_edge_colors=[GENTOO_PURPLE_GREY_A50,GENTOO_PURPLE_LIGHT2_A75],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		highlight_edge_color=GENTOO_GREEN_A75,
		textcolor=GENTOO_PURPLE,
		)
	circular_depgraph(g,
		save_as="~/neuro_gentoo_science.pdf"
		)

def neurogentoo_maxdeps():
	g = seeded_graph(['/usr/portage'], NEUROGENTOO,
		highlight_overlays=["/usr/local/portage/neurogentoo"],
		use_match="all",
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
		save_as="~/neurogentoo_maxdeps.pdf"
		)

def neurogentoo_mindeps():
	g = seeded_graph(['/usr/portage'], NEUROGENTOO,
		highlight_overlays=["/usr/local/portage/neurogentoo"],
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
		save_as="~/neurogentoo_mindeps.pdf"
		)

if __name__ == '__main__':
	neurogentoo_maxdeps()
	neurogentoo_mindeps()
	# neuro_gentoo_science()
	# gentoo_science()
