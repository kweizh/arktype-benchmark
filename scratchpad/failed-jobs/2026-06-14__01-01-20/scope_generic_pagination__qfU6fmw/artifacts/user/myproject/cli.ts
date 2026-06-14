import { validatePage } from "./src/validator.ts";
import { ArkErrors } from "arktype";

async function main(): Promise<void> {
  // Read all of stdin
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.from(chunk));
  }
  const raw = Buffer.concat(chunks).toString("utf-8").trim();

  let input: { kind: string; page: unknown };
  try {
    input = JSON.parse(raw);
  } catch {
    console.log("INVALID: input is not valid JSON");
    return;
  }

  if (input.kind !== "User" && input.kind !== "Post") {
    console.log(`INVALID: unknown kind '${input.kind}', expected 'User' or 'Post'`);
    return;
  }

  try {
    const validated = validatePage(input.kind as "User" | "Post", input.page);
    console.log("VALID");
    console.log(JSON.stringify(validated));
  } catch (err) {
    const message = err instanceof ArkErrors ? err.summary : String(err);
    console.log(`INVALID: ${message}`);
  }
}

main();
