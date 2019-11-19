import logging

from netCDF4 import Dataset, Group, Variable
import numpy as np
from ogr import osr

from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.raw.parsers.reson.dg_formats import ResonDatagrams
from hyo2.openbst.lib.raw.parsers.reson.reader import Reson

logger = logging.getLogger(__name__)


class RawImport:
    
    def __init__(self):
        pass

    @classmethod
    def import_raw(cls, raw: Reson, ds: Dataset):
        try:
            imported = RawImport.get_runtime_settings(raw=raw, ds=ds)
            imported = RawImport.get_raw_bathy(raw=raw, ds=ds)
            imported = RawImport.get_beam_geo(raw=raw, ds=ds)
            importted = RawImport.get_tvg(raw=raw, ds=ds)
            importted = RawImport.get_attitude(raw=raw, ds=ds)
            importted = RawImport.get_position(raw=raw, ds=ds)

        except RuntimeError:
            return False

    @classmethod
    def get_position(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()
        lat = list()
        lon = list()

        position = raw.get_datagram(dg_type=ResonDatagrams.POSITION)
        times = [dg_pos.time for dg_pos in position]
        for dg_pos in position:
            if dg_pos.datum is "WGS":
                lat.append(dg_pos.latitude * (180 / np.pi))
                lon.append(dg_pos.longitude * (180 / np.pi))
            else:
                raise AttributeError("unrecognized datum: %s" % dg_pos.datum)

        grp_pos = ds.createGroup("position")
        grp_pos.createDimension(dimname="time", size=None)
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(4326)
        grp_pos.spatial_ref = str(spatial_reference)

        var_time = grp_pos.createVariable(varname="time", datatype="f8", dimensions=("time",))
        var_time[:] = times
        var_lat = grp_pos.createVariable(varname="latitude", datatype="f8", dimensions=("time",))
        var_lat[:] = lat
        var_lon = grp_pos.createVariable(varname="longitude", datatype="f8", dimensions=("time",))
        var_lon[:] = lon

        NetCDFHelper.update_modified(ds=ds)
        return True
        # TODO: Write spatial reference check and formatter

    @classmethod
    def get_attitude(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()

        attitude = raw.get_datagram(dg_type=ResonDatagrams.ROLLPITCHHEAVE)
        times_rph = [dg_att.time for dg_att in attitude]
        roll = np.rad2deg([dg_att.roll for dg_att in attitude])
        pitch = np.rad2deg([dg_att.pitch for dg_att in attitude])
        heave = np.rad2deg([dg_att.heave for dg_att in attitude])

        heading = raw.get_datagram(dg_type=ResonDatagrams.HEADING)
        times_head = [dg_head.time for dg_head in heading]
        head = np.rad2deg([dg_head.heading for dg_head in heading])

        grp_attitude = ds.createGroup("attitude")
        grp_attitude.units = "arc-degree"
        grp_attitude.createDimension(dimname="time", size=None)

        var_time = grp_attitude.createVariable(varname="time", datatype="f8", dimensions=("time",))
        var_time[:] = times_rph
        var_roll = grp_attitude.createVariable(varname="roll", datatype="f8", dimensions=("time",))
        var_roll[:] = roll
        var_pitch = grp_attitude.createVariable(varname="pitch", datatype="f8", dimensions=("time",))
        var_pitch[:] = pitch
        var_heave = grp_attitude.createVariable(varname="heave", datatype="f8", dimensions=("time",))
        var_heave[:] = heave
        if times_head is not None:
            var_times_head = grp_attitude.createVariable(varname="heading_time", datatype="f8", dimensions=("time",))
            var_times_head[:] = times_head
        var_heading = grp_attitude.createVariable(varname="heading", datatype="f8", dimensions=("time",))
        var_heading[:] = head

        NetCDFHelper.update_modified(ds=ds)
        return True

    @classmethod
    def get_tvg(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()

        tvg = raw.get_datagram(dg_type=ResonDatagrams.TVG)
        times_tvg = [dg_tvg.time for dg_tvg in tvg]

        grp_tvg = ds.createGroup("time_varying_gain")
        grp_tvg.createDimension(dimname="ping", size=None)

        var_time = grp_tvg.createVariable(varname="time", datatype="f8", dimensions=("ping",))
        var_time[:] = times_tvg
        vlen_tvg = grp_tvg.createVLType(datatype="f4", datatype_name="tvg_variable_length")
        var_tvg = grp_tvg.createVariable(varname="tvg", datatype=vlen_tvg, dimensions=("ping",))
        for n in range(len(tvg)):
            tvg_curve = np.asarray(tvg[n].tvg_curve, dtype="f4")
            var_tvg[n] = tvg_curve

        NetCDFHelper.update_modified(ds=ds)
        return True

    @classmethod
    def get_beam_geo(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()

        beam_geo = raw.get_datagram(dg_type=ResonDatagrams.BEAMGEO)
        num_beams = beam_geo[0].num_rx_beams
        beam_angle_along = np.empty(shape=(len(beam_geo), num_beams))
        beam_angle_across = np.empty(shape=(len(beam_geo), num_beams))
        beam_width_along = np.empty(shape=(len(beam_geo), num_beams))
        beam_width_across = np.empty(shape=(len(beam_geo), num_beams))
        times_beam_geo = [dg_beam_geo.time for dg_beam_geo in beam_geo]

        for index, dg_beam_geo in enumerate(beam_geo):
            if dg_beam_geo.num_rx_beams != num_beams:
                return False
            beam_angle_along[index, :] = np.rad2deg(dg_beam_geo.rx_angle_vertical)
            beam_angle_across[index, :] = np.rad2deg(dg_beam_geo.rx_angle_horizontal)
            beam_width_along[index, :] = np.rad2deg(dg_beam_geo.rx_beam_width_along)
            beam_width_across[index, :] = np.rad2deg(dg_beam_geo.rx_beam_width_across)

        grp_beam_geo = ds.createGroup("beam_geometry")
        grp_beam_geo.createDimension(dimname="ping", size=None)
        grp_beam_geo.createDimension(dimname="beam_number", size=num_beams)

        var_time = grp_beam_geo.createVariable(varname="time", datatype="f8", dimensions=("ping",))
        var_time[:] = times_beam_geo

        var_beam_number = grp_beam_geo.createVariable(varname="beam_number", datatype="i4", dimensions=("beam_number",))
        var_beam_number[:] = [range(num_beams)]

        var_beam_angle_along = \
            grp_beam_geo.createVariable(varname="beam_along_angle", datatype="f4", dimensions=("ping", "beam_number"))
        var_beam_angle_along[:] = beam_angle_along

        var_beam_angle_across = \
            grp_beam_geo.createVariable(varname="beam_across_angle", datatype="f4", dimensions=("ping", "beam_number"))
        var_beam_angle_across[:] = beam_angle_across

        var_beam_width_along = \
            grp_beam_geo.createVariable(varname="along_beamwdith", datatype="f4", dimensions=("ping", "beam_number"))
        var_beam_width_along[:] = beam_width_along

        var_beam_width_across = \
            grp_beam_geo.createVariable(varname="across_beamwidth", datatype="f4", dimensions=("ping", "beam_number"))
        var_beam_width_across[:] = beam_width_across

        NetCDFHelper.update_modified(ds=ds)
        return True


    @classmethod
    def get_raw_bathy(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()
        fill_value = -999

        raw_bathy = raw.get_datagram(dg_type=ResonDatagrams.RAWDETECTDATA)
        times_bathy = [dg_raw_bathy.time for dg_raw_bathy in raw_bathy]
        samp_rate = [dg_raw_bathy.sample_rate for dg_raw_bathy in raw_bathy]
        tx_steering = [dg_raw_bathy.tx_steering_angle for dg_raw_bathy in raw_bathy]
        rx_steering = [dg_raw_bathy.rx_steering_angle for dg_raw_bathy in raw_bathy]

        num_beams = 512
        num_pings = len(raw_bathy)
        detect_point = np.ones(shape=(num_pings, num_beams)) * fill_value
        rx_angle = np.ones(shape=(num_pings, num_beams)) * fill_value
        quality = np.ones(shape=(num_pings, num_beams)) * fill_value
        bs_beam_average = np.ones(shape=(num_pings, num_beams)) * fill_value
        bs_beam_min_gate = np.ones(shape=(num_pings, num_beams)) * fill_value
        bs_beam_max_gate = np.ones(shape=(num_pings, num_beams)) * fill_value

        for index, dg_raw_bathy in enumerate(raw_bathy):
            beam_num = dg_raw_bathy.beam
            detect_point[index, beam_num] = dg_raw_bathy.detect_point
            rx_angle[index, beam_num] = dg_raw_bathy.rx_angle
            quality[index, beam_num] = dg_raw_bathy.quality_flag
            bs_beam_average[index, beam_num] = dg_raw_bathy.signal_strength
            bs_beam_min_gate[index, beam_num] = dg_raw_bathy.min_limit
            bs_beam_max_gate[index, beam_num] = dg_raw_bathy.max_limit

        grp_bathy = ds.createGroup("raw_bathymetry_data")
        grp_bathy.createDimension(dimname="ping", size=None)
        grp_bathy.createDimension(dimname="beam_number", size=num_beams)

        var_time = grp_bathy.createVariable(varname="time",
                                            datatype="f8",
                                            dimensions=("ping",),
                                            fill_value=fill_value)
        var_time[:] = times_bathy

        var_beam_number = grp_bathy.createVariable(varname="beam_number",
                                                   datatype="i4",
                                                   dimensions=("beam_number",),
                                                   fill_value=fill_value)
        var_beam_number[:] = [range(num_beams)]

        var_samp_rate = grp_bathy.createVariable(varname="sample_rate",
                                                 datatype="f8",
                                                 dimensions=("ping",),
                                                 fill_value=fill_value)
        var_samp_rate[:] = samp_rate

        var_tx_steering = grp_bathy.createVariable(varname="tx_steering",
                                                   datatype="f8",
                                                   dimensions=("ping",),
                                                   fill_value=fill_value)
        var_tx_steering[:] = tx_steering

        var_rx_steering = grp_bathy.createVariable(varname="rx_steering",
                                                   datatype="f8",
                                                   dimensions=("ping",),
                                                   fill_value=fill_value)
        var_rx_steering[:] = rx_steering

        var_detect_point = grp_bathy.createVariable(varname="detect_point",
                                                    datatype="f8",
                                                    dimensions=("ping", "beam_number"),
                                                    fill_value=fill_value)
        var_detect_point[:] = detect_point
        var_rx_angle = grp_bathy.createVariable(varname="rx_angle",
                                                datatype="f8",
                                                dimensions=("ping", "beam_number"),
                                                fill_value=fill_value)
        var_rx_angle[:] = detect_point

        var_quality = grp_bathy.createVariable(varname="quality",
                                               datatype="f8",
                                               dimensions=("ping", "beam_number"),
                                               fill_value=fill_value)
        var_quality[:] = quality

        var_beam_average = grp_bathy.createVariable(varname="bs_beam_average",
                                                    datatype="f8",
                                                    dimensions=("ping", "beam_number"),
                                                    fill_value=fill_value)
        var_beam_average[:] = bs_beam_average

        var_min_gate = grp_bathy.createVariable(varname="min_sample_gate",
                                                datatype="f8",
                                                dimensions=("ping", "beam_number"),
                                                fill_value=fill_value)
        var_min_gate[:] = bs_beam_min_gate

        var_max_gate = grp_bathy.createVariable(varname="max sample gate",
                                                datatype="f8",
                                                dimensions=("ping", "beam_number"),
                                                fill_value=fill_value)
        var_max_gate[:] = bs_beam_max_gate

        NetCDFHelper.update_modified(ds=ds)
        return True

    @classmethod
    def get_runtime_settings(cls, raw: Reson, ds: Dataset):
        raw.is_mapped()

        runtime = raw.get_datagram(dg_type=ResonDatagrams.SONARSETTINGS)
        times_runtime = [dg_runtime.time for dg_runtime in runtime]
        frequency = [dg_runtime.frequency for dg_runtime in runtime]
        sample_rate = [dg_runtime.sample_rate for dg_runtime in runtime]
        rx_band_width = [dg_runtime.rx_band_width for dg_runtime in runtime]
        tx_pulse_width = [dg_runtime.tx_pulse_width for dg_runtime in runtime]
        tx_wave_form = [dg_runtime.tx_wave_form for dg_runtime in runtime]
        source_level = [dg_runtime.power_select for dg_runtime in runtime]
        static_gain = [dg_runtime.gain_select for dg_runtime in runtime]
        tx_along_steering = [np.rad2deg(dg_runtime.tx_beam_steering_vertical) for dg_runtime in runtime]
        tx_across_steering = [np.rad2deg(dg_runtime.tx_beam_steering_horizontal) for dg_runtime in runtime]
        tx_along_beam_width = [np.rad2deg(dg_runtime.tx_beam_width_vertical) for dg_runtime in runtime]
        tx_across_beam_width = [np.rad2deg(dg_runtime.tx_beam_width_horizontal) for dg_runtime in runtime]
        tx_focus = [dg_runtime.tx_focus for dg_runtime in runtime]
        stabilization_roll = [int(dg_runtime.stabilization_roll) for dg_runtime in runtime]
        stabilization_pitch = [int(dg_runtime.stabilization_pitch) for dg_runtime in runtime]
        stabilization_yaw = [int(dg_runtime.stabilization_yaw) for dg_runtime in runtime]
        rx_beam_width = [np.rad2deg(dg_runtime.rx_beam_width) for dg_runtime in runtime]
        absorption_gain = [dg_runtime.absorption for dg_runtime in runtime]
        sound_velocity = [dg_runtime.sound_velocity for dg_runtime in runtime]
        spreading_gain = [dg_runtime.spreading for dg_runtime in runtime]

        grp_runtime = ds.createGroup("runtime_settings")
        grp_runtime.createDimension(dimname="ping", size=None)

        var_time = grp_runtime.createVariable(varname="time", datatype="f8", dimensions=("ping",))
        var_time[:] = times_runtime

        var_frequency = grp_runtime.createVariable(varname="frequency", datatype="f8", dimensions=("ping",))
        var_frequency[:] = frequency

        var_sample_rate = grp_runtime.createVariable(varname="sample_rate", datatype="f8", dimensions=("ping",))
        var_sample_rate[:] = sample_rate

        var_rx_band_width = grp_runtime.createVariable(varname="rx_band_width", datatype="f8", dimensions=("ping",))
        var_rx_band_width[:] = rx_band_width

        var_tx_pulse_width = grp_runtime.createVariable(varname="tx_pulse_width", datatype="f8", dimensions=("ping",))
        var_tx_pulse_width[:] = tx_pulse_width

        var_tx_wave_form = grp_runtime.createVariable(varname="tx_wave_form", datatype="S1", dimensions=("ping",))
        var_tx_wave_form[:] = tx_wave_form

        var_source_level = grp_runtime.createVariable(varname="source_level", datatype="f8", dimensions=("ping",))
        var_source_level[:] = source_level

        var_static_gain = grp_runtime.createVariable(varname="static_gain", datatype="f8", dimensions=("ping",))
        var_static_gain[:] = static_gain

        var_tx_along_steering = grp_runtime.createVariable(varname="tx_along_steering",
                                                           datatype="f8",
                                                           dimensions=("ping",))
        var_tx_along_steering[:] = tx_along_steering

        var_tx_across_steering = grp_runtime.createVariable(varname="tx_across_steering",
                                                            datatype="f8",
                                                            dimensions=("ping",))
        var_tx_across_steering[:] = tx_across_steering

        var_along_beam_width = grp_runtime.createVariable(varname="tx_along_beam_width",
                                                          datatype="f8",
                                                          dimensions=("ping",))
        var_along_beam_width[:] = tx_along_beam_width

        var_tx_across_beam_width = grp_runtime.createVariable(varname="tx_across_beam_width",
                                                              datatype="f8",
                                                              dimensions=("ping",))
        var_tx_across_beam_width[:] = tx_across_beam_width

        var_focus = grp_runtime.createVariable(varname="focus", datatype="f8", dimensions=("ping",))
        var_focus[:] = tx_focus

        var_stab_roll = grp_runtime.createVariable(varname="roll_stabilization", datatype="i4", dimensions=("ping",))
        var_stab_roll[:] = stabilization_roll

        var_stab_pitch = grp_runtime.createVariable(varname="pitch_stabilization", datatype="i4", dimensions=("ping",))
        var_stab_pitch[:] = stabilization_pitch

        var_stab_yaw = grp_runtime.createVariable(varname="yaw_stabilization", datatype="i4", dimensions=("ping",))
        var_stab_yaw[:] = stabilization_yaw

        var_rx_beam_width = grp_runtime.createVariable(varname="rx_beam_width", datatype="f8", dimensions=("ping",))
        var_rx_beam_width[:] = rx_beam_width

        var_absorp = grp_runtime.createVariable(varname="absorption_gain", datatype="f8", dimensions=("ping",))
        var_absorp[:] = absorption_gain

        var_sound_velocity = grp_runtime.createVariable(varname="sound_velocity", datatype="f8", dimensions=("ping",))
        var_sound_velocity[:] = sound_velocity

        var_spreading_gain = grp_runtime.createVariable(varname="spreading_gain", datatype="f8", dimensions=("ping",))
        var_spreading_gain[:] = spreading_gain

        NetCDFHelper.update_modified(ds=ds)
        return True
