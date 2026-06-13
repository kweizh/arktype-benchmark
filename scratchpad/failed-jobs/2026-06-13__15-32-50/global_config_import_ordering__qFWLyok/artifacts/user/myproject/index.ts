// Import global configuration first to ensure it is applied
import "./config.js"
// Then import the shared schema
import { mySchema } from "./schema.js"
import { ArkErrors } from "arktype"

const input = { x: NaN }
const result = mySchema(input)

if (result instanceof ArkErrors) {
	console.error("Validation failed unexpectedly:", result.summary)
	process.exit(1)
} else {
	console.log("Validation succeeded as expected:", result)
}
