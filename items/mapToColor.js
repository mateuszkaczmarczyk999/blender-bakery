#!/usr/bin/env node
"use strict";

/**
 * For every .glb found under the given folder:
 * 1) Read GLB (supports Draco via decoder).
 * 2) For each material, find diffuse/baseColor texture, compute a mean color
 *    while IGNORING (near) transparent pixels, convert to linear, set baseColorFactor.
 * 3) Clear all material texture slots and dispose textures/images/samplers.
 * 4) Strip KHR_draco_mesh_compression so writer does not attempt to re-encode Draco.
 * 5) Write to <srcdir>/mobile/<same-name>.glb
 *
 * Usage:
 *   node mapToColor.js ./path/to/folder
 */

const path = require("node:path");
const fs = require("node:fs/promises");
const fg = require("fast-glob");
const sharp = require("sharp");

// ------------------ color helpers ------------------
function srgbToLinear01(c) {
  const cs = c / 255;
  return cs <= 0.04045 ? cs / 12.92 : Math.pow((cs + 0.055) / 1.055, 2.4);
}
function toLinearFactor(rgb, a = 1) {
  return [srgbToLinear01(rgb.r), srgbToLinear01(rgb.g), srgbToLinear01(rgb.b), a];
}

// ------------------ material helpers ------------------
function getDiffuseTexture(material, KHRMaterialsPBRSpecularGlossiness) {
  const sg = material.getExtension?.(KHRMaterialsPBRSpecularGlossiness.EXTENSION_NAME);
  if (sg?.getDiffuseTexture?.()) return sg.getDiffuseTexture();
  return material.getBaseColorTexture?.() ?? null;
}
function setDiffuseColor(material, factor, KHRMaterialsPBRSpecularGlossiness) {
  material.setBaseColorFactor?.(factor);
  const sg = material.getExtension?.(KHRMaterialsPBRSpecularGlossiness.EXTENSION_NAME);
  sg?.setDiffuseFactor?.(factor.slice(0, 4));
}
function clearAllMaterialTextures(material, KHRMaterialsPBRSpecularGlossiness) {
  material.setBaseColorTexture?.(null);
  material.setNormalTexture?.(null);
  material.setMetallicRoughnessTexture?.(null);
  material.setOcclusionTexture?.(null);
  material.setEmissiveTexture?.(null);
  const sg = material.getExtension?.(KHRMaterialsPBRSpecularGlossiness.EXTENSION_NAME);
  sg?.setDiffuseTexture?.(null);
  sg?.setSpecularGlossinessTexture?.(null);
}

// ------------------ dominant color (ignore alpha) ------------------
/**
 * Compute mean sRGB color from image bytes, ignoring pixels with alpha < threshold.
 * Returns {r,g,b} in 0..255, or null if no opaque pixels.
 */
async function meanColorIgnoringAlpha(imageBytes, alphaThreshold = 16) {
  // Decode to raw RGBA regardless of input format (PNG/JPEG/WebP)
  const { data, info } = await sharp(Buffer.from(imageBytes))
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const { channels } = info; // should be 4
  if (channels !== 4) return null;

  let sumR = 0, sumG = 0, sumB = 0, wsum = 0;
  const N = data.length;
  // Optional sampling step for speed on huge images (e.g., take every nth pixel)
  const step = 1; // increase to 2/4 for faster approximation
  for (let i = 0; i < N; i += 4 * step) {
    const r = data[i], g = data[i + 1], b = data[i + 2], a = data[i + 3];
    if (a >= alphaThreshold) {
      const w = a / 255; // weight by alpha
      sumR += r * w;
      sumG += g * w;
      sumB += b * w;
      wsum += w;
    }
  }
  if (wsum === 0) return null;
  return {
    r: Math.round(sumR / wsum),
    g: Math.round(sumG / wsum),
    b: Math.round(sumB / wsum),
  };
}

async function readDominantColorFromTexture(tex) {
  const mime = tex.getMimeType?.();
  const img = tex.getImage?.();
  if (!img || !mime) return null;

  // Handle common raster formats via sharp.
  if (mime === "image/png" || mime === "image/jpeg" || mime === "image/webp") {
    return await meanColorIgnoringAlpha(img, 16); // ignore near-transparent pixels
  }

  // If your baseColor maps are KTX2, tell me and I’ll add a tiny decoder.
  return null;
}

// ------------------ strip Draco on write ------------------
function stripDracoExtension(doc, KHRDracoMeshCompression) {
  const root = doc.getRoot();
  const used = root.listExtensionsUsed?.() || [];
  for (const extInst of used) {
    if (extInst?.extensionName === KHRDracoMeshCompression.EXTENSION_NAME) {
      try { extInst.dispose?.(); } catch {}
    }
  }
}

// ------------------ main ------------------
(async () => {
  const { NodeIO } = await import("@gltf-transform/core");
  const ext = await import("@gltf-transform/extensions");
  const { MeshoptDecoder } = await import("meshoptimizer");
  const draco3dMod = await import("draco3dgltf");

  const {
    EXTMeshoptCompression,
    KHRDracoMeshCompression,
    KHRTextureTransform,
    KHRMeshQuantization,
    KHRMaterialsUnlit,
    KHRMaterialsSpecular,
    KHRMaterialsEmissiveStrength,
    KHRMaterialsPBRSpecularGlossiness,
  } = ext;

  // Draco decoder (no encoder; we output uncompressed)
  const createDecoderModule =
    draco3dMod.createDecoderModule || draco3dMod.default?.createDecoderModule;
  if (!createDecoderModule) {
    throw new Error('draco3dgltf did not expose createDecoderModule(). Is "draco3dgltf" installed?');
  }
  const dracoDecoderModule = await createDecoderModule();

  const folder = process.argv[2] || ".";
  const abs = path.resolve(process.cwd(), folder);
  const files = await fg("**/*.glb", { cwd: abs, dot: false, onlyFiles: true, absolute: true });

  if (!files.length) {
    console.log("No .glb files found.");
    return;
  }
  console.log(`Found ${files.length} GLB file(s). Processing...`);

  for (const file of files) {
    try {
      const io = new NodeIO()
        .registerExtensions([
          EXTMeshoptCompression,
          KHRDracoMeshCompression,     // read-time only
          KHRMeshQuantization,
          KHRTextureTransform,
          KHRMaterialsUnlit,
          KHRMaterialsSpecular,
          KHRMaterialsEmissiveStrength,
          KHRMaterialsPBRSpecularGlossiness,
        ])
        .registerDependencies({
          "meshopt.decoder": MeshoptDecoder,
          "draco3d.decoder": dracoDecoderModule,
        });

      // 1) Read (Draco is decoded to raw primitives during read)
      const doc = await io.read(file);
      const root = doc.getRoot();

      // 2) Strip Draco usage so write won't try to re-encode
      stripDracoExtension(doc, KHRDracoMeshCompression);

      // 3) For each material: derive color and clear textures
      for (const mat of root.listMaterials()) {
        try {
          const tex = getDiffuseTexture(mat, KHRMaterialsPBRSpecularGlossiness);
          const existing = mat.getBaseColorFactor?.() ?? [1, 1, 1, 1];

          let factor = existing;
          if (tex) {
            const rgb = await readDominantColorFromTexture(tex);
            if (rgb) factor = toLinearFactor(rgb, 1);
          }

          setDiffuseColor(mat, factor, KHRMaterialsPBRSpecularGlossiness);
        } catch (err) {
          console.warn(`   ⚠️ Material "${mat.getName?.() || "(unnamed)"}" color fallback:`, err?.message || err);
        }
      }

      // 4) Clear references and dispose textures
      for (const mat of root.listMaterials()) clearAllMaterialTextures(mat, KHRMaterialsPBRSpecularGlossiness);
      for (const tex of root.listTextures()) tex.dispose?.();

      // 5) Write to <srcdir>/mobile/<same-name>.glb (no Draco on output)
      const { dir, name, ext: extname } = path.parse(file);
      const mobileDir = path.join(dir, "mobile");
      await fs.mkdir(mobileDir, { recursive: true });
      const out = path.join(mobileDir, `${name}${extname}`);
      const glbOut = await io.writeBinary(doc);
      await fs.writeFile(out, Buffer.from(glbOut));
      console.log(`✔ ${path.basename(file)} → mobile/${name}${extname}`);
    } catch (e) {
      console.error(`✖ Failed ${file}:`, e?.message || e);
    }
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
