import { readFileSync } from "node:fs"
import { Catalog, type Catalog as CatalogType } from "./src/validator.js"
import { ArkErrors } from "arktype"

const input = readFileSync(0, "utf-8")

try {
  const data = JSON.parse(input)
  const result = Catalog(data)

  if (result instanceof ArkErrors) {
    console.log(`INVALID: ${result.summary}`)
  } else {
    console.log("VALID")
    console.log(JSON.stringify(result))
  }
} catch (e) {
  const message = e instanceof Error ? e.message : String(e)
  console.log(`INVALID: ${message}`)
}