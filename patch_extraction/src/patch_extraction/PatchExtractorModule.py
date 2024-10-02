# src/patch_extraction.py

from tiatoolbox.tools.patchextraction import get_patch_extractor 
import os
import logging
from pathlib import Path
import h5py
import numpy as np
class PatchExtractorModule:
    def __init__(self, slide_path: str, config: dict, logger: logging.Logger):
        self.slide_path = slide_path
        self.config = config
        self.logger = logger

        # Configuration Parameters
        self.patch_size = tuple(config.get("patch_size", [256, 256]))        # Patch dimensions
        self.method = config.get("method", "slidingwindow").lower()         # Extraction method: "slidingwindow" or "point"
        self.stride = tuple(config.get("stride", self.patch_size))
        self.input_mask = config.get("input_mask")
        self.min_mask_ratio = config.get("min_mask_ratio", 0.5)
        self.resolution = config.get("resolution", 0)
        self.units = config.get("units", "level")
        self.pad_mode = config.get("pad_mode", "constant")
        self.pad_constant_values = config.get("pad_constant_values", 0)
        self.within_bound = config.get("within_bound", False)

        # Define Output Directories
        self.save_dir = config.get("output_dir", "data/patches")
        self.patch_save_dir = os.path.join(self.save_dir, 'patches', Path(self.slide_path).stem)
        self.mask_save_dir = os.path.join(self.save_dir, 'masks', Path(self.slide_path).stem)
        self.stitch_save_dir = os.path.join(self.save_dir, 'stitches', Path(self.slide_path).stem)

        # Create Directories
        for dir_path in [self.patch_save_dir, self.mask_save_dir, self.stitch_save_dir]:
            os.makedirs(dir_path, exist_ok=True)

        
        if not os.path.isfile(self.slide_path):
            self.logger.error(f"Slide file does not exist: {self.slide_path}")
            raise FileNotFoundError(f"Slide file does not exist: {self.slide_path}")

        
        if self.method == "point" and not self.input_mask:
            self.logger.error("`input_mask` is required for point-based extraction.")
            raise ValueError("`input_mask` is required for point-based extraction.")

        
        if self.input_mask and not os.path.isfile(self.input_mask):
            self.logger.error(f"Input mask file does not exist: {self.input_mask}")
            raise FileNotFoundError(f"Input mask file does not exist: {self.input_mask}")

    def extract_patches(self):
        # Dictionary of params 
        params = {
            "input_img": self.slide_path,
            "patch_size": self.patch_size,
            "resolution": self.resolution,
            "units": self.units,
            "pad_mode": self.pad_mode,
            "pad_constant_values": self.pad_constant_values,
            "within_bound": self.within_bound
        }

        # Set the params 
        if self.method == "slidingwindow":
            params["stride"] = self.stride
            if self.input_mask:
                params["input_mask"] = self.input_mask
            params["min_mask_ratio"] = self.min_mask_ratio
        elif self.method == "point":
            params["locations_list"] = self.input_mask  
        else:
            self.logger.error(f"Unsupported method: {self.method}")
            return

        try:
            extractor = get_patch_extractor(self.method, **params)
            self.logger.info(f"Initialized {self.method} extractor for {self.slide_path}.")
        except Exception as e:
            self.logger.error(f"Failed to initialize extractor for {self.slide_path}: {e}")
            return

        h5_path = os.path.join(self.patch_save_dir, 'patches.h5')
        with h5py.File(h5_path, 'w') as h5f:
            # Determine patch shape
            first_patch = next(iter(extractor), None)
            if first_patch is None:
                self.logger.error("No patches extracted.")
                return

            patch_shape = first_patch.shape
            dtype = first_patch.dtype

            # Create dataset 
            dataset = h5f.create_dataset(
                'patches',
                shape=(0, *patch_shape),
                maxshape=(None, *patch_shape),
                dtype=dtype,
                chunks=True
            )

            # Append patches
            for i, patch in enumerate(extractor):
                dataset.resize(dataset.shape[0] + 1, axis=0)
                dataset[i] = patch
            self.logger.info(f"All patches saved to {h5_path}")
                    

    def validate_config(self):
        if not Path(self.slide_path).exists():
            self.logger.error(f"Slide does not exist: {self.slide_path}")
            raise FileNotFoundError(f"Slide does not exist: {self.slide_path}")
        if self.method == "point" and not self.input_mask:
            self.logger.error("`input_mask` is required for point-based extraction.")
            raise ValueError("`input_mask` is required for point-based extraction.")
