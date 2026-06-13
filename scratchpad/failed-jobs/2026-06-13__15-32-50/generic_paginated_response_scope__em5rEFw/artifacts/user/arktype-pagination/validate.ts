import { scope, TraversalError } from "arktype";
import * as fs from "fs";

// Define the generic paginated-response envelope Page<T> inside a scope
const myScope = scope({
  "Page<T>": {
    items: "T[]",
    total: "number",
    "cursor?": "string | null"
  },
  User: {
    id: "number",
    name: "string"
  },
  Product: {
    id: "number",
    title: "string",
    price: "number"
  },
  PageOfUser: "Page<User>",
  PageOfProduct: "Page<Product>"
});

// Export types from the scope
const types = myScope.export();

// Parse command line arguments
const schemaName = process.argv[2];

if (!schemaName) {
  console.error("Error: SchemaName argument is required. Usage: npx tsx validate.ts <SchemaName>");
  process.exit(1);
}

if (schemaName !== "PageOfUser" && schemaName !== "PageOfProduct") {
  console.error(`Error: Unsupported SchemaName "${schemaName}". Supported values: PageOfUser, PageOfProduct.`);
  process.exit(1);
}

// Read JSON from stdin
let input = "";
try {
  input = fs.readFileSync(0, "utf-8");
} catch (err: any) {
  console.error("Error reading stdin:", err.message);
  process.exit(1);
}

let data: any;
try {
  data = JSON.parse(input);
} catch (err: any) {
  console.error("Error parsing stdin as JSON:", err.message);
  process.exit(1);
}

// Validate using ArkType and handle TraversalError
try {
  const schema = types[schemaName as "PageOfUser" | "PageOfProduct"];
  schema.assert(data);
  console.log("OK");
  process.exit(0);
} catch (err: any) {
  if (err instanceof TraversalError) {
    console.error(err.message);
    process.exit(1);
  } else {
    console.error("Unexpected error:", err.message || err);
    process.exit(1);
  }
}
