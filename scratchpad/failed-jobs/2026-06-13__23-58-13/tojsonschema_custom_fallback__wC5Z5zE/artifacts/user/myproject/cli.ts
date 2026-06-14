import { exportSchema } from "./src/schema.ts";
import * as fs from "fs";
import * as path from "path";

const outDir = path.resolve(process.cwd(), "out");
if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

const outPath = path.join(outDir, "user.schema.json");
const schema = exportSchema();

fs.writeFileSync(outPath, JSON.stringify(schema, null, 2), "utf-8");
console.log(`WROTE ${outPath}`);
process.exit(0);
