import { scope, TraversalError } from "arktype";

const types = scope({
  "Page<t>": { items: "t[]", total: "number", cursor: "string | null" },
  User: { id: "string", name: "string", email: "string" },
  Product: { id: "string", name: "string", price: "number" },
  PageOfUser: "Page<User>",
  PageOfProduct: "Page<Product>",
}).export();

const schemaName = process.argv[2];

if (schemaName !== "PageOfUser" && schemaName !== "PageOfProduct") {
  process.stderr.write(`Unknown schema: ${schemaName}\n`);
  process.exit(1);
}

const validator = types[schemaName as "PageOfUser" | "PageOfProduct"];

let inputData = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk: string) => {
  inputData += chunk;
});
process.stdin.on("end", () => {
  const data = JSON.parse(inputData);
  try {
    validator.assert(data);
    process.stdout.write("OK\n");
    process.exit(0);
  } catch (err) {
    if (err instanceof TraversalError) {
      process.stderr.write(`${err.message}\n`);
      process.exit(1);
    }
    throw err;
  }
});