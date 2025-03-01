# 🎬 Nuke Importer

![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Nuke](https://img.shields.io/badge/nuke-13.0+-green.svg)

A powerful and user-friendly asset importer tool for Nuke, designed to streamline your workflow with advanced import capabilities for various media formats.

# ✨ Features

## 🌟 Examples



### 🎯 Core Functionality
- **Smart Scanning**: Recursively scans directories for supported media files
- **Sequence Detection**: Automatically identifies and groups image sequences
- **3D Model Support**: Preview and import FBX, OBJ, USD
- **Metadata Extraction**: Get Low Metadata LMB

### 🎨 Media Support
- **Image Sequences**: EXR, DPX, JPEG, PNG, TIFF, and more
- **Video Formats**: MOV, MP4
- **3D Models**: FBX, OBJ, USD

### 💻 User Interface
- **Thumbnail Preview**: Real-time preview of images, sequences, and 3D models
- **Advanced Filtering**: Search by name, format, version, or sequence type
- **Grid Layout**: Organized node placement in Nuke
- **Progress Tracking**: Real-time feedback for operations
- **Context Menus**: Quick access to common operations
- 
## ⚠️ Important Notes

1. **Project Directory Requirement**: The Project Directory must be set within Nuke. This plugin only scans folders within the configured project directory.

2. **No Content Without Project Directory**: If the project directory is not set, the plugin will not display any content.

3. **Scanning Scope**: This plugin only scans units under the project directory and doesn't access files in other locations.

> 💡 To set the project directory: Open the `Project Settings` panel in Nuke and enter a valid directory path in the `Project Directory` field.
> 
## 🚀 Installation (FOR DEVELOPERS)

```bash
git clone https://github.com/faithcure/nuke_importer.git
cd nuke_importer
pip install -r requirements.txt
```

### Dependencies
- PySide2 >= 5.15.2
- Open3D >= 0.13.0
- NumPy >= 1.21.0
- Pillow >= 8.3.1
- Nuke >= 13.0
- OpenCv 

## 🔧 Usage (FOR ALL)
#pip install open3d, opencv-python # if you need.
## ⚠️ Critical Installation Requirements
Before using this plugin, you must install required dependencies within Nuke's Python environment. Without these installations, the plugin **will not function properly** - specifically, thumbnails and 3D previews will fail to load.
- open terminal or cmd and run these:
### Windows
```batch
"C:\Program Files\Nuke14.1v3\python.exe" -m pip install open3d
"C:\Program Files\Nuke14.1v3\python.exe" -m pip install opencv-python
```
### macOS
```batch
/Applications/Nuke14.1v3/Nuke14.1v3.app/Contents/MacOS/python -m pip install open3d
/Applications/Nuke14.1v3/Nuke14.1v3.app/Contents/MacOS/python -m pip install opencv-python
```
### Linux
```batch
/opt/Nuke14.1v3/python -m pip install open3d
/opt/Nuke14.1v3/python -m pip install opencv-python
```
Paste "nuke_importer" folder in to ".nuke" path or where you want.
- menu.py: 
```python
import nuke_importer
import importlib # if you want!
# Nuke Importer
def start_nuke_importer():
   importlib.reload(nuke_importer) # if you want!
   nuke_importer.start()
i.addCommand("Plate Importer --online", "nuke_importer.start()")

```
- init.py:
```python
# add folder to he plugin path
nuke.pluginAddPath('nuke_importer')
```

## 📝 License

This project is licensed under the Apache License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/nuke-importer/issues)

---
Made with ❤️ for the VFX community
