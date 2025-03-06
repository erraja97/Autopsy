import os
import glob
import re
from PyPDF2 import PdfReader, PdfWriter

def parse_page_ranges(page_range_str, total_pages):
    pages = set()
    if page_range_str:
        ranges = page_range_str.split(',')
        # Helper to convert a value to an integer, handling macros.
        def convert_value(val):
            val = val.strip().upper()
            if val == "FIRST":
                return 1
            elif val == "LAST":
                return total_pages
            else:
                return int(val)
        
        for r in ranges:
            r = r.strip()
            if '-' in r:
                start_str, end_str = r.split('-')
                start_val = convert_value(start_str)
                end_val = convert_value(end_str)
                # Adjust indices: page numbers are 1-based in input, but we store 0-based.
                pages.update(range(max(0, start_val - 1), min(end_val, total_pages)))
            else:
                page = convert_value(r) - 1
                if 0 <= page < total_pages:
                    pages.add(page)
    return pages


def get_matching_files(directory, pattern):
    """
    Returns a sorted list of absolute paths for files in `directory` that match the given pattern.
    
    Matching rules:
    - If pattern starts with "=": Exact match (case-insensitive).
    - If pattern starts with "^": File name starts with the given string (case-insensitive).
    - If pattern starts with "$": File name ends with the given string (case-insensitive).
    - If pattern starts with "~": Treat the rest as a regex pattern (case-insensitive).
    - If pattern starts and ends with "*": Contains match (same as default, but asterisks are stripped).
    - Otherwise, default to contains match (case-insensitive).
    Only files ending with ".pdf" are returned.
    """
    files = sorted(os.listdir(directory))
    pattern = pattern.strip()
    
    if pattern.startswith("="):
        match_func = lambda f: f.lower() == pattern[1:].lower()
    elif pattern.startswith("^"):
        match_func = lambda f: f.lower().startswith(pattern[1:].lower())
    elif pattern.startswith("$"):
        match_func = lambda f: f.lower().endswith(pattern[1:].lower())
    elif pattern.startswith("~"):
        regex = re.compile(pattern[1:], re.IGNORECASE)
        match_func = lambda f: bool(regex.search(f))
    elif pattern.startswith("*") and pattern.endswith("*"):
        core = pattern.strip("*")
        match_func = lambda f: core.lower() in f.lower()
    else:
        match_func = lambda f: pattern.lower() in f.lower()
    
    return sorted([os.path.join(directory, f) for f in files if match_func(f) and f.lower().endswith(".pdf")])

def parse_page_selection(page_input):
    pages = set()
    if not page_input:
        return set()
    for part in page_input.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)

def process_pages(reader, include_pages, exclude_pages):
    writer = PdfWriter()
    total_pages = len(reader.pages)
    if include_pages:
        include_set = set(include_pages)
    else:
        include_set = set(range(1, total_pages + 1))
    exclude_set = set(exclude_pages)
    for i in range(total_pages):
        if (i + 1) in include_set and (i + 1) not in exclude_set:
            writer.add_page(reader.pages[i])
    return writer

def merge_batches(config_data):
    results = []
    for batch in config_data:
        working_dir = batch["working_directory"]
        output_name = batch["output_name"]
        output_path = os.path.join(working_dir, f"{output_name}.pdf")
        pdf_writer = PdfWriter()
        for file_config in sorted(batch["files"], key=lambda x: x["sequence"]):
            pattern = file_config["pattern"]
            include = file_config["include"]
            exclude = file_config["exclude"]
            pdf_files = get_matching_files(working_dir, pattern)
            
            # Log if no files found for this pattern:
            if not pdf_files:
                msg = f"❌ No PDF files found for pattern '{pattern}' in {working_dir}. Skipped."
                print(msg)
                results.append(msg)
                continue

            for pdf_file in pdf_files:
                # Ensure only PDF files are processed:
                if not pdf_file.lower().endswith(".pdf"):
                    msg = f"❌ Skipping non-PDF file: {pdf_file}"
                    print(msg)
                    results.append(msg)
                    continue

                # Check if the file exists and is a file:
                if not os.path.isfile(pdf_file):
                    msg = f"❌ File not found: {pdf_file}. Skipped."
                    print(msg)
                    results.append(msg)
                    continue

                try:
                    reader = PdfReader(pdf_file)
                except Exception as e:
                    msg = f"❌ Error reading {pdf_file}: {str(e)}. Skipped."
                    print(msg)
                    results.append(msg)
                    continue

                total_pages = len(reader.pages)
                include_pages = parse_page_ranges(include, total_pages) if include else set(range(total_pages))
                exclude_pages = parse_page_ranges(exclude, total_pages) if exclude else set()
                pages_to_merge = sorted(include_pages - exclude_pages)
                for page_num in pages_to_merge:
                    try:
                        pdf_writer.add_page(reader.pages[page_num])
                    except Exception as e:
                        msg = f"❌ Error adding page {page_num+1} of {pdf_file}: {str(e)}"
                        print(msg)
                        results.append(msg)
        try:
            with open(output_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)
            msg = f"✅ Merged PDF saved: {output_path}"
            print(msg)
            results.append(msg)
        except Exception as e:
            msg = f"❌ Error merging batch {batch['batch_number']}: {str(e)}"
            print(msg)
            results.append(msg)
        
        # Append a divider after processing each batch:
        divider = "-" * 50
        print(divider)
        results.append(divider)
    return results

