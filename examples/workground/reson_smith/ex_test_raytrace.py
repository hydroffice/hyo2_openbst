import logging
from pathlib import Path

from hyo2.abc.lib.logging import set_logging
from hyo2.abc.lib.testing_paths import TestingPaths
from hyo2.openbst.lib.openbst import OpenBST

from hyo2.openbst.lib.processing.process_methods.raytracing import RayTrace, RayTraceEnum


set_logging(ns_list=["hyo2.openbst", ])
logger = logging.getLogger(__name__)

# Set up project
testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())
bst = OpenBST(prj_name="test_raytrace", force_new=True).prj
# bst.open_project_folder()
raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

# Test 1 - Fail = interpolation requirement
bst.parameters.raytrace.method_type = RayTraceEnum.slant_range_approximation
bst.raytrace()


# Raw decode
bst.interpolation()

# Test 2 - Method:Simple, Pass = No Errors
bst.raytrace()