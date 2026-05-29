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
    print("Error: MR.pdf not found.")
    sys.exit(1)

reader = PdfReader(pdf_path)
print("Outline:")
outline = reader.outline

def print_outline(item, depth=0):
    indent = "  " * depth
    if isinstance(item, list):
        for sub_item in item:
            print_outline(sub_item, depth + 1)
    else:
        title = item.get('/Title')
        page_num = None
        try:
            # Get destination page number
            dest = reader.get_destination_page_number(item)
            page_num = dest + 1
        except Exception:
            pass
        print(f"{indent}- {title} (Page {page_num})")

if outline:
    print_outline(outline)
else:
    print("No outline found.")
