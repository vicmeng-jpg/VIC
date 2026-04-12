import os
import re
import json
import fitz  # PyMuPDF
import pymupdf4llm
from opencc import OpenCC
from pathlib import Path

class MaritimePreprocessor:
    def __init__(self, dictionary_path=None):
        # Initialize OpenCC (Simplified to Traditional Taiwan with phrase conversion)
        self.cc = OpenCC('s2twp')  
        self.custom_dict = {}
        if dictionary_path and os.path.exists(dictionary_path):
            with open(dictionary_path, 'r', encoding='utf-8') as f:
                self.custom_dict = json.load(f)
        
        # Prepare regex for custom replacements (longest match first)
        if self.custom_dict:
            sorted_keys = sorted(self.custom_dict.keys(), key=len, reverse=True)
            self.replace_pattern = re.compile('|'.join(re.escape(k) for k in sorted_keys))
        else:
            self.replace_pattern = None

    def convert_text(self, text):
        """Standard S2T followed by custom dictionary overrides."""
        # 1. Standard OpenCC conversion
        converted = self.cc.convert(text)
        
        # 2. Custom Dictionary Overrides
        if self.replace_pattern:
            def replace_match(match):
                return self.custom_dict[match.group(0)]
            converted = self.replace_pattern.sub(replace_match, converted)
            
        return converted

    def extract_toc(self, pdf_path):
        """Extract Table of Contents from PDF metadata."""
        doc = fitz.open(pdf_path)
        toc = doc.get_toc() # [[lvl, title, page], ...]
        doc.close()
        return toc

    def process_pdf(self, pdf_path, output_root):
        book_name = Path(pdf_path).stem
        book_output = Path(output_root) / book_name
        image_output = book_output / "assets"
        os.makedirs(image_output, exist_ok=True)
        
        print(f"[*] Processing: {book_name}")
        
        # 1. Extract TOC for chapter awareness
        toc = self.extract_toc(pdf_path)
        
        # 2. Extract entire MD content using pymupdf4llm
        # Note: In a production script, we might extract page-by-page to keep memory low,
        # but for NotebookLM optimization, we'll process chunks or the whole thing.
        print("[*] Extracting Markdown and Images...")
        md_text = pymupdf4llm.to_markdown(
            pdf_path, 
            write_images=True, 
            image_path=str(image_output),
            image_format="png"
        )
        
        # 3. Perform S2T Conversion
        print("[*] Performing S2T Conversion with Custom Dictionary...")
        final_md = self.convert_text(md_text)
        
        # 4. Save the Final Markdown
        output_file = book_output / f"{book_name}_Full.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_md)
            
        print(f"[+] Success! Output saved to: {output_file}")
        return output_file

if __name__ == "__main__":
    # Example usage logic
    dict_file = "maritime_custom_dict.json"
    preprocessor = MaritimePreprocessor(dict_file)
    
    # Ideally, scan a 'input' folder
    input_dir = "../inbox"
    output_dir = "../processed"
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Please put your PDFs in {input_dir}")
    else:
        for file in os.listdir(input_dir):
            if file.lower().endswith(".pdf"):
                preprocessor.process_pdf(os.path.join(input_dir, file), output_dir)
