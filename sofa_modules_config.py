import math

default_transform = {
    "position": { "x": 0, "y": 0, "z": 0 },
    "rotation": { "x": 0, "y": 0, "z": 0 },
    "scale": { "x": 0.03, "y": 0.03, "z": 0.0 },
}

rotate_transform = {
    "position": { "x": 0, "y": 0, "z": 0 },
    "rotation": { "x": 0, "y": 0, "z": math.radians(90) },
    "scale": { "x": 0.03, "y": 0.03, "z": 0.0 },
}

move_transform = {
    "position": { "x": 0, "y": 0.3, "z": 0 },
    "rotation": { "x": 0, "y": 0, "z": 0 },
    "scale": { "x": 0.03, "y": 0.03, "z": 0.0 },
}

default_decimate = {
    "apply": True,
    "unsubdiv": 2,
    "dissolve": math.radians(2),
}

small_decimate = {
    "apply": True,
    "unsubdiv": 0,
    "dissolve": math.radians(0.8),
}

no_decimate = {
    "apply": False,
    "unsubdiv": 0,
    "dissolve": math.radians(0),
}

default_bake = {
    "apply": True,
    "resolution": 1024,
    "cage_extrusion": 0.02,
    "max_ray_distance": 0.0,
    "margin": 16,
}

no_bake = {
    "apply": False,
    "resolution": 1024,
    "cage_extrusion": 0.02,
    "max_ray_distance": 0.0,
    "margin": 16,
}


config = {
    "S01_AR_D07_W02": {
        "filepath": "sofa_highpoly/Armrest.fbx",
        "transform": default_transform,
        "decimate": no_decimate,
        "bake": default_bake,
    },
    "S01_CN_D08_W08": {
        "filepath": "sofa_highpoly/Tylko Corner 100x100.fbx",
        "transform": rotate_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_CN_D09_W09": {
        "filepath": "sofa_highpoly/Tylko Corner 112,5x112,5.fbx",
        "transform": rotate_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D08_W06": {
        "filepath": "sofa_highpoly/Tylko Modul 75x100.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D08_W07": {
        "filepath": "sofa_highpoly/Tylko Modul 87,5x100.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D08_W08": {
        "filepath": "sofa_highpoly/Tylko Modul 100x100.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D08_W09": {
        "filepath": "sofa_highpoly/Tylko Modul 112,5x100.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D09_W06": {
        "filepath": "sofa_highpoly/Tylko Modul 75x112,5.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D09_W07": {
        "filepath": "sofa_highpoly/Tylko Modul 87,5x112,5.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D09_W08": {
        "filepath": "sofa_highpoly/Tylko Modul 100x112,5.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_ST_D09_W09": {
        "filepath": "sofa_highpoly/Tylko Modul 112,5x112,5.fbx",
        "transform": default_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_CL_D13_W07": {
        "filepath": "sofa_highpoly/Tylko Modul 87,5x162,5.fbx",
        "transform": move_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_CL_D13_W08": {
        "filepath": "sofa_highpoly/Tylko Modul 100x162,5.fbx",
        "transform": move_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_CL_D13_W09": {
        "filepath": "sofa_highpoly/Tylko Modul 112,5x162,5.fbx",
        "transform": move_transform,
        "decimate": default_decimate,
        "bake": default_bake,
    },
    "S01_FR_D05_W06": {
        "filepath": "sofa_highpoly/Tylko Ottoman 75x62,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D05_W07": {
        "filepath": "sofa_highpoly/Tylko Ottoman 87,5x62,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D05_W08": {
        "filepath": "sofa_highpoly/Tylko Ottoman 100x62,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D05_W09": {
        "filepath": "sofa_highpoly/Tylko Ottoman 112,5x62,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D06_W06": {
        "filepath": "sofa_highpoly/Tylko Ottoman 75x75.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D06_W07": {
        "filepath": "sofa_highpoly/Tylko Ottoman 87,5x75.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D06_W08": {
        "filepath": "sofa_highpoly/Tylko Ottoman 100x75.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D06_W09": {
        "filepath": "sofa_highpoly/Tylko Ottoman 112,5x75.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D07_W07": {
        "filepath": "sofa_highpoly/Tylko Ottoman 87,5x87,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D07_W08": {
        "filepath": "sofa_highpoly/Tylko Ottoman 100x87,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D07_W09": {
        "filepath": "sofa_highpoly/Tylko Ottoman 112,5x87,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D08_W08": {
        "filepath": "sofa_highpoly/Tylko Ottoman 100x100.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D08_W09": {
        "filepath": "sofa_highpoly/Tylko Ottoman 112,5x100.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
    "S01_FR_D09_W09": {
        "filepath": "sofa_highpoly/Tylko Ottoman 112,5x112,5.fbx",
        "transform": default_transform,
        "decimate": small_decimate,
        "bake": default_bake,
    },
}