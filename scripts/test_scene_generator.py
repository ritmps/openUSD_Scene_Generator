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
USD_PATH = os.path.join(OUTPUT_DIR, "scenes", "test_scene_03.usda")
# METADATA_PATH = os.path.join(OUTPUT_DIR, "metadata", "camera_metadata_01.json")

# Create USD stage
builder = SceneBuilder(USD_PATH)
stage = builder.stage

# Materials
matlib = MaterialLibrary(stage)
yellow_plastic = matlib.create_plastic("RedPlastic", color=(0.6, 0.6, 0.1))
blue_car_paint = matlib.create_car_paint(name = "BlueCarPaints")

# # Add backdrop
# backdrop_path = "assets/scenes/backdrop.usdc"
# builder.add_external_asset(
#     path="/World/Backdrop",
#     asset_path=pathlib.Path(backdrop_path).as_posix(),  # Ensure POSIX-style paths
#     reference=True,
#     material=yellow_plastic
# )

# Add objects
object_position = (0, 2, 0)
builder.add_sphere("/World/Sphere", radius=1.0, material=blue_car_paint, position=object_position)

# Environment Light
env = Environment(stage)
hdri_path = Path("./assets/textures/studio_small_09_4k.exr").resolve().as_posix()
env.add_dome_light(hdri_path=hdri_path, intensity=2.0)

# Camera
camera_mgr = Camera(stage)

# # add static camera ring
# camera_mgr.generate_orbit_cameras(center=object_position, num_views=8)

# Add an camera and animate it
camera_position = (0, 10, -10)
main_cam = camera_mgr.add_camera(position=camera_position, target=object_position, focal_length=50.0)

# Animate it
# frame_pos, frame_tgt = generate_orbit_path(center=object_position, radius=10, height=10, frame_range=(0, 119))
# animate_camera(main_cam, frame_pos, frame_tgt)

# Export camera metadata
# camera_mgr.export_camera_metadata(main_cam, "test_output/main_camera_metadata.json")

# Save USD
builder.save()
builder.print_stage()