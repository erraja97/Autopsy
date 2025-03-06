import os
import fitz  # PyMuPDF (version 1.21+ recommended for replace_image)
from PIL import Image
import io

def compress_pdf_advanced(
    input_path: str,
    output_path: str,
    mode: str = "preserve",
    quality: int = 60,
    max_width: int = None,
    max_height: int = None,
    dpi: int = 150,
    progress_callback=None
) -> float:
    """
    Compress a PDF using one of two modes:
      1) "preserve": Clone pages and re-encode embedded images as JPEG.
         Text and vector data remain intact.
      2) "rasterize": Render each page to an image at the given DPI, compress it,
         and rebuild a new PDF (all content becomes a raster image).
    
    Args:
      input_path (str): Path to the source PDF.
      output_path (str): Where to save the compressed PDF.
      mode (str): "preserve" or "rasterize".
      quality (int): JPEG quality (10-90).
      max_width (int, optional): If provided, downscale images wider than this.
      max_height (int, optional): If provided, downscale images taller than this.
      dpi (int): Used only in "rasterize" mode; rendering resolution.
      progress_callback (callable, optional): Function(int) for progress updates (0–100).
    
    Returns:
      float: Size of the resulting PDF in MB.
    
    Raises:
      Exception if an error occurs.
    """
    if mode not in ["preserve", "rasterize"]:
        raise ValueError("mode must be either 'preserve' or 'rasterize'")
    
    if mode == "rasterize":
        return _rasterize_pdf(input_path, output_path, dpi, quality, max_width, max_height, progress_callback)
    else:
        return _clone_and_compress_images(input_path, output_path, quality, max_width, max_height, progress_callback)


def _clone_and_compress_images(
    input_path: str,
    output_path: str,
    quality: int = 50,
    max_width: int = 1200,
    max_height: int = 1200,
    progress_callback=None
) -> float:
    """
    Clone each page from the source PDF into a new PDF using insert_pdf,
    then re-encode each image as JPEG at the specified quality.
    Preserves text & vectors.
    Detailed logs are printed for every step.
    """

    src_doc = fitz.open(input_path)
    dst_doc = fitz.open()  # New PDF document
    total_pages = len(src_doc)
    
    for i in range(total_pages):
        dst_doc.insert_pdf(src_doc, from_page=i, to_page=i)
        page = dst_doc[-1]
        processed_xrefs = set()
        
        # Process each image on the cloned page
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in processed_xrefs:
                continue
            processed_xrefs.add(xref)
            
            try:
                # Extract original image data from the page
                base_img = page.extract_image(xref)
                if not base_img or "image" not in base_img:
                    continue
                original_data = base_img["image"]
                ext = base_img.get("ext", "").lower()
                # Only process common formats
                if ext not in ["jpg", "jpeg", "png"]:
                    continue

                # Open image with Pillow
                pil_img = Image.open(io.BytesIO(original_data))
                if pil_img.mode not in ("RGB", "L"):
                    pil_img = pil_img.convert("RGB")
                
                # Downscale if dimensions exceed provided limits
                if max_width and max_height:
                    if pil_img.width > max_width or pil_img.height > max_height:
                        pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Re-encode image to JPEG using the provided quality
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                new_data = buf.getvalue()
                buf.close()
                
                # Always replace the image with the re-encoded version.
                page.replace_image(xref, new_data)
                
            except Exception as e:
                # On error, skip the image without stopping the process
                continue
        
        if progress_callback:
            progress_callback(int(((i + 1) / total_pages) * 100))
    
    src_doc.close()
    dst_doc.save(output_path, incremental=False, deflate=True, garbage=4)
    dst_doc.close()
    final_mb = os.path.getsize(output_path) / (1024 * 1024)
    return final_mb


def _rasterize_pdf(
    input_path: str,
    output_path: str,
    dpi: int,
    quality: int,
    max_width: int,
    max_height: int,
    progress_callback
) -> float:
    """
    Rasterizes each page of the PDF (converting text and vectors into an image),
    then compresses that image as JPEG and builds a new PDF.
    """
    src_doc = fitz.open(input_path)
    dst_doc = fitz.open()
    total_pages = len(src_doc)
    
    for i in range(total_pages):
        page = src_doc[i]
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        if max_width and max_height:
            if pil_img.width > max_width or pil_img.height > max_height:
                pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
        img_data = buf.getvalue()
        buf.close()
        new_page = dst_doc.new_page(width=pil_img.width, height=pil_img.height)
        rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
        new_page.insert_image(rect, stream=img_data)
        if progress_callback:
            progress_callback(int(((i + 1) / total_pages) * 100))
    
    src_doc.close()
    dst_doc.save(output_path, deflate=True, garbage=4)
    dst_doc.close()
    final_mb = os.path.getsize(output_path) / (1024 * 1024)
    return final_mb
