# Receipt Processing Scripts

This repository contains scripts for processing real receipts and generating synthetic versions using OpenAI's gpt-image-1 model.

## Directory Structure

- `raw_data/` - Original receipt files organized by year
- `real_receipts/` - Converted PNG receipt files (flattened naming)
- `synthetic_receipts/` - AI-generated synthetic receipts
- `main_prompt.jinja2` - Prompt template for synthetic receipt generation

## Setup

1. Install Python dependencies:
```bash
pip install Pillow PyMuPDF tqdm openai python-dotenv jinja2 requests
```

2. Create a `.env` file with your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Scripts

### 1. Convert Receipts to PNG (`convert_receipts.py`)

Converts all receipts from `raw_data/` to PNG format in `real_receipts/`. Filename structure is flattened: `2020/de/cafe/feiste-20200815.pdf` → `2020_de_cafe_feiste-20200815.png`

**Usage:**
```bash
./convert_receipts.py
```

### 2. Generate Synthetic Receipts (`generate_synthetic_receipts.py`)

Uses OpenAI's gpt-image-1 model to generate synthetic receipts based on real ones.

**Usage:**
```bash
# Process all receipts
./generate_synthetic_receipts.py

# Process only first 10 receipts (for testing)
./generate_synthetic_receipts.py -n 10

# Custom directories and prompt template
./generate_synthetic_receipts.py \
  --input-dir ./real_receipts \
  --output-dir ./synthetic_receipts \
  --prompt-template ./main_prompt.jinja2
```

**Options:**
- `-n, --num-files N` - Process only the first N files (default: process all)
- `--prompt-template PATH` - Path to Jinja2 prompt template (default: ./main_prompt.jinja2)
- `--input-dir PATH` - Input directory (default: ./real_receipts)
- `--output-dir PATH` - Output directory (default: ./synthetic_receipts)

## Prompt Customization

Edit `main_prompt.jinja2` to customize how synthetic receipts are generated. The prompt instructs the AI to:
- Match the visual style and quality of the original
- Preserve language, currency, and format
- Change the total sum and company name
- Optionally modify other details like dates and transaction IDs

## Notes

- The conversion script uses PyMuPDF for PDF conversion and PIL for image processing
- Synthetic receipt generation requires an OpenAI API key with access to gpt-image-1
- Generated images are 1024x1024 PNG files at high quality
