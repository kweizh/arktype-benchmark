import { PageOfUser, PageOfProduct } from "./schemas.js";
import { TraversalError } from "arktype";

const schemaName = process.argv[2];

// Read stdin
const chunks: Buffer[] = [];
process.stdin.on("data", (chunk: Buffer) => {
  chunks.push(chunk);
});

process.stdin.on("end", () => {
  const input = Buffer.concat(chunks).toString("utf-8");
  let data: unknown;
  try {
    data = JSON.parse(input);
  } catch {
    console.error("Invalid JSON input");
    process.exit(1);
  }

  try {
    switch (schemaName) {
      case "PageOfUser":
        PageOfUser.assert(data);
        break;
      case "PageOfProduct":
        PageOfProduct.assert(data);
        break;
      default:
        console.error(`Unknown schema: ${schemaName}`);
        process.exit(1);
    }
    console.log("OK");
    process.exit(0);
  } catch (err) {
    if (err instanceof TraversalError) {
      console.error(err.message);
      process.exit(1);
    }
    throw err;
  }
});
