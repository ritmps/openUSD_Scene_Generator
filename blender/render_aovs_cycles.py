import bpy
import os
import math

# Input and output directory (relative to .blend file)
usd_path = bpy.path.abspath("//usd_stages/test_scene_01.usda")
output_dir = bpy.path.abspath("//aov_export")
os.makedirs(output_dir, exist_ok=True)

target_object = "Target"

# import and rotate everything 
bpy.ops.wm.usd_import(filepath=usd_path)

for obj in bpy.context.scene.objects:
    obj.select_set(True)
    obj.rotation_euler[0] += 1.5708  # 90 deg in radians (X)
    obj.rotation_euler[2] += 3.1416  # 180 deg in radians (Z)
bpy.ops.object.select_all(action='DESELECT')

# set up renderers
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 128
bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" 

# setup compositor nodes
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
tree.nodes.clear()

# Render Layers Node
rl = tree.nodes.new("CompositorNodeRLayers")

# Normalize depth
normalize = tree.nodes.new("CompositorNodeNormalize")
tree.links.new(rl.outputs["Depth"], normalize.inputs[0])

# File outputs
file_output = tree.nodes.new("CompositorNodeOutputFile")
file_output.base_path = output_dir
tree.links.new(rl.outputs["Image"], file_output.inputs["Image"])
tree.links.new(normalize.outputs[0], file_output.inputs.new("Depth", "Depth"))
tree.links.new(rl.outputs["Normal"], file_output.inputs.new("Normal", "Normal"))
tree.links.new(rl.outputs["DiffDir"], file_output.inputs.new("Diffuse_Direct", "Diffuse_Direct"))
tree.links.new(rl.outputs["CryptoObject00"], file_output.inputs.new("Cryptomatte", "Cryptomatte"))

# Setup cryptomatte passes
view_layer = bpy.context.view_layer
view_layer.use_pass_combined = True
view_layer.use_pass_z = True
view_layer.use_pass_normal = True
view_layer.use_pass_diffuse_direct = True
view_layer.use_pass_cryptomatte_object = True
view_layer.cycles.use_denoising = False

# find target and bind material for each iteration and render
target_obj = bpy.data.objects.get(target_object)
if not target_obj:
    raise ValueError(f"Target object '{target_object}' not found.")