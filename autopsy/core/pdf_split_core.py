import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_advanced(input_path, output_folder, mode, pages_list=None, chunk_size=None):
    """
    Splits the input PDF in different ways:
    
    1. mode = "every_page" -> Splits after every page.
    2. mode = "after_pages" -> Splits after specific page numbers in pages_list (1-based).
    3. mode = "n_pages" -> Splits every 'chunk_size' pages.
    
    Returns:
        list of str: Paths to the newly created split PDFs.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_paths = []

    def save_range(start_page, end_page):
        """Save pages from start_page to end_page (inclusive) to a new PDF."""
        writer = PdfWriter()
        for p in range(start_page, end_page + 1):
            writer.add_page(reader.pages[p - 1])  # Convert 1-based to 0-based
        out_file = os.path.join(output_folder, f"{base_name}_pages_{start_page}_to_{end_page}.pdf")
        with open(out_file, "wb") as f:
            writer.write(f)
        output_paths.append(out_file)

    if mode == "every_page":
        # Split after every page
        for i in range(1, total_pages + 1):
            save_range(i, i)

    elif mode == "after_pages":
        # pages_list is a list of 1-based page numbers where we split AFTER that page.
        # Example: if pages_list=[5,10], then we create:
        #   pages 1..5, pages 6..10, pages 11..end
        if not pages_list:
            raise ValueError("pages_list cannot be empty for mode 'after_pages'.")
        # Sort and remove duplicates just in case
        pages_list = sorted(set(pages_list))
        
        last_end = 1
        for split_page in pages_list:
            if split_page < 1 or split_page >= total_pages:
                # You might decide to handle out-of-range differently
                continue
            save_range(last_end, split_page)
            last_end = split_page + 1
        # Save remaining pages after the last split
        if last_end <= total_pages:
            save_range(last_end, total_pages)

    elif mode == "n_pages":
        # chunk_size is an integer specifying how many pages per chunk
        if not chunk_size or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer for mode 'n_pages'.")
        current_start = 1
        while current_start <= total_pages:
            current_end = min(current_start + chunk_size - 1, total_pages)
            save_range(current_start, current_end)
            current_start = current_end + 1
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return output_paths
