import * as fs from "node:fs"
import { validatePage } from "./src/validator.js"

function main() {
    let inputStr = ""
    try {
        inputStr = fs.readFileSync(0, "utf-8")
    } catch (e: any) {
        console.log(`INVALID: Failed to read stdin: ${e.message}`)
        process.exit(0)
    }

    let payload: any
    try {
        payload = JSON.parse(inputStr)
    } catch (e: any) {
        console.log(`INVALID: Invalid JSON input: ${e.message}`)
        process.exit(0)
    }

    if (typeof payload !== "object" || payload === null) {
        console.log("INVALID: Input is not a JSON object")
        process.exit(0)
    }

    const { kind, page } = payload

    if (kind !== "User" && kind !== "Post") {
        console.log(`INVALID: Unknown kind: ${kind}`)
        process.exit(0)
    }

    try {
        const validated = validatePage(kind, page)
        console.log("VALID")
        console.log(JSON.stringify(validated))
    } catch (e: any) {
        // e.message contains the validation errors
        // Print exactly one line starting with "INVALID: " followed by a space and an error description.
        // Replace any newlines in e.message with spaces to ensure it is exactly one line.
        const msg = e.message.replace(/\s+/g, " ").trim()
        console.log(`INVALID: ${msg}`)
    }
}

main()
