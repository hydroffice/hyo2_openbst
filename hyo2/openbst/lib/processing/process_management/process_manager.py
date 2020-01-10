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

    @property
    def step(self) -> int:
        return self._step

    @step.setter
    def step(self, step):
        self._step = step

    @property
    def parent_process(self) -> str:
        return self._parent

    @parent_process.setter
    def parent_process(self, current_process):
        self._parent = current_process

    # ## Processing Status Methods ##
    def compare_processes(self, nc_process: Dataset, process_hash: str):
        status = self.check_for_process(nc_process=nc_process, process_hash=process_hash)
        if status == ProcessStageStatus.PRIORPROCESS:
            logger.info("Current process is same as last process. Process not computed")
            step = self.step
            has_been_processed = True
            return has_been_processed, step

        elif status == ProcessStageStatus.REPEATEPROCESS:
            logger.info("Current process found in processing chain. Process not computed.")
            has_been_processed = True
            step = self.step
            return has_been_processed, step

        elif status == ProcessStageStatus.MODIFIEDPROCESS:
            logger.info("Current process is modifed version of last process. Process computing.")
            has_been_processed = False
            step = self.step
            return has_been_processed, step

        elif status == ProcessStageStatus.NEWPROCESS:
            logger.info("Current process not in processing chain. Process computing.")
            has_been_processed = False
            step = self.step + 1
            return has_been_processed, step
        else:
            raise RuntimeError("Unrecognized process status: %s" % status)

    def check_for_process(self, nc_process: Dataset, process_hash: str) -> ProcessStageStatus:
        process_identifiers = process_hash.split(self.seperator)
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
                                                        process_str=process_hash,
                                                        parent_str=self.parent_process)
            if in_process_chain is True:
                return ProcessStageStatus.REPEATEPROCESS
            else:
                return ProcessStageStatus.NEWPROCESS

    @classmethod
    def check_process_chain(cls, nc_process: Dataset, process_str: str, parent_str: str) -> bool:
        process_identifiers = process_str.split(cls.seperator)

        # Find grp_process that matches current parent
        grp_prior = nc_process.groups[parent_str]
        nc_parent_str = grp_prior.parent_process
        nc_parent_identifiers = nc_parent_str.split(cls.seperator)

        # Check if current process matches parent
        if nc_parent_identifiers[1] == '':
            # Reached the start of processing chain, no match found
            return False
        elif nc_parent_identifiers[1] == process_identifiers[1]:
            # Found process in current parent, match found
            return True
        else:
            # Process not in current parent, search next parent
            ProcessManager.check_process_chain(nc_process=nc_process, process_str=process_str, parent_str=nc_parent_str)

    @classmethod
    def generate_process_name(cls, step: int, process_hash: str) -> str:
        process_name = "%02d" % step + cls.seperator + process_hash
        return process_name
