// ❌ WRONG ORDER: schema is imported first, which causes arktype to load and
// compile the Point type BEFORE configure() runs.  At parse time, applyConfig
// sees no numberAllowsNaN in $ark.resolvedConfig, so the domain node is
// compiled as a strict "number" check (NaN excluded).
// Calling configure() afterwards is too late for already-compiled types.
import { type } from "arktype";
import { Point } from "./schema.ts";
import "./config.ts";

const result = Point({ x: NaN });

if (result instanceof type.errors) {
  console.log("✅ Expected: { x: NaN } was REJECTED (config applied too late):", result.summary);
} else {
  console.error("❌ Unexpected: { x: NaN } was accepted – config somehow applied early.");
  process.exit(1);
}
