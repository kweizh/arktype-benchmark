// ❌ Schema imported BEFORE config — numberAllowsNaN is NOT applied
import { schema } from "./schema.js";
import "./config.js";
import { type } from "arktype";

const result = schema({ x: NaN });

if (result instanceof type.errors) {
  console.log("PASS: NaN was rejected — numberAllowsNaN was not applied (import ordering issue)");
  console.log(result.summary);
} else {
  console.log("FAIL: NaN was accepted (should have been rejected due to import ordering)");
  console.log("Result:", result);
}
