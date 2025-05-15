from usd_scene import SceneBuilder, MaterialLibrary, Environment, Camera
import os

# Create a scene
builder = SceneBuilder("./outputs/scenes/test_scene.usda")
materials = MaterialLibrary(builder.stage)
environment = Environment(builder.stage)
camera = Camera(builder.stage)

# Create materials and objects

# # car paint
# material = materials.create_car_paint("BluePaint", (0.1, 0.2, 0.8))

# glass
material = materials.create_glass("Glass", roughness = 0.02)

# Create an object at the origin with a selected material
sphere = builder.add_sphere("/World/Sphere", radius=1.0, material=material)

# Add a static camera looking at the object
camera_position = (-10, -5, -10)
camera.add_camera("/World/Camera", camera_position, target=(0, 0, 0))

# Set HDRI lighting
hdri_path = os.path.abspath("./assets/textures/studio_env.exr")
environment.set_hdri_lighting(hdri_path)

# Save
builder.save()

# Print USDA
builder.print_stage()