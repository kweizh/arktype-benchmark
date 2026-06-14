import { type } from "arktype";
import { readFileSync } from "node:fs";

// Define the logical user shape: { id: 'string.uuid', name: 'string', email: 'string.email' }

// 1. ignoreSchema — default behavior, extras are kept
const ignoreSchema = type({
  id: "string.uuid",
  name: "string",
  email: "string.email",
});

// 2. rejectSchema — rejects objects with any undeclared key
const rejectSchema = type({
  "+": "reject",
  id: "string.uuid",
  name: "string",
  email: "string.email",
});

// 3. deleteSchema — deletes undeclared keys from the validated output
const deleteSchema = type({
  "+": "delete",
  id: "string.uuid",
  name: "string",
  email: "string.email",
});

function main(): void {
  const raw = readFileSync(0, "utf-8").trim();

  let input: { mode: string; payload: unknown };
  try {
    input = JSON.parse(raw);
  } catch {
    console.log("INVALID: input is not valid JSON");
    return;
  }

  if (typeof input !== "object" || input === null || !("mode" in input) || !("payload" in input)) {
    console.log("INVALID: input must be an object with 'mode' and 'payload' keys");
    return;
  }

  const { mode, payload } = input;

  let schema: typeof ignoreSchema;
  switch (mode) {
    case "ignore":
      schema = ignoreSchema;
      break;
    case "reject":
      schema = rejectSchema;
      break;
    case "delete":
      schema = deleteSchema;
      break;
    default:
      console.log(`INVALID: unknown mode '${mode}', expected 'ignore', 'reject', or 'delete'`);
      return;
  }

  const result = schema(payload);

  if (result instanceof type.errors) {
    // Use the summary which includes all error messages, replace newlines to keep it on one line
    const message = result.summary.replace(/\n/g, "; ");
    console.log(`INVALID: ${message}`);
  } else {
    console.log("VALID");
    console.log(JSON.stringify(result));
  }
}

main();
