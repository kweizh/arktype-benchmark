import * as fs from "fs";
import { userSchema, roundTrippedUserSchema, exportUserJsonSchema } from "./src/schema.js";

// Ensure the schema is exported to /home/user/myproject/out/user.schema.json
exportUserJsonSchema();

// Read all of stdin
const input = fs.readFileSync(0, "utf-8");
let payload: any;
try {
  payload = JSON.parse(input);
} catch (err) {
  // If the input is not valid JSON, treat it as invalid for both schemas
  console.log("INVALID");
  console.log(JSON.stringify({ original: false, roundtrip: false }));
  process.exit(0);
}

const originalValid = userSchema.allows(payload);
const roundtripValid = roundTrippedUserSchema.allows(payload);

console.log(originalValid ? "VALID" : "INVALID");
console.log(JSON.stringify({ original: originalValid, roundtrip: roundtripValid }));
process.exit(0);
