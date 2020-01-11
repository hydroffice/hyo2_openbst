import logging

from enum import Enum
from netCDF4 import Dataset

logger = logging.getLogger(__name__)


class ProcessStageStatus(Enum):
    # Already in processing chain
    PRIORPROCESS = 0
    REPEATEPROCESS = 1

    # Not in processing chain
    NEWPROCESS = 2
    MODIFIEDPROCESS = 3


class ProcessManager:
    seperator = '__'

    def __init__(self):
        self._step = 00
        self._parent = ''

        self._calc_in_progress = False
        self._cur_process = None
        self._status = None

    @property
    def step(self) -> int:
        return self._step

    @property
    def current_process(self) -> str:
        return self._cur_process

    @property
    def parent_process(self) -> str:
        return self._parent

    @parent_process.setter
    def parent_process(self, current_process):
        self._parent = current_process

    # ## Processing Status Methods ##
    def start_process(self, nc_process: Dataset, process_identifiers: list):
        self._calc_in_progress = True

        # Check current process against stored processes
        status = self.check_for_process(nc_process=nc_process, process_identifiers=process_identifiers)
        if status == ProcessStageStatus.PRIORPROCESS:
            self.end_process()
            logger.info("Process ID is same as last process. Process not computed")
            has_been_processed = True
        elif status == ProcessStageStatus.REPEATEPROCESS:
            self.end_process()
            logger.info("Process ID found in processing chain. Process not computed.")
            has_been_processed = True
        elif status == ProcessStageStatus.MODIFIEDPROCESS:
            self._calc_in_progress = True
            self._status = status
            logger.info("Process ID is modifed version of last process. Process computing.")
            has_been_processed = False
        elif status == ProcessStageStatus.NEWPROCESS:
            self._calc_in_progress = True
            self._status = status
            logger.info("Process ID not in processing chain. Process computing.")
            has_been_processed = False
        else:
            raise RuntimeError("Unrecognized process status: %s" % status)

        self.generate_process_name(process_identifiers=process_identifiers)
        return has_been_processed

    def update_process(self):
        pass

    def end_process(self):
        self._calc_in_progress = False
        self._status = None
        self._cur_process = None

    def check_for_process(self, nc_process: Dataset, process_identifiers: list) -> ProcessStageStatus:
        parent_identifiers = self.parent_process.split(self.seperator)

        # Check if this is the first time processing
        if self.parent_process == '':
            return ProcessStageStatus.NEWPROCESS

        # Check new process against parent process
        if process_identifiers[0] == parent_identifiers[1]:
            if process_identifiers[-1] == parent_identifiers[-1]:
                return ProcessStageStatus.PRIORPROCESS
            else:
                return ProcessStageStatus.MODIFIEDPROCESS
        else:
            # Check if step has been computed prior in chain
            in_process_chain = self.check_process_chain(nc_process=nc_process,
                                                        process_identifiers=process_identifiers,
                                                        parent_str=self.parent_process)
            if in_process_chain is True:
                return ProcessStageStatus.REPEATEPROCESS
            else:
                return ProcessStageStatus.NEWPROCESS

    def generate_process_name(self, process_identifiers: list) -> str:
        if self._status == ProcessStageStatus.MODIFIEDPROCESS:
            step = self.step
            process_name = "%02d" % step\
                           + self.seperator + \
                           process_identifiers[0] \
                           + self.seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.NEWPROCESS:
            step = self.step + 1
            process_name = "%02d" % step\
                           + self.seperator + \
                           process_identifiers[0] \
                           + self.seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.PRIORPROCESS:
            process_name = self.parent_process
        elif self._status == ProcessStageStatus.REPEATEPROCESS:
            logger.warn("The generated process name has not been computed. For reference only")
            step = self.step + 1
            process_name = "%02d" % step \
                           + self.seperator + \
                           process_identifiers[0] \
                           + self.seperator + \
                           process_identifiers[1]
        else:
            raise RuntimeError("Unknown process status: %s" % self._status)
        self._cur_process = process_name
        return process_name

    @classmethod
    def check_process_chain(cls, nc_process: Dataset, process_identifiers: list, parent_str: str) -> bool:

        # Find grp_process that matches current parent
        grp_prior = nc_process.groups[parent_str]
        nc_parent_str = grp_prior.parent_process
        nc_parent_identifiers = nc_parent_str.split(cls.seperator)

        # Check if current process matches parent
        if nc_parent_identifiers[1] == '':
            # Reached the start of processing chain, no match found
            return False
        elif nc_parent_identifiers[1] == process_identifiers[0]:
            # Found process in current parent, match found
            return True
        else:
            # Process not in current parent, search next parent
            ProcessManager.check_process_chain(nc_process=nc_process,
                                               process_identifiers=process_identifiers,
                                               parent_str=nc_parent_str)
