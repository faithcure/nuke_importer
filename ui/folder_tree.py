# nuke_importer/ui/folder_tree.py
from PySide2.QtCore import QThread, Signal, Qt
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
import os
from ..config.settings import FOLDER_TREE_WIDTH, SUPPORTED_FORMATS
from ..utils.file_utils import get_file_extensions

class ScannerThread(QThread):
    progress = Signal(int)
    directory_found = Signal(str, list)
    scan_complete = Signal()
    
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.total_dirs = 0
        self.scanned_dirs = 0
        
    def run(self):
        for root, dirs, files in os.walk(self.path):
            extensions = {os.path.splitext(f)[1].lower() for f in files 
                        if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS}
            if extensions:
                self.directory_found.emit(root, list(extensions))
            
            self.scanned_dirs += 1
            progress = int((self.scanned_dirs / max(1, self.total_dirs)) * 100)
            self.progress.emit(progress)
            
        self.scan_complete.emit()

class FolderTree(QTreeWidget):
    def __init__(self, current_first=None, current_last=None):
        super().__init__()
        self.current_first = current_first
        self.current_last = current_last
        self.scanner_thread = None
        self.setup_ui()
        self.total_dirs = 0
        self.current_dir = 0

    def setup_ui(self):
        """Setup the folder tree UI"""
        self.setHeaderLabels(["Project Folders", "File Types"])
        self.setColumnWidth(0, FOLDER_TREE_WIDTH)

    def scan_directory(self, path, status_bar=None):
        """Scan directory and create tree structure"""
        if not path or not os.path.exists(path):
            return

        self.clear()
        self.status_bar = status_bar

        # Create root item
        self.root_item = QTreeWidgetItem(self)
        self.root_item.setText(0, os.path.basename(path))
        self.root_item.setData(0, Qt.UserRole, path)

        # Initialize scanner thread
        self.scanner_thread = ScannerThread(path)
        self.scanner_thread.progress.connect(
            lambda p: status_bar.setValue(p) if status_bar else None
        )
        self.scanner_thread.directory_found.connect(self._add_directory_item)
        self.scanner_thread.scan_complete.connect(self._on_scan_complete)

        # Scan root directory files
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        extensions = get_file_extensions(files)
        if extensions:
            self.root_item.setText(1, ", ".join(sorted(extensions)))

        # Start scanning
        if status_bar:
            status_bar.setFormat("Scanning directories...")
        self.scanner_thread.start()

    def _add_directory_item(self, path, extensions):
        """Add directory item to tree with extensions"""
        if not hasattr(self, 'root_item'):
            return

        parent = self.root_item
        rel_path = os.path.relpath(path, self.root_item.data(0, Qt.UserRole))
        parts = rel_path.split(os.sep)

        for i, part in enumerate(parts):
            found = False
            for j in range(parent.childCount()):
                child = parent.child(j)
                if child.text(0) == part:
                    parent = child
                    found = True
                    break

            if not found:
                item = QTreeWidgetItem(parent)
                item.setText(0, part)
                item.setData(0, Qt.UserRole, os.path.join(
                    parent.data(0, Qt.UserRole), part
                ))
                parent = item

        if extensions:
            parent.setText(1, ", ".join(sorted(extensions)))

    def _on_scan_complete(self):
        """Handle scan completion"""
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.setFormat("Ready")
            self.status_bar.setValue(100)