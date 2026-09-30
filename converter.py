import os
import pymupdf
from PIL import Image
from datetime import datetime
import rawpy
import time
from concurrent.futures import ThreadPoolExecutor

def get_unique_filename(base_path):
    """Generates a unique filename if the target already exists and overwriting is disabled."""
    if not os.path.exists(base_path):
        return base_path
    name, ext = os.path.splitext(base_path)
    counter = 1
    while os.path.exists(f"{name}_{counter}{ext}"):
        counter += 1
    return f"{name}_{counter}{ext}"

def process_single_file(index, path, target, prefix, output_dir, merge_pdf, quality_setting, overwrite_files, status_callback, log_callback):
    """Worker function executed by threads to handle a single file input."""
    try:
        ext = path.lower()
        current_images = []
        
        # Grab original filename to prevent collisions later
        original_name = os.path.splitext(os.path.basename(path))[0]

        # --- 1. READING ---
        if ext.endswith(".pdf"):
            doc = pymupdf.open(path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                current_images.append((img, f"{original_name}_p{page_num+1}"))
            doc.close()
        elif ext.endswith((".cr2", ".nef", ".arw", ".dng")):
            with rawpy.imread(path) as raw:
                img = Image.fromarray(raw.postprocess())
                current_images.append((img, original_name))
        else:
            # Pillow handles .heic natively now due to register_heif_opener() in main.py
            current_images.append((Image.open(path), original_name))

        # --- 2. PROCESSING & SAVING ---
        saved_frames = []
        output_size_accumulated = 0
        
        for img, suffix in current_images:
            # Fix transparency crash for JPG/PDF by adding a white background
            if target in ['jpg', 'jpeg', 'pdf']:
                if img.mode in ("RGBA", "P", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split()[3]) # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                else:
                    img = img.convert("RGB")
            
            if target == "pdf" and merge_pdf:
                # RAM EXPLOSION FIX: Save to temporary PDF immediately, release RAM!
                temp_name = f".temp_merge_{index}_{suffix}.pdf"
                temp_path = os.path.join(output_dir, temp_name)
                img.save(temp_path, "PDF", resolution=100.0)
                saved_frames.append(temp_path) # We save the PATH, not the image data
            else:
                # Use original name if no prefix is set
                base_name = f"{prefix}_{suffix}" if prefix else suffix
                save_name = f"{base_name}.{target}"
                save_path = os.path.join(output_dir, save_name)
                
                # Respect the overwrite switch!
                if not overwrite_files:
                    save_path = get_unique_filename(save_path)
                
                # Apply quality dynamically to compatible formats
                if target in ['jpg', 'jpeg', 'webp']:
                    img.save(save_path, quality=quality_setting)
                else:
                    img.save(save_path)
                    
                output_size_accumulated += os.path.getsize(save_path)

        status_callback(path, "✅ Done", "green")
        return saved_frames, os.path.getsize(path), output_size_accumulated
    except Exception as e:
        status_callback(path, "❌ Error", "red")
        log_callback(f"Error on {path}: {str(e)}")
        return [], os.path.getsize(path) if os.path.exists(path) else 0, 0


def run_conversion(file_paths, target_format, output_dir, prefix_input, merge_pdf, quality_setting, overwrite_files, progress_callback, status_callback, log_callback):
    start_time = time.time()
    target = target_format.lower()
    prefix = prefix_input.strip()
    all_temp_pdfs = []

    total_files = len(file_paths)
    completed_files = 0
    total_input_size = 0
    total_output_size = 0

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                process_single_file, i, path, target, prefix, output_dir, merge_pdf, quality_setting, overwrite_files, status_callback, log_callback
            )
            for i, path in enumerate(file_paths)
        ]

        for future in futures:
            result_frames, in_size, out_size = future.result()
            total_input_size += in_size
            total_output_size += out_size
            if target == "pdf" and merge_pdf:
                all_temp_pdfs.extend(result_frames)
            
            completed_files += 1
            progress_callback(completed_files / total_files)

    # RAM EXPLOSION FIX: Merge the temp files from disk, not memory!
    if target == "pdf" and merge_pdf and all_temp_pdfs:
        final_pdf_name = f"{prefix}.pdf" if prefix else f"merged_pixelswitch_{datetime.now().strftime('%m%d%H%M')}.pdf"
        final_pdf_path = os.path.join(output_dir, final_pdf_name)
        
        if not overwrite_files:
            final_pdf_path = get_unique_filename(final_pdf_path)

        merged_doc = pymupdf.open()
        for temp_pdf in all_temp_pdfs:
            try:
                if os.path.exists(temp_pdf):
                    doc = pymupdf.open(temp_pdf)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                    os.remove(temp_pdf) # Clean up after merging!
            except Exception as e:
                log_callback(f"Error merging {temp_pdf}: {e}")
        
        merged_doc.save(final_pdf_path)
        merged_doc.close()
        total_output_size += os.path.getsize(final_pdf_path)

    return {"duration": time.time() - start_time, "input_mb": total_input_size / (1024*1024), "output_mb": total_output_size / (1024*1024)}