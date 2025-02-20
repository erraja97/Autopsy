import os
from PyPDF2 import PdfReader, PdfMerger

def merge_selected_pdfs(files_to_merge, pages_to_include, save_path):
    pdf_merger = PdfMerger()
    for pdf_file in files_to_merge:
        pdf_reader = PdfReader(pdf_file)
        # For each page, check if its checkbox is selected
        for page_num in range(len(pdf_reader.pages)):
            checkbox = pages_to_include.get((pdf_file, page_num))
            if checkbox and checkbox.isChecked():
                pdf_merger.append(pdf_file, pages=(page_num, page_num + 1))
    with open(save_path, "wb") as f:
        pdf_merger.write(f)
    pdf_merger.close()
