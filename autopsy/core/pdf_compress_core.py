import os
import fitz  # PyMuPDF
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
    remove_metadata: bool = False,
    convert_cmyk: bool = True,
    skip_text_rich: bool = False,
    skip_vector_only: bool = False,
    progress_callback=None
) -> float:
    if mode not in ["preserve", "rasterize"]:
        raise ValueError("mode must be either 'preserve' or 'rasterize'")
    
    if mode == "rasterize":
        return _rasterize_pdf(
            input_path=input_path,
            output_path=output_path,
            dpi=dpi,
            quality=quality,
            max_width=max_width,
            max_height=max_height,
            skip_text_rich=skip_text_rich,
            skip_vector_only=skip_vector_only,
            progress_callback=progress_callback
        )
    else:
        return _clone_and_compress_images(
            input_path=input_path,
            output_path=output_path,
            quality=quality,
            max_width=max_width,
            max_height=max_height,
            remove_metadata=remove_metadata,
            convert_cmyk=convert_cmyk,
            progress_callback=progress_callback
        )


def _clone_and_compress_images(
    input_path: str,
    output_path: str,
    quality: int,
    max_width: int,
    max_height: int,
    remove_metadata: bool,
    convert_cmyk: bool,
    progress_callback
) -> float:
    src_doc = fitz.open(input_path)
    dst_doc = fitz.open()
    total_pages = len(src_doc)
    
    for i in range(total_pages):
        dst_doc.insert_pdf(src_doc, from_page=i, to_page=i)
        page = dst_doc[-1]
        processed_xrefs = set()
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in processed_xrefs:
                continue
            processed_xrefs.add(xref)
            
            try:
                base_img = page.extract_image(xref)
                if not base_img or "image" not in base_img:
                    continue
                original_data = base_img["image"]
                ext = base_img.get("ext", "").lower()
                if ext not in ["jpg", "jpeg", "png"]:
                    continue

                pil_img = Image.open(io.BytesIO(original_data))
                if convert_cmyk and pil_img.mode == "CMYK":
                    pil_img = pil_img.convert("RGB")
                elif pil_img.mode not in ("RGB", "L"):
                    pil_img = pil_img.convert("RGB")
                
                if remove_metadata:
                    new_img = Image.new(pil_img.mode, pil_img.size)
                    new_img.paste(pil_img)
                    pil_img = new_img
                
                if max_width and max_height:
                    if pil_img.width > max_width or pil_img.height > max_height:
                        pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                new_data = buf.getvalue()
                buf.close()
                page.replace_image(xref, new_data)
            except Exception:
                continue
        
        if progress_callback:
            progress_callback(int(((i + 1) / total_pages) * 100))
    
    src_doc.close()
    dst_doc.save(output_path, incremental=False, deflate=True, garbage=4)
    dst_doc.close()
    return os.path.getsize(output_path) / (1024 * 1024)


def _rasterize_pdf(
    input_path: str,
    output_path: str,
    dpi: int,
    quality: int,
    max_width: int,
    max_height: int,
    progress_callback,
    skip_text_rich: bool = False,
    skip_vector_only: bool = False
) -> float:
    """
    Rasterizes each page unless either:
      - skip_text_rich is True and text is dominant relative to images, or
      - skip_vector_only is True and vector drawings exceed images.
      
    Additionally, if any image on the page is large (area exceeds threshold),
    the page is forced to rasterize.
    
    The new page size is kept the same as the original.
    """
    src_doc = fitz.open(input_path)
    dst_doc = fitz.open()
    total_pages = len(src_doc)
    
    # Define thresholds.
    TEXT_THRESHOLD = 200       # minimum characters to consider page text-rich
    TEXT_FACTOR = 100          # text length should exceed image_count * TEXT_FACTOR
    LARGE_IMAGE_THRESHOLD = 500000  # e.g., an image with area >= 500,000 pixels is "large"
    
    for i in range(total_pages):
        page = src_doc[i]
        page_rect = page.rect  # original page size in points
        
        # Retrieve images, vector drawings, and text.
        img_list = page.get_images(full=True)
        img_count = len(img_list)
        drawings = page.get_drawings()
        text = page.get_text("text").strip()
        text_length = len(text)
        
        # Check if any image is "large"
        large_image_found = False
        for img_info in img_list:
            # img_info: (xref, smask, width, height, bpc, colorspace, ...)
            w = img_info[2]
            h = img_info[3]
            if w * h >= LARGE_IMAGE_THRESHOLD:
                large_image_found = True
                break
        
        # Decide whether to skip rasterizing this page:
        # Force rasterization if a large image is found.
        # Otherwise, if skip conditions are met, skip rasterizing.
        skip_this_page = False
        
        if not large_image_found:
            if skip_vector_only:
                # If vector drawings outnumber images, skip rasterization.
                if len(drawings) > img_count:
                    skip_this_page = True
                    print(f"Page {i+1}: Skipping rasterization because vector count ({len(drawings)}) > image count ({img_count}).")
            if not skip_this_page and skip_text_rich:
                if text_length >= TEXT_THRESHOLD and (img_count == 0 or text_length > img_count * TEXT_FACTOR):
                    skip_this_page = True
                    print(f"Page {i+1}: Skipping rasterization because text length ({text_length}) is high relative to image count ({img_count}).")
        
        # If skip_this_page is True, insert original page; else, rasterize.
        if skip_this_page:
            dst_doc.insert_pdf(src_doc, from_page=i, to_page=i)
        else:
            print(f"Page {i+1}: Rasterizing page (large_image_found={large_image_found}).")
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
            
            new_page = dst_doc.new_page(width=page_rect.width, height=page_rect.height)
            new_page.insert_image(page_rect, stream=img_data)
        
        if progress_callback:
            progress_callback(int(((i + 1) / total_pages) * 100))
    
    src_doc.close()
    dst_doc.save(output_path, deflate=True, garbage=4)
    dst_doc.close()
    return os.path.getsize(output_path) / (1024 * 1024)
