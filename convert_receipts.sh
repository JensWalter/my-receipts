#!/bin/bash
set -e

# Create output directory
mkdir -p ./real_receipts

echo "Converting receipts to PNG format..."
echo "Source: ./raw_data"
echo "Destination: ./real_receipts"
echo ""

# Counter for tracking progress
count=0
total=$(find ./raw_data -type f \( -iname "*.pdf" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)

echo "Found $total receipt files to convert"
echo ""

# Find all receipt files and convert them
find ./raw_data -type f \( -iname "*.pdf" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | while read -r filepath; do
    # Remove the ./raw_data/ prefix
    relative_path="${filepath#./raw_data/}"

    # Convert slashes to underscores and get the directory path
    # e.g., 2020/de/cafe/feiste-20200815.pdf -> 2020_de_cafe_feiste-20200815
    filename=$(echo "$relative_path" | sed 's/\//_/g')

    # Remove the original extension and add .png
    filename_base="${filename%.*}"
    output_file="./real_receipts/${filename_base}.png"

    # Increment counter
    count=$((count + 1))

    # Convert the file to PNG
    echo "[$count/$total] Converting: $relative_path -> ${filename_base}.png"

    # Check file extension to determine conversion method
    extension="${filepath##*.}"
    extension_lower=$(echo "$extension" | tr '[:upper:]' '[:lower:]')

    if [ "$extension_lower" = "pdf" ]; then
        # Convert PDF to PNG using ImageMagick
        # -density 150 ensures good quality
        # -flatten removes transparency
        # [0] takes only the first page
        convert -density 150 "${filepath}[0]" -flatten "$output_file" 2>/dev/null || {
            echo "  Warning: Failed to convert $filepath, trying alternative method..."
            pdftoppm -png -f 1 -l 1 -singlefile "$filepath" "${output_file%.png}" 2>/dev/null || {
                echo "  Error: Could not convert $filepath"
            }
        }
    else
        # Convert image files (JPG, JPEG, PNG) to PNG
        convert "$filepath" -flatten "$output_file" 2>/dev/null || {
            echo "  Error: Could not convert $filepath"
        }
    fi
done

echo ""
echo "Conversion complete!"
echo "Total files processed: $count"
echo "Output directory: ./real_receipts"
