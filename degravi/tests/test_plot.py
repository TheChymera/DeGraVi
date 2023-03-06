import pytest
import os

from ..plot import package_deps

def test_package_deps(tmp_path):
	save_as=os.path.join(str(tmp_path),"{package_name}_mindeps.pdf")
	package_deps('dev-python/heudiconv', save_as=save_as)
