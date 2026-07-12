import customtkinter as ctk

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, settings, on_format_change, toggle_theme, clear_list):
        super().__init__(master, width=220, corner_radius=0)
        self.settings = settings
        
        self.logo_label = ctk.CTkLabel(self, text="PixelSwitch Pro", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.format_label = ctk.CTkLabel(self, text="Convert to:", anchor="w")
        self.format_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.format_var = ctk.StringVar(value=self.settings.get("last_format", "JPG"))
        self.format_menu = ctk.CTkOptionMenu(self, variable=self.format_var, values=["JPG", "PNG", "WEBP", "PDF", "TIFF"], command=on_format_change)
        self.format_menu.grid(row=2, column=0, padx=20, pady=10)

        self.name_label = ctk.CTkLabel(self, text="Custom Prefix:", anchor="w")
        self.name_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.name_entry = ctk.CTkEntry(self, placeholder_text="e.g. Vacation")
        self.name_entry.grid(row=4, column=0, padx=20, pady=5)

        # --- Quality Slider UI Module ---
        self.quality_label = ctk.CTkLabel(self, text="Quality: 95%", anchor="w")
        self.quality_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.quality_slider = ctk.CTkSlider(self, from_=10, to=100, number_of_steps=18, command=self.update_quality_label)
        self.quality_slider.set(self.settings.get("last_quality", 95))
        self.quality_slider.grid(row=6, column=0, padx=20, pady=5)
        self.update_quality_label(self.quality_slider.get())

        self.overwrite_var = ctk.BooleanVar(value=True)
        self.overwrite_switch = ctk.CTkSwitch(self, text="Overwrite Files", variable=self.overwrite_var)
        self.overwrite_switch.grid(row=7, column=0, padx=20, pady=10)

        self.merge_pdf_var = ctk.BooleanVar(value=True)
        self.merge_pdf_switch = ctk.CTkSwitch(self, text="Merge into one PDF", variable=self.merge_pdf_var)
        self.merge_pdf_switch.grid(row=8, column=0, padx=20, pady=10)
        self.merge_pdf_switch.grid_remove()

        self.clear_btn = ctk.CTkButton(
            self, text="🗑️ Clear List", fg_color="transparent", border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"), command=clear_list
        )
        self.clear_btn.grid(row=9, column=0, padx=20, pady=20)

        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", command=toggle_theme)
        self.theme_switch.grid(row=11, column=0, padx=20, pady=20)
        self.grid_rowconfigure(10, weight=1)
        
        if self.settings.get("theme") == "Dark":
            self.theme_switch.select()

    def update_quality_label(self, value):
        self.quality_label.configure(text=f"Quality: {int(value)}%")

    def set_widgets_state(self, state):
        self.format_menu.configure(state=state)
        self.name_entry.configure(state=state)
        self.quality_slider.configure(state=state)
        self.overwrite_switch.configure(state=state)
        self.merge_pdf_switch.configure(state=state)
        self.clear_btn.configure(state=state)
        self.theme_switch.configure(state=state)