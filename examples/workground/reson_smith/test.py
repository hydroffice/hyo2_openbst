import logging

from hyo2.openbst.lib.raw.parsers.reson.reader import ResonDatagrams


from pathlib import Path
from hyo2.openbst.lib.raw.parsers.reson.reader import Reson


logging.basicConfig(level=logging.DEBUG)
raw_path = Path(__file__).parents[3].joinpath('data', 'download', 'reson', '20190730_144835.s7k')
# raw_path = Path(__file__).parents[3].joinpath('data', 'download', 'reson', '20190321_185116.s7k')
if not raw_path.exists():
    raise RuntimeError("unable fmtto locate: %s" % raw_path)

#
# infile = prr.x7kRead(str(raw_path))
# infile.mapfile()
# tst = infile.getrecord('7027', 0)

reson_file = Reson(raw_path)
reson_file.data_map()
# raw_position = reson_file.get_position()
tst = reson_file.get_datagram(ResonDatagrams.RAWDETECTDATA)
# key = list(tst.keys())
# ping = tst[key[0]]
# tvg = np.asarray(ping.tvg_curve)

print('ahh')