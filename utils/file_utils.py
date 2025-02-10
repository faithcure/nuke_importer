# nuke_importer/utils/file_utils.py
import os
import sys
import subprocess
from PySide2.QtWidgets import QProgressBar
from ..config.settings import STYLES, SUPPORTED_FORMATS

def format_size(size_bytes):
    """Format file size to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_sequence_size(folder_path, base_name=None, frame_range=None, ext=None):
    """Calculate total size of a sequence"""
    try:
        if frame_range == "Single Frame" or not frame_range:
            return format_size(os.path.getsize(folder_path))

        total_size = 0
        start_frame, end_frame = map(int, frame_range.split('-'))

        for frame in range(start_frame, end_frame + 1):
            frame_path = os.path.join(os.path.dirname(folder_path),
                                    f"{base_name}.{frame:04d}{ext}")
            if os.path.exists(frame_path):
                total_size += os.path.getsize(frame_path)

        return format_size(total_size)
    except:
        return "N/A"

def setup_status_bar():
    """Create and configure status bar"""
    status_bar = QProgressBar()
    status_bar.setMaximumHeight(14)
    status_bar.setTextVisible(True)
    status_bar.setStyleSheet(STYLES['progress_bar'])
    return status_bar

def reveal_in_explorer(path):
    """Open file explorer at the specified path"""
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])

def set_root_frame_range(start_frame, end_frame):
    """Set frame range in Nuke root"""
    if start_frame is not None and end_frame is not None:
        nuke.Root()['first_frame'].setValue(start_frame)
        nuke.Root()['last_frame'].setValue(end_frame)

def get_supported_files(path):
    """Get list of supported files in directory"""
    supported_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                supported_files.append(os.path.join(root, file))
    return supported_files

def get_file_extensions(files):
    """Get set of supported file extensions from files"""
    return {os.path.splitext(f)[1].lower() for f in files 
            if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS}

def on_selection_changed(self):
    """Handle selection change"""
    if hasattr(self, 'current_first') and hasattr(self, 'current_last') and \
       self.current_first is not None and self.current_last is not None:
        set_root_frame_range(self.current_first, self.current_last)