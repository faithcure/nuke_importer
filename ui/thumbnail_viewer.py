from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage
import os
import nuke
import open3d as o3d
import numpy as np
import cv2


class ThumbnailViewer(QWidget):
    def __init__(self, parent=None):
        super(ThumbnailViewer, self).__init__(parent)
        self.setup_ui()
        self.current_3d_file = None
        self.supported_3d_formats = ['.fbx', '.obj', '.abc']
        self.supported_image_formats = ['.jpg', '.jpeg', '.png']
        self.supported_video_formats = ['.mov', '.mp4', '.mkv', '.avi']
        self.exr_file_ext = [".exr"]

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setMinimumHeight(200)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                color: white;
            }
        """)
        layout.addWidget(self.thumbnail_label)
        self.thumbnail_label.mousePressEvent = self.on_thumbnail_click

    def set_thumbnail(self, file_path):
        """Set thumbnail based on file type"""
        if not file_path or not os.path.exists(file_path):
            self.clear_thumbnail()
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext in self.supported_3d_formats:
            self.set_thumbnail_3D(file_path)
        elif ext in self.supported_image_formats:
            self.set_image_thumbnail(file_path)
        elif ext in self.supported_video_formats:
            self.set_video_thumbnail(file_path)
        elif ext in self.exr_file_ext:
            self.set_thumbnail_exr(file_path)
        else:
            self.clear_thumbnail()

    def set_video_thumbnail(self, file_path):
        """Set thumbnail for video files using OpenCV"""
        try:
            # Open video file
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise Exception("Could not open video file")

            # Read first frame
            ret, frame = cap.read()
            if not ret:
                raise Exception("Could not read video frame")

            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get frame dimensions
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width

            # Create QImage from frame
            q_img = QImage(frame_rgb.data, width, height,
                         bytes_per_line, QImage.Format_RGB888)

            # Convert to pixmap and scale
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Set thumbnail
            self.thumbnail_label.setPixmap(scaled_pixmap)

            # Release video capture
            cap.release()

        except Exception as e:
            print(f"Error loading video thumbnail: {str(e)}")
            self.thumbnail_label.setText("Video Preview\nError")

    def set_image_thumbnail(self, file_path):
        """Set thumbnail for regular image files"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
            else:
                self.clear_thumbnail()
        except Exception as e:
            print(f"Error loading image thumbnail: {str(e)}")
            self.clear_thumbnail()

    def set_thumbnail_exr(self, file_path):
        """Set thumbnail for EXR files"""
        print("Set thumbnail exr clicked")
        self.clear_thumbnail()

    def set_thumbnail_3D(self, file_path):
        """Set thumbnail for 3D files"""
        if not file_path or not os.path.exists(file_path):
            self.clear_thumbnail()
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.supported_3d_formats:
            self.current_3d_file = file_path
            self.thumbnail_label.setText("3D File\nClick to View")
            self.thumbnail_label.setStyleSheet("""
                QLabel {
                    background-color: #2b2b2b;
                    border: 1px solid #3a3a3a;
                    color: white;
                    font-size: 14px;
                }
            """)
        else:
            self.clear_thumbnail()

    def clear_thumbnail(self):
        """Clear the thumbnail"""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("No Preview Available")
        self.current_3d_file = None

    def on_thumbnail_click(self, event):
        """Handle thumbnail click"""
        if self.current_3d_file and os.path.exists(self.current_3d_file):
            self.show_3d_viewer(self.current_3d_file)

    def show_3d_viewer(self, file_path):
        """Show 3D viewer for supported files"""
        try:
            mesh = o3d.io.read_triangle_mesh(file_path)
            if mesh.is_empty():
                nuke.message("Could not load 3D file.")
                return

            mesh.compute_vertex_normals()
            vis = o3d.visualization.Visualizer()
            vis.create_window(width=800, height=600)

            opt = vis.get_render_option()
            opt.background_color = np.asarray([0.2, 0.2, 0.2])
            opt.show_coordinate_frame = True
            opt.mesh_show_wireframe = False

            vis.add_geometry(mesh)
            ctr = vis.get_view_control()
            ctr.set_zoom(0.8)

            vis.run()
            vis.destroy_window()

        except Exception as e:
            nuke.message(f"Error viewing 3D file: {str(e)}")