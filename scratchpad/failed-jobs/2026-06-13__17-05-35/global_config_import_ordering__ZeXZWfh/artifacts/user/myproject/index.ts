// ✅ Config imported BEFORE schema — numberAllowsNaN is applied
import "./config.js";
import { schema } from "./schema.js";
import { type } from "arktype";

const result = schema({ x: NaN });

if (result instanceof type.errors) {
  console.log("FAIL: NaN was rejected (expected it to be allowed)");
  console.log(result.summary);
} else {
  console.log("PASS: { x: NaN } was accepted — numberAllowsNaN is active");
  console.log("Result:", result);
}
