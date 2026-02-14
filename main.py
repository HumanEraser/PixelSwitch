import tkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import customtkinter as ctk
import os
import sys  # Needed for the .exe path logic
import threading
import json
from PIL import Image
from tkinter import filedialog

# --- HELPER: Find files inside the .exe ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- App Configuration ---
ctk.set_appearance_mode("System")

# Load Theme
theme_path = resource_path("pixel_theme.json")
ctk.set_default_color_theme(theme_path)

class PixelSwitchApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        
        self.TkdndVersion = TkinterDnD._require(self)

        # --- SETTINGS MANAGEMENT---
        self.settings_file = "settings.json" 
        self.settings = self.load_settings()

        # --- Window Setup ---
        self.title("PixelSwitch - Batch Converter")
        self.geometry("900x700")
        
        # LOAD ICON 
        icon_path = resource_path("icon.ico")
        try:
            self.iconbitmap(icon_path)
        except:
            pass 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="PixelSwitch", 
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.format_label = ctk.CTkLabel(self.sidebar_frame, text="Convert to:", anchor="w")
        self.format_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.format_var = ctk.StringVar(value=self.settings.get("last_format", "JPG"))
        self.format_menu = ctk.CTkOptionMenu(self.sidebar_frame, variable=self.format_var,
                                           values=["JPG", "PNG", "WEBP"], command=self.save_settings)
        self.format_menu.grid(row=2, column=0, padx=20, pady=10)

        self.clear_btn = ctk.CTkButton(self.sidebar_frame, text="🗑️ Clear List", 
                                     fg_color="transparent", border_width=2, 
                                     text_color=("gray10", "#DCE4EE"),
                                     command=self.clear_list)
        self.clear_btn.grid(row=3, column=0, padx=20, pady=20)

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=5, column=0, padx=20, pady=20)
        
        if self.settings.get("theme") == "Dark":
            self.theme_switch.select()
            ctk.set_appearance_mode("Dark")
        else:
            self.theme_switch.deselect()
            ctk.set_appearance_mode("Light")

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.file_list_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Files to Convert")
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Drag & Drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)
        self.file_list_frame.drop_target_register(DND_FILES)
        self.file_list_frame.dnd_bind('<<Drop>>', self.drop_event)

        self.placeholder_label = ctk.CTkLabel(self.file_list_frame, 
                                            text="📂 Drag & Drop files here!",
                                            text_color="gray", font=("Arial", 14))
        self.placeholder_label.pack(pady=50)

        self.file_paths = []
        self.status_labels = {}
        self.row_widgets = []

        # --- BOTTOM ACTION AREA ---
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self.folder_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.folder_frame.pack(fill="x", pady=5)

        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Save to:", width=60)
        self.folder_label.pack(side="left")

        current_out = self.settings.get("output_folder", "")
        self.path_display = ctk.CTkEntry(self.folder_frame, placeholder_text="Documents/PixelSwitch")
        self.path_display.insert(0, current_out)
        self.path_display.configure(state="readonly") 
        self.path_display.pack(side="left", fill="x", expand=True, padx=5)

        self.browse_btn = ctk.CTkButton(self.folder_frame, text="📂 Change", width=80, 
                                      command=self.browse_folder)
        self.browse_btn.pack(side="right")
        
        self.open_folder_btn = ctk.CTkButton(self.action_frame, text="Open Output Folder ↗️", 
                                           fg_color="#A5D6A7", text_color="#2E7D32", 
                                           hover_color="#81C784",
                                           command=self.open_output_folder)
        
        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(10, 5))
        self.progress_bar.pack_forget()

        self.convert_btn = ctk.CTkButton(self.action_frame, text="CONVERT FILES", 
                                       height=40, font=ctk.CTkFont(size=15, weight="bold"),
                                       command=self.start_conversion_thread)
        self.convert_btn.pack(fill="x")

    # --- SETTINGS LOGIC ---
    def get_default_folder(self):
        docs = os.path.join(os.path.expanduser("~"), "Documents", "PixelSwitch")
        if not os.path.exists(docs):
            try:
                os.makedirs(docs)
            except OSError:
                pass 
        return docs

    def load_settings(self):
        default_path = self.get_default_folder()
        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)
                if not data.get("output_folder"):
                    data["output_folder"] = default_path
                return data
        except FileNotFoundError:
            return {"theme": "System", "last_format": "JPG", "output_folder": default_path}

    def save_settings(self, _=None):
        self.settings["theme"] = "Dark" if self.theme_switch.get() == 1 else "Light"
        self.settings["last_format"] = self.format_var.get()
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        self.save_settings()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.settings["output_folder"] = folder
            self.path_display.configure(state="normal")
            self.path_display.delete(0, "end")
            self.path_display.insert(0, folder)
            self.path_display.configure(state="readonly")
            self.save_settings()
            
    def open_output_folder(self):
        path = self.settings.get("output_folder", self.get_default_folder())
        if os.path.exists(path):
            os.startfile(path)

    # --- LIST LOGIC ---
    def clear_list(self):
        self.file_paths = []
        self.status_labels = {}
        for widget in self.row_widgets:
            widget.destroy()
        self.row_widgets = []
        
        self.placeholder_label.pack(pady=50)
        self.progress_bar.pack_forget()
        self.open_folder_btn.pack_forget() 
        self.convert_btn.pack(fill="x")

    # --- CORE LOGIC ---
    def drop_event(self, event):
        self.placeholder_label.pack_forget()
        raw_files = event.data
        if raw_files.startswith('{'):
            paths = raw_files.split('} {')
            cleaned_paths = [p.strip('{}') for p in paths]
        else:
            cleaned_paths = raw_files.split()

        valid_exts = ('.heic', '.jpg', '.jpeg', '.png', '.webp', '.bmp')
        for path in cleaned_paths:
            if path.lower().endswith(valid_exts):
                if path not in self.file_paths:
                    self.file_paths.append(path)
                    self.add_file_row(path)

    def add_file_row(self, path):
        row_frame = ctk.CTkFrame(self.file_list_frame)
        row_frame.pack(fill="x", pady=2)
        
        self.row_widgets.append(row_frame)

        icon = ctk.CTkLabel(row_frame, text="🖼️", width=30)
        icon.pack(side="left", padx=5)

        filename = os.path.basename(path)
        name_label = ctk.CTkLabel(row_frame, text=filename, anchor="w")
        name_label.pack(side="left", fill="x", expand=True)

        status = ctk.CTkLabel(row_frame, text="Pending", text_color="orange", width=80)
        status.pack(side="right", padx=10)
        self.status_labels[path] = status

    def start_conversion_thread(self):
        if not self.file_paths:
            return
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.progress_bar.pack(fill="x", pady=(10, 5))
        self.progress_bar.set(0)
        threading.Thread(target=self.run_conversion).start()

    def get_safe_filepath(self, folder, filename, ext):
        base_name = os.path.splitext(filename)[0]
        counter = 1
        new_filename = f"{base_name}.{ext}"
        full_path = os.path.join(folder, new_filename)
        while os.path.exists(full_path):
            new_filename = f"{base_name}_{counter}.{ext}"
            full_path = os.path.join(folder, new_filename)
            counter += 1
        return full_path

    def run_conversion(self):
        import pillow_heif
        
        target_format = self.format_var.get().lower()
        total = len(self.file_paths)
        output_dir = self.settings.get("output_folder", self.get_default_folder())
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, filepath in enumerate(self.file_paths):
            try:
                if filepath.lower().endswith(".heic"):
                    heif_file = pillow_heif.read_heif(filepath)
                    img = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
                else:
                    img = Image.open(filepath)
                
                if target_format in ['jpg', 'jpeg']:
                    img = img.convert("RGB")
                
                filename = os.path.basename(filepath)
                save_path = self.get_safe_filepath(output_dir, filename, target_format)
                
                img.save(save_path, quality=95)
                self.after(0, self.update_status, filepath, "✅ Done", "green")
                
            except Exception as e:
                print(f"Error on {filepath}: {e}")
                self.after(0, self.update_status, filepath, "❌ Error", "red")
            
            self.after(0, self.progress_bar.set, (i + 1) / total)

        self.after(0, lambda: self.convert_btn.configure(state="normal", text="CONVERT FILES"))
        self.after(0, lambda: self.open_folder_btn.pack(fill="x", pady=5))

    def update_status(self, filepath, text, color):
        if filepath in self.status_labels:
            self.status_labels[filepath].configure(text=text, text_color=color)

if __name__ == "__main__":
    app = PixelSwitchApp()
    app.mainloop()