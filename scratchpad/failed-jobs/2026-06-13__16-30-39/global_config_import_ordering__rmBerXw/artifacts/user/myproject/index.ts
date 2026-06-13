// ✅ Correct import order: configure global config BEFORE importing the schema.
// The `configure()` call runs first, setting `numberAllowsNaN: true` globally,
// so when schema.ts is loaded it picks up the config.
import { type } from "arktype"
import "./config"
import { schema } from "./schema"

const result = schema({ x: NaN })

if (result instanceof type.errors) {
  console.error("UNEXPECTED rejection:", result.summary)
  process.exit(1)
} else {
  console.log("✅ index.ts: { x: NaN } validated successfully:", result)
}