#!/bin/bash

set -e  # Exit on first error

mkdir -p ktx2_output

for file in sofa_textures/leather/*.png; do
  if [[ -f "$file" ]]; then
    base=$(basename "$file" .png)
    echo "🔄 Compressing $file → ktx2_output/${base}.ktx2"
    toktx --encode etc1s --clevel 4 --qlevel 128 --genmipmap --2d --assign_oetf srgb \
      "ktx2_output/${base}.ktx2" "$file"
  fi
done

echo "✅ All textures compressed into ktx2_output/"