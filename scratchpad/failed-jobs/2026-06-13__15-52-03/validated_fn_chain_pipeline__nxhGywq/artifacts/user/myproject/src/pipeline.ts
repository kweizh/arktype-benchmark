import { type, TraversalError } from "arktype";

// Re-export TraversalError so consumers can use it for instanceof checks
export { TraversalError };

/**
 * applyTax(amount, rate = 0.1) => amount * (1 + rate)
 *
 * Parameters:
 *   [0] amount – number
 *   [1] rate   – number (optional, defaults to 0.1)
 *
 * Returns: number
 */
export const applyTax = type.fn(
  "number",
  "number = 0.1",
  ":",
  "number"
)(
  (amount: number, rate: number): number => {
    // Round to 10 significant decimal places to avoid IEEE-754 drift
    return parseFloat((amount * (1 + rate)).toPrecision(15));
  }
);

/**
 * formatInvoice(items, discount = 0) => { total: sum * (1 - discount), count }
 *
 * Parameters:
 *   [0] items    – number[]
 *   [1] discount – number (optional, defaults to 0)
 *
 * Returns: { total: number; count: number }
 */
export const formatInvoice = type.fn(
  "number[]",
  "number = 0",
  ":",
  { total: "number", count: "number" }
)(
  (items: number[], discount: number): { total: number; count: number } => {
    const sum = items.reduce((acc, n) => acc + n, 0);
    return {
      total: sum * (1 - discount),
      count: items.length,
    };
  }
);
