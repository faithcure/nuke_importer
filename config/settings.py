
# nuke_importer/config/settings.py
"""
Global configuration settings for nuke_importer.
"""
# PC Mappings Configuration
PC_USER_MAPPINGS = {
    'CGR-02': 'Faithcure',
    'CGR-01': 'Behnan',
    'TUF21-COMP11': 'Efe',
    'TUF17-COMP10': 'Eralp',
    'TUF22-COMP12': 'Seckin',
    'TUF23-TD11': 'Sefa',
    'DEFAULT': 'User'  # Default kullanıcı adı
}

# Welcome Message Template
WELCOME_MESSAGE = "Your logs are being saved safely, GOOD LUCK {user_name}..."

# Supported file formats
SUPPORTED_FORMATS = [
    # Image Sequences / Still Images
    '.exr',         # OpenEXR (linear workflow için standart)
    '.dpx',         # Digital Picture Exchange (film scanning)
    '.cin',         # Cineon (film industry standard)
    '.jpg',         # JPEG
    '.jpeg',        # JPEG Alternative
    '.png',         # PNG (alpha channel support)
    '.tiff',        # TIFF (high quality)
    '.tif',         # TIFF Alternative
    '.tga',         # Targa (texture maps)
    '.sgi',         # Silicon Graphics Image
    '.rgb',         # SGI RGB
    '.rgba',        # SGI RGBA
    '.bmp',         # Windows Bitmap
    '.iff',         # Maya IFF
    '.pic',         # Softimage PIC
    '.psd',         # Photoshop Document
    '.psb',         # Photoshop Large Document
    '.hdr',         # High Dynamic Range
    '.rla',         # Wavefront RLA
    '.rpf',         # Rich Pixel Format
    '.zfile',       # Z-Depth
    '.dng',         # Digital Negative
    '.ari',         # ARRI Raw
    '.raw',         # Raw Image
    
    # Video Formats
    '.mov',         # QuickTime (industry standard)
    '.mp4',         # MPEG-4
    '.mxf',         # Material Exchange Format (broadcast)
    '.r3d',         # RED Raw
    '.avi',         # Audio Video Interleave
    '.mkv',         # Matroska Video
    '.wmv',         # Windows Media Video
    '.m4v',         # iTunes Video Format
    '.prores',      # Apple ProRes
    
    # Industry Specific
    '.ale',         # Avid Log Exchange
    '.cdl',         # Color Decision List
    '.cube',        # LUT format
    '.3dl',         # 3D LUT
    '.csp',         # Color Space
    '.clf',         # Common LUT Format
    
    # Deep Image Formats
    '.deepexr',     # Deep EXR
    '.dtex',        # Deep Texture
    '.deep',        # Generic Deep Format
    
    # Stereo/Multi-View
    '.sxr',         # Stereo EXR
    '.s3d',         # Stereo 3D
    
    # Render Passes/AOVs
    '.aov',         # Arbitrary Output Variables
    '.beauty',      # Beauty Pass
    '.shadow',      # Shadow Pass
    '.crypto',      # Cryptomatte
    
    # Legacy Formats
    '.pal',         # PAL Format
    '.yuv',         # YUV Format
    '.pict',        # PICT Format
    '.qtif',        # QuickTime Image Format
    '.sun',         # Sun Raster
    '.alias',       # Alias Image Format
    
    # Modern HDR/Wide Gamut
    '.arw',         # Sony Raw
    '.cr2',         # Canon Raw
    '.nef',         # Nikon Raw
    '.ocio',        # OpenColorIO Config

    # 3D Model Formats
    '.abc',         # Alembic Cache (animation, simulation)
    '.obj',         # Wavefront OBJ (geometry)
    '.fbx',         # Filmbox (3D interchange)
    '.usd',         # Universal Scene Description
    '.usda',        # USD ASCII
    '.usdc',        # USD Binary
    '.usdz',        # USD Zipped
    '.vdb',         # OpenVDB (volumetrics)
    '.ptc',         # Point Cloud

     # Deep Image Formats
    '.deepexr',     # Deep EXR
    '.dtex',        # Deep Texture
    '.deep',        # Generic Deep Format
]

# UI Configuration
WINDOW_SIZE = (1200, 800)
GRID_SPACING = 80
GRID_COLUMNS = 5

# Column widths for plate list
PLATE_LIST_COLUMNS = [
    "Plate Name", "Version", "Frame Range",
    "Resolution", "Format", "Colorspace", "Size", "Path"
]

COLUMN_WIDTHS = {
    0: 200,  # Plate Name
    1: 80,   # Version
    2: 100,  # Frame Range
    3: 100,  # Resolution
    4: 80,   # Format
    5: 100,  # Colorspace
    6: 80    # Size
}

# Style settings
STYLES = {
    'progress_bar': """
        QProgressBar {
            text-align: left;
        }
        QProgressBar::chunk {
            background-color: #606060;
        }
    """,
    'plate_list': """
        QTreeWidget::item:hover {
            background-color: #404040;
        }
    """
}

# Tree column settings
FOLDER_TREE_WIDTH = 250

# Filter settings
FORMAT_FILTERS = [
    'All Formats',
    # Image Formats
    '.exr',      # OpenEXR
    '.dpx',      # Digital Picture Exchange
    '.jpg',      # JPEG
    '.jpeg',     # JPEG Alternative
    '.png',      # Portable Network Graphics
    '.tiff',     # Tagged Image File Format
    '.tif',      # TIFF Alternative
    '.tga',      # Targa
    # '.bmp',      # Bitmap
    '.cin',      # Cineon
    '.dng',      # Digital Negative
    '.ari',      # ARRIRAW
    '.arw',      # Sony RAW
    '.cr2',      # Canon RAW
    # '.nef',      # Nikon RAW
    '.raw',      # RAW
    # '.iff',      # Maya IFF
    # '.gif',      # Graphics Interchange Format
    '.hdr',      # High Dynamic Range
    # '.webp',     # WebP
    '.psd',      # Photoshop Document
    # '.psb',      # Photoshop Big
    
    # Video Formats
    '.mov',      # QuickTime Movie
    '.mp4',      # MPEG-4
    '.mxf',      # Material Exchange Format
    # '.r3d',      # RED Raw Video
    '.avi',      # Audio Video Interleave
    # '.wmv',      # Windows Media Video
    '.mkv',      # Matroska Video
    '.m4v',      # iTunes Video
    '.prores',   # Apple ProRes
    
    # 3D Formats
    '.abc',      # Alembic Cache
    '.fbx',      # Filmbox
    '.obj',      # Wavefront Object
    '.usd',      # Universal Scene Description
    # '.usda',     # USD ASCII
    # '.usdc',     # USD Crate
    # '.usdz',     # USD Zip
    # '.ma',       # Maya ASCII
    # '.mb',       # Maya Binary
    # '.blend',    # Blender
    # '.c4d',      # Cinema 4D
    # '.hip',      # Houdini
    # '.hipnc',    # Houdini Non-Commercial
    # '.hda',      # Houdini Digital Asset
    '.vdb',      # OpenVDB
    # '.glb',      # GL Transmission Binary
    # '.gltf',     # GL Transmission Format
    # '.3ds',      # 3D Studio
    # '.max',      # 3ds Max
    # '.lwo',      # Lightwave Object
    # '.ply',      # Polygon File Format
    # '.stl',      # Stereolithography
    # '.vrst',     # VRST Cache
    # '.x3d',      # Extensible 3D Graphics
    
    # Point Cloud Formats
    '.pts',      # Points
    '.ptx',      # Leica Point Cloud
    # '.las',      # LAS Point Cloud
    # '.laz',      # Compressed LAS
    
    # Additional Image Sequence Formats
    # '.rgb',      # Silicon Graphics Image
    # '.rgba',     # RGBA Image
    # '.sgi',      # Silicon Graphics Format
    # '.pic',      # Softimage Picture
    # '.rla',      # Wavefront RLA
    # '.rpf',      # Rich Pixel Format
    # '.zfile',    # Z-Depth File
]
VERSION_FILTERS = ['All Versions', 'Latest Version']