#!/bin/bash

version="v2"
source_dir="./sofa_glb"
target_dir="./versioned/glb"

mkdir -p "$target_dir"

for file in "$source_dir"/*.glb; do
  base=$(basename "$file" .glb)
  cp "$file" "$target_dir/${base}_${version}.glb"
  echo "Copied: $file → $target_dir/${base}_${version}.glb"
done