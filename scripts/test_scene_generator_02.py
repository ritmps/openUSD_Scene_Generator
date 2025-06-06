import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pathlib
from core.scene_builder import SceneBuilder
from core.material_lib import MaterialLibrary
from core.lighting import Environment
from core.camera import Camera
from animation.animator import animate_camera, generate_orbit_path

# Output directory
OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
USD_PATH = os.path.join(OUTPUT_DIR, "scenes", "test_scene_09.usda")

# Create USD stage
builder = SceneBuilder(USD_PATH)
stage = builder.stage

# Materials
matlib = MaterialLibrary(stage)
yellow_plastic = matlib.create_plastic("RedPlastic", color=(0.6, 0.6, 0.1))
blue_car_paint = matlib.create_car_paint(name = "BlueCarPaints")

# Add objects
object_position = (0, 0, 0)
builder.add_sphere("/World/Target", radius=1.0, material=blue_car_paint, position=object_position)

# Environment Light
env = Environment(stage)
hdri_path = Path("./assets/textures/studio_small_09_4k.exr").resolve().as_posix()
env.add_dome_light(hdri_path=hdri_path, intensity=2.0)

# Camera
camera_mgr = Camera(stage)

# ============ One Main Camera ==============#
# Add an camera
# camera_position = (0, 10, 10)
# main_cam = camera_mgr.add_camera(position=camera_position, target=object_position, focal_length=50.0)

# ============ Camera Ring ==================#
camera_mgr.generate_orbit_cameras(target=object_position, num_views=8)

# Save USD
builder.save()
builder.print_stage()