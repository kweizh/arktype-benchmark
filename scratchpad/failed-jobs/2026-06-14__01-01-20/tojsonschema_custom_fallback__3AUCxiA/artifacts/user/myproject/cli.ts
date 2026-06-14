import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { userJsonSchema } from "./src/schema.js";

const outDir = resolve(import.meta.dirname!, "out");
mkdirSync(outDir, { recursive: true });

const outPath = resolve(outDir, "user.schema.json");
writeFileSync(outPath, JSON.stringify(userJsonSchema, null, 2));

console.log(`WROTE ${outPath}`);
process.exit(0);
