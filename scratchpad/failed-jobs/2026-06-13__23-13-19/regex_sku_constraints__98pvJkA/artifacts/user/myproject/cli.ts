import { readFileSync } from "fs";
import { type } from "arktype";
import { catalogSchema } from "./src/validator.js";

function main() {
  let input = "";
  try {
    input = readFileSync(0, "utf-8");
  } catch (e: any) {
    console.log(`INVALID: Failed to read stdin: ${e.message}`);
    process.exit(0);
  }

  let payload: any;
  try {
    payload = JSON.parse(input);
  } catch (e: any) {
    console.log(`INVALID: Invalid JSON: ${e.message}`);
    process.exit(0);
  }

  try {
    const result = catalogSchema(payload);
    if (result instanceof type.errors) {
      const errDescription = result.summary.replace(/\n/g, "; ");
      console.log(`INVALID: ${errDescription}`);
    } else {
      console.log("VALID");
      console.log(JSON.stringify(result));
    }
  } catch (e: any) {
    console.log(`INVALID: Unexpected error: ${e.message}`);
  }
  process.exit(0);
}

main();
