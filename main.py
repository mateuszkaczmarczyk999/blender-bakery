# ✅ Standard Python Modules
import os
import sys

# ✅ Blender Modules
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

# ✅ Ensure Blender Can Find the Config Module
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# ✅ Custom Imports
from sofa_modules_config import config
from common import save_scene
from common import save_in_json
from mesh_utils import select_mesh
from mesh_utils import select_none
from mesh_utils import split_selected_mesh
from mesh_utils import set_object_mode
from mesh_utils import decimate_mesh
from mesh_utils import transform_mesh
from mesh_utils import collection_flush
from sofa_utils import categorize_meshes_in_collection
from sofa_utils import export_meshes_from_collection
from sofa_utils import setup_scene
from sofa_utils import setup_studio

directory = os.path.dirname(os.path.abspath(__file__))
json_output_path = os.path.join(directory, "sofa_parts.json")
sofa_parts = {}

scene = setup_scene()
studio = setup_studio()

for module, cfg in config.items():
    module_parts = {
        "legs": [],
        "seat": [],
        "backrest": [],
        "headrest": [],
    }

    fbx_file_path = os.path.join(directory, cfg["filepath"])
    bake_output_path = os.path.join(directory, "sofa_ao/" + module + "_AO.hdr")  # HDR AO texture (1K)
    blend_file_path = os.path.join(directory, "sofa_blend/" + module + ".blend")  # Blender file

    print(f"✅ MODULE: {module}")
    # ✅ Import Input Models
    input_collection = bpy.data.collections.new(name="INPUT")
    bpy.context.scene.collection.children.link(input_collection)

    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        transform_mesh(obj, cfg["transform"])
        input_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    # ✅ Duplicate Input for Output
    output_collection = bpy.data.collections.new(name="OUTPUT")
    bpy.context.scene.collection.children.link(output_collection)

    for obj in input_collection.objects:
        duplicate = obj.copy()
        duplicate.data = obj.data.copy()
        output_collection.objects.link(duplicate)

    # ✅ Apply Decimate Modifiers
    if (cfg["decimate"]["apply"]):
        for obj in output_collection.objects:
            decimate_mesh(obj, cfg["decimate"])

    # ✅ Add Lightmap UV Channel
    for obj in output_collection.objects:
        mesh = obj.data
        uv_layer = mesh.uv_layers.new(name="lightmap")
        mesh.uv_layers.active = mesh.uv_layers["lightmap"]
        for uv in mesh.uv_layers:
            uv.active_render = (uv.name == "lightmap")

    # ✅ Create 4K AO Image for Baking
    ao_image = bpy.data.images.new(name="Baked_AO_4K", width=4096, height=4096, alpha=False, float_buffer=True)
    ao_image.generated_color = (1, 1, 1, 1)

    # ✅ Merge Input Models
    bpy.ops.object.select_all(action="DESELECT")
    for obj in input_collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

    # ✅ Merge Output Models
    bpy.ops.object.select_all(action="DESELECT")
    for obj in output_collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

    # ✅ Prepare for UV Unwrapping
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="SELECT")

    # ✅ Unwrapping UV
    bpy.ops.uv.smart_project(angle_limit=60, island_margin=0.001, correct_aspect=True)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin=0.001)

    # ✅ Prepare Material for AO Baking
    for obj in output_collection.objects:
        obj.data.materials.clear()
        material = bpy.data.materials.new(name=f"{obj.name}_material")
        obj.data.materials.append(material)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        img_tex_node = nodes.new(type="ShaderNodeTexImage")
        img_tex_node.image = ao_image
        img_tex_node.label = "AO_Baked_Texture"
        img_tex_node.select = True
        material.node_tree.nodes.active = img_tex_node

    set_object_mode()

    # ✅ Set Up AO Baking
    select_none()
    for obj in input_collection.objects:
        obj.select_set(True)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj  # Make active for baking

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True
    scene.render.bake.cage_extrusion = cfg["bake"]["cage_extrusion"]
    scene.render.bake.max_ray_distance = cfg["bake"]["max_ray_distance"]
    scene.render.bake.margin_type = "ADJACENT_FACES"
    scene.render.bake.margin = cfg["bake"]["margin"]

    # if (cfg["bake"]["apply"]):
    #     print("🔥 Baking AO... This may take some time.")
    #     bpy.ops.object.bake(type="AO")
    #     print("✅ AO Baking Completed!")

    #     # ✅ Resize AO Image to 1K and Save as HDR
    #     ao_image.scale(cfg["bake"]["resolution"], cfg["bake"]["resolution"])
    #     ao_image.filepath_raw = bake_output_path
    #     ao_image.file_format = "HDR"
    #     ao_image.save()
    #     print(f"✅ AO texture resized to 1K and saved as HDR: {bake_output_path}")

    # ✅ Separate Output Meshes
    # bpy.ops.object.mode_set(mode="OBJECT")
    select_none()
    for obj in output_collection.objects:
        select_mesh(obj)
    split_selected_mesh()

    # bpy.ops.object.mode_set(mode="OBJECT")
    select_none()
    for obj in input_collection.objects:
        select_mesh(obj)
    split_selected_mesh()

    categorize_meshes_in_collection(output_collection, module)
    categorize_meshes_in_collection(input_collection, module, module_parts)
    export_meshes_from_collection(output_collection, directory, "glb")
    export_meshes_from_collection(input_collection, directory, "fbx")
        
    sofa_parts[module] = module_parts

    # ✅ Save Blend File
    save_scene(blend_file_path)

    # ✅ Clean the scene
    collection_flush(input_collection)
    collection_flush(output_collection)

# ✅ Save JSON with origins
save_in_json(sofa_parts, json_output_path)
