import "./config.js";
import { mySchema } from "./schema.js";
import { type } from "arktype";

const result = mySchema({ x: NaN });
if (result instanceof type.errors) {
    console.error("index.ts failed:", result.summary);
    process.exit(1);
} else {
    console.log("index.ts succeeded:", result);
}
