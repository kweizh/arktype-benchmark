// Import the shared schema first (before config is applied)
import { mySchema } from "./schema.js"
// Import config too late
import "./config.js"
import { ArkErrors } from "arktype"

const input = { x: NaN }
const result = mySchema(input)

if (result instanceof ArkErrors) {
	console.log("Validation failed as expected (due to import order):", result.summary)
} else {
	console.error("Validation unexpectedly succeeded:", result)
	process.exit(1)
}
