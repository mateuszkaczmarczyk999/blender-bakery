/Applications/Blender.app/Contents/MacOS/Blender --background --python main.py

chmod +x version_glb_assets.sh
chmod +x version_ktx_assets.sh

toktx --encode uastc --uastc_quality 2 --2d --generate-mipmap rewool_babyBlue_diffuse_2K.ktx2 rewool_babyBlue_diffuse_2K.png
