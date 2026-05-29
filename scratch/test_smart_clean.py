# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
import sys
import re
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

def smart_clean_text(text: str) -> str:
    # Join hyphenations at line ends
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        line_str = line.strip()
        if not line_str:
            continue
            
        # Check if this line looks like a displayed equation
        is_equation = bool(re.search(r'\(\d+\.\d+\)\s*$', line_str)) or line_str.startswith('Tab =') or line_str.startswith('T cb =') or '[' in line_str or ']' in line_str or line_str.startswith('T =') or line_str.startswith('R =')
        
        # Check if next line looks like a list item
        is_list_item = bool(re.match(r'^\([a-z]\)', line_str))
        
        # If previous line exists and we want to append to it
        if cleaned_lines and not is_list_item and not is_equation:
            prev_line = cleaned_lines[-1].strip()
            prev_is_eq = bool(re.search(r'\(\d+\.\d+\)\s*$', prev_line)) or '[' in prev_line or ']' in prev_line or prev_line.endswith(':') or prev_line.endswith('.') or prev_line.endswith('?')
            if not prev_is_eq:
                cleaned_lines[-1] = cleaned_lines[-1] + " " + line_str
                continue
                
        cleaned_lines.append(line_str)
        
    return "\n".join(cleaned_lines)

pdf_path = "MR-v2.pdf"
reader = PdfReader(pdf_path)

# Let's inspect the exercises of Chapter 3 (Rigid-Body Motions)
# Exercises start at page 134 (index 133)
ex_text = reader.pages[134].extract_text()
# Let's clean the footer
ex_text = re.sub(r'(?i)Dec\s+2019\s+preprint.*', '', ex_text)

print("=== Raw Text (first 1000 chars) ===")
print(ex_text[:1000])
print("\n" + "="*50 + "\n")
print("=== Cleaned Text (first 1000 chars) ===")
print(smart_clean_text(ex_text[:1000]))
