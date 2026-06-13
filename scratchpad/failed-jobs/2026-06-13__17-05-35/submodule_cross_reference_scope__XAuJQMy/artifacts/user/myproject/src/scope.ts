import { scope, type } from "arktype";

const module = scope({
  "db.config": {
    host: "string",
    port: "number",
  },
  "http.server": {
    db: "db.config",
    host: "string",
    port: "number",
  },
}).export();

export default module;

console.log("=== Module structure ===");
console.log("Keys:", Object.keys(module));
console.log("module['db.config']:", module["db.config"]);
console.log("module.db:", (module as any).db);
console.log("module['http.server']:", module["http.server"]);
console.log("module.http:", (module as any).http);
console.log("");

// Test 1: db.config should validate a config payload
const dbResult = module["db.config"].assert({
  host: "localhost",
  port: 5432,
});
console.log("1. db.config assert:", dbResult);

// Test 2: http.server should validate when given a payload with a nested db.config-shaped property
const serverResult = module["http.server"].assert({
  db: { host: "localhost", port: 5432 },
  host: "0.0.0.0",
  port: 8080,
});
console.log("2. http.server assert:", serverResult);

// Test 3: Invalid db.config payload via server schema should be rejected
try {
  module["http.server"].assert({
    db: { host: 123, port: "not-a-number" },
    host: "0.0.0.0",
    port: 8080,
  });
  console.log("3. ERROR: Should have thrown");
} catch (e) {
  console.log("3. Correctly rejected invalid db.config:", (e as Error).message);
}
