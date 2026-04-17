import os
import sys
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # pyrefly: ignore [missing-import]
    from docling.document_converter import DocumentConverter
    has_docling = True
except ImportError:
    has_docling = False

def process_invoices(input_pattern, output_dir):
    if not has_docling:
        logger.error("Docling SDK not found. Please run 'pip install docling'.")
        return

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory initialized: {output_path}")

    # Initialize converter (This loads models, take a few seconds)
    logger.info("Initializing Docling DocumentConverter...")
    converter = DocumentConverter()

    # Find all PDFs recursively
    files = glob.glob(input_pattern, recursive=True)
    logger.info(f"Found {len(files)} candidate files.")

    success_count = 0
    fail_count = 0

    for file_file in files:
        try:
            abs_input = os.path.abspath(file_file)
            file_name = Path(abs_input).stem
            dest_file = output_path / f"{file_name}.md"

            logger.info(f"Processing: {file_name}...")
            
            result = converter.convert(abs_input)
            md_content = result.document.export_to_markdown()

            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            logger.info(f"Successfully saved to: {dest_file}")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {file_file}: {str(e)}")
            fail_count += 1

    logger.info("Batch Processing Finished.")
    logger.info(f"Summary: Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    # Use the pattern requested by user
    INPUT_PATTERN = r"Z:\invoiceV30\1月份\**\*.pdf"
    OUTPUT_DIR = r"z:\del"
    
    process_invoices(INPUT_PATTERN, OUTPUT_DIR)
