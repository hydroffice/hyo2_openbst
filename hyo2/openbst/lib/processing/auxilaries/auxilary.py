import logging

from pathlib import Path

logger = logging.getLogger(__name__)


class Auxiliary:
    ext = ".nc"

    def __init__(self, auxiliary_path: Path) -> None:
        self._path = auxiliary_path

    @property
    def path(self) -> Path:
        return self._path

    @property
    def ssp_list(self) -> list:
        pass

    @property
    def calibration_list(self) -> list:
        pass

    # common project management methods #
    def add_ssp(self) -> bool:
        pass

    def remove_ssp(self) -> bool:
        pass

    def add_calibration(self) -> bool:
        pass

    def remove_calibration(self) -> bool:
        pass

    # support functions #
    def nc_ssp_name(self, path: Path):
        pass

    def nc_calibration_name(self, path: Path):
        pass
