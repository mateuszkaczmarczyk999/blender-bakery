import os
import bpy  # type: ignore
from mesh_utils import find_mesh_center
from mesh_utils import select_mesh
from mesh_utils import select_none
from mesh_utils import rename_mesh
from common import export_selected_fbx
from common import export_selected_glb

def setup_scene():
    # ✅ Initialize Blend File
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.cycles.samples = 128


def setup_studio():
    # ✅ Create Studio Setup
    studio_collection = bpy.data.collections.new(name="STUDIO")
    bpy.context.scene.collection.children.link(studio_collection)

    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "ground"
    studio_collection.objects.link(ground)
    bpy.context.scene.collection.objects.unlink(ground)

    bpy.ops.object.light_add(type="AREA", location=(0, 0, 5))
    area_light = bpy.context.object
    area_light.name = "primary_light"
    area_light.data.energy = 700
    area_light.data.shape = "DISK"
    area_light.data.size = 5
    studio_collection.objects.link(area_light)
    bpy.context.scene.collection.objects.unlink(area_light)

    return studio_collection

def setup_bake(bake_cfg):
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True
    bpy.context.scene.render.bake.cage_extrusion = bake_cfg["cage_extrusion"]
    bpy.context.scene.render.bake.max_ray_distance = bake_cfg["max_ray_distance"]
    bpy.context.scene.render.bake.margin_type = "ADJACENT_FACES"
    bpy.context.scene.render.bake.margin = bake_cfg["margin"]

def bake(image, bake_cfg, output_path):
    print("🔥 Baking AO... This may take some time.")
    bpy.ops.object.bake(type="AO")
    print("✅ AO Baking Completed!")

    image.scale(bake_cfg["resolution"], bake_cfg["resolution"])
    image.filepath_raw = output_path
    image.file_format = "HDR"
    image.save()
    print(f"💾 AO texture resized and saved as HDR: {output_path}")


def categorize_meshes_in_collection(collection, module, module_parts = None):
    for mesh in collection.objects:
        center = find_mesh_center(mesh)
        select_none()
        select_mesh(mesh)
        if (center.z < 0.01):
            rename_mesh(mesh, module + "_LEG")
            if (module_parts != None): module_parts["legs"].append({ mesh.name: [center.x, center.y, center.z] })
        elif (center.z > 0.1 and center.z < 0.4):
            rename_mesh(mesh, module + "_SEAT")
            if (module_parts != None): module_parts["seat"].append({ mesh.name: [center.x, center.y, center.z] })
        elif (center.z > 0.4 and center.z < 0.6):
            rename_mesh(mesh, module + "_BACKREST")
            if (module_parts != None): module_parts["backrest"].append({ mesh.name: [center.x, center.y, center.z] })
        else:
            rename_mesh(mesh, module + "_HEADREST")
            if (module_parts != None): module_parts["headrest"].append({ mesh.name: [center.x, center.y, center.z] })


def export_meshes_from_collection(collection, directory, format):
    for mesh in collection.objects:
        select_none()
        if "." in mesh.name:
            clean_name = mesh.name.rsplit(".", 1)[0]
        else:
            clean_name = mesh.name
        if not clean_name.endswith("_LEG"):
            file_path = os.path.join(directory, "sofa_" + format + "/" + clean_name + "." + format)
            select_mesh(mesh)
            if format == "glb": export_selected_glb(file_path)
            if format == "fbx": export_selected_fbx(file_path)
