import { scope } from "arktype";

// Test 1: Flat dot-notation keys
try {
  const mod1 = scope({
    "db.config": {
      host: "string",
      port: "number",
    },
    "http.server": {
      port: "number",
      config: "db.config",
    },
  }).export();
  console.log("Test 1 - Flat keys module keys:", Object.keys(mod1));
  console.log("Test 1 - module.db:", typeof (mod1 as any).db);
  console.log("Test 1 - module['db.config']:", typeof (mod1 as any)["db.config"]);
} catch (e) {
  console.log("Test 1 - Error:", e);
}

// Test 2: db as module, http.server as dot key
try {
  const dbModule = scope({ config: { host: "string", port: "number" } }).export();
  console.log("dbModule keys:", Object.keys(dbModule));
  
  const mod2 = scope({
    db: dbModule,
    "http.server": {
      port: "number",
      config: "db.config",
    },
  }).export();
  console.log("Test 2 - Module keys:", Object.keys(mod2));
  console.log("Test 2 - module.db:", typeof (mod2 as any).db);
  console.log("Test 2 - module.http:", typeof (mod2 as any).http);
  console.log("Test 2 - module['http.server']:", typeof (mod2 as any)["http.server"]);
  
  if ((mod2 as any).db) {
    console.log("Test 2 - module.db.config:", typeof (mod2 as any).db.config);
  }
  if ((mod2 as any).http) {
    console.log("Test 2 - module.http.server:", typeof (mod2 as any).http.server);
  }
} catch (e) {
  console.log("Test 2 - Error:", e);
}

// Test 3: Both as modules
try {
  const dbModule = scope({ config: { host: "string", port: "number" } }).export();
  const httpModule = scope({ server: { port: "number", config: "db.config" } }).export();
  
  const mod3 = scope({
    db: dbModule,
    http: httpModule,
  }).export();
  console.log("Test 3 - Module keys:", Object.keys(mod3));
  console.log("Test 3 - module.db.config:", typeof (mod3 as any).db?.config);
  console.log("Test 3 - module.http.server:", typeof (mod3 as any).http?.server);
} catch (e) {
  console.log("Test 3 - Error:", e);
}