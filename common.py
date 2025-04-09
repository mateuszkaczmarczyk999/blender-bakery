import bpy  # type: ignore
import json


"""
Exports the currently selected object as an GLB file.
:param filepath: The output file path for the GLB export.
"""
def export_selected_glb(filepath):
    if not bpy.context.selected_objects:
        print("⚠ No object selected for export.")
        return

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )
    print(f"💾 Exported and compressed selected object as GLB: {filepath}")


"""
Exports the currently selected object as an FBX file.
:param filepath: The output file path for the FBX export.
"""
def export_selected_fbx(filepath):
    if not bpy.context.selected_objects:
        print("⚠ No object selected for export.")
        return

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        apply_unit_scale=True,
        bake_space_transform=True,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode="AUTO"
    )
    print(f"💾 Exported selected object as FBX: {filepath}")


"""
Saves the current Blender scene as a .blend file.
:param filepath: The full file path where the Blender file will be saved.
"""
def save_scene(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"💾 File saved at: {filepath}")


"""
Saves a dictionary object as a JSON file.
:param object: The dictionary object to be saved.
:param filepath: The full file path where the JSON file will be saved.
:param indent: (Optional) The number of spaces for indentation in the JSON file (default: 4).
"""
def save_in_json(object, filepath, indent=4):
    with open(filepath, "w") as json_file:
        json.dump(object, json_file, indent=indent)
