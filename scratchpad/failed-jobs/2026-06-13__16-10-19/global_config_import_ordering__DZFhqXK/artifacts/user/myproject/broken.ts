import { mySchema } from "./schema.js";
import "./config.js";
import { type } from "arktype";

const result = mySchema({ x: NaN });
if (result instanceof type.errors) {
    console.error("broken.ts failed:", result.summary);
    process.exit(1);
} else {
    console.log("broken.ts succeeded:", result);
}
