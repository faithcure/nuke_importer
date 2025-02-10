# nuke_importer/core/plate_info.py
import os
import nuke

class PlateInfo:
    def __init__(self, file_path):
        self.file_path = file_path.replace('\\', '/')
        self.extension = os.path.splitext(self.file_path)[1].lower()
        self.resolution = None
        self.frame_range = None
        self.version = None
        self.colorspace = None
        self.size = None

    def analyze_metadata(self, current_first=None, current_last=None):
        """Analyze and extract metadata from the plate"""
        temp_node = None
        try:
            if not os.path.exists(self.file_path.replace('%04d', '0001')):
                return

            temp_node = nuke.createNode('Read', inpanel=False)
            temp_node['file'].fromUserText(self.file_path)

            self.resolution = f"{temp_node.width()} x {temp_node.height()}"
            if temp_node['last'].value() > temp_node['first'].value():
                self.frame_range = f"{int(temp_node['first'].value())}-{int(temp_node['last'].value())}"
            else:
                self.frame_range = "Single Frame"
            self.colorspace = temp_node['colorspace'].value()

        except Exception:
            pass
        finally:
            if temp_node:
                nuke.delete(temp_node)
            if current_first is not None and current_last is not None:
                nuke.Root()['first_frame'].setValue(current_first)
                nuke.Root()['last_frame'].setValue(current_last)