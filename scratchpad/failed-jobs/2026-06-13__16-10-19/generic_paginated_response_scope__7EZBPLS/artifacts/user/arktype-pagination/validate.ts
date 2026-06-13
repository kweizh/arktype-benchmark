import { scope } from "arktype";
import * as fs from "fs";

const myScope = scope({
    "Page<T>": {
        items: "T[]",
        total: "number",
        cursor: "string | null"
    },
    User: {
        id: "string",
        name: "string"
    },
    Product: {
        id: "string",
        price: "number"
    },
    PageOfUser: "Page<User>",
    PageOfProduct: "Page<Product>"
});

const types = myScope.export();

const schemaName = process.argv[2];
if (!schemaName || !(schemaName in types)) {
    console.error(`Invalid schema name: ${schemaName}`);
    process.exit(1);
}

const schema = (types as any)[schemaName];

const input = fs.readFileSync(0, "utf-8");
let data;
try {
    data = JSON.parse(input);
} catch (e) {
    console.error("Invalid JSON");
    process.exit(1);
}

try {
    schema.assert(data);
    console.log("OK");
    process.exit(0);
} catch (e: any) {
    console.error(e.message);
    process.exit(1);
}
