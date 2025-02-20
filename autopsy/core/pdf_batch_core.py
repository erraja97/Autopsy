import os
import glob
import re
from PyPDF2 import PdfReader, PdfWriter

def parse_page_ranges(page_range_str, total_pages):
    pages = set()
    if page_range_str:
        ranges = page_range_str.split(',')
        for r in ranges:
            if '-' in r:
                start, end = map(int, r.split('-'))
                pages.update(range(max(0, start - 1), min(end, total_pages)))
            else:
                page = int(r) - 1
                if 0 <= page < total_pages:
                    pages.add(page)
    return pages

def get_matching_files(directory, pattern):
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
    else:
        match_func = lambda f: pattern.lower() in f.lower()
    return sorted([os.path.join(directory, f) for f in files if match_func(f) and f.endswith(".pdf")])

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
            pdf_files = sorted(glob.glob(os.path.join(working_dir, pattern)))
            for pdf_file in pdf_files:
                try:
                    reader = PdfReader(pdf_file)
                except Exception as e:
                    results.append(f"❌ Error reading {pdf_file}: {str(e)}")
                    continue  # Skip to the next file if this one can't be read

                total_pages = len(reader.pages)
                include_pages = parse_page_ranges(include, total_pages) if include else set(range(total_pages))
                exclude_pages = parse_page_ranges(exclude, total_pages) if exclude else set()
                pages_to_merge = sorted(include_pages - exclude_pages)
                for page_num in pages_to_merge:
                    try:
                        pdf_writer.add_page(reader.pages[page_num])
                    except Exception as e:
                        results.append(f"❌ Error adding page {page_num+1} of {pdf_file}: {str(e)}")
        try:
            with open(output_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)
            results.append(f"✅ Merged PDF saved: {output_path}")
        except Exception as e:
            results.append(f"❌ Error merging batch {batch['batch_number']}: {str(e)}")
    return results
