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
            # Replace frame pattern for first frame if it exists
            test_path = self.file_path.replace('%04d', '0001')
            if not os.path.exists(test_path):
                return

            temp_node = nuke.createNode('Read', inpanel=False)
            temp_node['file'].fromUserText(self.file_path)

            # Try to get resolution directly from node
            try:
                self.resolution = f"{temp_node.width()} x {temp_node.height()}"
            except:
                # If failed and it's an EXR, try to get from project settings
                if self.extension == '.exr':
                    self.resolution = self._get_format_from_project()

            # Get frame range
            if temp_node['last'].value() > temp_node['first'].value():
                self.frame_range = f"{int(temp_node['first'].value())}-{int(temp_node['last'].value())}"
            else:
                self.frame_range = "Single Frame"

            # Get colorspace
            self.colorspace = temp_node['colorspace'].value()

        except Exception as e:
            print(f"Error analyzing metadata: {str(e)}")
            # If error occurred with EXR, still try to get format from project
            if self.extension == '.exr':
                self.resolution = self._get_format_from_project()

        finally:
            if temp_node:
                nuke.delete(temp_node)
            if current_first is not None and current_last is not None:
                nuke.Root()['first_frame'].setValue(current_first)
                nuke.Root()['last_frame'].setValue(current_last)

    def _get_format_from_project(self):
        """Get resolution from project settings format"""
        try:
            root = nuke.root()
            format_node = root['format'].value()
            return f"{format_node.width()} x {format_node.height()}"
        except Exception as e:
            print(f"Error getting format from project: {str(e)}")
            return "N/A"