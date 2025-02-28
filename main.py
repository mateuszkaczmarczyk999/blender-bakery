import bpy
import os

directory = os.path.dirname(os.path.abspath(__file__))
fbx_file_path = os.path.join(directory, "sofa_highpoly/Tylko Modul 100x100.fbx")
bake_output_path = os.path.join(directory, "baked_ao_4k.hdr")
export_glb_path = os.path.join(directory, "exported_output.glb")
blend_file_path = os.path.join(directory, "cube.blend")

# Init blend file
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
scene.cycles.samples = 128

if not os.path.exists(fbx_file_path):
    print(f"Error: FBX file not found at {fbx_file_path}")
else:
    # Setup studio
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

    # Input models
    input_collection = bpy.data.collections.new(name="INPUT")
    bpy.context.scene.collection.children.link(input_collection)

    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    for obj in bpy.context.selected_objects:
        input_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    # Output models prep
    output_collection = bpy.data.collections.new(name="OUTPUT")
    bpy.context.scene.collection.children.link(output_collection)
    for obj in input_collection.objects:
        if obj.type == "MESH":
            duplicate = obj.copy()
            duplicate.data = obj.data.copy()
            output_collection.objects.link(duplicate)

    # Apply decimate
    for obj in output_collection.objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        decimate_unsub = obj.modifiers.new(name="Decimate_Unsubdiv", type="DECIMATE")
        decimate_unsub.decimate_type = "UNSUBDIV"
        decimate_unsub.iterations = 2
        bpy.ops.object.modifier_apply(modifier=decimate_unsub.name)

        decimate_planar = obj.modifiers.new(name="Decimate_Planar", type="DECIMATE")
        decimate_planar.decimate_type = "DISSOLVE"
        decimate_planar.angle_limit = 2 * (3.14159265 / 180)
        decimate_planar.delimit = { "NORMAL", "MATERIAL", "SEAM", "SHARP", "UV" }
        bpy.ops.object.modifier_apply(modifier=decimate_planar.name)

        obj.select_set(False)

    # Add lightmap UV channel
    for obj in output_collection.objects:
        mesh = obj.data
        uv_layer = mesh.uv_layers.new(name="lightmap")
        mesh.uv_layers.active = mesh.uv_layers["lightmap"]
        for uv in mesh.uv_layers:
            uv.active_render = (uv.name == "lightmap")

    # Create image buffer for baked AO
    ao_image = bpy.data.images.new(name="Baked_AO_4K", width=4096, height=4096, alpha=False, float_buffer=True)
    ao_image.generated_color = (1, 1, 1, 1)

    # Merge input models
    bpy.ops.object.select_all(action="DESELECT")
    for obj in input_collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

    # Merge output models
    bpy.ops.object.select_all(action="DESELECT")
    for obj in output_collection.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()

    # Prepare meshes for uv unwrapping
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="SELECT")

    # Unwrapping UV
    bpy.ops.uv.smart_project(angle_limit=60, island_margin=0.001, correct_aspect=True)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin=0.001)

    # Prepra material for baking output
    for obj in output_collection.objects:
        ## Setup material
        obj.data.materials.clear()
        material = bpy.data.materials.new(name=f"{obj.name}_material")
        obj.data.materials.append(material)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        ## Create texture
        img_tex_node = nodes.new(type="ShaderNodeTexImage")
        img_tex_node.image = ao_image
        img_tex_node.label = "AO_baked_textture"
        img_tex_node.select = True
        material.node_tree.nodes.active = img_tex_node

    bpy.ops.object.mode_set(mode="OBJECT")
    # ✅ Select all INPUT objects as the source
    bpy.ops.object.select_all(action="DESELECT")
    for obj in input_collection.objects:
        obj.select_set(True)

    # ✅ Select all OUTPUT objects as the bake target (keeping INPUT selected)
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj  # Make active for baking

    # ✅ Set Bake Type to Ambient Occlusion
    scene.render.bake.use_selected_to_active = True  # Selected to Active Baking
    scene.render.bake.use_pass_direct = False  # Ignore direct lighting
    scene.render.bake.use_pass_indirect = False  # Ignore indirect lighting
    scene.render.bake.use_pass_color = True  # Bake AO onto texture

    # ✅ Set Bake Parameters from Screenshot
    scene.render.bake.cage_extrusion = 0.02  # 2 cm Extrusion (converted to meters)
    scene.render.bake.max_ray_distance = 0.0  # Max Ray Distance: 0 cm

    # ✅ Set Margin Type & Size
    scene.render.bake.margin_type = 'ADJACENT_FACES'
    scene.render.bake.margin = 16  # Margin Size: 16 px

    print("🔥 Baking AO... This may take some time.")
    bpy.ops.object.bake(type='AO')
    print("✅ AO Baking Completed!")

    # ✅ Save Baked AO Texture to Disk
    ao_image.scale(1024, 1024)
    ao_image.filepath_raw = bake_output_path
    ao_image.file_format = 'HDR'
    ao_image.save()

    # ✅ Ensure we're in Object Mode before separating meshes
    bpy.ops.object.mode_set(mode="OBJECT")
    # ✅ Select the merged OUTPUT object
    bpy.ops.object.select_all(action="DESELECT")
    for obj in output_collection.objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    # ✅ Separate all objects by Loose Parts (Splits into individual meshes)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode="OBJECT")


    # ✅ Export as GLB (Without Materials, with Y-Up)
    bpy.ops.export_scene.gltf(
        filepath=export_glb_path,
        export_format='GLB',  # Export as .glb
        use_selection=True,  # Only export selected objects
        export_apply=True,  # Apply all transforms
        export_yup=True,  # Set Y as Up
        export_materials='NONE'  # Do not export materials
    )

    print(f"✅ Exported GLB file: {export_glb_path}")

    # Save file
    bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
    print(f"File saved at:  {blend_file_path}")
