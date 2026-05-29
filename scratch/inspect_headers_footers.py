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

# Let's inspect pages 58, 59, 60
for page_num in [57, 58, 59]:
    text = reader.pages[page_num].extract_text()
    lines = text.split('\n')
    print(f"=== Page {page_num+1} ===")
    print("First 3 lines:")
    for line in lines[:3]:
        print(f"  {repr(line)}")
    print("Last 3 lines:")
    for line in lines[-3:]:
        print(f"  {repr(line)}")
    print("-" * 50)
