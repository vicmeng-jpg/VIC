import fitz  # PyMuPDF
import os
import sys
from pathlib import Path

def rasterize_pdf(pdf_path, output_dir, pages=None, dpi=300):
    """
    Step 1: Convert PDF pages into images.
    Step 2: Combine those images back into a 'Flattened' PDF.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return False

    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    
    page_indices = range(len(doc))
    if pages:
        try:
            start, end = map(int, pages.split('-'))
            page_indices = range(start - 1, min(end, len(doc)))
        except:
            print("Invalid page range format. Using all pages.")

    print(f"[*] Rasterizing {len(page_indices)} pages at {dpi} DPI...")
    
    # New PDF to hold flattened pages
    new_doc = fitz.open()
    
    for i in page_indices:
        page = doc.load_page(i)
        # Convert to high-res image
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_data = pix.tobytes()
        
        # Create a new page with the same size
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        # Insert the image filling the whole page
        new_page.insert_image(new_page.rect, stream=img_data)
        
        if (i+1) % 10 == 0:
            print(f"    [+] Flattened {i+1} pages")
            
    flattened_path = os.path.join(output_dir, "flattened_input.pdf")
    new_doc.save(flattened_path)
    new_doc.close()
    doc.close()
    
    print(f"[+] Flattened PDF created: {flattened_path}")
    return flattened_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py rasterize_pdf.py <input.pdf> <output_dir> [pages]")
    else:
        pdf = sys.argv[1]
        out = sys.argv[2]
        pgs = sys.argv[3] if len(sys.argv) > 3 else None
        rasterize_pdf(pdf, out, pgs)
