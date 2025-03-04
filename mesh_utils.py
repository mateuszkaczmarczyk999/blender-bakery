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

def set_object_mode():
    bpy.ops.object.mode_set(mode="OBJECT")

def set_edit_mode():
    bpy.ops.object.mode_set(mode="EDIT")

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

def add_ligthmap_channel(mesh):
    mesh_data = mesh.data
    uv_layer = mesh_data.uv_layers.new(name="lightmap")
    mesh_data.uv_layers.active = mesh_data.uv_layers["lightmap"]
    for uv in mesh_data.uv_layers:
        uv.active_render = (uv.name == "lightmap")

def unwrap_uv():
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=60, island_margin=0.001, correct_aspect=True)

def pack_uv():
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin=0.001)

def set_bake_result_material(mesh, img):
    mesh.data.materials.clear()
    material = bpy.data.materials.new(name=f"{mesh.name}_material")
    mesh.data.materials.append(material)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    img_tex_node = nodes.new(type="ShaderNodeTexImage")
    img_tex_node.image = img
    img_tex_node.label = "AO_Baked_Texture"
    img_tex_node.select = True
    material.node_tree.nodes.active = img_tex_node

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

def create_collection(name):
    collection = bpy.data.collections.new(name=name)
    bpy.context.scene.collection.children.link(collection)
    return collection

def flush_collection(collection):
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)

def duplicate_collection(source, name):
    output_collection = create_collection(name)
    for obj in source.objects:
        duplicate = obj.copy()
        duplicate.data = obj.data.copy()
        output_collection.objects.link(duplicate)
    return output_collection

def merge_collection(collection):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

def create_image_for_baking():
    ao_image = bpy.data.images.new(name="Baked_AO_4K", width=4096, height=4096, alpha=False, float_buffer=True)
    ao_image.generated_color = (1, 1, 1, 1)
    return ao_image
