import logging

from enum import Enum
from netCDF4 import Dataset
from typing import Optional

from hyo2.openbst.lib.processing.parameters import Parameters
from hyo2.openbst.lib.processing.process_methods.dicts import ProcessMethods, process_requirements

logger = logging.getLogger(__name__)


class ProcessStageStatus(Enum):
    # Case: Not in current processing chain
    ROOTNODE = 0
    NEWNODE = 1
    MODIFIEDCURRENTNODE = 2

    # Case: Already in processing chain
    CURRENTNODE = 3
    ANCESTORNODE = 4

    # Case: In chain but chain was reset
    OLDROOTNODE = 5
    CHILDNODE = 6


class ProcessManager:
    root = 'ROOT'
    proc_seperator = '__'
    child_seperator = '//'

    def __init__(self, parent_process: Optional[str]):
        self._step = 00
        self._parent = None
        self._setup(parent_process)

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

    @property
    def calculation_in_progress(self):
        return self._calc_in_progress

    def _setup(self, parent_process: Optional[str]):
        if parent_process == '':
            self._step = 00
            self._parent = self.root
        else:
            parent_identifiers = self.get_process_identifiers(process_string=parent_process)
            self._step = int(parent_identifiers[0])
            self._parent = parent_process

    # ## Processing Status Methods ##
    def start_process(self, process_type: ProcessMethods, nc_process: Dataset, parameter_object: Parameters):
        self._calc_in_progress = True

        # Check this is a valid process
        if process_type not in ProcessMethods:
            logger.warning("Process Method is not valid: %s" % process_type)
            self.end_process()
            return False

        # Grab the relevant parameter object
        method_params = parameter_object.get_process_params(process_type=process_type)

        # Check current process against stored processes
        status = self.check_for_process(nc_process=nc_process, process_identifiers=method_params.process_identifiers())
        if status == ProcessStageStatus.ROOTNODE:
            self._calc_in_progress = True
            self._status = status
            logger.info("Process ID = %s. Start of chain, computing root node" % status)
            self.generate_process_name(process_identifiers=method_params.process_identifiers())
            do_process = True
        elif status == ProcessStageStatus.OLDROOTNODE:
            node_string = self.generate_process_name(process_identifiers=method_params)
            self.end_process(_set_parent=node_string)
            logger.info("Process ID = %s. Process not computed, parent updated" % status)
            do_process = False
        elif status == ProcessStageStatus.CURRENTNODE:
            self.end_process()
            logger.info("Process ID = %s. Process not computed" % status)
            do_process = False
        elif status == ProcessStageStatus.MODIFIEDCURRENTNODE:
            self._calc_in_progress = True
            self._status = status
            logger.info("Process ID = %s. Process computing modified current node." % status)
            self.generate_process_name(process_identifiers=method_params.process_identifiers())
            do_process = True
        elif status == ProcessStageStatus.ANCESTORNODE:
            self.end_process()
            logger.info("Process ID = %s. Process not computed." % status)
            do_process = False
        elif status == ProcessStageStatus.CHILDNODE:
            node_string = self.generate_process_name(process_identifiers=method_params)
            self.end_process(_set_parent=node_string)
            logger.info("Process ID = %s. Process not computed, parent updated")
            do_process = False
        elif status == ProcessStageStatus.NEWNODE:
            self._calc_in_progress = True
            self._status = status
            logger.info("Process ID not in processing chain. Process computing new node.")
            self.generate_process_name(process_identifiers=method_params.process_identifiers())
            do_process = True
        else:
            raise RuntimeError("Unrecognized process status: %s" % status)

        # Check for required processes
        if do_process is True:
            meets_required = self.check_requirements(process_method=process_type,
                                                     nc_process=nc_process,
                                                     parameters_object=parameter_object)
            if meets_required is False:
                self.end_process()
                do_process = False

        return do_process

    def finalize_process(self, ds: Dataset):
        # TODO: Error Handling: This will fail if the cur_process group not yet written to nc. Need try/except clause

        # Write parent meta data
        parent_written = self.write_parent(ds=ds)

        # Write children meta data.
        children_written = self.write_children(ds=ds)

        if children_written is False or parent_written is False:
            raise RuntimeError('Something went wrong writing parent/children')

        process_identifiers = self.get_process_identifiers(self.current_process)
        self._step = int(process_identifiers[0])
        self._parent = self._cur_process
        self.end_process()

    def end_process(self, _set_parent: Optional[str] = None):
        self._calc_in_progress = False
        self._status = None
        self._cur_process = None
        if _set_parent is not None:
            self._parent = _set_parent
            parent_identifiers = self.get_process_identifiers(process_string=_set_parent)
            self._step = int(parent_identifiers[0])

    def reset_process(self):
        self._setup(parent_process='')
        self.end_process()

    # # NC files methods
    def write_parent(self, ds: Dataset):
        grp_process = ds.groups[self.current_process]

        if self._status == ProcessStageStatus.ROOTNODE:
            grp_process.parent_process = self.root

        elif self._status == ProcessStageStatus.NEWNODE:
            grp_process.parent_process = self.parent_process

        elif self._status == ProcessStageStatus.ANCESTORNODE or self._status == ProcessStageStatus.CURRENTNODE:
            pass

        elif self._status == ProcessStageStatus.MODIFIEDCURRENTNODE:
            grp_parent = ds.groups[self.parent_process]
            grp_process.parent_process = grp_parent.parent_process

        else:
            raise TypeError('%s is not of enum type %s' % (self._status, ProcessStageStatus))

        return True

    def write_children(self, ds: Dataset):
        grp_process = ds.groups[self.current_process]
        child_str = self.child_seperator + self.current_process

        if self._status == ProcessStageStatus.ROOTNODE:
            grp_process.children_process = str()

        elif self._status == ProcessStageStatus.NEWNODE:
            grp_parent = ds.groups[self.parent_process]
            grp_parent.children_process += child_str
            grp_process.children_process = str()

        elif self._status == ProcessStageStatus.MODIFIEDCURRENTNODE:
            grp_brother = ds.groups[self.parent_process]     # TODO: Confusing Nomenclature, use NetworkX to manage
            if grp_brother.parent_process != self.root:
                grp_ancestor = ds.groups[grp_brother.parent_process]
                grp_ancestor.children_process += child_str

            grp_process.children_process = str()

        elif self._status == ProcessStageStatus.ANCESTORNODE or self._status == ProcessStageStatus.CURRENTNODE:
            pass

        else:
            raise TypeError('%s is not of enum type %s' % (self._status, ProcessStageStatus))

        return True

    # # Support Methods #
    def check_for_process(self, nc_process: Dataset, process_identifiers: list) -> ProcessStageStatus:
        parent_identifiers = self.parent_process.split(self.proc_seperator)

        # Root Node Handling - Check if this is the first time processing
        if len(nc_process.groups) == 0:
            return ProcessStageStatus.ROOTNODE

        # Root Node Handling - Check for a reset
        if self.parent_process == self.root and len(nc_process.groups) != 0:
            # Loop through nodes checking for repeats
            for node_name, grp_node in nc_process.groups.items():
                node_identifiers = node_name.split(self.proc_seperator)
                if node_identifiers[1] == process_identifiers[0] and node_identifiers[-1] == process_identifiers[-1]:
                    # This is a repeat process based on identifiers.
                    if grp_node.parent_process == self.root:
                        # This is an old root node, no need to recalculate
                        return ProcessStageStatus.OLDROOTNODE
                    else:
                        # This is a process with same parameters, but not a root node, thus this is a new root node
                        return ProcessStageStatus.ROOTNODE
                else:
                    continue

        # Not a Root Node - Check parent, ancestors and check parent's children for repeats
        # Check cur_process against parent process
        if process_identifiers[0] == parent_identifiers[1] and process_identifiers[-1] == parent_identifiers[-1]:
            return ProcessStageStatus.CURRENTNODE
        elif process_identifiers[0] == parent_identifiers[1] and process_identifiers[-1] != parent_identifiers[-1]:
            return ProcessStageStatus.MODIFIEDCURRENTNODE
        else:
            # Check ancestors for process match
            in_process_chain = self.check_process_chain(nc_process=nc_process,
                                                        process_identifiers=process_identifiers,
                                                        parent_str=self.parent_process)
            if in_process_chain is True:
                return ProcessStageStatus.ANCESTORNODE
            else:
                # Not in ancestors, check parent children
                grp_parent = nc_process.groups[self.parent_process]
                if grp_parent.children_process != '':
                    # There are children nodes, check each to make sure it doesn't match
                    list_child_nodes = grp_parent.children_process.split(self.child_seperator)
                    for child_node in list_child_nodes:
                        child_identifiers = child_node.split(self.proc_seperator)
                        if child_identifiers[1] == process_identifiers[0] \
                                and child_identifiers[-1] == process_identifiers[-1]:
                            return ProcessStageStatus.CHILDNODE
                        elif child_identifiers[1] == process_identifiers[0] \
                                and child_identifiers[-1] != process_identifiers[-1]:
                            return ProcessStageStatus.NEWNODE
                        else:
                            # No match, continue loop
                            continue
                else:
                    # There are no children for the parent, thus this is a new process
                    return ProcessStageStatus.NEWNODE

    def check_requirements(self, process_method: ProcessMethods, nc_process: Dataset, parameters_object: Parameters):
        meets_required = False
        for process, requirement in process_requirements.items():
            if process_method == process:
                if requirement is None:
                    meets_required = True
                    break
                else:
                    required_identifiers = parameters_object.get_process_params(requirement).process_identifiers()

                    # Check if parent is required process
                    parent_identifiers = self.get_process_identifiers(self.parent_process)
                    if parent_identifiers[1] == required_identifiers[0]:
                        meets_required = True
                        break
                    else:
                        # Check processing tree for required process
                        in_process_chain = self.check_process_chain(nc_process=nc_process,
                                                                    process_identifiers=required_identifiers,
                                                                    parent_str=self.parent_process)
                        if in_process_chain is True:
                            meets_required = True
                        else:
                            logger.warning("Process: %s has a requirement: %s\n"
                                           "Calculate required process to run current process" % process, requirement)
        return meets_required

    def generate_process_name(self, process_identifiers: list) -> str:
        if self._status == ProcessStageStatus.ROOTNODE:
            step = 00
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.OLDROOTNODE:
            step = 00
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.CURRENTNODE:
            process_name = self.parent_process
        elif self._status == ProcessStageStatus.MODIFIEDCURRENTNODE:
            step = self.step
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
                           process_identifiers[1]

        elif self._status == ProcessStageStatus.ANCESTORNODE:
            # TODO: Find a way to return the proper node name
            logger.warning("The generated process name has not been computed. For reference only")
            step = self.step + 1
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.CHILDNODE:
            step = self.step + 1
            step = self.step + 1
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
                           process_identifiers[1]
        elif self._status == ProcessStageStatus.NEWNODE:
            step = self.step + 1
            process_name = "%02d" % step \
                           + self.proc_seperator + \
                           process_identifiers[0] \
                           + self.proc_seperator + \
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
        nc_parent_identifiers = nc_parent_str.split(cls.proc_seperator)

        # Check if current process matches parent
        if nc_parent_identifiers[0] == ProcessManager.root:
            # Reached the start of processing chain, no match found
            return False
        elif nc_parent_identifiers[1] == process_identifiers[0]:
            # Found process in current parent, match found
            return True
        else:
            # Process not in current parent, search next parent
            in_chain = ProcessManager.check_process_chain(nc_process=nc_process,
                                                          process_identifiers=process_identifiers,
                                                          parent_str=nc_parent_str)
            return in_chain

    @staticmethod
    def get_process_identifiers(process_string: str) -> list:
        process_identifiers = process_string.split(ProcessManager.proc_seperator)
        return process_identifiers
