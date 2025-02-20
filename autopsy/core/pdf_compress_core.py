import os
import fitz  # PyMuPDF
from PIL import Image
import io

def compress_pdf(input_path, output_path, quality, progress_callback):
    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        for i, page in enumerate(doc):
            img_list = page.get_images(full=True)
            for img in img_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_data = base_image["image"]
                img_ext = base_image["ext"]
                if img_ext.lower() in ["jpeg", "jpg", "png"]:
                    image = Image.open(io.BytesIO(img_data))
                    img_io = io.BytesIO()
                    image.save(img_io, format="JPEG", quality=quality)
                    doc.update_stream(xref, img_io.getvalue())
            progress_callback(int((i + 1) / total_pages * 100))
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return os.path.getsize(output_path) / (1024 * 1024)  # Size in MB
    except Exception as e:
        return str(e)
