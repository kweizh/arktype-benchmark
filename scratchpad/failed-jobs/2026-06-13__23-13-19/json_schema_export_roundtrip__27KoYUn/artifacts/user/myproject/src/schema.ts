import { scope } from "arktype";
import { jsonSchemaToType } from "@ark/json-schema";
import * as fs from "fs";
import * as path from "path";

// 1. Define the original ArkType schema using scope({ ... }).export()
export const typesScope = scope({
  Comment: {
    id: "string.uuid",
    body: "string>=1",
    "replies?": "Comment[]"
  },
  Post: {
    title: "1<=string<=120",
    tags: "1<=string[]<=10",
    comments: "Comment[]"
  },
  User: {
    id: "string.uuid",
    email: "string.email",
    username: "string.alphanumeric & 3<=string<=20",
    score: ["string.numeric", "=>", (s: string) => Number(s)],
    address: {
      street: "string",
      city: "string",
      zip: /^\d{5}(-\d{4})?$/
    },
    posts: "Post[]"
  }
});

export const { User: userSchema } = typesScope.export();

// 2. Export JSON Schema functionality
export function exportUserJsonSchema(): object {
  const schema = userSchema.toJsonSchema({
    fallback: (node: any) => node.base
  });

  const outDir = "/home/user/myproject/out";
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  fs.writeFileSync(
    path.join(outDir, "user.schema.json"),
    JSON.stringify(schema, null, 2),
    "utf-8"
  );

  return schema;
}

// Helper to dereference cyclic JSON Schema for @ark/json-schema
function dereference(schema: any, defs: any, currentPath: string[] = [], maxDepth = 5): any {
  if (schema === null || typeof schema !== "object") {
    return schema;
  }

  if (Array.isArray(schema)) {
    return schema.map(item => dereference(item, defs, currentPath, maxDepth));
  }

  if (schema.$ref) {
    const refKey = schema.$ref.replace("#/$defs/", "");
    const refSchema = defs[refKey];
    if (!refSchema) {
      throw new Error(`Unresolved ref: ${schema.$ref}`);
    }

    const occurrences = currentPath.filter(x => x === refKey).length;
    if (occurrences >= maxDepth) {
      const resolved = { ...refSchema };
      if (resolved.properties) {
        const props = { ...resolved.properties };
        delete props.replies;
        resolved.properties = props;
      }
      if (resolved.required) {
        resolved.required = resolved.required.filter((k: string) => k !== "replies");
      }
      return dereference(resolved, defs, [...currentPath, refKey], maxDepth);
    }

    return dereference(refSchema, defs, [...currentPath, refKey], maxDepth);
  }

  const result: any = {};
  for (const key of Object.keys(schema)) {
    if (key === "$defs") continue;
    result[key] = dereference(schema[key], defs, [...currentPath], maxDepth);
  }
  return result;
}

// 3. Build the round-tripped ArkType schema from the exported JSON Schema
const schemaObj = userSchema.toJsonSchema({
  fallback: (node: any) => node.base
});
const derefSchema = dereference(schemaObj, schemaObj.$defs);
export const roundTrippedUserSchema = jsonSchemaToType(derefSchema);
