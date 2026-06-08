"""
ResumeSense AI - PDF Text Extractor
Extracts clean text from uploaded resume PDFs using pdfplumber.
"""

import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract and return all text from a PDF file.

    Args:
        pdf_path: Local file path or file-like object path to the PDF.

    Returns:
        A single string with all extracted text, pages separated by newlines.
    """
    all_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text.strip())
                else:
                    print(f"Warning: No text found on page {page_num}")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    return "\n\n".join(all_text)

# Quick test (when run as script)
if __name__ == "__main__":
    # You can test this later with a sample PDF
    print("extractor.py ready.")
