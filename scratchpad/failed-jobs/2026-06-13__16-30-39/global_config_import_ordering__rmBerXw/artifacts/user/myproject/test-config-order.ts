// Test: Import arktype/config first, configure, then import arktype
import { configure } from "arktype/config"
configure({ numberAllowsNaN: true })
import { type } from "arktype"

const schema = type({ x: "number" })
const result = schema({ x: NaN })
if (result instanceof type.errors) {
  console.log("Rejected:", result.summary)
} else {
  console.log("Accepted:", result)
}