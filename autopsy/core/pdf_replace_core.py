import os
from PyPDF2 import PdfReader, PdfWriter

def replace_pages_in_pdf(base_pdf, replacement_pdf, start_page, end_page, output_path):
    """
    Replace pages in base_pdf from start_page to end_page (inclusive, 1-based indexing)
    with all pages from replacement_pdf, and write the result to output_path.

    :param base_pdf: Path to the base PDF file.
    :param replacement_pdf: Path to the replacement PDF file.
    :param start_page: Starting page number in base_pdf to replace (1-based).
    :param end_page: Ending page number in base_pdf to replace (1-based).
    :param output_path: Path to save the new PDF.
    :raises ValueError: If the page range is invalid.
    """
    base_reader = PdfReader(base_pdf)
    replacement_reader = PdfReader(replacement_pdf)
    writer = PdfWriter()

    total_pages = len(base_reader.pages)
    if start_page < 1 or end_page > total_pages or start_page > end_page:
        raise ValueError("Invalid page range specified.")

    # Add pages before the replacement range
    for i in range(0, start_page - 1):  # 0-indexed
        writer.add_page(base_reader.pages[i])
    
    # Add all pages from the replacement PDF
    for page in replacement_reader.pages:
        writer.add_page(page)
    
    # Add pages after the replacement range
    for i in range(end_page, total_pages):
        writer.add_page(base_reader.pages[i])
    
    with open(output_path, "wb") as f:
        writer.write(f)
