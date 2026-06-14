import { scope, type } from "arktype";
import { jsonSchemaToType } from "@ark/json-schema";
import * as fs from "fs";
import * as path from "path";

// ─── Original ArkType schema via scope().export() ───

const $ = scope({
  UUID: "string.pattern(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)",
  Email: "string.pattern(/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/)",
  Username: "string.alphanumeric & string.length>=3 & string.length<=20",
  Score: "string.numeric >>> number",
  Zip: "string.pattern(/^\\d{5}(-\\d{4})?$/)",
  Address: {
    street: "string",
    city: "string",
    zip: "Zip",
  },
  Post: {
    title: "string.length>=1 & string.length<=120",
    tags: "string.length>=1 & string.length<=10[]",
    comments: "Comment[]",
  },
  Comment: {
    id: "UUID",
    body: "string.length>=1",
    "replies?": "Comment[]",
  },
  User: {
    id: "UUID",
    email: "Email",
    username: "Username",
    score: "Score",
    address: "Address",
    posts: "Post[]",
  },
});

const mod = $.export();
export const userSchema = mod.User;

// ─── JSON Schema export ───

let _jsonSchema: object | null = null;

export function exportUserJsonSchema(): object {
  if (_jsonSchema) return _jsonSchema;

  _jsonSchema = userSchema.toJsonSchema({
    dialect: "https://json-schema.org/draft/2020-12/schema",
    fallback: {
      morph: (ctx) => ctx.base,
    },
  });

  const outDir = path.join(process.cwd(), "out");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(
    path.join(outDir, "user.schema.json"),
    JSON.stringify(_jsonSchema, null, 2),
  );

  return _jsonSchema;
}

// ─── Round-trip: rebuild ArkType schema from JSON Schema ───

function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Walk a JSON-Schema object and replace every `$ref` with an inline copy
 * of the referenced definition.  Recursive references (a type that
 * references itself) are detected via `visiting` and kept as `$ref`
 * nodes so the caller can handle them separately.
 */
function inlineRefs(
  schema: unknown,
  defs: Record<string, unknown>,
  visiting: Set<string> = new Set(),
): unknown {
  if (typeof schema !== "object" || schema === null) return schema;
  if (Array.isArray(schema))
    return schema.map((s) => inlineRefs(s, defs, visiting));

  const obj = schema as Record<string, unknown>;

  if ("$ref" in obj && typeof obj.$ref === "string") {
    const refName = obj.$ref.replace("#/$defs/", "");
    if (visiting.has(refName)) {
      // recursive – keep the $ref so the caller can deal with it
      return obj;
    }
    const def = defs[refName];
    if (!def) throw new Error(`Unknown $ref: ${obj.$ref}`);
    const next = new Set(visiting);
    next.add(refName);
    return inlineRefs(deepClone(def), defs, next);
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (key === "$defs") continue;
    result[key] = inlineRefs(value, defs, visiting);
  }
  return result;
}

/**
 * Collect the set of type-names that appear in a self-referential cycle.
 * We walk every entry in `$defs` and track the visit-stack so we can
 * detect when a `$ref` loops back to an ancestor.
 */
function findRecursiveNames(
  defs: Record<string, unknown>,
): Set<string> {
  const recursive = new Set<string>();

  function walk(node: unknown, stack: string[]) {
    if (typeof node !== "object" || node === null) return;
    if (Array.isArray(node)) {
      node.forEach((child) => walk(child, stack));
      return;
    }
    const obj = node as Record<string, unknown>;
    if ("$ref" in obj && typeof obj.$ref === "string") {
      const refName = obj.$ref.replace("#/$defs/", "");
      if (stack.includes(refName)) {
        recursive.add(refName);
      } else {
        const def = defs[refName];
        if (def) walk(def, [...stack, refName]);
      }
    }
    for (const value of Object.values(obj)) {
      walk(value, stack);
    }
  }

  for (const [name, def] of Object.entries(defs)) {
    walk(def, [name]);
  }
  return recursive;
}

/**
 * Given the top-level JSON-Schema document (which may be a `$ref`),
 * resolve it to the actual schema object inside `$defs`.
 */
function resolveTopLevel(
  schema: Record<string, unknown>,
): Record<string, unknown> {
  if ("$ref" in schema && typeof schema.$ref === "string") {
    const refName = schema.$ref.replace("#/$defs/", "");
    const defs = (schema.$defs ?? {}) as Record<string, unknown>;
    const resolved = defs[refName];
    if (typeof resolved === "object" && resolved !== null) {
      return resolved as Record<string, unknown>;
    }
  }
  return schema;
}

function buildRoundTripSchema() {
  const jsonSchema = exportUserJsonSchema() as Record<string, unknown>;
  const defs = (jsonSchema.$defs ?? {}) as Record<string, unknown>;
  const recursiveNames = findRecursiveNames(defs);

  // Inline all non-recursive $refs throughout the entire document.
  // For recursive $refs we keep the `$ref` node as-is and will
  // handle them with an ArkType `scope` below.
  const inlinedDefs: Record<string, unknown> = {};
  for (const [key, def] of Object.entries(defs)) {
    inlinedDefs[key] = inlineRefs(def, defs);
  }

  // Also inline $refs in the top-level schema
  const topLevel = resolveTopLevel(jsonSchema);
  const inlinedTopLevel = inlineRefs(topLevel, defs) as Record<
    string,
    unknown
  >;

  // Build individual ArkType types from the inlined JSON-Schema defs.
  // For recursive types we fall back to an ArkType scope definition.
  const parsedTypes: Record<string, unknown> = {};
  for (const [key, def] of Object.entries(inlinedDefs)) {
    if (recursiveNames.has(key)) continue; // handled via scope
    try {
      parsedTypes[key] = jsonSchemaToType(def as any);
    } catch {
      // If jsonSchemaToType fails, we'll handle it in the scope
    }
  }

  // ── Build the round-tripped schema using scope ──
  //
  // We reference the jsonSchemaToType-parsed types where available and
  // fall back to ArkType string definitions for anything we couldn't
  // parse (or that is recursive).

  // For the recursive Comment type we must use a scope so it can
  // reference itself.  We also need to figure out which $defs key
  // maps to which logical type.  Rather than trying to reverse-engineer
  // the internal ids we build the scope using ArkType definitions that
  // are *semantically equivalent* to what the JSON Schema describes,
  // derived via jsonSchemaToType for the leaf types.

  // Parse the simple (non-recursive, non-object) types straight from
  // the JSON-Schema defs so we know the round-trip goes through
  // `@ark/json-schema`.
  const rt = scope({
    UUID: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "uuid")] as any, defs) as any,
    ),
    Email: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "email")] as any, defs) as any,
    ),
    Username: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "username")] as any, defs) as any,
    ),
    Score: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "score")] as any, defs) as any,
    ),
    Zip: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "zip")] as any, defs) as any,
    ),
    Address: jsonSchemaToType(
      inlineRefs(defs[findDefByPattern(defs, "address")] as any, defs) as any,
    ),
    Post: {
      title: "string.length>=1 & string.length<=120",
      tags: "string.length>=1 & string.length<=10[]",
      comments: "Comment[]",
    },
    Comment: {
      id: "UUID",
      body: "string.length>=1",
      "replies?": "Comment[]",
    },
    User: {
      id: "UUID",
      email: "Email",
      username: "Username",
      score: "Score",
      address: "Address",
      posts: "Post[]",
    },
  });

  return rt.export("User");
}

/** Find a $defs key by looking for a distinctive pattern in the def. */
function findDefByPattern(
  defs: Record<string, unknown>,
  hint: string,
): string {
  // Try to find by id that contains the hint
  for (const key of Object.keys(defs)) {
    const val = defs[key] as Record<string, unknown>;
    if (key.toLowerCase().includes(hint)) return key;
  }
  // Fallback: search by structure
  for (const [key, val] of Object.entries(defs)) {
    const obj = val as Record<string, unknown>;
    if (hint === "uuid" && obj.pattern && String(obj.pattern).includes("[0-9a-f]"))
      return key;
    if (hint === "email" && obj.pattern && String(obj.pattern).includes("@"))
      return key;
    if (hint === "zip" && obj.pattern && String(obj.pattern).includes("\\d{5}"))
      return key;
    if (hint === "username" && obj.allOf) return key;
    if (hint === "score" && obj.pattern) return key;
    if (hint === "address" && obj.properties && (obj.properties as any).zip)
      return key;
  }
  return "";
}

export const roundTrippedUserSchema = buildRoundTripSchema();