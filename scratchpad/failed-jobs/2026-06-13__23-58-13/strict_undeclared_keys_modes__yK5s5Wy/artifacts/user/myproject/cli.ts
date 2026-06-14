import { type } from "arktype";
import { readFileSync } from "fs";

const ignoreSchema = type({
    id: "string.uuid",
    name: "string",
    email: "string.email",
    "+": "ignore"
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

function main() {
    try {
        const input = readFileSync(0, "utf-8");
        const data = JSON.parse(input);
        
        const mode = data.mode;
        const payload = data.payload;
        
        let schema;
        if (mode === "ignore") {
            schema = ignoreSchema;
        } else if (mode === "reject") {
            schema = rejectSchema;
        } else if (mode === "delete") {
            schema = deleteSchema;
        } else {
            console.log(`INVALID: Unknown mode '${mode}'`);
            process.exit(0);
        }
        
        const result = schema(payload);
        
        if (result instanceof type.errors) {
            console.log(`INVALID: ${result.toString().replace(/\n/g, '; ')}`);
        } else {
            console.log("VALID");
            console.log(JSON.stringify(result));
        }
    } catch (e: any) {
        const msg = e && e.message ? e.message : String(e);
        console.log(`INVALID: ${msg.replace(/\n/g, '; ')}`);
    }
}

main();
