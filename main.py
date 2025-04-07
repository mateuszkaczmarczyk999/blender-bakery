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
from mesh_utils import set_edit_mode
from mesh_utils import decimate_mesh
from mesh_utils import transform_mesh
from mesh_utils import flush_collection
from mesh_utils import create_collection
from mesh_utils import duplicate_collection
from mesh_utils import merge_collection
from mesh_utils import create_image_for_baking
from mesh_utils import add_ligthmap_channel
from mesh_utils import unwrap_uv
from mesh_utils import pack_uv
from mesh_utils import set_bake_result_material
from sofa_utils import categorize_meshes_in_collection
from sofa_utils import export_meshes_from_collection
from sofa_utils import setup_scene
from sofa_utils import setup_studio
from sofa_utils import setup_bake
from sofa_utils import bake

directory = os.path.dirname(os.path.abspath(__file__))

json_output_path = os.path.join(directory, "sofa_parts.json")
sofa_parts = {}

setup_scene()
setup_studio()

for module, cfg in config.items():
    # ✅ Import Input Models
    input_collection = create_collection("INPUT")
    fbx_file_path = os.path.join(directory, cfg["filepath"])
    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        transform_mesh(obj, cfg["transform"])
        input_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    output_collection = duplicate_collection(input_collection, "OUTPUT")
    print("✅ Models imported!")


    # ✅ Apply Decimate Modifiers
    if (cfg["decimate"]["apply"]):
        for obj in output_collection.objects:
            decimate_mesh(obj, cfg["decimate"])
    print("✅ Decimate applied!")


    # ✅ Add Lightmap UV Channel
    for obj in output_collection.objects:
        add_ligthmap_channel(obj)
    print("✅ UV Lightmap added!")



    # ✅ Merge Models
    merge_collection(input_collection)
    merge_collection(output_collection)
    print("✅ Collection merged!")



    # ✅ Create 4K AO Image for Baking
    ao_image = create_image_for_baking("Baked_AO_4K", 4096)
    bake_output_path = os.path.join(directory, "sofa_ao/" + module + "_AO.hdr")
    # ✅ Prepare UVs
    set_edit_mode()
    # ✅ Unwrapping UV
    unwrap_uv()
    # ✅ Packing UV
    pack_uv()
    # ✅ Prepare Material for AO Baking
    for obj in output_collection.objects:
        set_bake_result_material(obj, ao_image)
    print("✅ Materials ready for baking!")


    # ✅ AO Baking
    set_object_mode()
    select_none()
    for obj in input_collection.objects:
        obj.select_set(True)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj  # Make active for baking
    setup_bake(cfg["bake"])
    if (cfg["bake"]["apply"]):
        bake(ao_image, cfg["bake"], bake_output_path)



    # ✅ Separate Output Meshes
    select_none()
    for obj in output_collection.objects:
        select_mesh(obj)
    split_selected_mesh()
    select_none()
    for obj in input_collection.objects:
        select_mesh(obj)
    split_selected_mesh()
    print("✅ Meshes in collections separated!")


    # ✅ Categorize and Export Meshes in Collections
    module_parts = {
        "legs": [],
        "seat": [],
        "backrest": [],
        "headrest": [],
    }
    categorize_meshes_in_collection(output_collection, module)
    categorize_meshes_in_collection(input_collection, module, module_parts)
    export_meshes_from_collection(output_collection, directory, "glb")
    export_meshes_from_collection(input_collection, directory, "fbx")
    sofa_parts[module] = module_parts
    print("✅ Exports done!")


    # ✅ Save Blend File
    blend_file_path = os.path.join(directory, "sofa_blend/" + module + ".blend")  # Blender file
    save_scene(blend_file_path)



    # ✅ Clean the scene
    flush_collection(input_collection)
    flush_collection(output_collection)
    print("✅ Scene is clean!")

# ✅ Save JSON with origins
save_in_json(sofa_parts, json_output_path)
