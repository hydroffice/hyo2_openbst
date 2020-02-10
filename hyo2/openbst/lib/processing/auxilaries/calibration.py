import logging
import numpy as np

from pathlib import Path
from hyo2.openbst.lib.processing.auxilaries.files import FileManager

logger = logging.getLogger(__name__)


class Calibration:

    def __init__(self):
        self._ext = ".csv"
        self.frequency = None
        self.angle = None
        self.c_values = None

        self.common_path = None
        self.cur_row_idx = None
        self.max_nr_lines = None
        self.section_token = "Section"
        self.num_samples = None

    def read(self, data_path: Path):
        logger.debug("*** %s ***: start" % self._ext)

        do_read = self.check_ext(data_path=data_path)
        if do_read is False:
            return False

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

    def check_ext(self, data_path: Path):
        if data_path.suffix != self._ext:
            return False
        else:
            return True

    def _read(self, data_path: Path, encoding: str = 'utf8'):
        data_path = str(data_path.resolve())
        self.fid = FileManager(data_path, mode='r', encoding=encoding)
        try:
            self.total_data = self.fid.io.read()
            self.lines = self.total_data.splitlines()
        except UnicodeDecodeError as e:
            if encoding == 'utf8':
                logger.info("changing encoding to latin: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='latin')
                self.total_data = self.fid.io.read()
                self.lines = self.total_data.splitlines()
            elif encoding == 'latin':
                logger.info("changing encoding to utf8: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='utf8')
                self.total_data = self.fid.io.read()
                self.lines = self.total_data.splitlines()
            else:
                raise e

        self.samples_offset = 0
        self.field_index = dict()
        self.more_fields = list()

        if self.fid is not None:
            self.fid.close()

    def _parse_header(self):
        logger.debug('parsing header')

        self.max_nr_lines = len(self.lines)
        if self.max_nr_lines < 3:
            raise RuntimeError("The input file is only %d-lines long" % self.max_nr_lines)

        try:
            self.cur_row_idx = 0
            first_line = self.lines[self.cur_row_idx]
            first_token = "frequency:"
            tokens = first_line.split(sep=',')

            if tokens[0] != first_token:
                raise RuntimeError("Unknown start of file: it should be %s, but it is %s" % (first_token, tokens[0]))
            else:
                self.frequency = float(tokens[1])

            self.cur_row_idx += 1
            tokens = self.lines[self.cur_row_idx].split(sep=',')
            second_tokens = ('angle', 'cal_point')

            if tokens[0] != second_tokens[0] and tokens[0] != second_tokens[1]:
                raise RuntimeError("UNknown second line of file: it should be '%s , %s" % second_tokens)
        except Exception as e:
            raise e

    def _parse_body(self):
        logger.debug("parsing_body")
        count = 0
        self._init_data(self.max_nr_lines - self.cur_row_idx)

        while self.cur_row_idx < self.max_nr_lines:
            if len(self.lines[self.cur_row_idx]) == 0:
                continue

            tokens = self.lines[self.cur_row_idx].strip().split(',')
            if len(tokens) != 2:
                logger.warning("invalid number of tokens. skipping line: %s" % self.lines[self.cur_row_idx])
                self.cur_row_idx += 1
                continue

            try:
                self.angle[count] = float(tokens[0])
                self.c_values[count] = float(tokens[1])
            except ValueError:
                logger.warning("invalid conversion parsing line #%d" % (self.cur_row_idx,))
                self.cur_row_idx += 1
            count += 1
            self.cur_row_idx += 1
        self.resize(count)

    def _init_data(self, num_samples: int):
        self.angle = np.ones(num_samples) * np.nan
        self.c_values = np.ones(num_samples) * num_samples

    def resize(self, count):
        """Resize the arrays (if present) to the new given number of elements"""
        if self.num_samples == count:
            return
        self.num_samples = count

        if self.angle is not None:
            self.angle = np.resize(self.angle, count)
        if self.c_values is not None:
            self.c_values = np.resize(self.c_values, count)