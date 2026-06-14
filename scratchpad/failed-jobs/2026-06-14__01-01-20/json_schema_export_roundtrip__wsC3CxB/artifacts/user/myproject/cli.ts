import { userSchema, roundTrippedUserSchema, exportUserJsonSchema } from "./src/schema.ts";
import * as fs from "node:fs";
import * as path from "node:path";

async function main(): Promise<void> {
  // Read all of stdin
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.from(chunk));
  }
  const input = Buffer.concat(chunks).toString("utf8");

  let payload: unknown;
  try {
    payload = JSON.parse(input);
  } catch {
    // If JSON parsing fails, both schemas reject
    console.log("INVALID");
    console.log(JSON.stringify({ original: false, roundtrip: false }));
    return;
  }

  // Validate against original schema
  const originalResult = userSchema(payload);
  const originalValid = !(originalResult instanceof userSchema.errors);

  // Validate against round-tripped schema
  const roundTripResult = roundTrippedUserSchema(payload);
  const roundTripValid = !(roundTripResult instanceof roundTrippedUserSchema.errors);

  // Write JSON Schema to out/user.schema.json
  const outDir = path.join(import.meta.dirname ?? ".", "out");
  fs.mkdirSync(outDir, { recursive: true });
  const schemaJson = exportUserJsonSchema();
  fs.writeFileSync(
    path.join(outDir, "user.schema.json"),
    JSON.stringify(schemaJson, null, 2) + "\n"
  );

  // Output results
  console.log(originalValid ? "VALID" : "INVALID");
  console.log(
    JSON.stringify({ original: originalValid, roundtrip: roundTripValid })
  );
}

main();
