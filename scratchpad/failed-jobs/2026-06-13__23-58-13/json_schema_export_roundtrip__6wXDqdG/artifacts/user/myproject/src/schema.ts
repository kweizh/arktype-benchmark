import * as ark from "arktype";
import * as js from "@ark/json-schema";
import * as fs from "fs";

export const myScope = ark.scope({
  Comment: {
    id: "string.uuid",
    body: "string > 0",
    "replies?": "Comment[]"
  },
  Post: {
    title: "string >= 1 <= 120",
    tags: "(string >= 1 <= 10)[] >= 1 <= 10",
    comments: "Comment[]"
  },
  User: {
    id: "string.uuid",
    email: "string.email",
    username: ark.type("string.alphanumeric").and("string >= 3 <= 20"),
    score: ark.type("string.numeric").pipe((s) => parseFloat(s)),
    address: {
      street: "string",
      city: "string",
      zip: /^\d{5}(-\d{4})?$/
    },
    posts: "Post[]"
  }
});

export const userSchema = myScope.export().User;

export function exportUserJsonSchema() {
  const schema = userSchema.toJsonSchema({
    fallback: {
      morph: (ctx) => ctx.base,
      predicate: (ctx) => ctx.base
    }
  });
  
  if (!fs.existsSync("/home/user/myproject/out")) {
    fs.mkdirSync("/home/user/myproject/out", { recursive: true });
  }
  fs.writeFileSync("/home/user/myproject/out/user.schema.json", JSON.stringify(schema, null, 2));
  
  return schema;
}

function unroll(schema: any, defs: any, depth: number): any {
  if (depth === 0) return { type: ["string", "number", "object", "array", "boolean", "null"] };
  if (!schema) return schema;
  if (schema.$ref) {
    const name = schema.$ref.split("/").pop();
    if (!defs[name]) return {}; // fallback
    return unroll(defs[name], defs, depth - 1);
  }
  if (schema.type === "object" && schema.properties) {
    const props: any = {};
    for (const k of Object.keys(schema.properties)) {
      props[k] = unroll(schema.properties[k], defs, depth);
    }
    const res = { ...schema, properties: props };
    if (schema.patternProperties) {
      const pp: any = {};
      for (const k of Object.keys(schema.patternProperties)) {
        pp[k] = unroll(schema.patternProperties[k], defs, depth);
      }
      res.patternProperties = pp;
    }
    return res;
  }
  if (schema.type === "array" && schema.items) {
    return { ...schema, items: unroll(schema.items, defs, depth) };
  }
  if (schema.anyOf) {
    return { ...schema, anyOf: schema.anyOf.map((s: any) => unroll(s, defs, depth)) };
  }
  if (schema.allOf) {
    return { ...schema, allOf: schema.allOf.map((s: any) => unroll(s, defs, depth)) };
  }
  if (schema.oneOf) {
    return { ...schema, oneOf: schema.oneOf.map((s: any) => unroll(s, defs, depth)) };
  }
  return schema;
}

const rawSchema = exportUserJsonSchema();
const unrolled = unroll(rawSchema, rawSchema.$defs, 20);
delete unrolled.$defs;
delete unrolled.$schema;

export const roundTrippedUserSchema = js.jsonSchemaToType(unrolled);
