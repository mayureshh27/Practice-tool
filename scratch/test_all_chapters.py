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

# Map our book chapters (2 to 13) to the indices in the outline
# Let's locate the chapters dynamically based on titles
main_chapters = []
chapter_num_map = {}

# Outline items:
# 4: Configuration Space (Page 31) -> Chapter 2
# 6: Rigid-Body Motions (Page 77) -> Chapter 3
# 8: Forward Kinematics (Page 155) -> Chapter 4
# 10: Velocity Kinematics and Statics (Page 189) -> Chapter 5
# 12: Inverse Kinematics (Page 237) -> Chapter 6
# 14: Kinematics of Closed Chains (Page 263) -> Chapter 7
# 16: Dynamics of Open Chains (Page 289) -> Chapter 8
# 18: Trajectory Generation (Page 347) -> Chapter 9
# 20: Motion Planning (Page 375) -> Chapter 10
# 22: Robot Control (Page 425) -> Chapter 11
# 24: Grasping and Manipulation (Page 483) -> Chapter 12
# 26: Wheeled Mobile Robots (Page 535) -> Chapter 13

# We can dynamically identify the actual chapter number based on order of occurrence of chapters starting with Configuration Space
expected_chapters = [
    "Configuration Space",
    "Rigid-Body Motions",
    "Forward Kinematics",
    "Velocity Kinematics and Statics",
    "Inverse Kinematics",
    "Kinematics of Closed Chains",
    "Dynamics of Open Chains",
    "Trajectory Generation",
    "Motion Planning",
    "Robot Control",
    "Grasping and Manipulation",
    "Wheeled Mobile Robots"
]

chapter_counter = 2
for ch in chapters:
    title = ch["title"]
    if title in expected_chapters:
        ch_num = chapter_counter
        chapter_counter += 1
        
        exercises_node = None
        for sub in ch.get("sub_items", []):
            if "exercises" in sub["title"].lower():
                exercises_node = sub
                break
                
        if exercises_node:
            ex_start = exercises_node["page_idx"]
            # Find next outline chapter page
            next_ch_page = len(reader.pages)
            # Find the outline node after this chapter in chapters
            found_idx = chapters.index(ch)
            for k in range(found_idx + 1, len(chapters)):
                if chapters[k]["page_idx"] is not None:
                    next_ch_page = chapters[k]["page_idx"]
                    break
            
            ex_text_list = []
            for p in range(ex_start, next_ch_page):
                ex_text_list.append(reader.pages[p].extract_text())
            full_ex_text = "\n".join(ex_text_list)
            
            # Using our precise header match regex
            pattern = rf'(?:\n|^)\s*Exercise\s+{ch_num}\.(\d+)\b'
            matches = list(re.finditer(pattern, full_ex_text))
            
            print(f"Chapter {ch_num}: '{title}' (Pages {ch['page_idx']+1} - {next_ch_page}, Exercises on page {ex_start+1})")
            print(f"  Regex '{pattern}' found {len(matches)} exercises.")
            if len(matches) > 0:
                print(f"  First exercise number: {matches[0].group(1)}")
                print(f"  Last exercise number: {matches[-1].group(1)}")
            print("-" * 60)
