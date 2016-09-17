import os

from graph import dependency_graph
from plotting import draw_depgraph

#relative paths
thisscriptspath = os.path.dirname(os.path.realpath(__file__))
neurogentoo_file = os.path.join(thisscriptspath,"neurogentoo.txt")
NEUROGENTOO = [line.strip() for line in open(neurogentoo_file, 'r')]

#gentoo color scheme
GENTOO_PURPLE = (0.329,0.282,0.478,1)
GENTOO_PURPLE_LIGHT = (0.38,0.325,0.553,1)
GENTOO_PURPLE_LIGHT2 = (0.432,0.337,0.686,1)
GENTOO_PURPLE_GREY = (0.867,0.855,0.925,1)
GENTOO_GREEN = (0.451,0.824,0.086,1)

def neurogentoo_graph():
	g = dependency_graph(['/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_LIGHT],
		overlay_text_colors=[GENTOO_PURPLE],
		extraneous_colors=[GENTOO_PURPLE_GREY],
		extraneous_text_colors=[GENTOO_PURPLE],
		extraneous_edge_colors=[GENTOO_PURPLE_GREY],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		textcolor=GENTOO_PURPLE,
		only_overlay=False,
		)
	draw_depgraph(g,
	save_as="~/g.pdf"
	)
def neurogentoo_full_graph():
	g = dependency_graph(['/usr/portage','/usr/local/portage/neurogentoo'],
		overlay_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE_LIGHT],
		overlay_text_colors=[GENTOO_PURPLE_LIGHT,GENTOO_PURPLE_LIGHT],
		overlay_edge_colors=[GENTOO_PURPLE_GREY,GENTOO_PURPLE_LIGHT],
		highlight=NEUROGENTOO,
		highlight_color=GENTOO_GREEN,
		textcolor=GENTOO_PURPLE,
		)
	draw_depgraph(g,
	save_as="~/g.svg"
	)

if __name__ == '__main__':
	neurogentoo_full_graph()
	# neurogentoo_graph()
