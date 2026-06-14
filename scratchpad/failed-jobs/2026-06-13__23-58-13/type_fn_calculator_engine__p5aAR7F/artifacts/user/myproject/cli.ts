import { type } from "arktype";
import * as fs from "fs";

const add = type.fn("number", "number", ":", "number")((a, b) => a + b);
const subtract = type.fn("number", "number", ":", "number")((a, b) => a - b);
const multiply = type.fn("number", "number", ":", "number")((a, b) => a * b);
const divide = type.fn("number", "number > 0 | number < 0", ":", "number")((a, b) => a / b);
const modulo = type.fn("number", "(number % 1) & (number > 0 | number < 0)", ":", "number")((a, b) => a % b);

const compute = type.fn(
    "'add' | 'subtract' | 'multiply' | 'divide' | 'modulo'",
    "number",
    "number",
    ":",
    "number"
)((op, a, b) => {
    switch (op) {
        case "add": return add(a, b);
        case "subtract": return subtract(a, b);
        case "multiply": return multiply(a, b);
        case "divide": return divide(a, b);
        case "modulo": return modulo(a, b);
        default: throw new Error("Unreachable");
    }
});

function main() {
    let input = "";
    try {
        input = fs.readFileSync(0, "utf-8").trim();
    } catch {
        return;
    }
    
    if (!input) return;
    
    let parsed;
    try {
        parsed = JSON.parse(input);
    } catch {
        return;
    }

    try {
        const result = compute(parsed.op, parsed.a, parsed.b);
        console.log(`OK ${result}`);
    } catch (e: any) {
        console.log(`ERR ${e.message}`);
    }
}

main();
