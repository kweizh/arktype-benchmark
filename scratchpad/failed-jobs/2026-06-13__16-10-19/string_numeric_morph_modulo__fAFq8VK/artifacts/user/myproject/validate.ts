import { type } from "arktype";

const schema = type({
  score: ["string.numeric.parse", "|>", "number % 2"]
});

const input = process.argv[2];

if (!input) {
  console.error("No input provided");
  process.exit(1);
}

let parsed;
try {
  parsed = JSON.parse(input);
} catch (e) {
  console.log("INVALID: Invalid JSON");
  process.exit(1);
}

const out = schema(parsed);

if (out instanceof type.errors) {
  console.log("INVALID: " + out.summary);
  process.exit(1);
} else {
  console.log("OK: " + JSON.stringify(out));
  process.exit(0);
}
