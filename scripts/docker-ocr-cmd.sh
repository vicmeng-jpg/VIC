#!/bin/bash
# Docker OCRmyPDF optimization for Intel Core Ultra 7 (Meteor Lake)
# This command runs OCR on a PDF and uses multi-threading to speed up the process.

INPUT_FILE=$1
OUTPUT_FILE=$2

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: ./docker-ocr-cmd.sh <input.pdf> <output_searchable.pdf>"
    exit 1
fi

docker run --rm -v "$(pwd):/home/docker" jbarlow83/ocrmypdf \
    --language chi_sim \
    --optimize 1 \
    --jobs 8 \
    "/home/docker/$INPUT_FILE" \
    "/home/docker/$OUTPUT_FILE"

echo "[+] OCR Complete: $OUTPUT_FILE"
