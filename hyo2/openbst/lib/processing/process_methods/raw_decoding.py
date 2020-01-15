import logging
import numpy as np
from typing import Optional

from enum import Enum
from netCDF4 import Dataset, Group

from hyo2.openbst.lib.nc_helper import NetCDFHelper

logger = logging.getLogger(__name__)


# ## Raw Decode Enum and Dictionaries ##
class RawDecodeEnum(Enum):
    perbeam_from_snippets_using_median = 0
    perbeam_from_snippets_using_mean = 1
    perbeam_from_sonar_beam_average = 2


raw_decode_title = {
    RawDecodeEnum.perbeam_from_snippets_using_median: "Raw decoded backscatter - from snippets using median ",
    RawDecodeEnum.perbeam_from_snippets_using_mean: "Raw decoded backscatter - from snippets using mean",
    RawDecodeEnum.perbeam_from_sonar_beam_average: "Raw decoded backscatter - Sonar provided beam averages"
}


# ## Raw Decode Parameter Object ##
class RawDecodeParameters:
    process_name = "raw_decoding"

    def __init__(self):

        self.method_type = RawDecodeEnum.perbeam_from_snippets_using_mean
        self.use_window = False
        self.sample_window_size = 5

    def nc_write_parameters(self, grp_process: Group):
        try:
            grp_process.title = raw_decode_title[self.method_type]
            grp_process.method_type = self.method_type.name
            grp_process.use_window = str(self.use_window)
            grp_process.sample_window_size = self.sample_window_size
            return True
        except TypeError:
            return False

    def process_identifiers(self) -> list:
        process_string = RawDecodeParameters.process_name
        parameter_string = str()
        for key, value in self.__dict__.items():
            parameter_string = parameter_string + key + str(value)
        parameter_hash = NetCDFHelper.hash_string(input_str=parameter_string)
        process_ids = [process_string, parameter_hash]
        return process_ids


# ## Raw Decode Class and methods ##
class RawDecoding:

    def __init__(self):
        pass

    @classmethod
    def decode(cls, ds_raw: Dataset, parameters: RawDecodeParameters) -> dict:
        p_method_type = parameters.method_type
        p_use_window = parameters.use_window
        p_sample_window_size = parameters.sample_window_size

        grp_snippets = ds_raw.groups['snippets']
        var_snippets = grp_snippets.variables['snippets']
        data_snippets = var_snippets[:]
        data_beam_mask = ~data_snippets.mask[:, :, 0]

        if p_method_type is RawDecodeEnum.perbeam_from_snippets_using_mean:
            if p_use_window is False:
                bs_raw_decode = cls.perbeam_bs_from_snippits_using_mean(snippet_samples=data_snippets,
                                                                        beam_mask=data_beam_mask,
                                                                        use_window=False)
            else:
                var_detection_sample = grp_snippets.variables['detect_sample']
                data_dection_samples = var_detection_sample[:]
                var_snippets_start_sample = grp_snippets.variables['snippet_start_sample']
                data_snippets_start_sample = var_snippets_start_sample[:]
                var_snippets_end_sample = grp_snippets.variables['snippet_end_sample']
                data_snippets_end_sample = var_snippets_end_sample

                bs_raw_decode = cls.perbeam_bs_from_snippits_using_mean(snippet_samples=data_snippets,
                                                                        beam_mask=data_beam_mask,
                                                                        ping_detect_samples=data_dection_samples,
                                                                        ping_snippet_start=data_snippets_start_sample,
                                                                        ping_snippet_end=data_snippets_end_sample,
                                                                        use_window=p_use_window,
                                                                        window_size=p_sample_window_size)

        elif p_method_type is RawDecodeEnum.perbeam_from_snippets_using_median:
            if p_use_window is False:
                bs_raw_decode = cls.perbeam_bs_from_snippets_using_median(snippet_samples=data_snippets,
                                                                          beam_mask=data_beam_mask,
                                                                          use_window=False)
            else:
                var_detection_sample = grp_snippets.variables['detect_sample']
                data_dection_samples = var_detection_sample[:]
                var_snippets_start_sample = grp_snippets.variables['snippet_start_sample']
                data_snippets_start_sample = var_snippets_start_sample[:]
                var_snippets_end_sample = grp_snippets.variables['snippet_end_sample']
                data_snippets_end_sample = var_snippets_end_sample

                bs_raw_decode = cls.perbeam_bs_from_snippets_using_median(snippet_samples=data_snippets,
                                                                          beam_mask=data_beam_mask,
                                                                          ping_detect_samples=data_dection_samples,
                                                                          ping_snippet_start=data_snippets_start_sample,
                                                                          ping_snippet_end=data_snippets_end_sample,
                                                                          use_window=p_use_window,
                                                                          window_size=p_sample_window_size)

        elif p_method_type is RawDecodeEnum.perbeam_from_sonar_beam_average:
            grp_raw_bathy = ds_raw.groups['raw_bathymetry_data']
            bs_raw_decode = RawDecoding.perbeam_bs_from_beam_average(raw_bathy=grp_raw_bathy)

        else:
            raise TypeError("Unrecognized Raw Decode Method: %s")  # TODO: Fix the error message

        data_out = {
            'backscatter_data': bs_raw_decode
        }
        return data_out

    @classmethod
    def write_data_to_nc(cls, data_dict: dict, grp_process: Group):
        try:
            for data_name, data in data_dict.items():
                if data_name == 'backscatter_data':
                    grp_process.createDimension(dimname='ping', size=None)
                    grp_process.createDimension(dimname='beam', size=None)
                    var_bs_data = grp_process.createVariable(varname='backscatter_data',
                                                             datatype='f8',
                                                             dimensions=('ping', 'beam'))
                    var_bs_data[:] = data

            return True
        except RuntimeError:
            return False

    # # Processing Method Types #
    @classmethod
    def perbeam_bs_from_snippets_using_median(cls,
                                              snippet_samples: np.ma.MaskedArray,
                                              beam_mask: np.ma.MaskedArray,
                                              ping_detect_samples: Optional[np.ma.MaskedArray] = None,
                                              ping_snippet_start: Optional[np.ma.MaskedArray] = None,
                                              ping_snippet_end: Optional[np.ma.MaskedArray] = None,
                                              use_window: bool = False, window_size: int = 5) -> np.ndarray:
        if use_window is False:
            perbeam_bs = 20 * np.ma.log10(np.ma.median(snippet_samples, axis=2))
        elif use_window is True:
            # Check that all needed data is present and set up the window
            window_start_id, window_end_id = RawDecoding.setup_window(window_size=window_size,
                                                                      detect_samples=ping_detect_samples,
                                                                      snippet_start_samples=ping_snippet_start,
                                                                      snippet_end_samples=ping_snippet_end)

            num_pings = snippet_samples.shape[0]
            num_beams = snippet_samples.shape[1]

            perbeam_bs = np.ones(shape=(num_pings, num_beams,)) * np.nan
            for ping in range(num_pings):
                for beam in range(num_beams):
                    if beam_mask[ping, beam]:
                        samples = snippet_samples[ping, beam, :]
                        detection_sample_index = ping_detect_samples[ping, beam] - ping_snippet_start[ping, beam]
                        end_sample_index = ping_snippet_end[ping, beam] - ping_snippet_start[ping, beam]
                        number_of_snippets = end_sample_index + 1

                        if number_of_snippets <= window_size:
                            perbeam_bs = np.ma.mean(samples)
                        else:
                            start_index = int(detection_sample_index - window_start_id)
                            end_index = int(detection_sample_index + window_end_id)

                            if start_index < 0:
                                start_index = 0
                            if end_index > end_sample_index:
                                end_index = int(end_sample_index)

                            perbeam_bs[ping, beam] = np.median(samples[start_index:end_index + 1])
            perbeam_bs = 20 * np.log10(perbeam_bs)
        else:
            raise TypeError("'use_window' must be of type 'bool': %s" % type(use_window))

        return perbeam_bs

    @classmethod
    def perbeam_bs_from_snippits_using_mean(cls,
                                            snippet_samples: np.ma.MaskedArray,
                                            beam_mask: np.ma.MaskedArray,
                                            ping_detect_samples: Optional[np.ma.MaskedArray] = None,
                                            ping_snippet_start: Optional[np.ma.MaskedArray] = None,
                                            ping_snippet_end: Optional[np.ma.MaskedArray] = None,
                                            use_window: bool = False, window_size: int = 5) -> np.ndarray:
        if use_window is False:
            perbeam_bs = 20 * np.ma.log10(np.ma.mean(snippet_samples, axis=2))
        elif use_window is True:
            # Check that all needed data is present and set up the window
            window_start_id, window_end_id = RawDecoding.setup_window(window_size=window_size,
                                                                      detect_samples=ping_detect_samples,
                                                                      snippet_start_samples=ping_snippet_start,
                                                                      snippet_end_samples=ping_snippet_end)

            num_pings = snippet_samples.shape[0]
            num_beams = snippet_samples.shape[1]

            perbeam_bs = np.ones(shape=(num_pings, num_beams,)) * np.nan
            for ping in range(num_pings):
                for beam in range(num_beams):
                    if beam_mask[ping, beam]:
                        samples = snippet_samples[ping, beam, :]
                        detection_sample_index = ping_detect_samples[ping, beam] - ping_snippet_start[ping, beam]
                        end_sample_index = ping_snippet_end[ping, beam] - ping_snippet_start[ping, beam]
                        number_of_snippets = end_sample_index + 1

                        if number_of_snippets <= window_size:
                            perbeam_bs = np.ma.mean(samples)
                        else:
                            start_index = int(detection_sample_index - window_start_id)
                            end_index = int(detection_sample_index + window_end_id)

                            if start_index < 0:
                                start_index = 0
                            if end_index > end_sample_index:
                                end_index = int(end_sample_index)

                            perbeam_bs[ping, beam] = np.mean(samples[start_index:end_index + 1])
            perbeam_bs = 20 * np.log10(perbeam_bs)

        else:
            raise TypeError("'use_window' must be of type 'bool': %s" % type(use_window))

        return perbeam_bs

    @classmethod
    def perbeam_bs_from_beam_average(cls, raw_bathy: Group) -> np.ndarray:
        var_bs_beam_averages = raw_bathy.variables['bs_beam_average']
        perbeam_bs = var_bs_beam_averages[:]
        return 20 * np.ma.log10(perbeam_bs)

    @staticmethod
    def setup_window(window_size: int, detect_samples: Optional[np.ma.MaskedArray],
                     snippet_start_samples: Optional[np.ma.MaskedArray],
                     snippet_end_samples: Optional[np.ma.MaskedArray]):

        # Check that all needed data is present
        data_list = [snippet_start_samples, snippet_end_samples, detect_samples]
        missing_data = list()
        for data in data_list:
            if data is None:
                missing_data.append(True)

        if any(missing_data) is True:
            error_string = "Parameters indicate use_window=True, but required data is missing.:"
            raise RuntimeError(error_string)

        # Determine how many samples to grab around the center detection
        if window_size & 1:  # Odd
            start_index_identifier = (window_size - 1) / 2
            end_index_identifier = (window_size - 1) / 2
        else:  # Even
            start_index_identifier = window_size / 2
            end_index_identifier = window_size / 2 - 1
        return start_index_identifier, end_index_identifier
