import tkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import customtkinter as ctk
import os
import sys
import threading
import json
import pymupdf  # Standard import for PyMuPDF (fitz)
from PIL import Image
from tkinter import filedialog
from datetime import datetime, date

# --- HELPER: Find files inside the .exe ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- App Configuration ---
ctk.set_appearance_mode("System")
theme_path = resource_path("pixel_theme.json")
ctk.set_default_color_theme(theme_path)

class PixelSwitchApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        
        self.TkdndVersion = TkinterDnD._require(self)
        self.settings_file = "settings.json" 
        self.settings = self.load_settings()

        # Window Setup
        self.title("PixelSwitch - Pro Edition")
        self.geometry("950x800")
        
        icon_path = resource_path("icon.ico")
        try: self.iconbitmap(icon_path)
        except: pass 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="PixelSwitch Pro", 
                                     font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Format Selection
        self.format_label = ctk.CTkLabel(self.sidebar_frame, text="Convert to:", anchor="w")
        self.format_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.format_var = ctk.StringVar(value=self.settings.get("last_format", "JPG"))
        self.format_menu = ctk.CTkOptionMenu(self.sidebar_frame, variable=self.format_var,
                                           values=["JPG", "PNG", "WEBP", "PDF", "TIFF"],
                                           command=self.on_format_change)
        self.format_menu.grid(row=2, column=0, padx=20, pady=10)

        # Custom Naming Box
        self.name_label = ctk.CTkLabel(self.sidebar_frame, text="Custom Prefix:", anchor="w")
        self.name_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.name_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. Vacation")
        self.name_entry.grid(row=4, column=0, padx=20, pady=5)

        # Logic Switches
        self.overwrite_var = ctk.BooleanVar(value=True)
        self.overwrite_switch = ctk.CTkSwitch(self.sidebar_frame, text="Overwrite Files", variable=self.overwrite_var)
        self.overwrite_switch.grid(row=5, column=0, padx=20, pady=10)

        self.merge_pdf_var = ctk.BooleanVar(value=True)
        self.merge_pdf_switch = ctk.CTkSwitch(self.sidebar_frame, text="Merge into one PDF", variable=self.merge_pdf_var)
        self.merge_pdf_switch.grid(row=6, column=0, padx=20, pady=10)
        self.merge_pdf_switch.grid_remove() # Hide by default

        self.clear_btn = ctk.CTkButton(self.sidebar_frame, text="🗑️ Clear List", fg_color="transparent", border_width=2, command=self.clear_list)
        self.clear_btn.grid(row=7, column=0, padx=20, pady=20)

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=9, column=0, padx=20, pady=20)
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        if self.settings.get("theme") == "Dark":
            self.theme_switch.select()
            ctk.set_appearance_mode("Dark")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.file_list_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Files to Convert")
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)
        self.file_list_frame.drop_target_register(DND_FILES)
        self.file_list_frame.dnd_bind('<<Drop>>', self.drop_event)

        self.placeholder_label = ctk.CTkLabel(self.file_list_frame, text="📂 Drag Photos, RAWs, or PDFs here!", text_color="gray", font=("Arial", 14))
        self.placeholder_label.pack(pady=50)

        self.file_paths, self.status_labels, self.row_widgets = [], {}, []

        # --- BOTTOM ACTION AREA ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self.path_display = ctk.CTkEntry(self.action_frame, state="readonly")
        self.path_display.pack(fill="x", pady=5)
        self.path_display.insert(0, self.settings.get("output_folder", self.get_default_folder()))

        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.pack_forget()

        self.convert_btn = ctk.CTkButton(self.action_frame, text="START CONVERSION", height=45, font=("Arial", 15, "bold"), command=self.start_conversion_thread)
        self.convert_btn.pack(fill="x", pady=5)
        
        self.open_folder_btn = ctk.CTkButton(self.action_frame, text="Open Folder ↗️", fg_color="#A5D6A7", text_color="#2E7D32", command=self.open_output_folder)
        self.open_folder_btn.pack_forget()

    # --- UI EVENT HANDLERS ---
    def on_format_change(self, choice):
        if choice == "PDF":
            self.merge_pdf_switch.grid()
        else:
            self.merge_pdf_switch.grid_remove()
        self.save_settings()

    def on_drop_files(self, filenames):
        self.after(0, lambda: self.process_dropped_files(filenames))

    # --- LOGIC HELPERS ---
    def get_default_folder(self):
        docs = os.path.join(os.path.expanduser("~"), "Documents", "PixelSwitch")
        os.makedirs(docs, exist_ok=True)
        return docs

    def log_event(self, message):
        log_path = os.path.join(self.get_default_folder(), "log.txt")
        mode = "w" if os.path.exists(log_path) and date.fromtimestamp(os.path.getmtime(log_path)) < date.today() else "a"
        with open(log_path, mode, encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as f: return json.load(f)
        except: return {"theme": "System", "last_format": "JPG", "output_folder": self.get_default_folder()}

    def save_settings(self, _=None):
        self.settings.update({"theme": "Dark" if self.theme_switch.get() else "Light", "last_format": self.format_var.get()})
        with open(self.settings_file, "w") as f: json.dump(self.settings, f)

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")
        self.save_settings()

    def open_output_folder(self):
        os.startfile(self.settings.get("output_folder", self.get_default_folder()))

    def clear_list(self):
        for w in self.row_widgets: w.destroy()
        self.file_paths, self.status_labels, self.row_widgets = [], {}, []
        self.placeholder_label.pack(pady=50)
        self.progress_bar.pack_forget()
        self.open_folder_btn.pack_forget()

    # --- CORE CONVERSION LOGIC ---
    def drop_event(self, event):
        self.placeholder_label.pack_forget()
        data = event.data
        paths = [p.strip('{}') for p in (data.split('} {') if data.startswith('{') else data.split())]
        valid = ('.heic', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.psd', '.cr2', '.nef', '.arw', '.dng', '.pdf')
        for p in paths:
            if p.lower().endswith(valid) and p not in self.file_paths:
                self.file_paths.append(p)
                self.add_file_row(p)

    def add_file_row(self, path):
        row = ctk.CTkFrame(self.file_list_frame)
        row.pack(fill="x", pady=2)
        self.row_widgets.append(row)
        ctk.CTkLabel(row, text="📄" if path.lower().endswith(".pdf") else "🖼️").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=os.path.basename(path), anchor="w").pack(side="left", fill="x", expand=True)
        status = ctk.CTkLabel(row, text="Pending", text_color="orange")
        status.pack(side="right", padx=10)
        self.status_labels[path] = status

    def start_conversion_thread(self):
        if not self.file_paths: return
        self.convert_btn.configure(state="disabled", text="Working...")
        self.progress_bar.pack(fill="x", pady=5)
        threading.Thread(target=self.run_conversion).start()

    def run_conversion(self):
        import pillow_heif, rawpy, numpy as np
        target = self.format_var.get().lower()
        output_dir = self.settings["output_folder"]
        prefix = self.name_entry.get().strip() or f"pixelswitch_{datetime.now().strftime('%m-%d-%Y')}"
        overwrite = self.overwrite_var.get()
        all_frames = [] # For PDF merging

        for i, path in enumerate(self.file_paths):
            try:
                ext = path.lower()
                current_images = []

                # --- 1. READING ---
                if ext.endswith(".pdf"):
                    doc = pymupdf.open(path)
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)) # Higher quality
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
                for img, suffix in current_images:
                    if target in ['jpg', 'jpeg', 'pdf']:
                        img = img.convert("RGB")
                    
                    if target == "pdf" and self.merge_pdf_var.get():
                        all_frames.append(img)
                    else:
                        final_suffix = f"_{suffix}" if suffix else f"_{i+1}"
                        save_name = f"{prefix}{final_suffix}.{target}"
                        save_path = os.path.join(output_dir, save_name)
                        
                        if overwrite and os.path.exists(save_path):
                            os.remove(save_path)
                        
                        img.save(save_path, quality=95)

                self.after(0, self.update_status, path, "✅ Done", "green")
            except Exception as e:
                self.after(0, self.update_status, path, "❌ Error", "red")
                self.log_event(f"Error on {path}: {str(e)}")

            self.after(0, self.progress_bar.set, (i + 1) / len(self.file_paths))

        # --- 3. FINAL PDF MERGE ---
        if target == "pdf" and self.merge_pdf_var.get() and all_frames:
            pdf_path = os.path.join(output_dir, f"{prefix}.pdf")
            if overwrite and os.path.exists(pdf_path): os.remove(pdf_path)
            all_frames[0].save(pdf_path, save_all=True, append_images=all_frames[1:])

        self.after(0, lambda: self.convert_btn.configure(state="normal", text="START CONVERSION"))
        self.after(0, lambda: self.open_folder_btn.pack(fill="x", pady=5))

    def update_status(self, path, text, color):
        self.status_labels[path].configure(text=text, text_color=color)

if __name__ == "__main__":
    PixelSwitchApp().mainloop()