import logging
import numpy as np

from datetime import datetime as dt
from pathlib import Path

from hyo2.openbst.lib.processing.auxilaries.files import FileManager
logger = logging.getLogger(__name__)

# TODO: How should ssp files be handled? Restrict to single format or implement multiformat reader
# TODO: This is copy paste from SSM and made to quickly work. Needs a rework if it is being kept


class SSP:

    def __init__(self):
        self._ext = '.svp'
        self.lat = None
        self.lon = None
        self.time = None
        self.depth = None
        self.sv = None

        self.common_path = None
        self.cur_row_idx = None
        self.max_nr_lines = None
        self.section_token = "Section"
        self.num_samples = None

    def read(self, data_path):
        logger.debug('*** %s ***: start' % self._ext)

        do_read = self.check_ext(data_path=data_path)  # create a new empty profile list
        if do_read is False:
            return False

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        logger.debug('*** %s ***: done' % self._ext)
        return True

    def check_ext(self, data_path: Path):
        if data_path.suffix != self._ext:
            return False
        else:
            return True

    def _read(self, data_path, encoding='utf8'):
        """Helper function to read the raw file"""
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
        """Parsing top header: common path"""
        logger.debug('parsing header')

        self.max_nr_lines = len(self.lines)
        if self.max_nr_lines < 4:
            raise RuntimeError("The input file is only %d-line long" % len(self.lines))

        try:

            self.cur_row_idx = 0
            first_line = self.lines[self.cur_row_idx]
            first_token = "[SVP_VERSION_2]"
            if first_token not in first_line:
                raise RuntimeError("Unknown start of file: it should be %s, but it is %s" % (first_token, first_line))

            self.cur_row_idx += 1
            if self.lines[self.cur_row_idx][:len(self.section_token)] != self.section_token:
                self.common_path = self.lines[self.cur_row_idx].strip()
                self.cur_row_idx += 1
                logger.debug("common path: %s" % self.common_path)

        except Exception as e:
            raise RuntimeError("While parsing header, %s" % e)

    def _parse_body(self):
        """Parsing all the section"""
        logger.debug('parsing body')

        while self.cur_row_idx < self.max_nr_lines:

            # skip empty lines
            if len(self.lines[self.cur_row_idx]) == 0:
                continue

            # new profile
            if self.lines[self.cur_row_idx][:len(self.section_token)] == self.section_token:
                self._parse_section_header()
                self._parse_section_body()
                continue

            # this point should be never reached.. unless troubles
            logger.debug("skipping line #%03d" % self.cur_row_idx)
            self.cur_row_idx += 1

    def _parse_section_header(self):
        """Parsing header: time, latitude, longitude"""
        logger.debug('parsing section header')

        tokens = self.lines[self.cur_row_idx].strip().split()
        if len(tokens) < 5:
            logger.warning("skipping section header for invalid number of tokens: %s " % self.lines[self.cur_row_idx])
            return

        time_fields = "%s %s" % (tokens[1], tokens[2])
        try:
            self.time = dt.strptime(time_fields, "%Y-%j %H:%M:%S")

        except Exception as e:
            logger.warning("unable to interpret the timestamp: %s, %s" % (time_fields, e))

        try:
            self.lat = self._interpret_caris_coord(tokens[3])

        except Exception as e:
            logger.warning("unable to interpret the latitude: %s, %s" % (tokens[3], e))

        try:
            self.lon = self._interpret_caris_coord(tokens[4])

        except Exception as e:
            logger.warning("unable to interpret the longitude: %s, %s" % (tokens[4], e))

        # initialize data sample fields
        self._init_data(self.max_nr_lines - self.cur_row_idx)

        self.cur_row_idx += 1

    def _init_data(self, num_samples):
        self.depth = np.zeros(num_samples)
        self.sv = np.zeros(num_samples)
        self.num_samples = num_samples

    @classmethod
    def _interpret_caris_coord(cls, value):

        tokens = value.strip().split(':')
        if len(tokens) != 3:
            raise RuntimeError("invalid number of tokens for %s" % value)

        is_negative = False
        deg = float(tokens[0])
        if deg < 0:
            is_negative = True
            deg = abs(deg)
        minimum = float(tokens[1]) / 60.0
        sec = float(tokens[2]) / 3600.0

        coord = deg + minimum + sec
        if is_negative:
            coord = -coord

        return coord

    def _parse_section_body(self):
        """Parsing samples: depth, speed"""
        logger.debug('parsing section body')

        # valid samples counter
        count = 0

        while self.cur_row_idx < self.max_nr_lines:

            # A new section is coming
            if self.lines[self.cur_row_idx][:len(self.section_token)] == self.section_token:
                self.cur_row_idx += 1
                return

            # skip empty lines
            if len(self.lines[self.cur_row_idx]) == 0:
                self.cur_row_idx += 1
                continue

            tokens = self.lines[self.cur_row_idx].strip().split()
            if len(tokens) != 2:
                logger.warning("skipping line for invalid number of tokens: %s " % self.lines[self.cur_row_idx])
                self.cur_row_idx += 1
                continue

            try:
                self.depth[count] = float(tokens[0])
                self.sv[count] = float(tokens[1])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%03d" % (self.cur_row_idx,))
                self.cur_row_idx += 1
                continue

            except IndexError:
                logger.warning("invalid index parsing of line #%03d" % (self.cur_row_idx,))
                self.cur_row_idx += 1
                continue

            count += 1
            self.cur_row_idx += 1

        self.resize(count)

    def resize(self, count):
        """Resize the arrays (if present) to the new given number of elements"""
        if self.num_samples == count:
            return
        self.num_samples = count

        if self.depth is not None:
            self.depth = np.resize(self.depth, count)
        if self.sv is not None:
            self.sv = np.resize(self.sv, count)