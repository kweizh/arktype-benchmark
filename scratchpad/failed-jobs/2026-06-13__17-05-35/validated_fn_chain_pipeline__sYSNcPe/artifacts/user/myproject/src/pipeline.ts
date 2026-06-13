import { type } from "arktype";

export const applyTax = type.fn("number", "number=0.1", ":", "number")(
  (amount: number, rate: number = 0.1): number => {
    return amount + amount * rate;
  }
);

export const formatInvoice = type.fn(
  "number[]",
  "number=1",
  ":",
  { total: "number", count: "number" }
)(
  (items: number[], rate: number = 1): { total: number; count: number } => {
    const total = items.reduce((sum, n) => sum + n, 0) * rate;
    return { total, count: items.length };
  }
);
