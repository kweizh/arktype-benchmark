import { readFileSync } from "node:fs";
import { validatePage } from "./src/validator.js";

const input = readFileSync(0, "utf-8").trim();

let data: { kind: string; page: unknown };
try {
  data = JSON.parse(input);
} catch {
  console.log("INVALID: malformed JSON input");
  process.exit(0);
}

try {
  const result = validatePage(data.kind as "User" | "Post", data.page);
  console.log("VALID");
  console.log(JSON.stringify(result));
} catch (e) {
  const message = e instanceof Error ? e.message : String(e);
  console.log(`INVALID: ${message}`);
}