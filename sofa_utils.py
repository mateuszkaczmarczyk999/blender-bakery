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
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 128

    return scene


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


def categorize_meshes_in_collection(collection, module, module_parts = None):
    for mesh in collection.objects:
        center = find_mesh_center(mesh)
        select_none()
        select_mesh(mesh)

        if (center.z < 0.2):
            rename_mesh(mesh, module + "_LEG")
            if (module_parts != None): module_parts["legs"].append({ mesh.name: [center.x, center.y, center.z] })
        elif (center.z > 0.3 and center.z < 0.8):
            rename_mesh(mesh, module + "_SEAT")
            if (module_parts != None): module_parts["seat"].append({ mesh.name: [center.x, center.y, center.z] })
        elif (center.z > 0.8 and center.z < 1.0):
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
