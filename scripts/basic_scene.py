from usd_scene import SceneBuilder, MaterialLibrary, Environment

# Create a scene
builder = SceneBuilder("../outputs/scenes/test_scene.usda")
materials = MaterialLibrary(builder.stage)
environment = Environment(builder.stage)

# Create materials and objects
car_paint = materials.create_car_paint("BluePaint", (0.1, 0.2, 0.8))
sphere = builder.add_sphere("/World/CarPaintSphere", radius=2.0, material=car_paint)

# Add static camera looking at the sphere
builder.add_camera("/World/Camera", position=(0, 3, 10), target=(0, 0, 0))

# Set HDRI lighting
environment.set_hdri_lighting("../assets/textures/studio_env.exr")

# Save
builder.save()
