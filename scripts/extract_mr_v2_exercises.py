# /// script
# dependencies = [
#   "pypdf",
# ]
# ///

import os
import sys
import json
import re
from pypdf import PdfReader

# Reconfigure stdout for UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

def parse_outline_hierarchy(outline, reader):
    """Parses the outline list from pypdf into a clean parent-child hierarchy."""
    flat_structure = []
    
    def walk(lst, parent=None):
        for item in lst:
            if isinstance(item, list):
                # These are sub-items of the last parsed item
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

def clean_page_text(text: str) -> str:
    """Removes page footers and normalizes Unicode ligatures."""
    # Remove the preprint footer on every page
    footer_pattern = r'(?i)(?:dec\s+2019|may\s+2017)\s+preprint\s+of\s+(?:updated\s+ﬁrst\s+edition\s+of\s+)?Modern\s+Robotics\s*(?:,\s*\d{4})?\.?\s*http://modernrobotics\.org'
    text = re.sub(footer_pattern, '', text)
    
    # Replace common PDF ligatures
    text = text.replace('\ufb01', 'fi').replace('\ufb02', 'fl').replace('\ufb03', 'ffi')
    return text

def smart_clean_exercise_text(text: str) -> str:
    """Intelligently cleans exercise text: joins line breaks in paragraphs,
    but preserves equations, lists, and matrix structures."""
    # 1. Join hyphenations at line ends: e.g. trans- \n formation -> transformation
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # Check if this line looks like a displayed equation or matrix row
        # (Contains brackets, equal signs, or ends with an equation label like (3.99))
        is_equation = (
            bool(re.search(r'\(\d+\.\d+\)\s*$', line_str)) or 
            line_str.startswith('Tab =') or 
            line_str.startswith('Tcb =') or 
            line_str.startswith('T =') or 
            line_str.startswith('R =') or 
            '[' in line_str or 
            ']' in line_str or 
            line_str.startswith('') or 
            line_str.startswith('') or
            line_str.startswith('') or
            line_str.startswith('') or
            line_str.startswith('') or
            line_str.startswith('')
        )
        
        # Check if line looks like a list item: e.g. "(a) What is...", "(1) Calculate..."
        is_list_item = bool(re.match(r'^\([a-zA-Z0-9]\)', line_str))
        
        # Determine if we should join this line with the previous one
        if cleaned_lines and not is_list_item and not is_equation:
            prev_line = cleaned_lines[-1].strip()
            # Don't join if the previous line was an equation, matrix, or ended with terminal punctuation
            prev_is_terminal = (
                bool(re.search(r'\(\d+\.\d+\)\s*$', prev_line)) or 
                '[' in prev_line or 
                ']' in prev_line or 
                prev_line.endswith(':') or 
                prev_line.endswith('.') or 
                prev_line.endswith('?') or
                prev_line.startswith('') or
                prev_line.endswith('') or
                prev_line.endswith('')
            )
            if not prev_is_terminal:
                # Join with a single space
                cleaned_lines[-1] = cleaned_lines[-1] + " " + line_str
                continue
                
        cleaned_lines.append(line_str)
        
    return "\n".join(cleaned_lines)

def clean_chapter_title(title: str) -> str:
    """Removes leading numbers and section markers from chapter titles."""
    return re.sub(r'^\d+\s+', '', title).strip()

def main():
    print("====================================================================")
    print("        MODERN ROBOTICS V2 STRUCTURED EXERCISE EXTRACTOR            ")
    print("====================================================================")
    
    pdf_path = "MR-v2.pdf"
    alt_pdf_path = "MR.pdf"
    out_path = "data/mr_v2_exercises.json"
    
    # Fallback check
    if not os.path.exists(pdf_path):
        if os.path.exists(alt_pdf_path):
            print(f"[!] Warning: '{pdf_path}' not found. Falling back to '{alt_pdf_path}'.")
            pdf_path = alt_pdf_path
        else:
            print(f"[!] Error: Neither '{pdf_path}' nor '{alt_pdf_path}' was found in the current directory.")
            print("Please place the book PDF in the current folder.")
            sys.exit(1)
            
    print(f"[*] Loading PDF '{pdf_path}'...")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"[✓] Loaded PDF with {total_pages} pages.")
    
    print("[*] Reconstructing outline structure...")
    outline = reader.outline
    if not outline:
        print("[!] Error: No outline found in the PDF. Outlines are required for structured extraction.")
        sys.exit(1)
        
    chapters = parse_outline_hierarchy(outline, reader)
    print(f"[✓] Outline parsed. Found {len(chapters)} main outline nodes.")
    
    # The 12 core chapters we expect (skipping Chapter 1 "Preview" since it has no exercises)
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
    
    structured_chapters = []
    chapter_counter = 2 # In Modern Robotics, Configuration Space is Chapter 2
    
    for ch in chapters:
        title = ch["title"]
        page_idx = ch["page_idx"]
        
        if title not in expected_chapters or page_idx is None:
            continue
            
        print(f"\n[*] Processing Chapter {chapter_counter}: '{title}'...")
        
        # Locate the sub-item 'Exercises'
        exercises_node = None
        for sub in ch.get("sub_items", []):
            if "exercises" in sub["title"].lower():
                exercises_node = sub
                break
                
        if not exercises_node:
            print(f"  [-] Warning: No 'Exercises' sub-node found for Chapter {chapter_counter}. Skipping.")
            chapter_counter += 1
            continue
            
        ex_start = exercises_node["page_idx"]
        
        # The exercises run up to the start of the next chapter or appendix
        next_ch_page = total_pages
        ch_idx = chapters.index(ch)
        for k in range(ch_idx + 1, len(chapters)):
            if chapters[k]["page_idx"] is not None:
                next_ch_page = chapters[k]["page_idx"]
                break
                
        ex_end = next_ch_page - 1
        print(f"  [✓] Exercises range: Page {ex_start + 1} to Page {ex_end + 1} (PDF Page indices {ex_start} to {ex_end})")
        
        # Extract and clean text page-by-page
        ex_pages_text = []
        for p in range(ex_start, ex_end + 1):
            if p < total_pages:
                raw_text = reader.pages[p].extract_text()
                clean_text = clean_page_text(raw_text)
                ex_pages_text.append(clean_text)
                
        full_ex_text = "\n".join(ex_pages_text)
        
        # Precise regex to match exercise headers like "Exercise C.N"
        pattern = rf'(?:\n|^)\s*Exercise\s+{chapter_counter}\.(\d+)\b'
        matches = list(re.finditer(pattern, full_ex_text))
        
        print(f"  [✓] Found {len(matches)} exercise headers using pattern: '{pattern}'")
        
        parsed_exercises = []
        for idx, match in enumerate(matches):
            ex_num = int(match.group(1))
            label = f"Exercise {chapter_counter}.{ex_num}"
            
            # Text starts after this header and runs until the next header or end of section
            start_pos = match.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_ex_text)
            
            raw_q_text = full_ex_text[start_pos:end_pos].strip()
            
            # Clean page headers if they remain at the very start of the exercise text
            # E.g. "38 2.8. Exercises" or "Chapter 2. Configuration Space 39"
            header_clean_pattern = r'(?m)^\s*(?:\d+\s+\d+\.\d+\.\s+Exercises|Chapter\s+\d+\.\s+.*\s+\d+|\d+\.\d+\.\s+Exercises\s+\d+)\s*$'
            raw_q_text = re.sub(header_clean_pattern, '', raw_q_text).strip()
            
            # Smart formatting clean
            cleaned_q_text = smart_clean_exercise_text(raw_q_text)
            
            parsed_exercises.append({
                "exercise_id": f"exercise-{chapter_counter}-{ex_num}",
                "number": ex_num,
                "label": label,
                "text": cleaned_q_text
            })
            
        structured_chapters.append({
            "chapter_number": chapter_counter,
            "chapter_id": f"ch{chapter_counter}",
            "chapter_title": clean_chapter_title(title),
            "start_page": page_idx + 1,
            "end_page": next_ch_page,
            "exercises_start_page": ex_start + 1,
            "exercises_end_page": ex_end + 1,
            "exercises_count": len(parsed_exercises),
            "exercises": parsed_exercises
        })
        
        chapter_counter += 1

    # Package output database
    output_data = {
        "book": "Modern Robotics: Mechanics, Planning, and Control",
        "version": "v2",
        "authors": "Kevin M. Lynch and Frank C. Park",
        "extracted_chapters_count": len(structured_chapters),
        "chapters": structured_chapters
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("\n====================================================================")
    print("                     EXTRACTION COMPLETE                            ")
    print("====================================================================")
    print(f"  Total Chapters Extracted    : {len(structured_chapters)}")
    total_exercises = sum(ch["exercises_count"] for ch in structured_chapters)
    print(f"  Total Exercises Parsed       : {total_exercises}")
    print(f"  Output JSON Database Path    : {out_path}")
    print("====================================================================")
    
    # Detailed breakdown table
    print("\nChapter-wise Exercise Count Table:")
    print("-" * 60)
    print(f"{'Ch':<4} | {'Chapter Title':<35} | {'Exercises':<10}")
    print("-" * 60)
    for ch in structured_chapters:
        print(f"{ch['chapter_number']:<4} | {ch['chapter_title']:<35} | {ch['exercises_count']:<10}")
    print("-" * 60)
    print("[✓] Perfect Extraction Successful! The clean JSON database is ready.")

if __name__ == "__main__":
    main()
