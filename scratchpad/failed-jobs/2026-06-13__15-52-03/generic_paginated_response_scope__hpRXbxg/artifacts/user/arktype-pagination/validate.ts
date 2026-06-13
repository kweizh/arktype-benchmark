/**
 * Usage:
 *   echo '<json>' | npx tsx validate.ts PageOfUser
 *   echo '<json>' | npx tsx validate.ts PageOfProduct
 *
 * Exit 0 + prints "OK"  on success.
 * Exit 1 + prints error on validation failure.
 */
import { ArkErrors } from "arktype"
import { PageOfUser, PageOfProduct } from "./schemas.ts"

const schemaName = process.argv[2]

const validators = {
  PageOfUser,
  PageOfProduct,
} as const

type SchemaName = keyof typeof validators

if (!schemaName || !(schemaName in validators)) {
  process.stderr.write(
    `Error: unknown schema "${schemaName ?? ""}". ` +
      `Supported values: ${Object.keys(validators).join(", ")}\n`,
  )
  process.exit(1)
}

// Read entire stdin, then parse + validate.
const chunks: Buffer[] = []
process.stdin.on("data", (chunk: Buffer) => chunks.push(chunk))
process.stdin.on("end", () => {
  const raw = Buffer.concat(chunks).toString("utf8")

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch (e) {
    process.stderr.write(`JSON parse error: ${(e as Error).message}\n`)
    process.exit(1)
  }

  const validator = validators[schemaName as SchemaName]

  try {
    validator.assert(parsed)
    process.stdout.write("OK\n")
    process.exit(0)
  } catch (err) {
    if (err instanceof ArkErrors) {
      process.stderr.write(err.message + "\n")
    } else {
      process.stderr.write(String(err) + "\n")
    }
    process.exit(1)
  }
})
