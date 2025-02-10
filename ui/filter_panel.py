# filter_panel.py
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QCheckBox, QGroupBox)
from ..config.settings import FORMAT_FILTERS, VERSION_FILTERS

class FilterPanel(QWidget):
    def __init__(self, parent=None):
        super(FilterPanel, self).__init__(parent)
        
        # Create main layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Create group box
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout()
        filter_group.setLayout(filter_layout)

        # Search filter
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search in plate names...")

        # Format filter
        self.format_filter = QComboBox()
        self.format_filter.addItems(FORMAT_FILTERS)

        # Version filter
        self.version_filter = QComboBox()
        self.version_filter.addItems(VERSION_FILTERS)

        # Sequence filter
        self.sequence_only = QCheckBox("Sequences Only")

        # Add components to layout
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_filter)
        filter_layout.addWidget(QLabel("Format:"))
        filter_layout.addWidget(self.format_filter)
        filter_layout.addWidget(QLabel("Version:"))
        filter_layout.addWidget(self.version_filter)
        filter_layout.addWidget(self.sequence_only)

        # Add group to main layout
        main_layout.addWidget(filter_group)

    def setup_connections(self, plate_list):
        """Setup signal connections with plate list"""
        self.search_filter.textChanged.connect(plate_list.apply_filters)
        self.format_filter.currentTextChanged.connect(plate_list.apply_filters)
        self.version_filter.currentTextChanged.connect(plate_list.apply_filters)
        self.sequence_only.stateChanged.connect(plate_list.apply_filters)

    def update_filters(self, plate_list):
        """Update version filter based on available versions"""
        if not plate_list:
            return

        current_versions = set()
        for i in range(plate_list.topLevelItemCount()):
            item = plate_list.topLevelItem(i)
            current_versions.add(item.text(1))

        self.version_filter.clear()
        self.version_filter.addItems(VERSION_FILTERS + sorted(list(current_versions)))

    def get_filter_values(self):
        """Get current filter values"""
        return {
            'search': self.search_filter.text().lower(),
            'format': self.format_filter.currentText(),
            'version': self.version_filter.currentText(),
            'sequence_only': self.sequence_only.isChecked()
        }