import { writeFileSync, mkdirSync } from "node:fs"
import { resolve } from "node:path"
import { userJsonSchema } from "./src/schema.ts"

const outDir = resolve("out")
const outPath = resolve(outDir, "user.schema.json")

mkdirSync(outDir, { recursive: true })
writeFileSync(outPath, JSON.stringify(userJsonSchema, null, 2))
process.stdout.write(`WROTE ${outPath}\n`)
process.exit(0)
