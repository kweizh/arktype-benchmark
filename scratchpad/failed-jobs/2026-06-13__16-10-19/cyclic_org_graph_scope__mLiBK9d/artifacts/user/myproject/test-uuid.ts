import { type } from "arktype"
try {
  const uuidType = type("string.uuid")
  console.log("string.uuid works")
} catch (e) {
  console.log("string.uuid failed")
}
try {
  const uuidType2 = type("uuid")
  console.log("uuid works")
} catch (e) {
  console.log("uuid failed")
}
