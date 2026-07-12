import os
import pymupdf
from PIL import Image
from datetime import datetime
import pillow_heif
import rawpy
import time
from concurrent.futures import ThreadPoolExecutor

def process_single_file(index, path, target, prefix, output_dir, merge_pdf, status_callback, log_callback):
    """Worker function executed by threads to handle a single file input."""
    try:
        ext = path.lower()
        current_images = []
        input_size = os.path.getsize(path)

        # --- 1. READING ---
        if ext.endswith(".pdf"):
            doc = pymupdf.open(path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                current_images.append((img, f"p{page_num+1}"))
            doc.close()
        elif ext.endswith((".cr2", ".nef", ".arw", ".dng")):
            with rawpy.imread(path) as raw:
                img = Image.fromarray(raw.postprocess())
                current_images.append((img, ""))
        elif ext.endswith(".heic"):
            heif = pillow_heif.read_heif(path)
            img = Image.frombytes(heif.mode, heif.size, heif.data, "raw")
            current_images.append((img, ""))
        else:
            current_images.append((Image.open(path), ""))

        # --- 2. PROCESSING & SAVING ---
        saved_frames = []
        output_size_accumulated = 0
        
        for img, suffix in current_images:
            if target in ['jpg', 'jpeg', 'pdf']:
                img = img.convert("RGB")
            
            if target == "pdf" and merge_pdf:
                saved_frames.append(img)
            else:
                final_suffix = f"_{suffix}" if suffix else f"_{index+1}"
                save_name = f"{prefix}{final_suffix}.{target}"
                save_path = os.path.join(output_dir, save_name)
                
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

def run_conversion(file_paths, target_format, output_dir, prefix_input, merge_pdf, quality_setting, progress_callback, status_callback, log_callback):
    start_time = time.time()
    target = target_format.lower()
    prefix = prefix_input.strip() or f"pixelswitch_{datetime.now().strftime('%m-%d-%Y')}"
    all_frames = []

    total_files = len(file_paths)
    completed_files = 0
    total_input_size = 0
    total_output_size = 0

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                process_single_file, i, path, target, prefix, output_dir, merge_pdf, quality_setting, status_callback, log_callback
            )
            for i, path in enumerate(file_paths)
        ]

        for future in futures:
            result_frames, in_size, out_size = future.result()
            total_input_size += in_size
            total_output_size += out_size
            if target == "pdf" and merge_pdf:
                all_frames.extend(result_frames)
            completed_files += 1
            progress_callback(completed_files / total_files)

    if target == "pdf" and merge_pdf and all_frames:
        pdf_path = os.path.join(output_dir, f"{prefix}.pdf")
        all_frames[0].save(pdf_path, save_all=True, append_images=all_frames[1:])
        total_output_size += os.path.getsize(pdf_path)

    return {"duration": time.time() - start_time, "input_mb": total_input_size / (1024*1024), "output_mb": total_output_size / (1024*1024)}