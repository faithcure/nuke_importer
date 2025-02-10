# main_window.py
import nuke
import os
import socket
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QSplitter, QLabel, QPushButton)
from PySide2.QtCore import Qt
from .thumbnail_viewer import ThumbnailViewer
from ..config.settings import WINDOW_SIZE, PC_USER_MAPPINGS, WELCOME_MESSAGE
from ..utils.file_utils import setup_status_bar
from ..utils.nuke_utils import get_current_frame_range
from .folder_tree import FolderTree
from .plate_list import PlateList
from .filter_panel import FilterPanel


class ProjectScannerTool(QWidget):
    def __init__(self, parent=None):
        super(ProjectScannerTool, self).__init__(parent)
        self.setWindowTitle("Project Scanner")
        self.resize(*WINDOW_SIZE)

        # Store current frame range
        self.current_first, self.current_last = get_current_frame_range()

        # UI Setup
        self.init_ui()
        self.setup_connections()

        # Initialize scanning
        self.project_path = nuke.root()['project_directory'].value()
        if self.project_path:
            self.scan_project_directory()
        else:
            print("Project path err: 33, main_window.py")

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel with folder tree and thumbnail
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setLayout(left_layout)

        self.folder_tree = FolderTree()
        self.thumbnail_viewer = ThumbnailViewer()

        left_layout.addWidget(self.folder_tree)
        left_layout.addWidget(self.thumbnail_viewer)

        self.splitter.addWidget(left_panel)

        # Right panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

        # Add filter panel
        self.filter_panel = FilterPanel()
        self.right_layout.addWidget(self.filter_panel)

        # Add plate list
        self.plate_list = PlateList(self.current_first, self.current_last)
        self.right_layout.addWidget(self.plate_list)

        # Bottom panel with welcome message and close button
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_panel.setLayout(bottom_layout)

        # Get computer name and map to user
        computer_name = socket.gethostname()
        user_name = PC_USER_MAPPINGS.get(computer_name, 'User')

        # Create welcome label
        welcome_label = QLabel(WELCOME_MESSAGE.format(user_name=user_name))
        welcome_label.setStyleSheet("""
                    QLabel {
                        color: #808080;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #2b2b2b;
                        border-radius: 3px;
                        margin-right: 10px;
                    }
                """)

        # Create close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #808080;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        close_button.clicked.connect(self.close)

        # Add widgets to bottom layout
        bottom_layout.addWidget(welcome_label)
        bottom_layout.addWidget(close_button)

        self.right_layout.addWidget(bottom_panel)

        self.splitter.addWidget(self.right_panel)

        # Add splitter and status bar to main layout
        self.main_layout.addWidget(self.splitter)
        self.status_bar = setup_status_bar()
        self.main_layout.addWidget(self.status_bar)

    def setup_connections(self):
        """Setup signal connections"""
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        self.filter_panel.setup_connections(self.plate_list)
        self.plate_list.itemClicked.connect(self.update_thumbnail)

    def update_thumbnail(self, item):
        """Update thumbnail when plate is selected"""
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.thumbnail_viewer.set_thumbnail(file_path)
        else:
            self.thumbnail_viewer.clear_thumbnail()

    def scan_project_directory(self):
        """Start scanning project directory"""
        if not self.project_path:
            return

        self.status_bar.setValue(0)
        self.status_bar.setFormat("Scanning project directory...")
        self.folder_tree.scan_directory(self.project_path, self.status_bar)
        self.status_bar.setFormat("Ready")
        self.status_bar.setValue(100)

    def on_folder_selected(self, item):
        """Handle folder selection"""
        if not item:
            return
        folder_path = item.data(0, Qt.UserRole)
        if not folder_path:
            return

        self.status_bar.setValue(0)
        self.status_bar.setFormat(f"Scanning folder: {folder_path}")
        self.plate_list.scan_plates(folder_path, self.status_bar)
        self.filter_panel.update_filters(self.plate_list)
        self.status_bar.setFormat("Ready")
        self.status_bar.setValue(100)