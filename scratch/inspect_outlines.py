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

def print_outline(lst, depth=0):
    for item in lst:
        if isinstance(item, list):
            print_outline(item, depth + 1)
        else:
            title = item.get('/Title')
            page_idx = None
            try:
                page_idx = reader.get_destination_page_number(item)
            except Exception:
                pass
            print("  " * depth + f"- {title} (Page {page_idx + 1 if page_idx is not None else 'N/A'})")

if outline:
    print_outline(outline)  # print all items
else:
    print("No outline found.")
