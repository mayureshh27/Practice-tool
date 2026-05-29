# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
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

# Let's check Chapter 2 ("Configuration Space", which starts page 31)
# The outline item for Configuration Space is the 4th item (index 3)
ch2 = chapters[4]
print(f"Chapter 2 Title: {ch2['title']}")
exercises_node = [sub for sub in ch2["sub_items"] if "exercises" in sub["title"].lower()][0]
ex_start = exercises_node["page_idx"]
next_ch_start = chapters[5]["page_idx"]

ex_text_list = []
for p in range(ex_start, next_ch_start):
    ex_text_list.append(reader.pages[p].extract_text())
full_ex_text = "\n".join(ex_text_list)

# Let's find all occurrences of "Exercise 2." and print their surrounding text (e.g. 50 characters before and after)
for match in re.finditer(r'Exercise\s+2\.(\d+)', full_ex_text):
    start = max(0, match.start() - 30)
    end = min(len(full_ex_text), match.end() + 70)
    snippet = full_ex_text[start:end].replace('\n', ' [NL] ')
    print(f"Match: '{match.group(0)}' at pos {match.start()} | Snippet: ...{snippet}...")
