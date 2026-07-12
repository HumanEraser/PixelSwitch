# PixelSwitch 🚀
> Drag. Drop. Done. The last image converter you'll ever need.

![License](https://img.shields.io/github/license/[YourUsername]/[RepoName])
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**PixelSwitch** is a lightweight, offline image converter with a polished drag-and-drop interface.
Convert photos, RAW files, and PDFs locally with one click—no cloud upload, no login, no subscription.

## ✨ Key Features
- 🖼 **Drag & Drop:** Drop files directly into the app for instant queueing.
- 📁 **Batch Conversion:** Process many files at once with a single command.
- 🌙 **Dark Mode:** Clean UI with optional dark theme support.
- 📦 **Offline-first:** All processing happens locally on your device.
- 🖨️ **PDF Support:** Convert pages inside PDFs and optionally merge into a single PDF.
- 🔧 **Custom Prefix:** Add a filename prefix for easy output organization.
- 🎚️ **Quality Control:** Adjustable quality slider for JPG, JPEG, and WEBP exports.

## Supported Input Formats
- JPG / JPEG
- PNG
- WEBP
- HEIC
- BMP
- TIFF
- PSD
- RAW formats: CR2, NEF, ARW, DNG
- PDF

## Supported Output Formats
- JPG / JPEG
- PNG
- WEBP
- TIFF
- PDF

## Installation
```bash
git clone https://github.com/[YourUsername]/[RepoName].git
cd PixelSwitch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> Windows users should activate the virtual environment with `venv\Scripts\activate`.

## Usage
1. Run `python main.py`.
2. Drag files into the app window or click Browse to select an output folder.
3. Choose the output format and optional settings.
4. Click **START CONVERSION**.
5. Open the output folder when conversion completes.

## Packaging
The project includes PyInstaller packaging for standalone builds.
Example command:
```bash
pyinstaller --noconsole --onefile --name="PixelSwitchPro" --icon="icon.ico" --add-data "pixel_theme.json;." --add-data "icon.ico;." --add-data "gui;gui" main.py
```

## Dependencies
- customtkinter==5.2.2
- darkdetect==0.8.0
- pillow==12.1.1
- pillow_heif==1.2.0
- tkinterdnd2==0.4.3
- packaging==26.0

## Contributing
Contributions are welcome.
- Open an issue for feature requests or bugs.
- Submit a pull request with a clear description.
- Keep changes focused and easy to review.

## License
This project is released under the license shown in `LICENSE`.
