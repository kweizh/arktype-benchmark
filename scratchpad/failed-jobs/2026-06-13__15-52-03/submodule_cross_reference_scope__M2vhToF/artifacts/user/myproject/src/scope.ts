import { scope } from "arktype";

/**
 * ArkType scope with two submodules declared using dot-notation keys:
 *
 *   "db.config"   – database configuration shape
 *   "http.server" – HTTP server shape, with a nested `db` field that must
 *                   satisfy the `db.config` schema (cross-submodule reference)
 *
 * The exported Module is augmented with non-enumerable nested accessors so
 * that both `module["db.config"]` and `module.db.config` (and likewise for
 * `http.server`) resolve to the same Type objects.
 */
const module = scope({
  /** Sub-module key 1 – database configuration */
  "db.config": {
    host: "string",
    port: "number",
  },

  /** Sub-module key 2 – HTTP server; references db.config from the same scope */
  "http.server": {
    address: "string",
    /** The server must carry a valid db.config-shaped value. */
    db: "db.config",
  },
}).export();

// ---------------------------------------------------------------------------
// Augment the Module with nested property accessors.
//
// `scope({ "db.config": …, "http.server": … }).export()` stores types under
// the flat keys `"db.config"` and `"http.server"`.  We additionally expose
// them through a nested object per prefix (i.e. `module.db` and
// `module.http`) so callers can write `module.db.config.assert(…)`.
//
// The Module object itself is preserved – `module instanceof Module` remains
// true – and the flat dot-notation keys remain intact.
// ---------------------------------------------------------------------------
type SubmoduleMap = Record<string, Record<string, unknown>>;

const submodules: SubmoduleMap = {};

for (const key of Object.keys(module)) {
  const dotIdx = key.indexOf(".");
  if (dotIdx === -1) continue;

  const prefix = key.slice(0, dotIdx);
  const suffix = key.slice(dotIdx + 1);

  if (!submodules[prefix]) submodules[prefix] = {};
  submodules[prefix][suffix] = (module as Record<string, unknown>)[key];
}

for (const [prefix, sub] of Object.entries(submodules)) {
  Object.defineProperty(module, prefix, {
    value: sub,
    writable: false,
    enumerable: false, // keep Object.keys clean
    configurable: true,
  });
}

export default module;
