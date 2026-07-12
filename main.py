import tkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import customtkinter as ctk
import os
import threading
from tkinter import filedialog
import utils
import converter
from gui.sidebar import SidebarFrame
from gui.main_content import MainContentFrame

ctk.set_appearance_mode("System")
ctk.set_default_color_theme(utils.resource_path("pixel_theme.json"))

class PixelSwitchApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.settings = utils.load_settings()

        self.title("PixelSwitch - Pro Edition")
        self.geometry("950x800")
        
        try: self.iconbitmap(utils.resource_path("icon.ico"))
        except: pass 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.file_paths, self.status_labels, self.row_widgets = [], {}, []

        # Load Split Layout Frames
        self.sidebar = SidebarFrame(self, self.settings, self.on_format_change, self.toggle_theme, self.clear_list)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.main_content = MainContentFrame(self, self.settings, self.change_output_folder, self.start_conversion_thread, self.open_output_folder, utils.get_default_folder())
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Setup Drag and Drop Binds
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)
        self.main_content.file_list_frame.drop_target_register(DND_FILES)
        self.main_content.file_list_frame.dnd_bind('<<Drop>>', self.drop_event)
        
        if self.settings.get("theme") == "Dark":
            ctk.set_appearance_mode("Dark")

    def on_format_change(self, choice):
        if choice == "PDF":
            self.sidebar.merge_pdf_switch.grid()
        else:
            self.sidebar.merge_pdf_switch.grid_remove()
        self.save_settings()

    def change_output_folder(self):
        chosen_dir = filedialog.askdirectory(initialdir=self.settings.get("output_folder", utils.get_default_folder()))
        if chosen_dir:
            self.settings["output_folder"] = chosen_dir
            self.main_content.path_display.configure(state="normal")
            self.main_content.path_display.delete(0, "end")
            self.main_content.path_display.insert(0, chosen_dir)
            self.main_content.path_display.configure(state="readonly")
            self.save_settings()

    def save_settings(self):
        self.settings.update({
            "theme": "Dark" if self.sidebar.theme_switch.get() else "Light", 
            "last_format": self.sidebar.format_var.get(),
            "last_quality": int(self.sidebar.quality_slider.get())
        })
        utils.save_settings(self.settings)

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.sidebar.theme_switch.get() else "Light")
        self.save_settings()

    def open_output_folder(self):
        os.startfile(self.settings.get("output_folder", utils.get_default_folder()))

    def clear_list(self):
        for w in self.row_widgets: w.destroy()
        self.file_paths, self.status_labels, self.row_widgets = [], {}, []
        self.main_content.placeholder_label.pack(pady=50)
        self.main_content.progress_bar.pack_forget()
        self.main_content.open_folder_btn.pack_forget()
        self.main_content.convert_btn.configure(text="START CONVERSION") # Reset text

    def drop_event(self, event):
        paths = self.tk.splitlist(event.data)
        valid_extensions = ('.heic', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.psd', '.cr2', '.nef', '.arw', '.dng', '.pdf')
        
        ignored_folders = 0
        ignored_files = 0
        added_any = False

        for p in paths:
            # Check if the dropped item is a directory
            if os.path.isdir(p):
                ignored_folders += 1
                continue
                
            # Check if it's an unsupported file type
            if not p.lower().endswith(valid_extensions):
                ignored_files += 1
                continue
                
            # Prevent duplicate entries in the current queue
            if p not in self.file_paths:
                self.file_paths.append(p)
                self.add_file_row(p)
                added_any = True

        # Handle UI visibility for the drag-and-drop placeholder
        if self.file_paths:
            self.main_content.placeholder_label.pack_forget()
        else:
            self.main_content.placeholder_label.pack(pady=50)

        # Show a temporary alert message on the main button if invalid items were dropped
        if ignored_folders > 0 or ignored_files > 0:
            warning_text = f"⚠️ Ignored: "
            parts = []
            if ignored_folders > 0: parts.append(f"{ignored_folders} folder(s)")
            if ignored_files > 0: parts.append(f"{ignored_files} unsupported file(s)")
            warning_text += " & ".join(parts)
            
            # Temporarily flash the warning message on the conversion button
            self.main_content.convert_btn.configure(text=warning_text, fg_color="#EF5350")
            
            # Restore the button to normal after 3 seconds
            self.after(3000, lambda: self.main_content.convert_btn.configure(
                text="START CONVERSION", 
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            ))

    def add_file_row(self, path):
        row = ctk.CTkFrame(self.main_content.file_list_frame)
        row.pack(fill="x", pady=2)
        self.row_widgets.append(row)
        ctk.CTkLabel(row, text="📄" if path.lower().endswith(".pdf") else "🖼️").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=os.path.basename(path), anchor="w").pack(side="left", fill="x", expand=True)
        status = ctk.CTkLabel(row, text="Pending", text_color="orange")
        status.pack(side="right", padx=10)
        self.status_labels[path] = status

    def start_conversion_thread(self):
        if not self.file_paths: return
        
        # Disable inputs across both layout panels
        self.sidebar.set_widgets_state("disabled")
        self.main_content.set_widgets_state("disabled")
        
        self.main_content.convert_btn.configure(state="disabled", text="Working...")
        self.main_content.progress_bar.pack(fill="x", pady=5)
        threading.Thread(target=self.execute_conversion).start()

    def execute_conversion(self):
        stats = converter.run_conversion(
            file_paths=self.file_paths,
            target_format=self.sidebar.format_var.get(),
            output_dir=self.settings["output_folder"],
            prefix_input=self.sidebar.name_entry.get(),
            merge_pdf=self.sidebar.merge_pdf_var.get(),
            quality_setting=int(self.sidebar.quality_slider.get()), # Pass slider value
            progress_callback=self.update_progress,
            status_callback=self.update_status,
            log_callback=utils.log_event
        )
        self.after(0, lambda: self.conversion_complete(stats))

    def conversion_complete(self, stats):
        # Re-enable inputs across both panels
        self.sidebar.set_widgets_state("normal")
        self.main_content.set_widgets_state("normal")
        
        saved_bytes_percentage = 0
        if stats["input_mb"] > 0:
            saved_bytes_percentage = ((stats["input_mb"] - stats["output_mb"]) / stats["input_mb"]) * 100
            
        summary_msg = f"⚡ Finished in {stats['duration']:.2f}s | Original: {stats['input_mb']:.2f}MB ➔ Output: {stats['output_mb']:.2f}MB ({saved_bytes_percentage:.1f}% space change)"
        
        self.main_content.convert_btn.configure(state="normal", text=summary_msg)
        self.main_content.open_folder_btn.pack(fill="x", pady=5)

    def update_progress(self, value):
        self.after(0, self.main_content.progress_bar.set, value)

    def update_status(self, path, text, color):
        self.after(0, lambda: self.status_labels[path].configure(text=text, text_color=color))

if __name__ == "__main__":
    PixelSwitchApp().mainloop()