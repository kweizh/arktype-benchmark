import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { userSchema } from "./src/schema.js";

const outDir = join(process.cwd(), "out");
mkdirSync(outDir, { recursive: true });

const outPath = join(outDir, "user.schema.json");
writeFileSync(outPath, JSON.stringify(userSchema, null, 2) + "\n");

console.log(`WROTE ${outPath}`);