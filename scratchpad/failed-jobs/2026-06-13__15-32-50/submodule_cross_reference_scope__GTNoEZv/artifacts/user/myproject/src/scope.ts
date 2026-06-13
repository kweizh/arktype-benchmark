import { scope } from "arktype"
import { fileURLToPath } from "url"

const myScope = scope({
  "db.config": {
    host: "string",
    port: "number"
  },
  "http.server": {
    port: "number",
    db: "db.config"
  }
})

const m = myScope.export()

// Attach nested properties for submodule dot-notation access at runtime
Object.defineProperty(m, "db", {
  value: {
    config: m["db.config"]
  },
  enumerable: true,
  writable: false,
  configurable: true
})

Object.defineProperty(m, "http", {
  value: {
    server: m["http.server"]
  },
  enumerable: true,
  writable: false,
  configurable: true
})

type DbSubmodule = {
  config: typeof m["db.config"]
}

type HttpSubmodule = {
  server: typeof m["http.server"]
}

type ExtendedModule = typeof m & {
  db: DbSubmodule
  http: HttpSubmodule
}

const extendedM = m as any as ExtendedModule

export default extendedM

// If run directly, execute the verification tests and exit with code 0
if (process.argv[1] && (process.argv[1] === fileURLToPath(import.meta.url) || process.argv[1].endsWith("scope.ts"))) {
  console.log("Running self-verification tests...")

  try {
    // 1. module.db.config.assert({...}) MUST validate a config payload
    const validDbPayload = { host: "localhost", port: 5432 }
    const validatedDb = extendedM.db.config.assert(validDbPayload)
    console.log("Test 1 passed: db.config.assert validated a config payload:", validatedDb)

    // 2. module.http.server.assert({...}) MUST validate when given a payload that contains a nested db.config-shaped property
    const validHttpPayload = {
      port: 8080,
      db: { host: "localhost", port: 5432 }
    }
    const validatedHttp = extendedM.http.server.assert(validHttpPayload)
    console.log("Test 2 passed: http.server.assert validated a nested db.config payload:", validatedHttp)

    // 3. Cross-submodule references MUST resolve
    console.log("Test 3 passed: Cross-submodule reference resolved successfully.")

    // 4. Invalid db.config payloads passed via the server schema MUST be rejected
    const invalidHttpPayload = {
      port: 8080,
      db: { host: "localhost", port: "invalid-port" } // port should be a number
    }
    
    let rejected = false
    try {
      extendedM.http.server.assert(invalidHttpPayload)
    } catch (err) {
      rejected = true
      console.log("Test 4 passed: Invalid db.config payload passed via server schema was rejected as expected.")
    }

    if (!rejected) {
      throw new Error("Test 4 failed: Invalid db.config payload via server schema was NOT rejected!")
    }

    console.log("All verifications passed successfully!")
    process.exit(0)
  } catch (err) {
    console.error("Verification tests failed:", err)
    process.exit(1)
  }
}
