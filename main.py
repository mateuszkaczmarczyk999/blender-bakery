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
from mesh_utils import assign_material, create_plane
from mesh_utils import select_mesh
from mesh_utils import select_none
from mesh_utils import split_selected_mesh
from mesh_utils import set_object_mode
from mesh_utils import set_edit_mode
from mesh_utils import decimate_mesh
from mesh_utils import transform_mesh
from mesh_utils import flush_collection
from mesh_utils import create_collection
from mesh_utils import pack_uv_into_tile
from mesh_utils import merge_collection
from mesh_utils import create_image_for_baking
from mesh_utils import add_ligthmap_channel
from mesh_utils import unwrap_uv
from mesh_utils import pack_uv
from mesh_utils import set_bake_result_material
from sofa_utils import categorize_meshes_in_collection, combine_images_to_rgb
from sofa_utils import export_meshes_from_collection
from sofa_utils import setup_scene
from sofa_utils import setup_studio
from sofa_utils import setup_bake
from sofa_utils import bake
from sofa_utils import save_hdr_image

directory = os.path.dirname(os.path.abspath(__file__))

json_output_path = os.path.join(directory, "sofa_parts.json")
sofa_parts = {}

setup_scene()
setup_studio()

image_size=4096
tile_size=896
uv_tile_scale = tile_size / image_size

# ✅ Create 4K AO Image for Baking
ao_image = create_image_for_baking("Baked_AO_4K", image_size)

# ✅ Create 4K Combined Image for Baking
combined_image = create_image_for_baking("Baked_Combined_4K", image_size)


for module, cfg in config.items():
    walls_collection = create_collection("WALLS")

    bpy.ops.mesh.primitive_cube_add(size=2, location=((cfg["envelope"]["width"]/2 + 1.2), 0, 0))
    box_left = bpy.context.object
    box_left.name = "box-left"
    assign_material(box_left, "box-left")
    walls_collection.objects.link(box_left)
    bpy.context.scene.collection.objects.unlink(box_left)

    if module.startswith("S01_CN"):
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -(cfg["envelope"]["width"]/2 + 1.2), 0))
    else:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(-(cfg["envelope"]["width"]/2 + 1.2), 0 , 0))
    box_right = bpy.context.object
    box_right.name = "box-right"
    assign_material(box_right, "box_right")
    walls_collection.objects.link(box_right)
    bpy.context.scene.collection.objects.unlink(box_right)


    # ✅ Import Input Models
    input_collection = create_collection("INPUT")
    fbx_file_path = os.path.join(directory, cfg["highpoly_filepath"])
    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        transform_mesh(obj, cfg["transform"])
        input_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    output_collection = create_collection("OUTPUT")
    fbx_file_path = os.path.join(directory, cfg["lowpoly_filepath"])
    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        transform_mesh(obj, cfg["transform"])
        output_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    print("✅ Models imported!")


    # ✅ Apply Decimate Modifiers
    # if (cfg["decimate"]["apply"]):
    #     for obj in output_collection.objects:
    #         decimate_mesh(obj, cfg["decimate"])
    # print("✅ Decimate applied!")


    # ✅ Add Lightmap UV Channel
    for obj in output_collection.objects:
        add_ligthmap_channel(obj)
    print("✅ UV Lightmap added!")



    # ✅ Merge Models
    merge_collection(input_collection)
    merge_collection(output_collection)
    print("✅ Collection merged!")

    for obj in input_collection.objects:
        assign_material(obj, "input")

    # # ✅ Create 4K AO Image for Baking
    # ao_image = create_image_for_baking("Baked_AO_4K", 4096)
    # ao_output_path = os.path.join(directory, "sofa_ao/" + module + "_AO.hdr")
    # # ✅ Create 4K Combined Image for Baking
    # combined_image = create_image_for_baking("Baked_Combined_4K", 4096)
    # combined_output_path = os.path.join(directory, "sofa_combined/" + module + "_Combined.hdr")


    # ✅ Prepare UVs
    set_edit_mode()
    # ✅ Unwrapping UV
    # unwrap_uv()
    # ✅ Packing UV
    # pack_uv()

    for obj in output_collection.objects:
        pack_uv_into_tile(obj, cfg["index"], image_size, tile_size)

    # ✅ Prepare Material for AO Baking
    for obj in output_collection.objects:
        set_bake_result_material(obj, ao_image)
    print("✅ Materials ready for AO baking!")

    # ✅ AO Baking
    set_object_mode()
    select_none()
    for obj in input_collection.objects:
        obj.select_set(True)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    setup_bake(cfg["bake"])
    if (cfg["bake"]["apply"]):
        bake(ao_image, cfg["bake"], "AO")

    # ✅ Prepare Material for Combined Baking
    for obj in output_collection.objects:
        set_bake_result_material(obj, combined_image)
    print("✅ Materials ready for Combined baking!")

    # ✅ Combined Baking
    set_object_mode()
    select_none()
    for obj in input_collection.objects:
        obj.select_set(True)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    setup_bake(cfg["bake"], True)
    if (cfg["bake"]["apply"]):
        bake(combined_image, cfg["bake"], "COMBINED")


    # fin_output_path = os.path.join(directory, "sofa_final/" + module + "_FIN.hdr")
    # fin_image = combine_images_to_rgb(ao_image, combined_image)
    # fin_image.filepath_raw = fin_output_path
    # fin_image.file_format = "HDR"
    # fin_image.save()
    # print(f"💾 Baked texture resized and saved as HDR: {fin_image}")



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
    blend_file_path = os.path.join(directory, "sofa_blend/" + module + ".blend")
    save_scene(blend_file_path)



    # ✅ Clean the scene
    flush_collection(input_collection)
    flush_collection(output_collection)
    flush_collection(walls_collection)
    print("✅ Scene is clean!")


# # ✅ Create 4K AO Image for Baking
ao_output_path = os.path.join(directory, "sofa_ao/" + "FOOT" + "_AO.hdr")
# # ✅ Create 4K Combined Image for Baking
combined_output_path = os.path.join(directory, "sofa_combined/" + "FOOT" + "_GI.hdr")

fin_output_path = os.path.join(directory, "sofa_final/" + "FOOT" + "_AO_GI.hdr")
fin_image = combine_images_to_rgb(ao_image, combined_image)
save_hdr_image(fin_image, image_size, fin_output_path)
save_hdr_image(ao_image, image_size, ao_output_path)
save_hdr_image(combined_image, image_size, combined_output_path)

# ✅ Save JSON with origins
save_in_json(sofa_parts, json_output_path)
