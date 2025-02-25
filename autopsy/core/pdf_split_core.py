import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, output_folder):
    """
    Splits the input PDF into separate PDF files for each page.
    
    Parameters:
      input_path (str): Path to the input PDF file.
      output_folder (str): Folder where the split PDFs will be saved.
      
    Returns:
      list: A list of paths for the created PDF files.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    
    reader = PdfReader(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_paths = []
    
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_file = os.path.join(output_folder, f"{base_name}_page_{i+1}.pdf")
        with open(out_file, "wb") as f:
            writer.write(f)
        output_paths.append(out_file)
    
    return output_paths
