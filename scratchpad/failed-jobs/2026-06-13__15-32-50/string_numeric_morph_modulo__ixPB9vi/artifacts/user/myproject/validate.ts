import { type } from "arktype"

// Define the ArkType schema for an object with a single property `score`
const schema = type({
    score: ["string.numeric.parse", "|>", "number % 2"]
})

function main() {
    const inputArg = process.argv[2]
    if (inputArg === undefined) {
        console.log("INVALID: Missing JSON input argument")
        process.exit(1)
    }

    let parsedInput: any
    try {
        parsedInput = JSON.parse(inputArg)
    } catch (err: any) {
        console.log(`INVALID: Invalid JSON input - ${err.message}`)
        process.exit(1)
    }

    const result = schema(parsedInput)

    if (result instanceof type.errors) {
        console.log(`INVALID: ${result.summary}`)
        process.exit(1)
    } else {
        console.log(`OK: ${JSON.stringify(result)}`)
        process.exit(0)
    }
}

main()
