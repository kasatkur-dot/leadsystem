import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { Script, createContext } from "node:vm";

const babelUrl = "https://unpkg.com/@babel/standalone@7.29.0/babel.min.js";
const bundlePath = "site/assets/app.bundle.js";

const files = [
  ["site/src/images.js", false],
  ["site/src/icons.jsx", true],
  ["site/src/sections.jsx", true],
  ["site/src/app.jsx", true],
];

async function loadBabel() {
  try {
    return await fetch(babelUrl).then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch Babel: ${response.status}`);
      }
      return response.text();
    });
  } catch (error) {
    console.warn(`Babel fetch unavailable; trying cached JSX chunks (${error.cause?.code || error.message}).`);
    return "";
  }
}

function extractChunk(bundle, file, nextFile) {
  const marker = `/* ${file} */`;
  const start = bundle.indexOf(marker);
  if (start === -1) {
    throw new Error(`Missing cached bundle marker: ${marker}`);
  }
  const codeStart = start + marker.length;
  const end = nextFile ? bundle.indexOf(`/* ${nextFile} */`, codeStart) : bundle.indexOf("\n})();", codeStart);
  if (end === -1) {
    throw new Error(`Missing cached bundle end for: ${file}`);
  }
  return bundle.slice(codeStart, end).trim();
}

async function loadCachedChunks() {
  const bundleStat = await stat(bundlePath);
  for (const [file, needsJsxTransform] of files) {
    if (!needsJsxTransform) continue;
    const sourceStat = await stat(file);
    if (sourceStat.mtimeMs > bundleStat.mtimeMs + 1000) {
      throw new Error(`Cannot rebuild ${file} offline because its JSX source is newer than ${bundlePath}.`);
    }
  }

  const bundle = await readFile(bundlePath, "utf8");
  const chunks = new Map();
  for (let index = 0; index < files.length; index += 1) {
    const [file, needsJsxTransform] = files[index];
    if (!needsJsxTransform) continue;
    const nextFile = files[index + 1]?.[0] || "";
    chunks.set(file, extractChunk(bundle, file, nextFile));
  }
  return chunks;
}

const babelCode = await loadBabel();
const context = babelCode ? createContext({}) : null;
if (babelCode) {
  new Script(babelCode).runInContext(context);
}
const cachedChunks = babelCode ? new Map() : await loadCachedChunks();

const chunks = [
  "/* Generated from site/src/*.jsx for file:// and static preview. Do not edit by hand. */",
  "(function(){",
  "\"use strict\";",
];

for (const [file, needsJsxTransform] of files) {
  const source = await readFile(file, "utf8");
  const code = needsJsxTransform
    ? (babelCode ? context.Babel.transform(source, {
        presets: [["react", { runtime: "classic" }]],
        comments: false,
        compact: false,
      }).code : cachedChunks.get(file))
    : source;

  chunks.push(`\n/* ${file} */\n${code}`);
}

chunks.push("\n})();\n");

await mkdir("site/assets", { recursive: true });
await writeFile(bundlePath, chunks.join("\n"), "utf8");

console.log(`built ${bundlePath}`);
