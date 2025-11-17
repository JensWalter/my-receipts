#!/usr/bin/env python3
"""
Convert all receipts from raw_data to PNG format in real_receipts folder.
Converts filepath to filename format: 2020/de/cafe/feiste-20200815.pdf -> 2020_de_cafe_feiste-20200815.png
"""

import os
import sys
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm


def convert_filepath_to_filename(filepath: Path, base_dir: Path) -> str:
    """
    Convert a filepath to a flattened filename.

    Example: raw_data/2020/de/cafe/feiste-20200815.pdf -> 2020_de_cafe_feiste-20200815.png
    """
    # Get relative path from base_dir
    relative_path = filepath.relative_to(base_dir)

    # Convert path separators to underscores
    filename = str(relative_path).replace(os.sep, '_')

    # Remove original extension and add .png
    filename_base = filename.rsplit('.', 1)[0]
    return f"{filename_base}.png"


def convert_pdf_to_png(pdf_path: Path, output_path: Path) -> bool:
    """Convert PDF to PNG (first page only) using PyMuPDF."""
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)

        # Get the first page
        page = doc[0]

        # Render page to pixmap with decent resolution (150 DPI)
        zoom = 150 / 72  # Convert DPI to zoom factor
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Save as PNG
        pix.save(output_path)

        # Close document
        doc.close()
        return True
    except Exception as e:
        print(f"  Error converting PDF {pdf_path.name}: {e}")
        return False


def convert_image_to_png(image_path: Path, output_path: Path) -> bool:
    """Convert image file to PNG."""
    try:
        img = Image.open(image_path)

        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save as PNG
        img.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"  Error converting image {image_path.name}: {e}")
        return False


def main():
    # Setup paths
    raw_data_dir = Path('./raw_data')
    output_dir = Path('./real_receipts')

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("Converting receipts to PNG format...")
    print(f"Source: {raw_data_dir}")
    print(f"Destination: {output_dir}")
    print()

    # Find all receipt files
    receipt_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.PDF', '.JPG', '.JPEG', '.PNG']
    receipt_files = []

    for ext in receipt_extensions:
        receipt_files.extend(raw_data_dir.glob(f'**/*{ext}'))

    # Remove duplicates (in case of case-insensitive filesystems)
    receipt_files = list(set(receipt_files))
    receipt_files.sort()

    print(f"Found {len(receipt_files)} receipt files to convert")
    print()

    # Convert all files
    success_count = 0
    error_count = 0

    for filepath in tqdm(receipt_files, desc="Converting", unit="file"):
        # Generate output filename
        output_filename = convert_filepath_to_filename(filepath, raw_data_dir)
        output_path = output_dir / output_filename

        # Skip if already exists
        if output_path.exists():
            success_count += 1
            continue

        # Convert based on file type
        extension = filepath.suffix.lower()

        if extension == '.pdf':
            success = convert_pdf_to_png(filepath, output_path)
        else:
            success = convert_image_to_png(filepath, output_path)

        if success:
            success_count += 1
        else:
            error_count += 1

    print()
    print("Conversion complete!")
    print(f"Successfully converted: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
