import { type } from "arktype";
import { catalogSchema } from "./src/validator.js";

async function main(): Promise<void> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.from(chunk));
  }
  const input = Buffer.concat(chunks).toString("utf-8").trim();

  let payload: unknown;
  try {
    payload = JSON.parse(input);
  } catch {
    process.stdout.write("INVALID: invalid JSON\n");
    process.exit(0);
  }

  const result = catalogSchema(payload);

  if (result instanceof type.errors) {
    process.stdout.write(`INVALID: ${result.summary}\n`);
    process.exit(0);
  }

  process.stdout.write("VALID\n");
  process.stdout.write(JSON.stringify(result) + "\n");
  process.exit(0);
}

main();
