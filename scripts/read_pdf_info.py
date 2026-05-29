# /// script
# dependencies = [
#   "pypdf",
# ]
# ///

import os
import sys
from pypdf import PdfReader

# Reconfigure stdout for UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = "MR.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: {pdf_path} not found.")
    exit(1)

reader = PdfReader(pdf_path)
print(f"Number of pages: {len(reader.pages)}")

# Print metadata
meta = reader.metadata
print("\nMetadata:")
if meta:
    for key, val in meta.items():
        print(f"  {key}: {val}")
else:
    print("  No metadata found.")

# Read page 1 (often cover or title) and page 10
print("\nPage 1 text:")
print(reader.pages[0].extract_text()[:1000])

print("\nPage 10 text:")
print(reader.pages[9].extract_text()[:1000])
