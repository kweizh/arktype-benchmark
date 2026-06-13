/**
 * Verification script – exercises every acceptance criterion.
 * Exit 0 on full pass, exit 1 on any failure.
 */
import module from "./scope.js";
import { Module } from "arktype";

let failures = 0;

function ok(label: string) {
  console.log(`  ✓ ${label}`);
}

function fail(label: string, err?: unknown) {
  console.error(`  ✗ ${label}`, err ?? "");
  failures++;
}

// ---------------------------------------------------------------------------
// Criterion 1 – module.db.config must validate a config payload
// ---------------------------------------------------------------------------
console.log("\n[1] module.db.config validates a valid payload");
try {
  (module as any).db.config.assert({ host: "localhost", port: 5432 });
  ok("{ host: 'localhost', port: 5432 } accepted");
} catch (e) {
  fail("valid db.config payload rejected", e);
}

// ---------------------------------------------------------------------------
// Criterion 2 – module.http.server validates a payload with a nested db.config
// ---------------------------------------------------------------------------
console.log("\n[2] module.http.server validates a payload containing a db.config-shaped property");
try {
  (module as any).http.server.assert({
    address: "0.0.0.0:8080",
    db: { host: "db.example.com", port: 5432 },
  });
  ok("valid http.server payload accepted");
} catch (e) {
  fail("valid http.server payload rejected", e);
}

// ---------------------------------------------------------------------------
// Criterion 3 – cross-submodule reference resolves (exercise it)
// ---------------------------------------------------------------------------
console.log("\n[3] Cross-submodule reference resolves (db.config shape enforced inside http.server)");
try {
  (module as any).http.server.assert({
    address: "127.0.0.1:3000",
    db: { host: "replica", port: 3306 },
  });
  ok("cross-submodule reference resolved and validated correctly");
} catch (e) {
  fail("cross-submodule reference did not resolve", e);
}

// ---------------------------------------------------------------------------
// Criterion 4 – invalid db.config payloads MUST be rejected via server schema
// ---------------------------------------------------------------------------
console.log("\n[4] Invalid db.config payloads passed via server schema are rejected");
try {
  (module as any).http.server.assert({
    address: "0.0.0.0:8080",
    db: { host: 99, port: "not-a-number" }, // invalid!
  });
  fail("expected rejection of invalid db payload, but it was accepted");
} catch (_) {
  ok("invalid db.config correctly rejected by http.server schema");
}

// also directly
try {
  (module as any).db.config.assert({ host: 42, port: "oops" });
  fail("expected rejection of invalid db.config direct payload");
} catch (_) {
  ok("invalid db.config payload directly rejected");
}

// ---------------------------------------------------------------------------
// Criterion 5 – single scope({...}).export() with ≥ 2 dot-notation submodule keys
// ---------------------------------------------------------------------------
console.log("\n[5] Module structure: dot-notation keys present, valid Module instance");

const flatKeys = Object.keys(module);
const dotKeys = flatKeys.filter(k => k.includes("."));

if (dotKeys.length >= 2) {
  ok(`at least two dot-notation keys found: ${dotKeys.join(", ")}`);
} else {
  fail(`expected ≥ 2 dot-notation keys, found: ${dotKeys.join(", ")}`);
}

if ((module as any)["db.config"] && (module as any)["http.server"]) {
  ok(`"db.config" and "http.server" are accessible via bracket notation`);
} else {
  fail(`flat dot-notation keys not accessible`);
}

if (module instanceof Module) {
  ok("default export is an ArkType Module instance");
} else {
  fail("default export is NOT an ArkType Module instance");
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------
console.log(`\n${"─".repeat(50)}`);
if (failures === 0) {
  console.log("All acceptance criteria PASSED ✓");
  process.exit(0);
} else {
  console.log(`${failures} criterion/criteria FAILED ✗`);
  process.exit(1);
}
