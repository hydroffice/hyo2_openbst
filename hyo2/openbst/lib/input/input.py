from collections import OrderedDict
import logging
from pathlib import Path
logger = logging.getLogger(__name__)


class Input:

    def __init__(self,prj_path: Path):
        # Input File attributes
        self.prj_path = prj_path
        self.input_list = OrderedDict()

        # Standard Processing Parameters
        # - Raw Decode
        # - Gains

