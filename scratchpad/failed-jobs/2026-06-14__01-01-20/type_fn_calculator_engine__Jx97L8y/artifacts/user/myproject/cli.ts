import { fn, TraversalError } from "arktype";
import { operations } from "./operations.js";

const compute = fn(
  "'add'|'subtract'|'multiply'|'divide'|'modulo'",
  "number",
  "number",
  ":",
  "number",
)((op: "add" | "subtract" | "multiply" | "divide" | "modulo", a: number, b: number): number => {
  return operations[op](a, b);
});

async function main(): Promise<void> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.from(chunk));
  }

  const input = Buffer.concat(chunks).toString("utf-8").trim();
  if (!input) {
    process.exit(0);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(input);
  } catch {
    // If JSON parsing fails, it will fail at the type.fn boundary
    try {
      compute(parsed as never, undefined as never, undefined as never);
    } catch (err) {
      if (err instanceof TraversalError) {
        console.log(`ERR ${err.message}`);
        process.exit(0);
      }
      throw err;
    }
    process.exit(0);
  }

  const { op, a, b } = parsed as { op: string; a: number; b: number };

  try {
    const result = compute(op, a, b);
    console.log(`OK ${String(result)}`);
  } catch (err) {
    if (err instanceof TraversalError) {
      console.log(`ERR ${err.message}`);
    } else {
      throw err;
    }
  }

  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
