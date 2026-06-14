import { catalogSchema } from "./src/validator.js";
import { type } from "arktype";
import * as fs from "fs";

function main() {
  const input = fs.readFileSync(0, "utf-8");
  let data;
  try {
    data = JSON.parse(input);
  } catch (e) {
    console.log("INVALID: Invalid JSON");
    return;
  }

  const res = catalogSchema(data);
  if (res instanceof type.errors) {
    const errorMessage = res.summary.replace(/\n/g, ", ");
    console.log(`INVALID: ${errorMessage}`);
  } else {
    console.log("VALID");
    console.log(JSON.stringify(res));
  }
}

main();
