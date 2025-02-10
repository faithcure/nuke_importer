# 🎬 Nuke Importer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Nuke](https://img.shields.io/badge/nuke-13.0+-green.svg)

A powerful and user-friendly asset management tool for Nuke, designed to streamline your workflow with advanced import capabilities for various media formats.

## ✨ Features

### 🎯 Core Functionality
- **Smart Scanning**: Recursively scans directories for supported media files
- **Sequence Detection**: Automatically identifies and groups image sequences
- **Frame Range Management**: Intelligent handling of frame ranges and versioning
- **3D Model Support**: Preview and import FBX, OBJ, and Alembic files
- **Metadata Extraction**: Automatic colorspace and resolution detection

### 🎨 Media Support
- **Image Sequences**: EXR, DPX, JPEG, PNG, TIFF, and more
- **Video Formats**: MOV, MP4, MXF, ProRes
- **3D Models**: FBX, OBJ, ABC (Alembic)
- **Deep Image Support**: Deep EXR, DTEX
- **Industry Standards**: ACES, OCIO integration

### 💻 User Interface
- **Thumbnail Preview**: Real-time preview of images, sequences, and 3D models
- **Advanced Filtering**: Search by name, format, version, or sequence type
- **Grid Layout**: Organized node placement in Nuke
- **Progress Tracking**: Real-time feedback for operations
- **Context Menus**: Quick access to common operations

## 🚀 Installation

```bash
git clone https://github.com/faithcure/nuke_importer.git
cd nuke-importer
pip install -r requirements.txt
```

### Dependencies
- PySide2 >= 5.15.2
- Open3D >= 0.13.0
- NumPy >= 1.21.0
- Pillow >= 8.3.1
- Nuke >= 13.0
- OpenCv 

## 🔧 Usage

```python
import nuke_importer

# Start the application
nuke_importer.start()
```

## 🌟 Examples

### Basic Import
```python
# Import a sequence
read_node = create_read_node(
    file_path="path/to/sequence.%04d.exr",
    frame_range="1001-1100",
    colorspace="ACES"
)

# Import 3D model
geo_node = create_readgeo_node(
    file_path="path/to/model.fbx"
)
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- Documentation: [Wiki](https://github.com/yourusername/nuke-importer/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/nuke-importer/issues)
- Email: your.email@example.com

---
Made with ❤️ for the VFX community