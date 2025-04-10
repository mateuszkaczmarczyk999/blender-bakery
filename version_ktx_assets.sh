#!/bin/bash

version="v2"
source_dir="./sofa_ktx"
target_dir="./versioned/ktx"

mkdir -p "$target_dir"

for file in "$source_dir"/*.ktx2; do
  base=$(basename "$file" .ktx2)
  cp "$file" "$target_dir/${base}_${version}.ktx2"
  echo "Copied: $file → $target_dir/${base}_${version}.ktx2"
done