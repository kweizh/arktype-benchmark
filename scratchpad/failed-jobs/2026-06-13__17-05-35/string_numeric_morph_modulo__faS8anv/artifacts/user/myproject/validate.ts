import { type } from "arktype";

const schema = type({
  score: ["string.numeric.parse", "|>", "number % 2"],
});

const inputJson = process.argv[2];
let input: unknown;

try {
  input = JSON.parse(inputJson);
} catch {
  console.log("INVALID: input is not valid JSON");
  process.exit(1);
}

const result = schema(input);

if (result instanceof type.errors) {
  console.log(`INVALID: ${result.summary}`);
  process.exit(1);
}

console.log(`OK: ${JSON.stringify(result)}`);
