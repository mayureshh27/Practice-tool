# /// script
# dependencies = [
#   "pypdf",
# ]
# ///

import os
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = "MR.pdf"
if not os.path.exists(pdf_path):
    print(f"Error: {pdf_path} not found.")
    exit(1)

reader = PdfReader(pdf_path)
toc_text = []

# Extract pages 5 to 18 (typically where table of contents lies in a book)
start_page = 4
end_page = 18

for page_num in range(start_page, min(end_page, len(reader.pages))):
    text = reader.pages[page_num].extract_text()
    if "Contents" in text or "Chapter" in text or "CONTENTS" in text:
        toc_text.append(f"--- Page {page_num + 1} ---")
        toc_text.append(text)

os.makedirs("scratch", exist_ok=True)
with open("scratch/toc.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(toc_text))

print(f"Extracted TOC text from pages {start_page+1} to {end_page} to scratch/toc.txt")
