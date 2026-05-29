# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = "MR-v2.pdf"
reader = PdfReader(pdf_path)
outline = reader.outline

def parse_outline_hierarchy(outline, reader):
    flat_structure = []
    def walk(lst, parent=None):
        for item in lst:
            if isinstance(item, list):
                prev_node = flat_structure[-1] if flat_structure else None
                if prev_node:
                    walk(item, parent=prev_node)
            else:
                title = item.get('/Title')
                page_idx = None
                try:
                    page_idx = reader.get_destination_page_number(item)
                except Exception:
                    pass
                
                node = {
                    "title": title,
                    "page_idx": page_idx,
                    "sub_items": []
                }
                
                if parent is not None:
                    parent["sub_items"].append(node)
                else:
                    flat_structure.append(node)
    walk(outline)
    return flat_structure

chapters = parse_outline_hierarchy(outline, reader)
for ch in chapters:
    if "preview" in ch["title"].lower():
        print(f"Preview sub-items:")
        for sub in ch["sub_items"]:
            print(f"  - {sub['title']} (Page {sub['page_idx']+1})")
