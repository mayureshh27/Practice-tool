# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
import os
from pypdf import PdfReader

pdf_path = "MR-v2.pdf"
reader = PdfReader(pdf_path)
outline = reader.outline

def print_top_level(lst):
    for idx, item in enumerate(lst):
        if not isinstance(item, list):
            title = item.get('/Title')
            page_idx = None
            try:
                page_idx = reader.get_destination_page_number(item)
            except Exception:
                pass
            print(f"{idx}: {title} (Page {page_idx + 1 if page_idx is not None else 'N/A'})")

if outline:
    print_top_level(outline)
else:
    print("No outline found.")
