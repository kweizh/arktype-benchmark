import { type, ArkErrors } from "arktype"

const username = type("string>=3<=19").matching(/^[a-zA-Z][a-zA-Z0-9]*$/)

const input = process.argv[2]
const result = username(input)

if (result instanceof ArkErrors) {
  console.log("invalid")
  process.exit(1)
} else {
  console.log("valid")
  process.exit(0)
}