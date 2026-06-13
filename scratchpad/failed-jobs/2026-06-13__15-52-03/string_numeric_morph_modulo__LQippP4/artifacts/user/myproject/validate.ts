import { type } from "arktype";

const schema = type({
  score: ["string.numeric.parse", "|>", "number % 2"],
});

const raw = process.argv[2];

let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch {
  console.log("INVALID: input is not valid JSON");
  process.exit(1);
}

const result = schema(parsed);

if (result instanceof type.errors) {
  console.log(`INVALID: ${result.summary}`);
  process.exit(1);
}

console.log(`OK: ${JSON.stringify(result)}`);
process.exit(0);
