# nuke_importer/utils/nuke_utils.py
import nuke
import os
import re


def create_read_node(file_path, frame_range=None, colorspace=None,
                     localize=False, pos_x=0, pos_y=0):
    """Create a Read node with the given settings"""
    try:
        read_node = nuke.nodes.Read()
        read_node.setXYpos(pos_x, pos_y)
        read_node['file'].fromUserText(file_path)

        if frame_range and frame_range != "Single Frame":
            start_frame, end_frame = map(int, frame_range.split('-'))
            read_node['first'].setValue(start_frame)
            read_node['last'].setValue(end_frame)
            read_node['origfirst'].setValue(start_frame)
            read_node['origlast'].setValue(end_frame)

        if colorspace and colorspace != "N/A":
            read_node['colorspace'].setValue(colorspace)

        if localize:
            read_node['localizationPolicy'].setValue(1)

        # Create safe node name
        base_name = os.path.basename(file_path)
        node_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        try:
            read_node.setName(node_name)
        except:
            pass

        return read_node
    except Exception as e:
        print(f"Error creating Read node: {str(e)}")
        return None


def create_readgeo_node(file_path, pos_x=0, pos_y=0):
    """Create a ReadGeo node for 3D models"""
    try:
        # Create ReadGeo node
        geo_node = nuke.nodes.ReadGeo2()
        geo_node.setXYpos(pos_x, pos_y)

        # Set file path
        geo_node['file'].fromUserText(file_path)

        # Set common parameters
        geo_node['display'].setValue('solid')  # Solid display mode
        geo_node['render_mode'].setValue('textured')  # Textured render mode

        # Add Scene node for better viewport handling
        scene = nuke.nodes.Scene()
        scene.setInput(0, geo_node)
        scene.setXYpos(pos_x, pos_y + 50)

        # Add Camera node
        cam = nuke.nodes.Camera2()
        cam.setXYpos(pos_x - 100, pos_y)

        # Set initial camera position
        cam['translate'].setValue([0, 0, 5])  # Move camera back
        cam['rotate'].setValue([0, 0, 0])  # Reset rotation

        # Add ScanlineRender node
        render = nuke.nodes.ScanlineRender()
        render.setXYpos(pos_x, pos_y + 100)
        render.setInput(0, scene)  # Connect Scene
        render.setInput(1, cam)  # Connect Camera

        # Set safe node name
        base_name = os.path.basename(file_path)
        node_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        try:
            geo_node.setName(f"Geo_{node_name}")
            scene.setName(f"Scene_{node_name}")
            cam.setName(f"Cam_{node_name}")
            render.setName(f"Render_{node_name}")
        except:
            pass

        return {
            'geo': geo_node,
            'scene': scene,
            'camera': cam,
            'render': render
        }

    except Exception as e:
        print(f"Error creating ReadGeo node: {str(e)}")
        return None


def get_current_frame_range():
    """Get current frame range from Nuke root"""
    return (nuke.Root()['first_frame'].value(),
            nuke.Root()['last_frame'].value())


def set_root_frame_range(start_frame, end_frame):
    """Set frame range in Nuke root"""
    nuke.Root()['first_frame'].setValue(start_frame)
    nuke.Root()['last_frame'].setValue(end_frame)