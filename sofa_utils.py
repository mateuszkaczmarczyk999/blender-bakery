import math
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

    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, -0.01))
    ground = bpy.context.object
    ground.name = "ground"
    studio_collection.objects.link(ground)
    bpy.context.scene.collection.objects.unlink(ground)

    bpy.ops.object.light_add(type="AREA", location=(0, 0, 2.5), rotation=(0, 0, 0))
    area_light = bpy.context.object
    area_light.name = "secondary_light"
    area_light.data.energy = 150
    area_light.data.shape = "SQUARE"
    area_light.data.size = 1
    studio_collection.objects.link(area_light)
    bpy.context.scene.collection.objects.unlink(area_light)

    bpy.ops.object.light_add(type="SUN", location=(0, 0, 3), rotation=(0, 0, 0))
    sun_light = bpy.context.object
    sun_light.name = "primary_light"
    sun_light.data.energy = 1
    sun_light.data.angle = math.radians(180)
    studio_collection.objects.link(sun_light)
    bpy.context.scene.collection.objects.unlink(sun_light)

    return studio_collection

def setup_bake(bake_cfg, all=False):
    bpy.context.scene.render.bake.use_clear = False
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.use_pass_direct = all
    bpy.context.scene.render.bake.use_pass_indirect = all
    bpy.context.scene.render.bake.use_pass_color = True
    bpy.context.scene.render.bake.cage_extrusion = bake_cfg["cage_extrusion"]
    bpy.context.scene.render.bake.max_ray_distance = bake_cfg["max_ray_distance"]
    bpy.context.scene.render.bake.margin_type = "ADJACENT_FACES"
    bpy.context.scene.render.bake.margin = bake_cfg["margin"]

def bake(image, bake_cfg, bake_type, output_path="None"):
    print("🔥 Baking... This may take some time.")
    bpy.ops.object.bake(type=bake_type)
    print("✅ Baking Completed!")

    if output_path != "None":
        image.scale(bake_cfg["resolution"], bake_cfg["resolution"])
        image.filepath_raw = output_path
        image.file_format = "HDR"
        image.save()
        print(f"💾 Baked texture resized and saved as HDR: {output_path}")

def save_hdr_image(image, resolution, output_path):
    image.scale(resolution, resolution)
    image.filepath_raw = output_path
    image.file_format = "HDR"
    image.save()
    print(f"💾 Baked texture resized and saved as HDR: {output_path}")

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


def convert_image_to_grayscale(image):
    print(f"🎨 Converting image '{image.name}' to grayscale...")

    pixels = list(image.pixels)  # Flat list: [R, G, B, A, R, G, B, A, ...]
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]
        gray = 0.2126 * r + 0.7152 * g + 0.0722 * b
        pixels[i] = gray       # R
        pixels[i + 1] = gray   # G
        pixels[i + 2] = gray   # B

    image.pixels[:] = pixels
    image.update()
    print("✅ Grayscale conversion done.")


def write_grayscale_to_channel(image, target_channel="R"):
    print(f"🎯 Writing grayscale to {target_channel} channel of '{image.name}'...")
    channel_indices = {"R": 0, "G": 1, "B": 2}
    target_index = channel_indices[target_channel]

    pixels = list(image.pixels)
    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]
        gray = 0.2126 * r + 0.7152 * g + 0.0722 * b

        for j in range(3):  # R, G, B
            pixels[i + j] = gray if j == target_index else 0.0

    image.pixels[:] = pixels
    image.update()
    print(f"✅ Grayscale written to {target_channel} channel.")


def combine_images_to_rgb(r_image, g_image, b_image=None):
    width, height = r_image.size
    result_image = bpy.data.images.new("CombinedRGB", width=width, height=height, alpha=True, float_buffer=True)

    r_pixels = list(r_image.pixels)
    g_pixels = list(g_image.pixels)
    b_pixels = list(b_image.pixels) if b_image else [0.0] * (width * height * 4)

    combined_pixels = [0.0] * (width * height * 4)

    for i in range(0, len(combined_pixels), 4):
        # Compute grayscale from each image
        r_gray = 0.2126 * r_pixels[i] + 0.7152 * r_pixels[i + 1] + 0.0722 * r_pixels[i + 2]
        g_gray = 0.2126 * g_pixels[i] + 0.7152 * g_pixels[i + 1] + 0.0722 * g_pixels[i + 2]
        b_gray = 0.2126 * b_pixels[i] + 0.7152 * b_pixels[i + 1] + 0.0722 * b_pixels[i + 2] if b_image else 0.0

        combined_pixels[i] = r_gray     # R
        combined_pixels[i + 1] = g_gray # G
        combined_pixels[i + 2] = b_gray # B
        combined_pixels[i + 3] = 1.0    # Alpha

    result_image.pixels[:] = combined_pixels
    result_image.update()
    return result_image
