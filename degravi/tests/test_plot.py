import pytest

from ..plot import package_deps

def test_package_deps():
	package_deps('dev-python/heudiconv')
