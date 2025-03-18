import fitz  # PyMuPDF
import os

class PDFEditor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_text(self):
        """Extracts text from all pages of the PDF."""
        extracted_text = []
        for page in self.doc:
            extracted_text.append(page.get_text("text"))
        return "\n".join(extracted_text)

    def update_text(self, old_text, new_text):
        """Replaces occurrences of old_text with new_text in the PDF."""
        for page in self.doc:
            text_instances = page.search_for(old_text)
            for inst in text_instances:
                page.insert_text(inst[:2], new_text, fontsize=12, color=(1, 0, 0))

    def save_pdf(self, output_path):
        """Saves the edited PDF to a new file."""
        self.doc.save(output_path)
        self.doc.close()
        return output_path

# Example usage:
# editor = PDFEditor("sample.pdf")
# print(editor.extract_text())
# editor.update_text("old text", "new text")
# editor.save_pdf("edited_sample.pdf")
