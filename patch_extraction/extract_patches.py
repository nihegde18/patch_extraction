# extract_patches.py

import os
from pathlib import Path
import logging
import h5py
from src.config import load_config_file
from src.patch_logger import setup_logging 
from src.patch_extraction.PatchExtractorModule import PatchExtractorModule
  # Correct class import

if __name__ == "__main__":
    # Load configuration from YAML file
    config = load_config_file("configs/default_config.yml")
    
    # Setup logging
    logger = setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file=config.get("log_file", "logs/patch_extraction.log")
    )
    
    logger.info("Starting Patch Extraction Process")
    
    # Define input and output directories
    input_dir = config.get("input_dir", "data/slides")
    output_dir = config.get("output_dir", "data/patches")
    os.makedirs(output_dir, exist_ok=True)
    
    # Gather all slide files
    try:
        slides = sorted([
            f for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ])
        logger.info(f"Found {len(slides)} slides to process.")
    except Exception as e:
        logger.error(f"Failed to list slides in {input_dir}: {e}")
        slides = []
    
    # Iterate over each slide and extract patches
    for slide in slides:
        slide_path = os.path.join(input_dir, slide)
        logger.info(f"Processing slide: {slide}")
        
        try:
            extractor = PatchExtractorModule(slide_path, config, logger)  # Correct class name
            extractor.extract_patches()
        except Exception as e:
            logger.error(f"An error occurred while processing {slide}: {e}")
            continue   
    
    logger.info("Patch Extraction Process Completed")

    

