from usd_scene import SceneBuilder, MaterialLibrary, Environment, Camera, RenderSettingsManager
import os

# Create a scene
builder = SceneBuilder("./outputs/scenes/test_scene.usda")
materials = MaterialLibrary(builder.stage)
environment = Environment(builder.stage)
camera = Camera(builder.stage)

# Create materials and objects

# --- Create multiple materials ---
blue_paint = materials.create_car_paint("BluePaint", (0.1, 0.2, 0.8))
red_paint = materials.create_car_paint("RedPaint", (0.8, 0.1, 0.1))
green_paint = materials.create_car_paint("GreenPaint", (0.1, 0.8, 0.1))
glass = materials.create_glass("Glass", roughness=0.02)

# Create an object at the origin with a selected material
sphere = builder.add_sphere("/World/Sphere", radius=1.0, material=blue_paint)

# Add a static camera looking at the object
camera_path = "/World/Camera"
camera_position = (-10, 5, -10)
camera.add_camera(camera_path, camera_position, target=(0, 0, 0))

# Set HDRI lighting
hdri_path = os.path.abspath("./assets/textures/studio_env.exr")
environment.set_hdri_lighting(hdri_path)

# ---------- Add Render Settings ----------

# Create render settings
render_mgr = RenderSettingsManager(builder.stage)

# Create RenderVars
color_var = render_mgr.create_render_var("color", "Ci")
depth_var = render_mgr.create_render_var("depth", "z", data_type="float", source_type="builtin")


# Create RenderProducts
color_product = render_mgr.create_render_product("ColorProduct", camera_path, "./outputs/renders/color.exr", [color_var])
depth_product = render_mgr.create_render_product("DepthProduct", camera_path, "./outputs/renders/depth.exr", [depth_var])

# Create RenderSettings prim referencing both products
render_mgr.create_basic_render_settings("PrimarySettings", camera_path, resolution=(512, 512), products=[
    color_product,
    depth_product
])
# -----------------------------------------

# Save
builder.save()

# Print USDA
builder.print_stage()
