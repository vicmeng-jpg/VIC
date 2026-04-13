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
        # Sanitize filename to avoid encoding issues with CJK
        book_name = Path(pdf_path).stem
        # Clean the name: only alphanumeric, underscores, hyphens, and CJK characters
        book_name = re.sub(r'[^\w\s\-\.\u4e00-\u9fff]', '_', book_name).strip()
        
        book_output = Path(output_root) / book_name
        image_output = book_output / "assets"
        os.makedirs(image_output, exist_ok=True)
        
        print(f"[*] Processing: {book_name}")
        
        # 1. Extract TOC for chapter awareness
        try:
            toc = self.extract_toc(pdf_path)
            print(f"[+] TOC found ({len(toc)} items)")
        except Exception as e:
            print(f"[!] TOC extraction failed (non-critical): {e}")
        
        # 2. Extract entire MD content using pymupdf4llm
        # We tune parameters to avoid aggressive table grouping that skips paragraphs
        print("[*] Extracting Markdown and Images (High-Fidelity Mode)...")
        try:
            # Using custom extraction parameters to favor text flow
            md_text = pymupdf4llm.to_markdown(
                pdf_path, 
                write_images=True, 
                image_path=str(image_output),
                image_format="png",
                show_progress=False
            )
            
            # If the MD text is suspiciously small, try a more aggressive 'Text-Only' extraction
            # for paragraphs as a fallback.
            if len(md_text) < 1000:
                print("[!] Result seems too small. Retrying with 'Table-Disabled' mode...")
                md_text = pymupdf4llm.to_markdown(
                    pdf_path,
                    write_images=True,
                    image_path=str(image_output),
                    image_format="png",
                    # Some versions support layout=False or specific table exclusion
                )
            
            print(f"[+] Extracted MD length: {len(md_text)} bytes")
            if len(md_text) < 500:
                print("[WARNING] Extracted text is unusually short. Please check if OCR was successful.")
                
        except Exception as e:
            print(f"[ERROR] Markdown extraction failed: {e}")
            return None
        
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
    input_dir = "./inbox"
    output_dir = "./processed"
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Please put your PDFs in {input_dir}")
    else:
        for file in os.listdir(input_dir):
            if file.lower().endswith(".pdf"):
                preprocessor.process_pdf(os.path.join(input_dir, file), output_dir)
