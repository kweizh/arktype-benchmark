import { validateCatalog } from "./src/validator.js";

async function main(): Promise<void> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk as Buffer);
  }

  const raw = Buffer.concat(chunks).toString("utf8").trim();

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    process.stdout.write("INVALID: input is not valid JSON\n");
    process.exit(0);
  }

  const result = validateCatalog(parsed);

  if (result.ok) {
    process.stdout.write("VALID\n");
    process.stdout.write(JSON.stringify(result.data) + "\n");
  } else {
    process.stdout.write(`INVALID: ${result.errors.summary}\n`);
  }

  process.exit(0);
}

main();
