import os

from graph import dependency_graph, tree_graph
from plotting import circular_depgraph
from utils import GENTOO_PURPLE, GENTOO_PURPLE_LIGHT, GENTOO_PURPLE_LIGHT2, GENTOO_PURPLE_GREY, GENTOO_GREEN

#relative paths
thisscriptspath = os.path.dirname(os.path.realpath(__file__))
neurogentoo_file = os.path.join(thisscriptspath,"neurogentoo.txt")
NEUROGENTOO = [line.strip() for line in open(neurogentoo_file, 'r')]

def neurogentoo_graph():
	g = dependency_graph(['/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_LIGHT],
		overlay_text_colors=[GENTOO_PURPLE],
		extraneous_colors=[GENTOO_PURPLE_GREY],
		extraneous_text_colors=[GENTOO_PURPLE_GREY],
		extraneous_edge_colors=[GENTOO_PURPLE],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		textcolor=GENTOO_PURPLE,
		only_overlay=False,
		)
	circular_depgraph(g,
	save_as="~/ng.pdf"
	)
def neurogentoo_full_graph():
	g = dependency_graph(['/usr/portage','/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE_LIGHT],
		overlay_text_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE],
		overlay_edge_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE_LIGHT],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		textcolor=GENTOO_PURPLE,
		)
	circular_depgraph(g,
	save_as="~/lg.pdf"
	)

def dep_tree():
	g = tree_graph(['/usr/portage'], NEUROGENTOO, highlight_overlays=["/usr/local/portage/neurogentoo"],
		seed_color=GENTOO_GREEN,
		seed_text_color=GENTOO_GREEN,
		seed_edge_color=GENTOO_GREEN,
		highlight_color=GENTOO_PURPLE_LIGHT2,
		highlight_text_color=GENTOO_PURPLE,
		highlight_edge_color=GENTOO_PURPLE_LIGHT2,
		base_color=GENTOO_PURPLE_LIGHT2,
		base_text_color=GENTOO_PURPLE,
		base_edge_color=GENTOO_PURPLE_LIGHT2,
		)
	circular_depgraph(g,
	save_as="~/tg.pdf"
	)

if __name__ == '__main__':
	neurogentoo_graph()
	# neurogentoo_full_graph()
	dep_tree()
