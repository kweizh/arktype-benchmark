import {
  userSchema,
  roundTrippedUserSchema,
  exportUserJsonSchema,
} from "./src/schema.js";

// Ensure out/user.schema.json is written on every invocation
exportUserJsonSchema();

// Read all of stdin
const chunks: Buffer[] = [];
for await (const chunk of process.stdin) {
  chunks.push(chunk as Buffer);
}
const raw = Buffer.concat(chunks).toString("utf-8");
const payload = JSON.parse(raw);

// Use .allows() to avoid cross-instance ArkErrors instanceof issues
const originalValid = userSchema.allows(payload);
const roundTripValid = roundTrippedUserSchema.allows(payload);

// Line 1: VALID / INVALID (based on original schema)
process.stdout.write(originalValid ? "VALID\n" : "INVALID\n");
// Line 2: JSON boolean summary
process.stdout.write(
  JSON.stringify({ original: originalValid, roundtrip: roundTripValid }) + "\n"
);
