const { execSync } = require("child_process");
const fs = require("fs");

const files = fs.readdirSync(".").filter(file => file.endsWith(".glb") || file.endsWith(".gltf"));

files.forEach(file => {
    const base = file.replace(/\.(glb|gltf)$/, "");
    const ext = file.split(".").pop();
    const output = `${base}_optimized.${ext}`;

    console.log(`Compressing: ${file} -> ${output}`);
    // execSync(`gltf-transform draco "${file}" "${output}"`, { stdio: "inherit" });
    //gltf-transform etc1s input.glb output.glb
    execSync(`gltf-transform optimize "${file}" "${output}"`, { stdio: "inherit" });
});
