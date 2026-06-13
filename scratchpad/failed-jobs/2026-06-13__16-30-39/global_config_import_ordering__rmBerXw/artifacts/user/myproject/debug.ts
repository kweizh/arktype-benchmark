import "./config"
import { type } from "arktype"
import { schema } from "./schema"

// Debug: check the config
const scopeRef = (type as any).$
console.log("resolvedConfig.numberAllowsNaN:", scopeRef?.resolvedConfig?.numberAllowsNaN)

const result = schema({ x: NaN })
if (result instanceof type.errors) {
  console.log("Rejected:", result.summary)
} else {
  console.log("Accepted:", result)
}