#!/usr/bin/env python3
"""
Synthetic Receipt Generator - Uses gpt-image-1 model to generate synthetic
receipts from real receipt images.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv
from jinja2 import Template
from tqdm import tqdm


def load_prompt_template(template_path: Path) -> str:
    """Load and render the Jinja2 prompt template."""
    with open(template_path, 'r') as f:
        template_content = f.read()

    template = Template(template_content)
    # Render with no variables for now (can be extended later)
    return template.render()


def generate_synthetic_receipt(
    client: OpenAI,
    input_image_path: Path,
    output_path: Path,
    prompt: str
) -> bool:
    """
    Generate a synthetic receipt from a real receipt image using gpt-image-1.

    Args:
        client: OpenAI client instance
        input_image_path: Path to the input receipt image
        output_path: Path to save the generated synthetic receipt
        prompt: The prompt instructing how to generate the synthetic receipt

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open and prepare the input image
        with open(input_image_path, "rb") as image_file:
            response = client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size="1024x1024",
                quality="high",
                n=1,
            )

        # Get the result
        if response.data[0].url:
            # Result is a URL - download it
            import requests
            from io import BytesIO
            from PIL import Image

            image_url = response.data[0].url
            img_response = requests.get(image_url)
            synthetic_img = Image.open(BytesIO(img_response.content))
            synthetic_img.save(output_path)
        elif response.data[0].b64_json:
            # Result is base64 encoded
            import base64
            from io import BytesIO
            from PIL import Image

            image_data = base64.b64decode(response.data[0].b64_json)
            synthetic_img = Image.open(BytesIO(image_data))
            synthetic_img.save(output_path)
        else:
            raise ValueError("No image data returned from API")

        return True

    except Exception as e:
        print(f"\n  Error generating synthetic receipt for {input_image_path.name}: {e}")
        return False


def main():
    """Main entry point for the synthetic receipt generator."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic receipts from real receipts using gpt-image-1"
    )
    parser.add_argument(
        "-n", "--num-files",
        type=int,
        default=None,
        help="Process only the first N files (default: process all)"
    )
    parser.add_argument(
        "--prompt-template",
        type=str,
        default="./main_prompt.jinja2",
        help="Path to the Jinja2 prompt template (default: ./main_prompt.jinja2)"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="./real_receipts",
        help="Input directory containing real receipt images (default: ./real_receipts)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./synthetic_receipts",
        help="Output directory for synthetic receipts (default: ./synthetic_receipts)"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in a .env file or export it in your shell.")
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Setup paths
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    prompt_template_path = Path(args.prompt_template)

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    # Validate prompt template
    if not prompt_template_path.exists():
        print(f"Error: Prompt template does not exist: {prompt_template_path}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Load prompt template
    print(f"Loading prompt template from: {prompt_template_path}")
    prompt = load_prompt_template(prompt_template_path)
    print(f"\nPrompt loaded successfully.")
    print(f"\n{'='*70}")
    print(f"Starting Synthetic Receipt Generation")
    print(f"{'='*70}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Model: gpt-image-1")
    print(f"{'='*70}\n")

    # Get list of receipt images
    receipt_files = sorted(list(input_dir.glob("*.png")))

    if not receipt_files:
        print(f"Error: No PNG files found in {input_dir}")
        sys.exit(1)

    # Limit number of files if specified
    if args.num_files is not None:
        receipt_files = receipt_files[:args.num_files]
        print(f"Processing first {len(receipt_files)} files (as requested)\n")
    else:
        print(f"Processing all {len(receipt_files)} files\n")

    # Process each receipt
    success_count = 0
    error_count = 0
    skipped_count = 0

    for receipt_file in tqdm(receipt_files, desc="Generating", unit="receipt"):
        # Use same filename for output
        output_path = output_dir / receipt_file.name

        # Skip if already exists
        if output_path.exists():
            skipped_count += 1
            continue

        # Generate synthetic receipt
        success = generate_synthetic_receipt(client, receipt_file, output_path, prompt)

        if success:
            success_count += 1
        else:
            error_count += 1

    print()
    print(f"{'='*70}")
    print(f"Synthetic Receipt Generation Complete!")
    print(f"{'='*70}")
    print(f"Successfully generated: {success_count}")
    print(f"Skipped (already exist): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
