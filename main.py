import bpy
import os

sofa_modules = {
    "S01_AR_D07_W02": "sofa_highpoly/Armrest.fbx",
    
    "S01_CN_D08_W08": "sofa_highpoly/Tylko Corner 100x100.fbx",
    "S01_CN_D09_W09": "sofa_highpoly/Tylko Corner 112,5x112,5.fbx",

    "S01_ST_D08_W06": "sofa_highpoly/Tylko Modul 75x100.fbx",
    "S01_ST_D08_W07": "sofa_highpoly/Tylko Modul 87,5x100.fbx",
    "S01_ST_D08_W08": "sofa_highpoly/Tylko Modul 100x100.fbx",
    "S01_ST_D08_W09": "sofa_highpoly/Tylko Modul 112,5x100.fbx",
    
    "S01_ST_D09_W06": "sofa_highpoly/Tylko Modul 75x112,5.fbx",
    "S01_ST_D09_W07": "sofa_highpoly/Tylko Modul 87,5x112,5.fbx",
    "S01_ST_D09_W08": "sofa_highpoly/Tylko Modul 100x112,5.fbx",
    "S01_ST_D09_W09": "sofa_highpoly/Tylko Modul 112,5x112,5.fbx",
    
    "S01_CL_D13_W07": "sofa_highpoly/Tylko Modul 87,5x162,5.fbx",
    "S01_CL_D13_W08": "sofa_highpoly/Tylko Modul 100x162,5.fbx",
    "S01_CL_D13_W09": "sofa_highpoly/Tylko Modul 112,5x162,5.fbx",

    "S01_FR_D05_W06": "sofa_highpoly/Tylko Ottoman 75x62,5.fbx",
    "S01_FR_D05_W07": "sofa_highpoly/Tylko Ottoman 87,5x62,5.fbx",
    "S01_FR_D05_W08": "sofa_highpoly/Tylko Ottoman 100x62,5.fbx",
    "S01_FR_D05_W09": "sofa_highpoly/Tylko Ottoman 112,5x62,5.fbx",

    "S01_FR_D06_W06": "sofa_highpoly/Tylko Ottoman 75x75.fbx",
    "S01_FR_D06_W07": "sofa_highpoly/Tylko Ottoman 87,5x75.fbx",
    "S01_FR_D06_W08": "sofa_highpoly/Tylko Ottoman 100x75.fbx",
    "S01_FR_D06_W09": "sofa_highpoly/Tylko Ottoman 112,5x75.fbx",

    "S01_FR_D07_W07": "sofa_highpoly/Tylko Ottoman 87,5x87,5.fbx",
    "S01_FR_D07_W08": "sofa_highpoly/Tylko Ottoman 100x87,5.fbx",
    "S01_FR_D07_W09": "sofa_highpoly/Tylko Ottoman 112,5x87,5.fbx",
    
    "S01_FR_D08_W08": "sofa_highpoly/Tylko Ottoman 100x100.fbx",
    "S01_FR_D08_W09": "sofa_highpoly/Tylko Ottoman 112,5x100.fbx",
    "S01_FR_D09_W09": "sofa_highpoly/Tylko Ottoman 112,5x112,5.fbx",
}

directory = os.path.dirname(os.path.abspath(__file__))

# ✅ Initialize Blend File
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
scene.cycles.samples = 128

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


for module, fbx_path in sofa_modules.items():

    fbx_file_path = os.path.join(directory, fbx_path)
    bake_output_path = os.path.join(directory, "sofa_ao/" + module + "AO_1k.hdr")  # HDR AO texture (1K)
    export_glb_path = os.path.join(directory, "sofa_glb/" + module + ".glb")  # GLB file
    # blend_file_path = os.path.join(directory, "cube.blend")  # Blender file

    # ✅ Import Input Models
    input_collection = bpy.data.collections.new(name="INPUT")
    bpy.context.scene.collection.children.link(input_collection)
    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        input_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    # ✅ Duplicate Input for Output
    output_collection = bpy.data.collections.new(name="OUTPUT")
    bpy.context.scene.collection.children.link(output_collection)
    for obj in input_collection.objects:
        if obj.type == "MESH":
            duplicate = obj.copy()
            duplicate.data = obj.data.copy()
            output_collection.objects.link(duplicate)

    # # ✅ Apply Decimate Modifiers
    # for obj in output_collection.objects:
    #     bpy.context.view_layer.objects.active = obj
    #     obj.select_set(True)

    #     decimate_unsub = obj.modifiers.new(name="Decimate_Unsubdiv", type="DECIMATE")
    #     decimate_unsub.decimate_type = "UNSUBDIV"
    #     decimate_unsub.iterations = 2
    #     bpy.ops.object.modifier_apply(modifier=decimate_unsub.name)

    #     decimate_planar = obj.modifiers.new(name="Decimate_Planar", type="DECIMATE")
    #     decimate_planar.decimate_type = "DISSOLVE"
    #     decimate_planar.angle_limit = 2 * (3.14159265 / 180)
    #     decimate_planar.delimit = {"NORMAL", "MATERIAL", "SEAM", "SHARP", "UV"}
    #     bpy.ops.object.modifier_apply(modifier=decimate_planar.name)

    #     obj.select_set(False)

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

    bpy.ops.object.mode_set(mode="OBJECT")

    # ✅ Set Up AO Baking
    bpy.ops.object.select_all(action="DESELECT")
    for obj in input_collection.objects:
        obj.select_set(True)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj  # Make active for baking

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True
    scene.render.bake.cage_extrusion = 0.02
    scene.render.bake.max_ray_distance = 0.0
    scene.render.bake.margin_type = "ADJACENT_FACES"
    scene.render.bake.margin = 16

    print("🔥 Baking AO... This may take some time.")
    bpy.ops.object.bake(type="AO")
    print("✅ AO Baking Completed!")

    # ✅ Resize AO Image to 1K and Save as HDR
    ao_image.scale(1024, 1024)
    ao_image.filepath_raw = bake_output_path
    ao_image.file_format = "HDR"
    ao_image.save()
    print(f"✅ AO texture resized to 1K and saved as HDR: {bake_output_path}")

    # ✅ Separate Output Meshes
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    print("✅ Output mesh split into separate objects.")

    # ✅ Export as GLB (Without Materials, with Y-Up)
    bpy.ops.export_scene.gltf(
        filepath=export_glb_path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials="NONE"
    )

    print(f"✅ Exported GLB file: {export_glb_path}")

    for obj in input_collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(input_collection)

    for obj in output_collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(output_collection)

    # # ✅ Save Blend File
    # bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
    # print(f"✅ File saved at: {blend_file_path}")
