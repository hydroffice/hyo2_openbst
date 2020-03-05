import logging

from pathlib import Path

from hyo2.openbst.lib.openbst import OpenBST
from hyo2.abc.lib.testing_paths import TestingPaths

from hyo2.openbst.lib.processing.process_methods.area_correction import AreaCorrectionEnum
from hyo2.openbst.lib.processing.process_methods.calibration import CalibrationEnum
from hyo2.openbst.lib.processing.process_methods.geolocate import Geolocation
from hyo2.openbst.lib.processing.process_methods.interpolation import InterpEnum
from hyo2.openbst.lib.processing.process_methods.raytracing import RayTraceEnum
from hyo2.openbst.lib.processing.process_methods.raw_decoding import RawDecodeEnum
from hyo2.openbst.lib.processing.process_methods.source_level import SourceLevelEnum
from hyo2.openbst.lib.processing.process_methods.static_gain_compensation import StaticGainEnum
from hyo2.openbst.lib.processing.process_methods.transmission_loss import TransmissionLossEnum
from hyo2.openbst.lib.processing.process_methods.tvg import TVGENUM


logger = logging.getLogger(__name__)

testing = TestingPaths(root_folder=Path(__file__).parents[3].resolve())

bst = OpenBST(prj_name="test_fullrun", force_new=True).prj

## Add a raw file to the project ##
raw_path = testing.download_data_folder().joinpath('raw_reson', '20190730_144835.s7k')
bst.add_raw(raw_path)
bst.check_health()

## Run the various methods ##

# Interp
bst.parameters.interpolation.method_type = InterpEnum.simple_linear
bst.interpolation()

# Calculate Ray Path
bst.parameters.raytrace.method_type = RayTraceEnum.slant_range_approximation
bst.raytrace()

# Raw Decode
bst.parameters.rawdecode.method_type = RawDecodeEnum.perbeam_from_sonar_beam_average
bst.raw_decode()

# Remove Static Gain
bst.parameters.static_gains.method_type = StaticGainEnum.gain_removal
bst.static_gain_correction()

# Remove TVG
bst.parameters.tvg.method_type = TVGENUM.gain_removal_tvg_curve_from_manufacturer
bst.tvg_gain_correction()

# Remove Source level
bst.parameters.source_level.method_type = SourceLevelEnum.gain_removal
bst.source_level_correction()

# Apply a Calibration
cal_path = testing.download_data_folder().joinpath('calibration', 'chain_14m_200kHz.csv')
bst.process.auxiliary_files.add_calibration(path=cal_path)
bst.parameters.calibration.method_type = CalibrationEnum.calibration_file
bst.parameters.calibration.fit_curve = True
bst.parameters.calibration.curve_order = 4
bst.calibration()

# Transmission loss correction
bst.parameters.transmissionloss.method_type = TransmissionLossEnum.spherical
bst.transmission_loss_correction()

# Area correction
bst.parameters.area_correction.method_type = AreaCorrectionEnum.flat_seafloor
bst.area_correction()