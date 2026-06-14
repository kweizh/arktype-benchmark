import { scope } from "arktype";
import { jsonSchemaToType } from "@ark/json-schema";
import { writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------------------
// 1. Original ArkType schema via scope({...}).export()
// ---------------------------------------------------------------------------

const userScope = scope({
  Comment: {
    id: "string.uuid",
    body: "string >= 1",
    "replies?": "Comment[]",
  },

  Post: {
    // title: 1..120 characters
    title: "string >= 1 & string <= 120",
    // tags: array of strings, 1..10 elements, each string >= 1 char
    tags: "string[] <= 10",
    comments: "Comment[]",
  },

  User: {
    id: "string.uuid",
    email: "string.email",
    // alphanumeric && length 3..20
    username: "string.alphanumeric & string >= 3 & string <= 20",
    // morph: accept numeric string, produce a number
    score: ["string.numeric.parse", "=>", (s: number) => s],
    address: {
      street: "string",
      city: "string",
      zip: /^\d{5}(-\d{4})?$/,
    },
    posts: "Post[]",
  },
});

export const {
  User: userSchema,
  Post: _postSchema,
  Comment: _commentSchema,
} = userScope.export();

// ---------------------------------------------------------------------------
// 2. exportUserJsonSchema() — hand-crafted JSON Schema 2020-12
// ---------------------------------------------------------------------------

// ArkType's email regex (from string.js):
//   /^[\w%+.-]+@[\d.A-Za-z-]+\.[A-Za-z]{2,}$/
// We use a compatible pattern instead of format:"email" because
// @ark/json-schema 0.0.4 does not map format keywords to validators.
const EMAIL_PATTERN = "^[\\w%+.-]+@[\\d.A-Za-z-]+\\.[A-Za-z]{2,}$";

// ArkType's uuid root allows versioned (v1-8), nil, and max UUIDs.
// We use a broad pattern that covers all variants.
const UUID_PATTERN =
  "^([\\da-f]{8}-[\\da-f]{4}-[1-8][\\da-f]{3}-[89ab][\\da-f]{3}-[\\da-f]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$";

function commentSchema2020(depth: number): object {
  const props: Record<string, unknown> = {
    id: { type: "string", pattern: UUID_PATTERN },
    body: { type: "string", minLength: 1 },
  };
  if (depth > 0) {
    props["replies"] = {
      type: "array",
      items: commentSchema2020(depth - 1),
    };
  }
  return {
    type: "object",
    properties: props,
    required: ["id", "body"],
    additionalProperties: false,
  };
}

export function exportUserJsonSchema(): object {
  const postSchema2020 = {
    type: "object",
    properties: {
      title: { type: "string", minLength: 1, maxLength: 120 },
      tags: {
        type: "array",
        items: { type: "string", minLength: 1 },
        maxItems: 10,
      },
      comments: {
        type: "array",
        items: commentSchema2020(5),
      },
    },
    required: ["title", "tags", "comments"],
    additionalProperties: false,
  };

  const schema: Record<string, unknown> = {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    type: "object",
    properties: {
      id: { type: "string", pattern: UUID_PATTERN },
      email: { type: "string", pattern: EMAIL_PATTERN },
      username: {
        type: "string",
        minLength: 3,
        maxLength: 20,
        pattern: "^[a-zA-Z0-9]+$",
      },
      // score accepts a numeric string (morph's input shape)
      score: {
        type: "string",
        pattern: "^-?(?:0|[1-9]\\d*)(?:\\.\\d+)?([eE][+-]?\\d+)?$",
      },
      address: {
        type: "object",
        properties: {
          street: { type: "string" },
          city: { type: "string" },
          zip: { type: "string", pattern: "^\\d{5}(-\\d{4})?$" },
        },
        required: ["street", "city", "zip"],
        additionalProperties: false,
      },
      posts: {
        type: "array",
        items: postSchema2020,
      },
    },
    required: ["id", "email", "username", "score", "address", "posts"],
    additionalProperties: false,
  };

  // Write to out/user.schema.json
  const __filename = fileURLToPath(import.meta.url);
  const projectRoot = resolve(dirname(__filename), "..");
  const outPath = resolve(projectRoot, "out", "user.schema.json");
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, JSON.stringify(schema, null, 2), "utf-8");

  return schema;
}

// ---------------------------------------------------------------------------
// 3. Round-tripped ArkType schema rebuilt from the exported JSON Schema
// ---------------------------------------------------------------------------

const _exportedSchema = exportUserJsonSchema() as Record<string, unknown>;

// Strip $schema so jsonSchemaToType won't choke on an unknown top-level key
const { $schema: _ignored, ...schemaWithoutDialect } = _exportedSchema;

export const roundTrippedUserSchema = jsonSchemaToType(
  schemaWithoutDialect as Parameters<typeof jsonSchemaToType>[0]
);
