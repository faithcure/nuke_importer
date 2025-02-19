# nuke_importer/ui/plate_list.py
import os
import re
import sys
import subprocess
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide2.QtCore import Qt
from .filter_panel import FilterPanel
from ..config.settings import PLATE_LIST_COLUMNS, COLUMN_WIDTHS, STYLES, SUPPORTED_FORMATS
from ..core.plate_info import PlateInfo
from ..utils.file_utils import get_sequence_size, reveal_in_explorer
from ..utils.nuke_utils import create_read_node, create_readgeo_node,set_root_frame_range

class PlateList(QTreeWidget):
    def __init__(self, current_first=1, current_last=100):
        super().__init__()
        self.current_first = current_first
        self.current_last = current_last
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the plate list UI"""
        self.setHeaderLabels(PLATE_LIST_COLUMNS)
        for col, width in COLUMN_WIDTHS.items():
            self.setColumnWidth(col, width)

        self.setSelectionMode(self.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setStyleSheet(STYLES['plate_list'])

        # Enable mouse tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

    def setup_connections(self):
        """Setup signal connections"""
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.on_plate_double_clicked)
        self.itemSelectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        """Handle selection change"""
        if hasattr(self, 'current_first') and hasattr(self, 'current_last'):
            set_root_frame_range(self.current_first, self.current_last)

    def on_plate_double_clicked(self, item):
        """Handle double click on plate item"""
        if not item:
            return

        file_path = item.text(7)  # Tam dosya yolunu al
        ext = item.text(4).lower()
        frame_range = item.text(2)

        try:
            if ext in ['.mov', '.mp4']:
                if sys.platform == 'win32':
                    os.startfile(file_path)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
            else:
                read_node = create_read_node(
                    file_path,
                    frame_range=frame_range,
                    colorspace=item.text(5)
                )

            if hasattr(self, 'current_first') and hasattr(self, 'current_last'):
                set_root_frame_range(self.current_first, self.current_last)

        except Exception as e:
            print(f"Error opening file {file_path}: {str(e)}")

    def scan_plates(self, folder_path, status_bar=None):
        """Scan plates in the selected folder"""
        self.clear()
        if not folder_path:
            return

        if status_bar:
            status_bar.setValue(0)
            status_bar.setFormat("Scanning plates...")

        # Debug print için format listesi
        # print("Supported formats:", SUPPORTED_FORMATS)

        # First pass: count total files and collect sequences
        total_files = 0
        plates = {}

        for root, _, files in os.walk(folder_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                # Debug: Her dosyanın uzantısını kontrol et
                # print(f"Checking file: {file} with extension: {file_ext}")

                if file_ext in SUPPORTED_FORMATS:
                    total_files += 1
                    # print(f"Found supported file: {file}")

        # print(f"Total supported files found: {total_files}")

        # Second pass: process files
        scanned_files = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in SUPPORTED_FORMATS:
                    if status_bar:
                        status_bar.setFormat(f"Scanning: {file}")

                    try:
                        # Video dosyaları için özel işleme
                        if file_ext in ['.mov', '.mp4', '.mkv', '.avi', '.wmv']:
                            # print(f"Processing video file: {file}")
                            self._handle_single_frame(os.path.join(root, file),
                                                      os.path.splitext(file)[0],
                                                      "v001")
                        else:
                            # Sequence veya diğer dosyalar için normal işleme
                            self._process_file(root, file, plates)

                        scanned_files += 1
                        if status_bar:
                            progress = int((scanned_files / total_files) * 100)
                            status_bar.setValue(progress)
                    except Exception as e:
                        print(f"Error processing file {file}: {str(e)}")

        # Add sequences to list
        if plates:
            self._add_sequences_to_list(plates, status_bar)

        if status_bar:
            status_bar.setFormat("Ready")
            status_bar.setValue(100)

        print(f"Scan complete. Processed {scanned_files} files.")

    def _process_file(self, root, file, plates):
        """Process individual file"""
        file_path = os.path.normpath(os.path.join(root, file))

        if not os.path.exists(file_path):
            return

        # Extract version
        version_match = re.search(r'v(\d+)', file, re.IGNORECASE)
        version = f"v{version_match.group(1)}" if version_match else "v001"

        # 3D dosya formatlarını kontrol et
        ext = os.path.splitext(file)[1].lower()
        is_3d_file = ext in ['.fbx', '.obj', '.abc']

        if is_3d_file:
            base_name = os.path.splitext(file)[0]
            self._handle_single_frame(file_path, base_name, version)
            return

        # Geliştirilmiş sekans algılama - farklı frame numaralandırma formatlarını destekle
        frame_patterns = [
            # Standard frame patterns
            r'_(\d+)\.([\w]+)$',  # underscore_number.ext
            r'\.(\d+)\.([\w]+)$',  # .number.ext
            r'(\d{2,})\.([\w]+)$',  # number.ext (en az 2 basamaklı)

            # Additional patterns for complex names
            r'[._](\d{2,})[._]',  # number between dots/underscores
            r'(\d{2,})_v\d+\.([\w]+)$',  # number_version.ext
            r'_v\d+_(\d+)\.([\w]+)$',  # version_number.ext
        ]

        base_name = None
        frame_num = None
        ext_match = None

        # Try each pattern until we find a match
        for pattern in frame_patterns:
            match = re.search(pattern, file)
            if match:
                frame_num = int(match.group(1))

                # Extract extension based on pattern
                if len(match.groups()) > 1:
                    ext_match = match.group(2)
                else:
                    # If pattern doesn't capture extension, get it directly
                    ext_match = os.path.splitext(file)[1][1:]  # Remove leading dot

                # Get base name by removing the frame number and extension
                full_match = match.group(0)
                base_name = file[:file.index(full_match)] + file[file.index(full_match):].replace(match.group(1),
                                                                                                  '%04d')
                break

        if frame_num is not None and base_name is not None:
            # Create plate key using the folder path and base name
            # This helps group frames that belong to the same sequence
            plate_key = (root, base_name, version)
            seq_path = os.path.join(root, f"{base_name}.{ext_match}")

            # Clean up display name
            display_name = os.path.basename(base_name.rstrip('._-'))

            if plate_key not in plates:
                plates[plate_key] = {
                    'min_frame': frame_num,
                    'max_frame': frame_num,
                    'ext': ext_match,
                    'path': seq_path,
                    'display_name': display_name,
                    'frames': {frame_num},
                    'first_frame_path': file_path
                }
            else:
                current_plate = plates[plate_key]
                current_plate['min_frame'] = min(current_plate['min_frame'], frame_num)
                current_plate['max_frame'] = max(current_plate['max_frame'], frame_num)
                current_plate['frames'].add(frame_num)

                # Update first frame path if this is the earliest frame
                if frame_num < min(current_plate['frames']):
                    current_plate['first_frame_path'] = file_path

        else:
            # Handle as single frame if no frame number pattern is found
            self._handle_single_frame(file_path, os.path.splitext(file)[0], version)

    def _handle_sequence(self, root, file, frame_match, display_name, version, plates):
        """Handle sequence file"""
        base_name = file[:frame_match.start()]
        frame_num = int(frame_match.group(1))
        ext = frame_match.group(2)

        plate_key = (root, base_name, version)
        seq_path = os.path.normpath(os.path.join(root, f"{base_name}.%04d.{ext}"))

        if plate_key not in plates:
            plates[plate_key] = {
                'min_frame': frame_num,
                'max_frame': frame_num,
                'ext': ext,
                'path': seq_path,
                'display_name': display_name
            }
        else:
            plates[plate_key]['min_frame'] = min(plates[plate_key]['min_frame'], frame_num)
            plates[plate_key]['max_frame'] = max(plates[plate_key]['max_frame'], frame_num)

    def _handle_single_frame(self, file_path, display_name, version):
        """Handle single frame file"""
        plate_info = PlateInfo(file_path)
        plate_info.analyze_metadata(self.current_first, self.current_last)

        item = QTreeWidgetItem(self)
        item.setText(0, display_name)
        item.setText(1, version)
        item.setText(2, "Single Frame")
        item.setText(3, plate_info.resolution if plate_info.resolution else "N/A")
        item.setText(4, os.path.splitext(file_path)[1])
        item.setText(5, plate_info.colorspace if plate_info.colorspace else "N/A")
        item.setText(6, get_sequence_size(file_path))
        item.setText(7, file_path)

        # UserRole'e tam dosya yolunu kaydediyoruz
        actual_path = file_path.replace('%04d', '0001') if '%04d' in file_path else file_path
        item.setData(0, Qt.UserRole, actual_path)

    def _add_sequences_to_list(self, plates, status_bar=None):
        """Add sequences to the plate list"""
        total_items = len(plates)

        for idx, ((root, base_name, version), info) in enumerate(plates.items()):
            try:
                frames = sorted(list(info['frames']))

                # If we have multiple frames, treat it as a sequence
                # regardless of frame numbering
                if len(frames) > 1:
                    plate_info = PlateInfo(info['path'])
                    plate_info.analyze_metadata(self.current_first, self.current_last)

                    item = QTreeWidgetItem(self)
                    item.setText(0, info['display_name'])
                    item.setText(1, version)
                    item.setText(2, f"{info['min_frame']}-{info['max_frame']}")
                    item.setText(3, plate_info.resolution if plate_info.resolution else "N/A")
                    item.setText(4, f".{info['ext']}")
                    item.setText(5, plate_info.colorspace if plate_info.colorspace else "N/A")
                    item.setText(6, get_sequence_size(
                        info['path'],
                        base_name,
                        f"{info['min_frame']}-{info['max_frame']}",
                        f".{info['ext']}"
                    ))
                    item.setText(7, info['path'])

                    # Thumbnail için ilk frame'in yolunu kullan
                    item.setData(0, Qt.UserRole, info.get('first_frame_path', info['path']))
                else:
                    # Single frame case
                    single_path = os.path.join(root, f"{base_name}.{info['ext']}")
                    if os.path.exists(single_path):
                        self._handle_single_frame(single_path, info['display_name'], version)

                if status_bar:
                    progress = int((idx + 1) / total_items * 100)
                    status_bar.setValue(progress)

            except Exception as e:
                print(f"Error adding sequence {info['path']}: {str(e)}")

    def show_context_menu(self, position):
        """Show context menu for plate list items"""
        item = self.itemAt(position)
        if item:
            menu = QMenu()
            import_local = menu.addAction("Import with Localization")
            import_normal = menu.addAction("Just Import")
            menu.addSeparator()
            reveal_action = menu.addAction("To Explorer")

            import_local.triggered.connect(
                lambda: self.import_single_plate(item, True))
            import_normal.triggered.connect(
                lambda: self.import_single_plate(item, False))
            reveal_action.triggered.connect(
                lambda: self.reveal_in_explorer(item))

            menu.exec_(self.viewport().mapToGlobal(position))

    def import_single_plate(self, item, localize=False):
        """Import a single plate"""
        if not item:
            return

        try:
            file_path = item.data(0, Qt.UserRole)
            frame_range = item.text(2)
            colorspace = item.text(5)
            file_ext = item.text(4).lower()

            # 3D dosyası kontrolü
            if file_ext in ['.fbx', '.obj', '.abc']:
                # 3D model import
                nodes = create_readgeo_node(file_path)
                if nodes:
                    print(f"Successfully imported 3D model: {file_path}")
            else:
                # Normal image/video import
                read_node = create_read_node(
                    file_path,
                    frame_range=frame_range,
                    colorspace=colorspace,
                    localize=localize
                )

                if frame_range != "Single Frame":
                    start_frame, end_frame = map(int, frame_range.split('-'))
                    set_root_frame_range(start_frame, end_frame)

        except Exception as e:
            print(f"Error importing plate {item.text(0)}: {str(e)}")

    # Bu metodu PlateList sınıfına ekleyin
    def apply_filters(self):
        """Apply filters to the plate list"""
        if not hasattr(self, 'parent'):
            return

        # Get filter values from filter panel
        filter_panel = self.parent().findChild(FilterPanel)
        if not filter_panel:
            return

        filters = filter_panel.get_filter_values()
        search_text = filters['search']
        format_filter = filters['format']
        version_filter = filters['version']
        sequence_only = filters['sequence_only']

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            show_item = True

            # Apply search filter
            if search_text and search_text not in item.text(0).lower():
                show_item = False

            # Apply format filter
            if format_filter != 'All Formats' and not item.text(4).endswith(format_filter):
                show_item = False

            # Apply version filter
            if version_filter != 'All Versions':
                if version_filter == 'Latest Version':
                    base_name = item.text(0)
                    versions = []
                    for j in range(self.topLevelItemCount()):
                        other_item = self.topLevelItem(j)
                        if other_item.text(0) == base_name:
                            versions.append(other_item.text(1))
                    if item.text(1) != max(versions):
                        show_item = False
                elif item.text(1) != version_filter:
                    show_item = False

            # Apply sequence filter
            if sequence_only and item.text(2) == "Single Frame":
                show_item = False

            item.setHidden(not show_item)

    def reveal_in_explorer(self, item):
        """Reveal file in explorer"""
        if item:
            path = os.path.dirname(item.data(0, Qt.UserRole))
            reveal_in_explorer(path)

    def import_plates(self, localize=False, status_bar=None):
        """Import multiple selected plates"""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        if status_bar:
            status_bar.setValue(0)

        # Grid layout settings
        spacing = 80
        columns = 5
        base_x = 0
        base_y = 0

        for idx, item in enumerate(selected_items):
            try:
                # Calculate grid position
                col = idx % columns
                row = idx // columns
                pos_x = base_x + (col * spacing)
                pos_y = base_y - (row * spacing)

                file_path = item.data(0, Qt.UserRole)
                frame_range = item.text(2)
                colorspace = item.text(5)
                file_ext = item.text(4).lower()

                # 3D dosyası kontrolü
                if file_ext in ['.fbx', '.obj', '.abc']:
                    # 3D model import with position
                    nodes = create_readgeo_node(file_path, pos_x, pos_y)
                    if nodes:
                        print(f"Successfully imported 3D model: {file_path}")
                else:
                    # Normal image/video import
                    read_node = create_read_node(
                        file_path,
                        frame_range=frame_range,
                        colorspace=colorspace,
                        localize=localize,
                        pos_x=pos_x,
                        pos_y=pos_y
                    )

                # Set project frame range for first plate (if it's not a 3D file)
                if idx == 0 and frame_range != "Single Frame" and file_ext not in ['.fbx', '.obj', '.abc']:
                    start_frame, end_frame = map(int, frame_range.split('-'))
                    set_root_frame_range(start_frame, end_frame)

                # Update progress
                if status_bar:
                    progress = int((idx + 1) / len(selected_items) * 100)
                    status_bar.setValue(progress)
                    status_bar.setFormat(f"Importing... {progress}%")

            except Exception as e:
                print(f"Error importing plate {item.text(0)}: {str(e)}")

        if status_bar:
            status_bar.setFormat("Ready")
            status_bar.setValue(100)

        # Reset frame range after import
        if hasattr(self, 'current_first') and hasattr(self, 'current_last'):
            set_root_frame_range(self.current_first, self.current_last)