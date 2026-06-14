import { type, ArkErrors } from "arktype";
import { readFileSync } from "node:fs";

const ignoreSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email"
});

const rejectSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "reject"
});

const deleteSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "delete"
});

const schemas: Record<string, ReturnType<typeof type.raw>> = {
    ignore: ignoreSchema,
    reject: rejectSchema,
    delete: deleteSchema
};

try {
    const input = JSON.parse(readFileSync(0, "utf-8"));
    const mode: string = input.mode;
    const payload: unknown = input.payload;

    const schema = schemas[mode];
    if (!schema) {
        console.log(`INVALID: unknown mode "${mode}"`);
        process.exit(0);
    }

    const result = schema(payload);
    if (result instanceof ArkErrors) {
        console.log(`INVALID: ${result.summary}`);
        process.exit(0);
    }

    console.log("VALID");
    console.log(JSON.stringify(result));
} catch (e) {
    console.log(`INVALID: ${e instanceof Error ? e.message : String(e)}`);
    process.exit(0);
}