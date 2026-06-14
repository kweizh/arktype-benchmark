import { userSchema, roundTrippedUserSchema, exportUserJsonSchema } from "./src/schema.js";
import * as fs from "fs";

exportUserJsonSchema();

let input = "";
try {
  input = fs.readFileSync(0, "utf-8");
} catch (e) {
  process.exit(1);
}

let payload;
try {
  payload = JSON.parse(input);
} catch (e) {
  process.exit(1);
}

function isError(res: any) {
  return res && typeof res === "object" && res[" arkKind"] === "errors";
}

const originalResult = userSchema(payload);
const originalValid = !isError(originalResult);

const roundTrippedResult = roundTrippedUserSchema(payload);
const roundTrippedValid = !isError(roundTrippedResult);

console.log(originalValid ? "VALID" : "INVALID");
console.log(JSON.stringify({ original: originalValid, roundtrip: roundTrippedValid }));
