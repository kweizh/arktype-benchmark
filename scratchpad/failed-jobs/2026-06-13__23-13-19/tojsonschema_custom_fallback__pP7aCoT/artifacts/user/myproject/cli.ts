import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { userJsonSchema } from "./src/user.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outDir = path.join(__dirname, "out");
const outFile = path.join(outDir, "user.schema.json");

if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

fs.writeFileSync(outFile, JSON.stringify(userJsonSchema, null, 2), "utf-8");

console.log(`WROTE ${path.resolve(outFile)}`);

process.exit(0);
