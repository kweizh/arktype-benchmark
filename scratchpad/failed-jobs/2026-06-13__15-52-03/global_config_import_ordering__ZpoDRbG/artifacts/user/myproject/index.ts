// ✅ CORRECT ORDER: config is imported first so configure() runs before
// arktype's kinds.js resolves $ark.resolvedConfig and before the Point
// type is compiled by applyConfig.
import "./config.ts";
import { type } from "arktype";
import { Point } from "./schema.ts";

const result = Point({ x: NaN });

if (result instanceof type.errors) {
  console.error("❌ Unexpected: { x: NaN } was REJECTED:", result.summary);
  process.exit(1);
} else {
  console.log("✅ { x: NaN } accepted (numberAllowsNaN: true is active):", result);
}
