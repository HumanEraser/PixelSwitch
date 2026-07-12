import customtkinter as ctk
import os

class MainContentFrame(ctk.CTkFrame):
    def __init__(self, master, settings, change_output_folder, start_conversion, open_output_folder, default_folder):
        super().__init__(master, corner_radius=10)
        self.settings = settings
        
        self.file_list_frame = ctk.CTkScrollableFrame(self, label_text="Files to Convert")
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.placeholder_label = ctk.CTkLabel(self.file_list_frame, text="📂 Drag Photos, RAWs, or PDFs here!", text_color="gray", font=("Arial", 14))
        self.placeholder_label.pack(pady=50)

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self.path_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.path_frame.pack(fill="x", pady=5)
        
        self.path_display = ctk.CTkEntry(self.path_frame, state="normal")
        self.path_display.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.path_display.insert(0, self.settings.get("output_folder", default_folder))
        self.path_display.configure(state="readonly")

        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse...", width=80, command=change_output_folder)
        self.browse_btn.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.pack_forget()

        self.convert_btn = ctk.CTkButton(self.action_frame, text="START CONVERSION", height=45, font=("Arial", 15, "bold"), command=start_conversion)
        self.convert_btn.pack(fill="x", pady=5)
        
        self.open_folder_btn = ctk.CTkButton(self.action_frame, text="Open Folder ↗️", fg_color="#A5D6A7", text_color="#2E7D32", command=open_output_folder)
        self.open_folder_btn.pack_forget()
        
    def set_widgets_state(self, state):
        self.browse_btn.configure(state=state)
        # Entry widgets use 'readonly' instead of 'disabled' to look cleaner
        if state == "disabled":
            self.path_display.configure(state="disabled")
        else:
            self.path_display.configure(state="readonly")