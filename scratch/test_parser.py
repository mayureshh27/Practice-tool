# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
import os
import sys
import re
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

# Let's inspect the exercises of Chapter 2 (Configuration Space) and Chapter 3 (Rigid-Body Motions)
for idx, ch in enumerate(chapters):
    title = ch["title"]
    page_idx = ch["page_idx"]
    if page_idx is None:
        continue
    
    exercises_node = None
    for sub in ch.get("sub_items", []):
        if "exercises" in sub["title"].lower():
            exercises_node = sub
            break
            
    if exercises_node:
        ex_start_page = exercises_node["page_idx"]
        next_ch_page = chapters[idx+1]["page_idx"] if idx + 1 < len(chapters) else len(reader.pages)
        print(f"Chapter: {title} (Starts Page {page_idx+1})")
        print(f"  Exercises outline found starting at page {ex_start_page+1} to {next_ch_page}")
        
        first_ex_page_text = reader.pages[ex_start_page].extract_text()
        print(f"  First 500 chars of exercises page text:")
        print("-" * 50)
        print(first_ex_page_text[:800].replace('\ufb01', 'fi').replace('\ufb02', 'fl'))
        print("-" * 50)
        
        ex_text_list = []
        for p in range(ex_start_page, next_ch_page):
            ex_text_list.append(reader.pages[p].extract_text())
        full_ex_text = "\n".join(ex_text_list)
        
        matches = re.findall(r'Exercise\s+(\d+)\.(\d+)', full_ex_text)
        print(f"  Found {len(matches)} matches of 'Exercise X.Y': {matches[:10]}")
        print("\n")
