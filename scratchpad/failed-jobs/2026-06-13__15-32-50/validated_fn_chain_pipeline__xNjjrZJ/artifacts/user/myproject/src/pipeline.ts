import { type } from "arktype";

/**
 * Applies a tax rate to a price.
 * Defaults to a tax rate of 0.1 (10%).
 */
export const applyTax = type.fn(
    "number",
    ["number", "=", 0.1],
    ":",
    "number"
)((price, rate) => {
    return price + price * rate;
});

/**
 * Formats an invoice by calculating the total and count.
 * Accepts an array of prices and an optional discount/multiplier (defaults to 1).
 */
export const formatInvoice = type.fn(
    "number[]",
    ["number", "=", 1],
    ":",
    { total: "number", count: "number" }
)((items, multiplier) => {
    const sum = items.reduce((a, b) => a + b, 0);
    return {
        total: sum * multiplier,
        count: items.length
    };
});
