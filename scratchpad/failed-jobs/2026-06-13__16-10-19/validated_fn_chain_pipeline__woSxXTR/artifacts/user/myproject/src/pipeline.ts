import { type } from "arktype";

export const applyTax = type.fn("number", "number?", ":", "number")((amount, taxRate = 0.1) => {
    return amount + (amount * taxRate);
});

export const formatInvoice = type.fn("number[]", "number?", ":", { total: "number", count: "number" })((amounts, discount = 0) => {
    const total = amounts.reduce((sum, a) => sum + a, 0);
    return {
        total: total * (1 - discount),
        count: amounts.length
    };
});
