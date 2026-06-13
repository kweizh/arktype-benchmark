// ❌ Wrong import order: schema is imported BEFORE the global config.
// When schema.ts is loaded, `numberAllowsNaN` has not been set yet,
// so the schema is compiled without the NaN allowance and will reject NaN.
import { type } from "arktype"
import { schema } from "./schema"
import "./config"

const result = schema({ x: NaN })

if (result instanceof type.errors) {
  console.log("❌ broken.ts: { x: NaN } rejected as expected:", result.summary)
} else {
  console.error("UNEXPECTED success:", result)
  process.exit(1)
}