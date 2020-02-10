import logging

from netCDF4 import Dataset, Group, date2num
from pathlib import Path


from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.processing.auxilaries.ssp import SSP
logger = logging.getLogger(__name__)


class Auxiliary:
    ext = ".nc"

    def __init__(self, process_path: Path) -> None:
        self._ssp_name = "sound_speed_profiles"
        self._calibration_name = "calibration_files"
        self._path = process_path.joinpath("auxiliary.nc")
        self._nc()
        self._ds.close()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def ds(self) -> Dataset:
        self._nc()
        return self._ds

    @property
    def ssp_group(self) -> Group:
        return self.ds.groups[self._ssp_name]

    @property
    def ssp_profiles(self):
        return self.ssp_group.groups

    @property
    def ssp_list(self) -> list:
        ssp_list = list()
        for ssp_name, ssp in self.ssp_profiles.items():
            if ssp.deleted == 0:
                ssp_list.append(ssp_name)
        self._ds.close()
        return ssp_list

    @property
    def ssp_times(self) -> dict:
        pass

    @property
    def ssp_location(self) -> dict:
        pass

    @property
    def claibration_group(self) -> Group:
        return self.ds.groups[self._calibration_name]

    @property
    def calibration_files(self):
        return self.claibration_group.groups

    @property
    def calibration_list(self) -> list:
        calibration_list = list()
        for cal_name, cal in self.calibration_files.items():
            if cal.deleted == 0:
                calibration_list.append(cal_name)
        self._ds.close()
        return calibration_list

    def _nc(self) -> None:
        if self._path.exists():
            open_mode = 'a'
        else:
            open_mode = 'w'
        self._ds = Dataset(filename=self._path, mode=open_mode)
        NetCDFHelper.init(ds=self._ds)
        NetCDFHelper.groups(ds=self._ds, names=[self._ssp_name, self._calibration_name])

    # common project management methods #
    def add_ssp(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path.resolve()))
        if path_hash in self.ssp_profiles.keys():
            if self.ssp_profiles[path_hash].deleted == 1:
                add_profile = True
                logger.info("previously deleted, re-adding: %s" % path)
            elif self.ssp_profiles[path_hash] == 0:
                add_profile = False
            else:
                logger.error("profile not added. %s.deleted is not 0 or 1" % str(self.ssp_profiles[path_hash]))
                add_profile = False
        else:
            add_profile = True

        if add_profile is True:
            # Read Profile
            ssp_obj = SSP()
            ssp_obj.read(data_path=path)

            # Write to
            ssp_group = self.ssp_group.createGroup(path_hash)
            # Add attributes
            ssp_group.source_path = str(path)
            ssp_group.deleted = 0
            # Add variables and data
            ssp_group.createDimension(dimname="depth", size=None)
            ssp_group.createDimension(dimname="lat", size=None)
            ssp_group.createDimension(dimname="lon", size=None)
            ssp_group.createDimension(dimname="time", size=None)

            var_time = ssp_group.createVariable(varname="time",
                                                datatype="i8",
                                                dimensions=("time",))
            var_time.long_name = "time_of_sound_speed_profile"
            var_time.units = NetCDFHelper.t_units
            var_time.calendar = NetCDFHelper.t_calendar
            var_time[:] = date2num(dates=ssp_obj.time, units=NetCDFHelper.t_units, calendar=NetCDFHelper.t_calendar)

            var_lat = ssp_group.createVariable(varname="latitude",
                                               datatype="f8",
                                               dimensions=("lat",))
            var_lat.long_name = "latitude_of_sound_speed_profile"
            var_lat.standard_name = "latitude"
            var_lat.units = "degree_north"
            var_lat[:] = ssp_obj.lat
            
            var_lon = ssp_group.createVariable(varname="longitude",
                                               datatype="f8",
                                               dimensions=("lon",))
            var_lon.long_name = "longitude_of_sound_speed_profile"
            var_lon.standard_name = "longitude"
            var_lon.units = "degree_east"
            var_lon[:] = ssp_obj.lon

            var_depth = ssp_group.createVariable(varname="depth",
                                                 datatype="f8",
                                                 dimensions=("depth",))
            var_depth.long_name = "depth_bin_m"
            var_depth.standard_name = "depth"
            var_depth.units = "m"
            var_depth.axis = "Z"
            var_depth.positive = "down"
            var_depth[:] = ssp_obj.depth

            var_sv = ssp_group.createVariable(varname="sound_speed",
                                              datatype="f8",
                                              dimensions=("depth",))
            var_sv.long_name = "sound_velocity"
            var_sv.standard_name = "speed_of_sound_in_sea_water"
            var_sv.units = "m s-1"
            var_sv.axis = 'X'
            var_sv[:] = ssp_obj.sv

            NetCDFHelper.update_modified(ds=self._ds)
            self._ds.close()
            return True

    def remove_ssp(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path.resolve()))
        if path_hash not in self.ssp_list:
            logger.info("absent: %s" % path)
            return False
        else:
            grp_profile = self.ssp_profiles[path_hash]
            grp_profile.deleted = 1
            return True

    def add_calibration(self, path: Path) -> bool:
        path_hash = NetCDFHelper.hash_string(str(path.resolve()))
        if path_hash in self.calibration_files.keys():
            if self.calibration_files[path_hash].deleted == 1:
                add_calibration = True
                logger.info("previously deleted: re-adding %s" % path)
            elif self.calibration_files[path_hash] == 0:
                add_calibration = False
            else:
                logger.error("profile not added. %s.deleted is not 0 or 1" % str(self.calibration_files[path_hash]))
                add_calibration = False
        else:
            add_calibration = True

        if add_calibration is True:
            # Read Calibration File
            cal_obj = Calibration()
            cal_obj.read(data_path=path)

    def remove_calibration(self) -> bool:
        pass

    # support functions #
    def nc_ssp_name(self, path: Path):
        pass

    def nc_calibration_name(self, path: Path):
        pass
