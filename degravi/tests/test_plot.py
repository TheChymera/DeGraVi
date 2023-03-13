import pytest
import os

from ..plot import package_deps

def test_package_deps(tmp_path):
	save_as=os.path.join(str(tmp_path),"{package_name}_mindeps.pdf")
	package_deps('dev-python/heudiconv', save_as=save_as)

def test_set_deps(tmp_path):
	thisscriptspath = os.path.dirname(os.path.realpath(__file__))
	neurogentoo_file = os.path.join(thisscriptspath,"..","neurogentoo.txt")
	NEUROGENTOO = [line.strip() for line in open(neurogentoo_file, 'r')]
	save_as=os.path.join(str(tmp_path),"NEUROGENTOO_mindeps.pdf")
	package_deps(NEUROGENTOO, save_as=save_as)
