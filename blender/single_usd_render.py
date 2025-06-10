import bpy
import os
import math

# Deselect all objects
bpy.ops.object.select_all(action='SELECT')

# Delete all selected objects
bpy.ops.object.delete()

# Remove all meshes, materials, cameras, lights, etc.
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)
for block in bpy.data.textures:
    bpy.data.textures.remove(block)
for block in bpy.data.images:
    bpy.data.images.remove(block)
for block in bpy.data.lights:
    bpy.data.lights.remove(block)
for block in bpy.data.cameras:
    bpy.data.cameras.remove(block)
for block in bpy.data.curves:
    bpy.data.curves.remove(block)
for block in bpy.data.collections:
    bpy.data.collections.remove(block)


# Input directory (relative to .blend file)
usd_path = bpy.path.abspath("//usd_stages/test_scene_01.usda")
bpy.ops.wm.usd_import(filepath=usd_path, import_all_materials=True)

# Rotate everything 
for obj in bpy.context.scene.objects:
   obj.select_set(True)
   obj.rotation_euler[0] += math.radians(90)  # 90 deg in radians (X)
   obj.rotation_euler[2] += math.radians(180)  # 180 deg in radians (Z)
bpy.ops.object.select_all(action='DESELECT')

# Set up output
output_dir = bpy.path.abspath("//aov_export")
os.makedirs(output_dir, exist_ok=True)
target_object = "Target"

# Set up Cycles Renderer
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 128
bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" 

# Set up view layers
view_layer = bpy.context.view_layer
view_layer.use_pass_combined = True
view_layer.use_pass_z = True
view_layer.use_pass_normal = True
view_layer.use_pass_diffuse_direct = True
view_layer.use_pass_cryptomatte_object = True
view_layer.cycles.use_denoising = True

# Activate openUSD camera
for obj in bpy.context.scene.objects:
    if obj.type == 'CAMERA':
        bpy.context.scene.camera = obj
        break

# Set up compositor nodes
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
tree.nodes.clear()

# Shared nodes (not reset between renders)
rl = tree.nodes.new("CompositorNodeRLayers")
normalize = tree.nodes.new("CompositorNodeNormalize")
tree.links.new(rl.outputs["Depth"], normalize.inputs[0])

# File Output node
file_output = tree.nodes.new("CompositorNodeOutputFile")
file_output.base_path = output_dir
file_output.format.file_format = 'OPEN_EXR'
file_output.format.color_depth = '32'
file_output.format.exr_codec = 'ZIP'

# Get all usable materials
material_list = [mat for mat in bpy.data.materials if mat.users > 0 and mat.node_tree]

# Find target object
target_obj = bpy.data.objects.get(target_object)
if not target_obj:
    raise ValueError(f"Target object '{target_object}' not found in scene.")
    
# Loop over materials
for mat in material_list:
    mat_name = mat.name
    print(f"Rendering with material: {mat_name}")

    # Assign material to target object
    if len(target_obj.data.materials) == 0:
        target_obj.data.materials.append(mat)
    else:
        target_obj.data.materials[0] = mat

    # Clear and recreate file slots
    file_output.file_slots.clear()
    file_output.file_slots.new("Combined")
    file_output.file_slots.new("Depth")
    file_output.file_slots.new("Normal")
    file_output.file_slots.new("Diffuse_Direct")
    file_output.file_slots.new("Cryptomatte")

    # Set output paths
    file_output.file_slots["Combined"].path = f"{mat_name}_combined_"
    file_output.file_slots["Depth"].path = f"{mat_name}_depth_"
    file_output.file_slots["Normal"].path = f"{mat_name}_normal_"
    file_output.file_slots["Diffuse_Direct"].path = f"{mat_name}_diffuse_"
    file_output.file_slots["Cryptomatte"].path = f"{mat_name}_crypto_"

    # Reconnect outputs to new file slot inputs
    tree.links.new(rl.outputs["Image"], file_output.inputs["Combined"])
    tree.links.new(normalize.outputs[0], file_output.inputs["Depth"])
    tree.links.new(rl.outputs["Normal"], file_output.inputs["Normal"])
    tree.links.new(rl.outputs["DiffDir"], file_output.inputs["Diffuse_Direct"])
    tree.links.new(rl.outputs["CryptoObject00"], file_output.inputs["Cryptomatte"])

    # Render frame
    bpy.context.scene.frame_set(1)
    bpy.ops.render.render(write_still=True)

print("All renders completed successfully.")