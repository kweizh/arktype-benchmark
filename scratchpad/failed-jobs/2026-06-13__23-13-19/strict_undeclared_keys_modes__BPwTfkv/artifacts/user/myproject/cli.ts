import * as fs from "node:fs";
import { type } from "arktype";

// Define schemas as required
const ignoreSchema = type({
  id: "string.uuid",
  name: "string",
  email: "string.email",
  "+": "ignore"
});

const rejectSchema = type({
  id: "string.uuid",
  name: "string",
  email: "string.email",
  "+": "reject"
});

const deleteSchema = type({
  id: "string.uuid",
  name: "string",
  email: "string.email",
  "+": "delete"
});

function main() {
  let inputStr = "";
  try {
    inputStr = fs.readFileSync(0, "utf-8").trim();
  } catch (err) {
    console.log("INVALID: Failed to read from stdin");
    process.exit(0);
  }

  if (!inputStr) {
    console.log("INVALID: Empty input");
    process.exit(0);
  }

  let inputJson: any;
  try {
    inputJson = JSON.parse(inputStr);
  } catch (err) {
    console.log("INVALID: Invalid JSON format");
    process.exit(0);
  }

  if (typeof inputJson !== "object" || inputJson === null) {
    console.log("INVALID: Input must be a JSON object");
    process.exit(0);
  }

  const { mode, payload } = inputJson;

  if (mode !== "ignore" && mode !== "reject" && mode !== "delete") {
    console.log(`INVALID: Unknown mode "${mode}"`);
    process.exit(0);
  }

  // Check if payload is present in the input JSON
  if (!("payload" in inputJson)) {
    console.log("INVALID: Missing payload");
    process.exit(0);
  }

  let schema: any;
  if (mode === "ignore") {
    schema = ignoreSchema;
  } else if (mode === "reject") {
    schema = rejectSchema;
  } else {
    schema = deleteSchema;
  }

  const result = schema(payload);

  if (result instanceof type.errors) {
    const errorMessage = result.summary.replace(/\r?\n/g, "; ");
    console.log(`INVALID: ${errorMessage}`);
  } else {
    console.log("VALID");
    console.log(JSON.stringify(result));
  }
}

main();
