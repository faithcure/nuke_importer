"""
Main entry point for the Nuke Importer application.
"""
from ui.main_window import ProjectScannerTool

def start():
    """Initialize and show the main window"""
    start.form = ProjectScannerTool()
    start.form.show()

if __name__ == "__main__":
    start()
