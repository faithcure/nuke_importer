# nuke_importer/__init__.py
from .ui.main_window import ProjectScannerTool

def start():
    """Initialize and show the main window"""
    start.form = ProjectScannerTool()
    start.form.show()