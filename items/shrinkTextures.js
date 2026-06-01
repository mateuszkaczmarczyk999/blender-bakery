#!/usr/bin/env node
"use strict";

/**
 * Shrink + KTX2-compress textures in every .glb under a folder.
 * - Step A: resize to TARGET px (max dimension).
 * - Step B: UASTC only for normals (better quality for vectors).
 * - Step C: ETC1S for baseColor/ORM/emissive (tiny).
 * Output: <srcdir>/mobile/<same-name>.glb
 *
 * Usage:
 *   node shrink-to-ktx2.js /abs/or/rel/folder [TARGET_MAX]
 */

const { promisify } = require("node:util");
const { execFile } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs/promises");
const fg = require("fast-glob");

const exec = promisify(execFile);
const CLI = "gltf-transform"; // use globally installed CLI

const folder = process.argv[2] || ".";
const TARGET = parseInt(process.argv[3] || "128", 10);
const abs = path.resolve(process.cwd(), folder);

// slots — pass as ONE argument so the CLI parses it correctly.
const NORMAL_SLOTS = "{normalTexture}";
const COLORLIKE_SLOTS = "{baseColorTexture,occlusionTexture,metallicRoughnessTexture,emissiveTexture}";

function logCmd(cmd, args) {
  console.log(`$ ${cmd} ${args.map(a => (/\s/.test(a) ? `"${a}"` : a)).join(" ")}`);
}

async function run(cmd, args, cwd) {
  logCmd(cmd, args);
  try {
    const { stdout, stderr } = await exec(cmd, args, { cwd, windowsHide: true });
    if (stdout) process.stdout.write(stdout);
    if (stderr) process.stderr.write(stderr);
  } catch (e) {
    const out = e.stdout?.toString?.() || "";
    const err = e.stderr?.toString?.() || e.message || String(e);
    if (out) process.stdout.write(out);
    console.error(err);
    throw e;
  }
}

(async () => {
  // Ensure CLI exists
  try {
    const { stdout } = await exec(CLI, ["--version"]);
    console.log(`Using ${CLI} ${stdout.trim()}`);
  } catch {
    console.error(`❌ "${CLI}" not found. Install it with:\n  npm i -g @gltf-transform/cli`);
    process.exit(1);
  }

  const files = await fg("**/*.glb", { cwd: abs, absolute: true, onlyFiles: true });
  if (!files.length) {
    console.log("No .glb files found.");
    return;
  }

  console.log(`Found ${files.length} GLB file(s). Processing at max ${TARGET}px ...`);

  for (const file of files) {
    const { dir, name, ext } = path.parse(file);
    const mobileDir = path.join(dir, "mobile");
    const tmp1 = path.join(dir, `${name}.tmp.resized.glb`);
    const tmp2 = path.join(dir, `${name}.tmp.uastc.glb`);
    const out = path.join(mobileDir, `${name}${ext}`);

    try {
      await fs.mkdir(mobileDir, { recursive: true });

      // A) Resize (preserve aspect; power-of-two not enforced here)
      await run(CLI, ["resize", file, tmp1, "--width", String(TARGET), "--height", String(TARGET)], dir);

      // B) UASTC for normals (good quality for tangent-space maps).
      await run(
        CLI,
        [
          "uastc",
          tmp1,
          tmp2,
          "--slots",
          NORMAL_SLOTS,        // <- single arg
          "--level",
          "2",
          "--rdo",
          "--zstd",
          "18",
          "--verbose",
        ],
        dir
      );

      // C) ETC1S for everything color-like (tiny, great for VRAM).
      await run(
        CLI,
        [
          "etc1s",
          tmp2,
          out,
          "--slots",
          COLORLIKE_SLOTS,     // <- single arg
          "--quality",
          "128",
          "--verbose",
        ],
        dir
      );

      await fs.rm(tmp1, { force: true });
      await fs.rm(tmp2, { force: true });

      console.log(`✔ ${path.basename(file)} → mobile/${name}${ext}`);
    } catch (e) {
      console.error(`✖ Failed ${file}`);
      // leave tmp files for debugging; or clean up:
      await fs.rm(tmp1, { force: true }).catch(() => {});
      await fs.rm(tmp2, { force:true }).catch(() => {});
    }
  }

  console.log("Done.");
})();
