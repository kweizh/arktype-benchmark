import { type } from "arktype";

const schema = type({
  score: ["string.numeric.parse", "|>", "number % 2"],
});

const input = JSON.parse(process.argv[2]);
const result = schema(input);

if (result instanceof type.errors) {
  console.log(`INVALID: ${result.summary}`);
  process.exit(1);
} else {
  console.log(`OK: ${JSON.stringify(result)}`);
  process.exit(0);
}