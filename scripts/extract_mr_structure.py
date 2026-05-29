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

def split_into_questions(exercises_text: str) -> list[dict]:
    """Splits raw PDF exercises text into individual numbered questions."""
    # Matches a newline (or start of text) followed by a number, a period, and a space
    pattern = r'(?:^|\n)\s*(\d+)\.\s+'
    
    matches = list(re.finditer(pattern, exercises_text))
    questions = []
    
    if not matches:
        cleaned = exercises_text.strip()
        if cleaned:
            questions.append({
                "number": 1,
                "text": cleaned
            })
        return questions
        
    for idx, match in enumerate(matches):
        start_pos = match.end()
        end_pos = matches[idx+1].start() if idx + 1 < len(matches) else len(exercises_text)
        
        q_num = int(match.group(1))
        q_text = exercises_text[start_pos:end_pos].strip()
        
        # Clean up PDF artifacts (word hyphenations and line breaks)
        # 1. Join hyphenated words (e.g. trans- \n formation -> transformation)
        q_text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', q_text)
        # 2. Convert newlines to spaces
        q_text = re.sub(r'\s*\n\s*', ' ', q_text)
        # 3. Clean up double spaces
        q_text = re.sub(r'\s+', ' ', q_text)
        
        questions.append({
            "number": q_num,
            "text": q_text
        })
        
    return questions

def clean_chapter_title(title: str) -> str:
    """Removes leading numbers from chapter titles (e.g., '3 Velocity Kinematics' -> 'Velocity Kinematics')."""
    return re.sub(r'^\d+\s+', '', title).strip()

def main():
    print("====================================================================")
    print("        MODERN ROBOTICS TEXTBOOK EXERCISE EXTRACTOR (PDF)           ")
    print("====================================================================")
    
    pdf_path = "MR.pdf"
    out_path = "data/mr_chapters_exercises.json"
    
    if not os.path.exists(pdf_path):
        print(f"[!] Error: {pdf_path} not found in the current directory.")
        sys.exit(1)
        
    print(f"[*] Reading PDF '{pdf_path}'...")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"[✓] Successfully loaded PDF with {total_pages} pages.")
    
    print("[*] Traversing outlines and building table of contents...")
    outline = reader.outline
    if not outline:
        print("[!] Error: No outline/TOC found in the PDF. Outlines are required for structural parsing.")
        sys.exit(1)
        
    chapters = parse_outline_hierarchy(outline, reader)
    print(f"[✓] Reconstructed {len(chapters)} main sections from outline.")
    
    structured_chapters = []
    chapter_count = 1
    
    for i, ch in enumerate(chapters):
        title = ch["title"]
        page_idx = ch["page_idx"]
        
        # Determine ending page of this chapter
        next_ch_page_idx = chapters[i+1]["page_idx"] if i + 1 < len(chapters) else total_pages
        
        if page_idx is None:
            continue
            
        # Ignore appendices, indices, bibliographies in the main chapter count
        if title.lower().startswith(("appendix", "bibliography", "index", "summary of")):
            continue
            
        print(f"\n[*] Processing Chapter {chapter_count}: '{title}' (Pages {page_idx + 1} to {next_ch_page_idx})...")
        
        # Look for the 'Exercises' sub-item in this chapter
        exercises_node = None
        for sub in ch.get("sub_items", []):
            if "exercise" in sub["title"].lower():
                exercises_node = sub
                break
                
        if not exercises_node:
            print("  [-] No 'Exercises' outline section found. Skipping text extraction.")
            continue
            
        ex_start_idx = exercises_node["page_idx"]
        ex_end_idx = next_ch_page_idx - 1 # up to the next chapter's start
        
        print(f"  [✓] Found 'Exercises' outline starting at Page {ex_start_idx + 1}")
        
        # Extract text from the exercise pages
        ex_text_list = []
        for p_idx in range(ex_start_idx, ex_end_idx + 1):
            if p_idx < total_pages:
                ex_text_list.append(reader.pages[p_idx].extract_text())
                
        raw_text = "\n".join(ex_text_list)
        
        # Split into individual questions
        questions = split_into_questions(raw_text)
        print(f"  [✓] Extracted and parsed {len(questions)} exercise questions.")
        
        structured_chapters.append({
            "chapter_number": chapter_count,
            "chapter_id": f"ch{chapter_count}",
            "chapter_title": clean_chapter_title(title),
            "start_page": page_idx + 1,
            "end_page": next_ch_page_idx,
            "exercises_start_page": ex_start_idx + 1,
            "exercises_end_page": ex_end_idx + 1,
            "exercises_count": len(questions),
            "exercises": questions
        })
        
        chapter_count += 1

    # Save to JSON
    output_data = {
        "book": "Modern Robotics: Mechanics, Planning, and Control",
        "author": "Kevin M. Lynch and Frank C. Park",
        "extracted_chapters_count": len(structured_chapters),
        "chapters": structured_chapters
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("\n====================================================================")
    print("                     EXTRACTION SUMMARY                             ")
    print("====================================================================")
    print(f"  Structured Chapters Extracted : {len(structured_chapters)}")
    total_q = sum(ch["exercises_count"] for ch in structured_chapters)
    print(f"  Total Exercises Parsed       : {total_q}")
    print(f"  Output JSON Saved to         : {out_path}")
    print("====================================================================")
    print("[✓] Success! You can now feed this clean JSON directly to your AI agent.")

if __name__ == "__main__":
    main()
