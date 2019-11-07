import logging
from netCDF4 import Dataset, Group, num2date
from pathlib import Path

from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress
# noinspection PyUnresolvedReferences

from hyo2.openbst.lib import lib_info
from hyo2.openbst.lib.input.input import Input
from hyo2.openbst.lib.nc_helper import NetCDFHelper
from hyo2.openbst.lib.products.product import Product
from hyo2.openbst.lib.project_info import ProjectInfo
from hyo2.openbst.lib.raw.raws import Raws
logger = logging.getLogger(__name__)


class Project:

    ext = ".openbst"

    def __init__(self, prj_path: Path,
                 progress: AbstractProgress = CliProgress(use_logger=True)):

        # check extension for passed project path
        if prj_path.suffix != self.ext:
            raise RuntimeError("invalid project extension: %s" % prj_path)
        prj_path.mkdir(parents=True, exist_ok=True)
        self._path = prj_path
        _ = self.raws_folder
        _ = self.process_folder
        _ = self.products_folder

        self.progress = progress

        self._i = ProjectInfo(prj_path=self._path)
        self._r = Raws(raws_path=self.raws_folder)
        self.input = Input(prj_path=self._path)

    @property
    def name(self) -> str:
        return self._path.stem

    @property
    def path(self) -> Path:
        return self._path

    @property
    def raws_folder(self) -> Path:
        path = self._path.joinpath("raws")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def process_folder(self) -> Path:
        path = self._path.joinpath("process")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def products_folder(self) -> Path:
        path = self._path.joinpath("products")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def info(self) -> ProjectInfo:
        return self._i

    # ### RAWS ###

    def add_raw(self, path: Path) -> bool:
        self.progress.start(title="Reading", text="Ongoing reading. Please wait!",
                            init_value=10)

        added = self._i.add_raw(path=path)
        if not added:
            self.progress.end()
            return False

        self.progress.update(50)

        added = self._r.add_raw(path=path)
        if not added:
            self.progress.end()
            return False
        self.progress.update(99)
        self.progress.end()
        return True

    def remove_raw(self, path: Path) -> bool:
        self.progress.start(title="Deleting", text="Ongoing deleting. Please wait!",
                            init_value=10)

        removed = self._i.remove_raw(path=path)
        if not removed:
            self.progress.end()
        self.progress.update(50)

        removed = self._r.remove_raw(path=path)
        if not removed:
            self.progress.end()
            return False

        self.progress.update(99)
        self.progress.end()
        return True

    def validate_raws(self, force_validate: bool =False) -> list:
        self.progress.start(title="Validating", text="Ongoing validation. Please wait!",
                            init_value=10)
        num_files = len(self._i.raws)
        progress_update = int((self.progress.range - self.progress.value) / num_files)
        for raw_key, raw_nc in self._i.raws.items():

            if (raw_nc.valid == 0 and raw_nc.deleted == 0) or force_validate:
                raw_object = self._i.validate_raw(Path(raw_nc.source_path))
                self.input.input_list[raw_key] = raw_object
                logger.debug("validation - File validated: %s" % raw_nc.source_path)
                self.progress.update(self.progress.value + progress_update)

            elif raw_nc.deleted == 1:
                logger.debug("validation - Deleted file: %s" % raw_nc.source_path)
                self.progress.update(self.progress.value + progress_update)

            elif raw_nc.deleted == 0 and raw_nc.valid == 1:
                # TODO: add logic to add the file to the self.input.input_list if not present
                # TODO: this will need a new reconstruct function in the raw_reader class
                logger.debug("validation - File is alread valid: %s" % raw_nc.source_path)
                self.progress.update(self.progress.value + progress_update)
                continue

        self.progress.update(self.progress.range)

        self.progress.end()

        return self._i.valid_raws

    def relink_raws(self):
        pass                    # TODO: Write a relink method to find source files

    # ### PRODUCTS ###

    def add_product(self, path: Path) -> bool:
        self.progress.start(title="Reading", text="Ongoing reading. Please wait!",
                            init_value=10)

        added = self._i.add_product(path=path)
        if not added:
            self.progress.end()

        self.progress.update(20)

        product = Product(project_folder=self.path, source_path=path)
        # product.close()

        self.progress.end()
        return True

    def remove_product(self, path: Path) -> bool:
        self.progress.start(title="Deleting", text="Ongoing deleting. Please wait!",
                            init_value=10)

        removed = self._i.remove_product(path=path)
        if not removed:
            self.progress.end()
        self.progress.update(20)

        self.progress.end()
        return True

    # # @classmethod
    # # def is_product_vr(cls, path: str) -> bool:
    # #
    # #     data_source_types = Product.retrieve_layer_and_format_types(path)
    # #     if len(data_source_types) == 0:
    # #         return False
    # #
    # #     if list(data_source_types.values())[0] != ProductFormatType.BAG:
    # #         return False
    # #
    # #     return ProductFormatBag.is_vr(path=path)
    # #
    # # @property
    # # def product_layers_dict(self) -> dict:
    # #     return self._product_layers_dict
    # #
    # # @property
    # # def product_layers_list(self) -> list:
    # #     return self._product_layers_list
    # #
    # # @property
    # # def ordered_product_layers_list(self) -> list:
    # #     layers_list = list()
    # #
    # #     basename_list = list()
    # #     last_name = None
    # #
    # #     for lk in list(reversed(self._product_layers_list)):
    # #
    # #         cur_token, cur_name = lk.split(":")
    # #         # logger.debug("%s : %s" % (cur_token, cur_name))
    # #
    # #         if last_name is None:
    # #             last_name = cur_name
    # #
    # #         if cur_name != last_name:
    # #             layers_list += basename_list
    # #             basename_list.clear()
    # #
    # #         if cur_token == "BAT":  # to have the bathymetry as latest
    # #             basename_list.insert(0, lk)
    # #         else:
    # #             basename_list.append(lk)
    # #
    # #     layers_list += basename_list
    # #
    # #     return layers_list
    # #
    # # @property
    # # def product_layer_paths_dict(self) -> dict:
    # #     return self._product_layer_paths_dict
    # #
    # # def product_layer_keys_by_basename(self, basename: str) -> list:
    # #     layer_keys = list()
    # #     key_list = list(self._product_layers_dict.keys())
    # #
    # #     for layer_key in key_list:
    # #
    # #         if basename == layer_key.split(":")[-1]:
    # #             layer_keys.append(layer_key)
    # #
    # #     return layer_keys
    # #
    # # def other_product_layers_for_key(self, layer_key: str):
    # #     other_layers = list()
    # #     key_list = list(self._product_layers_dict.keys())
    # #     layer_basename = layer_key.split(":")[-1]
    # #
    # #     for key in key_list:
    # #         if layer_key == key:
    # #             continue
    # #
    # #         if layer_basename == key.split(":")[-1]:
    # #             if self._product_layers_dict[key].is_raster():
    # #                 other_layers.append(self._product_layers_dict[key])
    # #
    # #     return other_layers
    # #
    # # def load_product_from_source(self, path: str,
    # #                              hint_type: ProductLayerType = ProductLayerType.UNKNOWN,
    # #                              exclude_types: Optional[list] = None) -> bool:
    # #     layer_format_types = Product.retrieve_layer_and_format_types(path, hint_type)
    # #
    # #     if exclude_types is not None:
    # #         logging.debug("filtering data types: %s " % (exclude_types,))
    # #         temp_raster_types = layer_format_types
    # #         layer_format_types = dict()
    # #         for raster_data_type in temp_raster_types.keys():
    # #
    # #             if raster_data_type in exclude_types:
    # #                 continue
    # #             layer_format_types[raster_data_type] = temp_raster_types[raster_data_type]
    # #
    # #     self.progress.start(title="Loading", text="Ongoing loading. Please wait!",
    # #                         init_value=10)
    # #
    # #     actual_layers = Product.load(input_path=path,
    # #                                  layer_types=list(layer_format_types.keys()),
    # #                                  input_format=list(layer_format_types.values())[0])
    # #
    # #     self.progress.update(value=60)
    # #
    # #     progress_quantum = 40 / (len(layer_format_types) + 1)
    # #
    # #     for layer_type in layer_format_types.keys():
    # #
    # #         layer_key = Product.make_layer_key(path=path, data_type=layer_type)
    # #         logger.debug("raster key: %s" % layer_key)
    # #
    # #         # if already exists, first close existing layer
    # #         self.close_product_layer_by_key(layer_key=layer_key)
    # #
    # #         if layer_type not in actual_layers.keys():
    # #             logging.warning("skipping unretrieved %s layer" % layer_type)
    # #             continue
    # #
    # #         # actually add the layer to the dicts and to the list
    # #         self._product_layers_dict[layer_key] = actual_layers[layer_type]
    # #         self._product_layers_list.append(layer_key)
    # #         self._product_layer_paths_dict[layer_key] = path
    # #
    # #         self.progress.add(quantum=progress_quantum)
    # #
    # #     self.progress.end()
    # #     return True
    # #
    # # def has_product_layers(self) -> bool:
    # #
    # #     return len(self._product_layers_list) != 0
    # #
    # # def has_modified_product_layers(self) -> bool:
    # #
    # #     for layer_key, layer in self._product_layers_dict.items():
    # #
    # #         if layer.modified:
    # #             logger.debug("%s was modified" % layer_key)
    # #             return True
    # #
    # #     return False
    # #
    # # def close_product_layer_by_key(self, layer_key: str) -> bool:
    # #     if layer_key not in self.product_layers_dict.keys():
    # #         return False
    # #
    # #     del self._product_layers_dict[layer_key]
    # #     del self._product_layer_paths_dict[layer_key]
    # #     self._product_layers_list.remove(layer_key)
    # #     return True
    # #
    # # def close_product_layer_by_basename(self, layer_basename: str) -> bool:
    # #
    # #     layers_key = self.product_layer_keys_by_basename(basename=layer_basename)
    # #
    # #     for layer_key in layers_key:
    # #         self.close_product_layer_by_key(layer_key)
    # #
    # #     return True
    # #
    # # def close_product_layers(self) -> None:
    # #     self._product_layers_dict.clear()
    # #     self._product_layers_list.clear()
    # #     self._product_layer_paths_dict.clear()
    # #
    # # def save_product_layer_by_key(self, layer_key: str, output_path: str, open_folder: bool = False) -> bool:
    # #
    # #     # first check whether the layer key is a valid one
    # #     if layer_key not in self._product_layers_dict.keys():
    # #         logger.warning("missing layer key: %s" % layer_key)
    # #         return False
    # #
    # #     # retrieve the input path and make a copy
    # #     input_path = self._product_layer_paths_dict[layer_key]
    # #     output_folder = os.path.dirname(output_path)
    # #     try:
    # #         shutil.copyfile(input_path, output_path)
    # #
    # #         # .prj file
    # #         prj_path = os.path.splitext(input_path)[0] + '.prj'
    # #         if os.path.exists(prj_path):
    # #             prj_basename = os.path.basename(prj_path)
    # #             prj_copy = os.path.join(output_folder, prj_basename)
    # #             shutil.copyfile(prj_path, prj_copy)
    # #
    # #     except Exception as e:
    # #         logger.error("unable to copy from %s to %s -> %s"
    # #                      % (input_path, output_path, e))
    # #         return False
    # #
    # #     # retrieve all the layer keys interested by the saving operations
    # #     layer_basename = layer_key.split(":")[-1]
    # #     output_layer_keys = self.product_layer_keys_by_basename(basename=layer_basename)
    # #     logger.debug("saving %s with keys %s" % (layer_basename, output_layer_keys))
    # #
    # #     # retrieve the layers interested by the saving operations
    # #     output_layers = dict()
    # #     output_format = None
    # #     for output_layer_key in output_layer_keys:
    # #         if output_layer_key not in self._product_layers_dict.keys():
    # #             continue
    # #         output_layers[self._product_layers_dict[output_layer_key].layer_type] = \
    # #             self._product_layers_dict[output_layer_key]
    # #         output_format = self._product_layers_dict[output_layer_key].format_type
    # #     # check if at least a layer was identified
    # #     if len(output_layers) == 0:
    # #         logger.warning("no layers to save")
    # #         return False
    # #
    # #     saved = Product.save(output_path=output_path, output_layers=output_layers, output_format=output_format)
    # #     if open_folder and saved:
    # #         Helper.explore_folder(os.path.dirname(output_path))
    # #
    # #     return True

    # ### LAYERS ###

    # TODO
    def has_layers(self) -> bool:
        return False

    # TODO
    def has_modified_layers(self) -> bool:
        return False

    # TODO
    def close_layers(self) -> None:
        return None

    # ### OTHER ###

    def info_str(self):
        txt = str()
        txt += "  <name: %s>\n" % self.name
        txt += "  <path: %s>\n" % self.path
        txt += "  <raws: %d>\n" % len(self._i.valid_raws)
        txt += "  <products: %d>\n" % len(self._i.valid_products)
        return txt

    def __repr__(self) -> str:
        msg = "<%s>\n" % self.__class__.__name__
        msg += self.info_str()
        return msg
