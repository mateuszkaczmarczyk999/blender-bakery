#!/usr/bin/env bash
set -euo pipefail

IN="${1:-./}"
OUT="${2:-./images_ktx2}"

# Tunables (override via env)
UASTC_QUALITY="${UASTC_QUALITY:-2}"   # 0..4 (higher = better/slower)
UASTC_RDO="${UASTC_RDO:-1.0}"         # ~0.25..10 (higher = smaller)
ETC1S_QLEVEL="${ETC1S_QLEVEL:-255}"   # 1..255 (higher = better/slower)
GENMIPS="${GENMIPS:-1}"               # 1 to generate mipmaps
AO_ETC1S="${AO_ETC1S:-0}"             # 1 = compress AO with ETC1S (smaller)

MIPFLAG=(); [[ "$GENMIPS" == "1" ]] && MIPFLAG+=(--genmipmap)

mkdir -p "$OUT"

# png + jpg
find "$IN" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) -print0 |
while IFS= read -r -d '' SRC; do
  REL="${SRC#"$IN"/}"
  DST_DIR="$OUT/$(dirname "$REL")"
  BASENAME="$(basename "${REL%.*}")"
  DST="$DST_DIR/$BASENAME.ktx2"
  mkdir -p "$DST_DIR"

  name_lc="$(echo "$BASENAME" | tr '[:upper:]' '[:lower:]')"

  if [[ "$name_lc" =~ (normal|_n|_nm|_nor|_nrm) ]]; then
    echo "→ NORMAL (uastc, linear): $SRC"
    toktx --t2 "${MIPFLAG[@]}" --encode uastc \
      --uastc_quality "$UASTC_QUALITY" --uastc_rdo_l "$UASTC_RDO" \
      --normal_mode --assign_oetf linear "$DST" "$SRC"

  elif [[ "$name_lc" =~ (rough|roughness) ]]; then
    echo "→ ROUGHNESS (uastc, linear): $SRC"
    toktx --t2 "${MIPFLAG[@]}" --encode uastc \
      --uastc_quality "$UASTC_QUALITY" --uastc_rdo_l "$UASTC_RDO" \
      --assign_oetf linear "$DST" "$SRC"

  elif [[ "$name_lc" =~ (bump|height|disp|displace) ]]; then
    echo "→ BUMP/HEIGHT (uastc, linear): $SRC"
    toktx --t2 "${MIPFLAG[@]}" --encode uastc \
      --uastc_quality "$UASTC_QUALITY" --uastc_rdo_l "$UASTC_RDO" \
      --assign_oetf linear "$DST" "$SRC"

  elif [[ "$name_lc" =~ (^|[^a-z])ao([^a-z]|$) ]]; then
    if [[ "$AO_ETC1S" == "1" ]]; then
      echo "→ AO (etc1s, linear): $SRC"
      toktx --t2 "${MIPFLAG[@]}" --encode etc1s --qlevel "$ETC1S_QLEVEL" \
        --assign_oetf linear "$DST" "$SRC"
    else
      echo "→ AO (uastc, linear): $SRC"
      toktx --t2 "${MIPFLAG[@]}" --encode uastc \
        --uastc_quality "$UASTC_QUALITY" --uastc_rdo_l "$UASTC_RDO" \
        --assign_oetf linear "$DST" "$SRC"
    fi

  elif [[ "$name_lc" =~ (albedo|basecolor|base_color|diffuse|emissive|alpha|bg_) ]]; then
    echo "→ COLOR (etc1s, srgb): $SRC"
    toktx --t2 "${MIPFLAG[@]}" --encode etc1s --qlevel "$ETC1S_QLEVEL" \
      --assign_oetf srgb "$DST" "$SRC"

  else
    echo "→ COLOR/FALLBACK (etc1s, srgb): $SRC"
    toktx --t2 "${MIPFLAG[@]}" --encode etc1s --qlevel "$ETC1S_QLEVEL" \
      --assign_oetf srgb "$DST" "$SRC"
  fi
done

echo "✔ Done → $OUT"
