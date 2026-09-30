# PixelSwitch Pro 🚀
> Drag. Drop. Done. The last image and document converter you'll ever need.

![License](https://img.shields.io/github/license/[HumanEraser]/[PixelSwitch])
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**PixelSwitch Pro** is a lightning-fast, 100% offline desktop application with a polished drag-and-drop interface. Convert photos, iPhone HEIC images, RAW files, and PDFs locally with zero cloud uploads, zero tracking, and complete data privacy.

## ✨ Key Features
- 🖼 **Flexible Import:** Drag & drop files directly into the window or use the built-in **Add Files** button.
- 📊 **Live Queue Management:** Real-time queue counter with total item count and payload size, individual file size indicators, instant **View** (👁️) preview, and **Remove** (❌) actions.
- 📁 **Batch Conversion:** Process large workloads locally using safe multithreading.
- 🌙 **Dark Mode:** Polished CustomTkinter UI with automatic light/dark mode and persistent preferences.
- 📦 **100% Offline-first:** All processing happens locally on your machine.
- 🖨️ **Smart PDF Integration:** Convert pages inside PDFs to individual images, or merge multiple images into a single multi-page PDF without memory spikes.
- 🔧 **Custom Prefix:** Add custom filename prefixes for clean, automated organization.
- 🎚️ **Dynamic Quality Control:** Adjustable quality slider with live compression tier descriptions for JPG, WEBP, and high-resolution exports.
- 🛡️ **Overwrite Protection:** Toggle file overwriting on or off with automatic unique-name fallback suffixes.

## Supported Input Formats
- JPG / JPEG
- PNG
- WEBP
- HEIC (iPhone / Apple format)
- BMP
- TIFF
- PSD
- RAW: CR2, NEF, ARW, DNG
- PDF

## Supported Output Formats
- JPG / JPEG
- PNG
- WEBP
- TIFF
- PDF

## Installation & Setup
```bash
git clone https://github.com/[HumanEraser]/[PixelSwitch].git
cd PixelSwitch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> Windows users should activate the virtual environment with `venv\Scripts\activate`.

## Usage
1. Run `python main.py`.
2. Drag files into the app window or click **Add Files** to select documents and photos.
3. Choose your target output format, quality level, prefix, and destination folder from the sidebar.
4. Click **START CONVERSION**.
5. Open your output folder directly from the app when complete.

## Packaging
The project includes PyInstaller packaging support for standalone desktop builds.

Example command:
```bash
pyinstaller --noconsole --onedir --name="PixelSwitch" --add-data "pixel_theme.json;." --add-data "icon.ico;." main.py
```

## Dependencies
- customtkinter==5.2.2
- darkdetect==0.8.0
- pillow==12.1.1
- pillow_heif==1.2.0
- tkinterdnd2==0.4.3
- pymupdf==1.25.0
- rawpy==0.23.0
- packaging==26.0

## Contributing
Contributions are welcome!

- Open an issue for feature requests or bug reports.
- Submit a pull request with a clear description of changes.

## License
This project is released under the license shown in `LICENSE`.