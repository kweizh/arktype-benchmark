import { ArkErrors } from "arktype";
import { validatePage } from "./src/validator.js";

async function main() {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk as Buffer);
  }
  const raw = Buffer.concat(chunks).toString("utf8").trim();

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    console.log("INVALID: input is not valid JSON");
    process.exit(0);
  }

  const input = parsed as Record<string, unknown>;

  const kind = input["kind"];
  if (kind !== "User" && kind !== "Post") {
    console.log(`INVALID: unknown kind "${String(kind)}" – expected "User" or "Post"`);
    process.exit(0);
  }

  try {
    const validated = validatePage(kind, input["page"]);
    console.log("VALID");
    console.log(JSON.stringify(validated));
  } catch (err) {
    if (err instanceof ArkErrors) {
      console.log(`INVALID: ${err.summary}`);
    } else {
      console.log(`INVALID: ${String(err)}`);
    }
  }

  process.exit(0);
}

main();
