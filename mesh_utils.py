import bpy  # type: ignore
from mathutils import Vector  # type: ignore

def find_mesh_center(mesh):
    vertices = mesh.data.vertices
    total_position = Vector((0.0, 0.0, 0.0))
    vertex_count = len(vertices)
    
    for v in vertices:
        vertex_pos = mesh.matrix_world @ v.co
        total_position += vertex_pos

    center = total_position / vertex_count
    return center

def select_none():
    bpy.ops.object.select_all(action='DESELECT')

def select_mesh(mesh):
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh

def rename_mesh(mesh, name):
    mesh.name = name
    mesh.data.name = name + "_data"

def deselect_mesh(mesh):
    mesh.select_set(False)

def split_selected_mesh():
    if not bpy.context.selected_objects:
        print("⚠ No mesh selected for splitting.")
        return
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    print("✅ Mesh splitted into separate objects.")

def set_object_mode():
    bpy.ops.object.mode_set(mode="OBJECT")

def decimate_mesh(mesh, decimate):
    select_mesh(mesh)

    decimate_unsub = mesh.modifiers.new(name="Decimate_Unsubdiv", type="DECIMATE")
    decimate_unsub.decimate_type = "UNSUBDIV"
    decimate_unsub.iterations = decimate["unsubdiv"]
    bpy.ops.object.modifier_apply(modifier=decimate_unsub.name)

    decimate_planar = mesh.modifiers.new(name="Decimate_Planar", type="DECIMATE")
    decimate_planar.decimate_type = "DISSOLVE"
    decimate_planar.angle_limit = decimate["dissolve"]
    decimate_planar.delimit = {"NORMAL", "MATERIAL", "SEAM", "SHARP", "UV"}
    bpy.ops.object.modifier_apply(modifier=decimate_planar.name)

    deselect_mesh(mesh)

def transform_mesh(mesh, transform):
    mesh.scale.x += transform["scale"]["x"]
    mesh.scale.y += transform["scale"]["y"]
    mesh.scale.z += transform["scale"]["z"]
    mesh.rotation_euler.x += transform["rotation"]["x"]
    mesh.rotation_euler.y += transform["rotation"]["y"]
    mesh.rotation_euler.z += transform["rotation"]["z"]
    mesh.location.x += transform["position"]["x"]
    mesh.location.y += transform["position"]["y"]
    mesh.location.z += transform["position"]["z"]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def collection_flush(collection):
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)