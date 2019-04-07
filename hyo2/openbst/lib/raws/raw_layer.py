import logging

from hyo2.openbst.lib.products.formats.product_format_type import ProductFormatType
from hyo2.openbst.lib.products.product_layer_type import ProductLayerType

logger = logging.getLogger(__name__)


class RawLayer:

    def __init__(self, layer_type: ProductLayerType = ProductLayerType.UNKNOWN,
                 format_type: ProductFormatType = ProductFormatType.UNKNOWN):
        self._layer_type = layer_type
        self._format_type = format_type

    @property
    def layer_type(self) -> ProductLayerType:
        return self._layer_type

    @property
    def format_type(self) -> ProductFormatType:
        return self._format_type

    # ### OTHER ###

    def info_str(self):

        msg = "- layer type: %s\n" % self._layer_type
        msg += "- format type: %s\n" % self._format_type

        return msg

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <layer type: %s>\n" % self._layer_type
        msg += "  <format type: %s>\n" % self._format_type

        return msg
