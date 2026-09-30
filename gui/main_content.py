import customtkinter as ctk
import os

class MainContentFrame(ctk.CTkFrame):
    def __init__(self, master, settings, change_output_folder, start_conversion, open_output_folder, default_folder):
        super().__init__(master, corner_radius=10)
        self.settings = settings
        self.master = master # Store reference to the main app

        # --- Top Header (Counter) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.queue_label = ctk.CTkLabel(self.header_frame, text="Queued: 0 files (0 MB)", font=("Arial", 14, "bold"))
        self.queue_label.pack(side="left", padx=5)

        # --- List Area ---
        self.file_list_frame = ctk.CTkScrollableFrame(self)
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # We need a frame to hold the placeholder text AND the new browse button
        self.placeholder_frame = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
        self.placeholder_frame.pack(pady=50)

        self.placeholder_label = ctk.CTkLabel(self.placeholder_frame, text="📂 Drag Photos, RAWs, or PDFs here!", text_color="gray", font=("Arial", 14))
        self.placeholder_label.pack(pady=(0, 10))
        
        self.add_files_btn = ctk.CTkButton(self.placeholder_frame, text="➕ Add Files", command=self.master.browse_files)
        self.add_files_btn.pack()

        # --- Bottom Action Area ---
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

        # This will hold the summary text now, so the button doesn't cut off
        self.summary_label = ctk.CTkLabel(self.action_frame, text="", text_color="green", font=("Arial", 12, "bold"))
        self.summary_label.pack(fill="x", pady=(0, 5))
        self.summary_label.pack_forget()

        self.convert_btn = ctk.CTkButton(self.action_frame, text="START CONVERSION", height=45, font=("Arial", 15, "bold"), command=start_conversion)
        self.convert_btn.pack(fill="x", pady=5)
        
        self.open_folder_btn = ctk.CTkButton(self.action_frame, text="Open Folder ↗️", fg_color="#A5D6A7", text_color="#2E7D32", command=open_output_folder)
        self.open_folder_btn.pack_forget()
        
    def set_widgets_state(self, state):
        self.browse_btn.configure(state=state)
        self.add_files_btn.configure(state=state)
        
        if state == "disabled":
            self.path_display.configure(state="disabled")
        else:
            self.path_display.configure(state="readonly")