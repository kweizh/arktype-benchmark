import { scope, type Type } from "arktype";
import { jsonSchemaToType } from "@ark/json-schema";
import type { JsonSchema } from "@ark/schema";

// Define the schema using scope() to support cyclic/recursive types (Comment → replies → Comment[])
const $ = scope({
  Comment: {
    id: "string.uuid",
    body: "string > 0",
    "replies?": "Comment[]",
  },
  Post: {
    title: "1 <= string <= 120",
    tags: "1 <= string[] <= 10",
    comments: "Comment[]",
  },
  User: {
    id: "string.uuid",
    email: "string.email",
    username: "string.alphanumeric & 3 <= string <= 20",
    score: ["string.numeric.parse", "=>", (s: string) => Number(s)],
    address: {
      street: "string",
      city: "string",
      zip: /^\d{5}(-\d{4})?$/,
    },
    posts: "Post[]",
  },
});

const module = $.export();

export const userSchema: Type = module.User as Type;

/**
 * Export the User schema as a JSON Schema document.
 * Uses a morph fallback that returns the input schema (the string type),
 * so the exported JSON Schema validates the same input shape as the original.
 * Also disables $refs to avoid cycles in the output (we inline $defs ourselves).
 */
export function exportUserJsonSchema(): object {
  const jsonSchema = userSchema.toJsonSchema({
    dialect: "https://json-schema.org/draft/2020-12/schema",
    useRefs: false,
    fallback: {
      morph: (ctx) => ctx.base,
    },
  });
  return jsonSchema;
}

/**
 * Resolve $ref references in a JSON Schema document by inlining $defs.
 * This is needed because @ark/json-schema@0.0.4 does not support $ref/$defs.
 */
function resolveRefs(schema: any): any {
  if (typeof schema !== "object" || schema === null) {
    return schema;
  }

  if (Array.isArray(schema)) {
    return schema.map(resolveRefs);
  }

  const resolved: any = {};
  const defs = schema.$defs as Record<string, any> | undefined;

  for (const [key, value] of Object.entries(schema)) {
    if (key === "$defs") {
      // Skip $defs — they'll be inlined
      continue;
    }
    if (key === "$ref" && defs && typeof value === "string" && value.startsWith("#/$defs/")) {
      const defName = value.slice("#/$defs/".length);
      const defSchema = defs[defName];
      if (defSchema) {
        // Recursively resolve the referenced definition
        const resolvedDef = resolveRefs(defSchema);
        // Also merge any other top-level keys (except $ref and $defs) into the result
        // But for $ref, we replace the entire schema with the resolved def
        Object.assign(resolved, resolvedDef);
        continue;
      }
    }
    resolved[key] = resolveRefs(value);
  }

  return resolved;
}

/**
 * Build a round-tripped ArkType schema from the exported JSON Schema.
 * Resolves $ref/$defs inline before passing to jsonSchemaToType.
 */
export function buildRoundTrippedSchema(): Type {
  const jsonSchema = exportUserJsonSchema();
  const resolved = resolveRefs(jsonSchema);
  const rt = jsonSchemaToType(resolved);
  return rt as Type;
}

export const roundTrippedUserSchema: Type = buildRoundTrippedSchema();
