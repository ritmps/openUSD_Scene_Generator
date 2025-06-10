import bpy
import os
import math

# === CONFIGURATION ===
usd_dir = bpy.path.abspath("//usd_stages")
output_dir_base = bpy.path.abspath("//aov_export")
target_object_name = "Target"

# Set up Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 128
bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

# === UTILITY: Scene Cleanup ===
def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)
    for data_block in [bpy.data.meshes, bpy.data.materials, bpy.data.textures,
                       bpy.data.images, bpy.data.lights, bpy.data.cameras, bpy.data.curves]:
        for block in data_block:
            data_block.remove(block)
    
    # reset environment lighting
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
        
    world = bpy.context.scene.world
    world.use_nodes = True
    node_tree = world.node_tree
    
    # Clear all nodes in the World shader
    if node_tree:
        node_tree.nodes.clear()
    bg = node_tree.nodes.new("ShaderNodeBackground")
    output = node_tree.nodes.new("ShaderNodeOutputWorld")
    node_tree.links.new(bg.outputs["Background"], output.inputs["Surface"])
    bg.inputs["Strength"].default_value = 1.0

            
# === LOOP THROUGH ALL USD FILES ===
for filename in os.listdir(usd_dir):
    if not filename.endswith(".usda"):
        continue
    
    # Prepare paths and names
    usd_path = os.path.join(usd_dir, filename)
    scene_name = os.path.splitext(filename)[0]
    output_dir = os.path.join(output_dir_base, scene_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Processing {scene_name}...")
    
    # Clean up the scene
    clean_scene()
    
    # Import USD
    bpy.ops.wm.usd_import(filepath=usd_path, import_all_materials=True)
    
    # Rotate everything around origin
    for obj in bpy.context.scene.objects:
        obj.rotation_euler[0] += math.radians(90)
        obj.rotation_euler[2] += math.radians(180)
    
    # Set up view layer AOVs
    view_layer = bpy.context.view_layer
    view_layer.use_pass_combined = True
    view_layer.use_pass_z = True
    view_layer.use_pass_normal = True
    view_layer.use_pass_diffuse_direct = True
    view_layer.use_pass_cryptomatte_object = True
    view_layer.cycles.use_denoising = False
        
    # Activate USD camera
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            break

    # Set up compositor
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    tree.nodes.clear()
    rl = tree.nodes.new("CompositorNodeRLayers")
    normalize = tree.nodes.new("CompositorNodeNormalize")
    tree.links.new(rl.outputs["Depth"], normalize.inputs[0])
    file_output = tree.nodes.new("CompositorNodeOutputFile")
    file_output.base_path = output_dir
    file_output.format.file_format = 'PNG'
#    file_output.format.color_depth = '32'
#    file_output.format.exr_codec = 'ZIP'

    # Find target object
    target_obj = bpy.data.objects.get(target_object_name)
    if not target_obj:
        print(f"Target object '{target_object_name}' not found in {scene_name}, skipping.")
        continue
    
    # Get all materials used
    material_list = [mat for mat in bpy.data.materials if mat.users > 0 and mat.node_tree]
    
    for mat in material_list:
        mat_name = mat.name
        print(f"Rendering with material: {mat_name}")

        # Assign to target object
        if len(target_obj.data.materials) == 0:
            target_obj.data.materials.append(mat)
        else:
            target_obj.data.materials[0] = mat

        # Rebuild file output slots and relink every time
        file_output.file_slots.clear()
        file_output.file_slots.new("Combined")
        file_output.file_slots.new("Depth")
        file_output.file_slots.new("Normal")
        file_output.file_slots.new("Diffuse_Direct")
        file_output.file_slots.new("Cryptomatte")

        file_output.file_slots["Combined"].path = f"{mat_name}_combined_"
        file_output.file_slots["Depth"].path = f"{mat_name}_depth_"
        file_output.file_slots["Normal"].path = f"{mat_name}_normal_"
        file_output.file_slots["Diffuse_Direct"].path = f"{mat_name}_diffuse_"
        file_output.file_slots["Cryptomatte"].path = f"{mat_name}_crypto_"

        tree.links.new(rl.outputs["Image"], file_output.inputs["Combined"])
        tree.links.new(normalize.outputs[0], file_output.inputs["Depth"])
        tree.links.new(rl.outputs["Normal"], file_output.inputs["Normal"])
        tree.links.new(rl.outputs["DiffDir"], file_output.inputs["Diffuse_Direct"])
        tree.links.new(rl.outputs["CryptoObject00"], file_output.inputs["Cryptomatte"])

        bpy.context.scene.frame_set(1)
        bpy.ops.render.render(write_still=True)

    print(f"Finished rendering {scene_name}")
