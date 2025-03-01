# nuke_importer/ui/plate_list.py
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu,
                              QDialog, QVBoxLayout, QTextEdit, QApplication)
from PySide2.QtCore import Qt
import nuke
import os
import sys
import subprocess
import json
import re
from .filter_panel import FilterPanel
from ..config.settings import PLATE_LIST_COLUMNS, COLUMN_WIDTHS, STYLES, SUPPORTED_FORMATS
from ..core.plate_info import PlateInfo
from ..utils.file_utils import get_sequence_size, reveal_in_explorer
from ..utils.nuke_utils import create_read_node, create_readgeo_node,set_root_frame_range


class MetadataDialog(QDialog):
    def __init__(self, metadata, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plate Metadata")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Create text edit for metadata display
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        # Format metadata as pretty JSON
        formatted_metadata = json.dumps(metadata, indent=2)
        text_edit.setText(formatted_metadata)

        layout.addWidget(text_edit)

class PlateList(QTreeWidget):
    def __init__(self, current_first=1, current_last=100):
        super().__init__()
        self.current_first = current_first
        self.current_last = current_last
        self.wrong_plates = set()

        # Config dosyası için sabit yol
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.wrong_plates_file = os.path.join(self.config_dir, 'wrong_plates.json')

        self.setup_ui()
        self.setup_connections()
        self.load_wrong_plates()  # Wrong plates'leri başlangıçta yükle

    def setup_ui(self):
        """Set up the plate list UI"""
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
        self.itemSelectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        """Handle selection change"""
        if hasattr(self, 'current_first') and hasattr(self, 'current_last'):
            set_root_frame_range(self.current_first, self.current_last)

    def on_plate_double_clicked(self, item):
        """Handle double click on plate item - DISABLED"""
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
        self.apply_wrong_plates_highlight()
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
        """Show enhanced context menu for plate list items"""
        items = self.selectedItems()
        if not items:
            return

        menu = QMenu()

        # Import actions
        import_normal = menu.addAction("Just Import")

        # First divider
        menu.addSeparator()

        # File operations
        reveal_action = menu.addAction("To Explorer")
        open_action = menu.addAction("Open")
        copy_path_action = menu.addAction("Copy Path")

        # Second divider
        menu.addSeparator()

        # Plate management
        wrong_plate_action = menu.addAction("Toggle Wrong Plate")
        wrong_plate_action.setCheckable(True)

        # Get the first selected item's path
        first_item_path = items[0].data(0, Qt.UserRole)
        wrong_plate_action.setChecked(first_item_path in self.wrong_plates)

        show_metadata_action = menu.addAction("Show Metadata")

        # Connect actions - lambda fonksiyonlarını düzeltelim
        import_normal.triggered.connect(
            lambda checked=False: self.import_selected_plates())
        reveal_action.triggered.connect(
            lambda checked=False: self.reveal_in_explorer(items[0]))
        open_action.triggered.connect(
            lambda checked=False: self.open_file(items[0]))
        copy_path_action.triggered.connect(
            lambda checked=False: self.copy_path(items[0]))
        wrong_plate_action.triggered.connect(
            lambda checked=False: self.toggle_wrong_plate(items[0]))
        show_metadata_action.triggered.connect(
            lambda checked=False: self.show_metadata(items[0]))

        menu.exec_(self.viewport().mapToGlobal(position))

    def copy_path(self, item):
        """Copy file path to clipboard"""
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)
        QApplication.clipboard().setText(file_path)

    def toggle_wrong_plate(self, item):
        """Toggle wrong plate status"""
        if not item:
            return

        file_path = self.normalize_path(item.data(0, Qt.UserRole))

        if file_path in self.wrong_plates:
            self.wrong_plates.remove(file_path)
            for col in range(item.columnCount()):
                item.setBackground(col, Qt.transparent)
        else:
            self.wrong_plates.add(file_path)
            for col in range(item.columnCount()):
                item.setBackground(col, QColor(150, 0, 40))

        self.save_wrong_plates()
        self.save_wrong_plates()

    def show_metadata(self, item):
        """Show metadata dialog"""
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)

        try:
            # Get basic metadata
            metadata = {
                "File Name": os.path.basename(file_path),
                "Path": file_path,
                "Size": item.text(6),
                "Resolution": item.text(3),
                "Format": item.text(4),
                "Colorspace": item.text(5),
                "Frame Range": item.text(2),
                "Version": item.text(1)
            }

            # Get additional metadata from Nuke if possible
            try:
                temp_node = nuke.createNode('Read', inpanel=False)
                temp_node['file'].fromUserText(file_path)

                # Add Nuke-specific metadata
                metadata.update({
                    "Pixel Aspect": temp_node.pixelAspect(),
                    "FPS": temp_node['fps'].value(),
                    "Original Colorspace": temp_node['colorspace'].value(),
                    "Premultiplied": temp_node['premultiplied'].value(),
                    "Input Layer": temp_node['label'].value()
                })

                nuke.delete(temp_node)
            except:
                pass

            # Show dialog
            dialog = MetadataDialog(metadata, self)
            dialog.exec_()

        except Exception as e:
            print(f"Error showing metadata: {str(e)}")

    def load_wrong_plates(self):
        """Load wrong plates from config file"""
        try:
            if os.path.exists(self.wrong_plates_file):
                with open(self.wrong_plates_file, 'r') as f:
                    loaded_plates = json.load(f)
                    # Normalize loaded paths
                    self.wrong_plates = set(self.normalize_path(path) for path in loaded_plates)
                print(f"Wrong plates loaded from: {self.wrong_plates_file}")
                # Apply highlighting after loading
                self.apply_wrong_plates_highlight()
        except Exception as e:
            print(f"Error loading wrong plates: {str(e)}")

    def apply_wrong_plates_highlight(self):
        """Apply highlighting to wrong plates"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            file_path = self.normalize_path(item.data(0, Qt.UserRole))
            if file_path in self.wrong_plates:
                for col in range(item.columnCount()):
                    item.setBackground(col, QColor(150, 0, 40))

    def import_selected_plates(self):
        """Import selected plates with organized layout and backdrops"""
        items = self.selectedItems()
        if not items:
            return

        # Improved grid layout settings
        spacing_x = 250  # Increased horizontal node spacing
        spacing_y = 200  # Increased vertical node spacing
        backdrop_padding = 30  # Padding around nodes inside backdrop
        columns = 5  # Maximum nodes per row
        base_x = 0
        base_y = 0
        created_nodes = []

        for idx, item in enumerate(items):
            try:
                file_path = item.data(0, Qt.UserRole)
                folder_path = os.path.dirname(file_path)
                file_ext = item.text(4).lower()

                # Calculate grid position with better spacing
                col = idx % columns
                row = idx // columns
                pos_x = base_x + (col * spacing_x)
                pos_y = base_y - (row * spacing_y)

                # Get clean plate name (without extension and pattern)
                plate_name = os.path.splitext(item.text(0))[0]  # Remove extension
                # Remove common pattern indicators
                plate_name = plate_name.replace('####', '').replace('%04d', '')
                plate_name = plate_name.rstrip('._- ')  # Remove trailing separators

                # Track nodes created for this plate
                plate_nodes = []

                # Check if it's a 3D file
                if file_ext in ['.fbx', '.obj', '.abc']:
                    node_result = create_readgeo_node(file_path, pos_x, pos_y)
                    if node_result:
                        for node_key, node in node_result.items():
                            plate_nodes.append(node)
                        created_nodes.extend(plate_nodes)
                else:
                    # Handle normal read nodes
                    read_node = create_read_node(file_path,
                                                 frame_range=item.text(2),
                                                 colorspace=item.text(5),
                                                 pos_x=pos_x,
                                                 pos_y=pos_y)
                    if read_node:
                        plate_nodes.append(read_node)
                        created_nodes.append(read_node)

                # Only create backdrop if we successfully created nodes
                if plate_nodes:
                    # Calculate backdrop bounds
                    min_x = min(node.xpos() for node in plate_nodes)
                    min_y = min(node.ypos() for node in plate_nodes)
                    max_x = max(node.xpos() + node.screenWidth() for node in plate_nodes)
                    max_y = max(node.ypos() + node.screenHeight() for node in plate_nodes)

                    # Create backdrop with proper size to contain all nodes
                    backdrop = nuke.nodes.BackdropNode(
                        xpos=min_x - backdrop_padding,
                        ypos=min_y - backdrop_padding,
                        bdwidth=(max_x - min_x) + (backdrop_padding * 2),
                        bdheight=(max_y - min_y) + (backdrop_padding * 2) + 40,  # Extra space for label
                        tile_color=int(0x7533C2FF),  # Purple color
                        note_font_size=24,
                        label=plate_name  # Clean plate name
                    )

                    # Add backdrop to created nodes list
                    created_nodes.append(backdrop)

            except Exception as e:
                print(f"Error importing plate {item.text(0)}: {str(e)}")

        # Select all created nodes for zooming
        for node in created_nodes:
            node['selected'].setValue(True)

        # Zoom to fit all created nodes
        nuke.zoomToFitSelected()

        # Clear selection after zoom
        for node in created_nodes:
            node['selected'].setValue(False)

    def normalize_path(self, path):
        """Normalize file path for consistent comparison"""
        if path:
            # Replace backslashes with forward slashes
            return os.path.normpath(path).replace('\\', '/')
        return path

    def save_wrong_plates(self):
        """Save wrong plates to a config file"""
        try:
            # Normalize paths before saving
            normalized_plates = [self.normalize_path(path) for path in self.wrong_plates]
            with open(self.wrong_plates_file, 'w') as f:
                json.dump(normalized_plates, f, indent=4)
            # print(f"Wrong plates saved to: {self.wrong_plates_file}")
        except Exception as e:
            print(f"Error saving wrong plates: {str(e)}")

    def open_file(self, item):
        """Open file with default application"""
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)
        if not os.path.exists(file_path):
            return

        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', file_path])
            else:
                subprocess.Popen(['xdg-open', file_path])
        except Exception as e:
            print(f"Error opening file: {str(e)}")

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
