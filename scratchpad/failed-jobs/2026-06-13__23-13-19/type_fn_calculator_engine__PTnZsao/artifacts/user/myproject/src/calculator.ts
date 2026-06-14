import { type } from "arktype";

export const add = type.fn("number", "number", ":", "number")(
  (a, b) => a + b
);

export const subtract = type.fn("number", "number", ":", "number")(
  (a, b) => a - b
);

export const multiply = type.fn("number", "number", ":", "number")(
  (a, b) => a * b
);

export const divide = type.fn("number", "number > 0 | number < 0", ":", "number")(
  (a, b) => a / b
);

export const modulo = type.fn(
  "number",
  "number.integer & (number > 0 | number < 0)",
  ":",
  "number"
)((a, b) => a % b);

export const compute = type.fn(
  "'add' | 'subtract' | 'multiply' | 'divide' | 'modulo'",
  "number",
  "number",
  ":",
  "number"
)((op, a, b) => {
  switch (op) {
    case "add":
      return add(a, b);
    case "subtract":
      return subtract(a, b);
    case "multiply":
      return multiply(a, b);
    case "divide":
      return divide(a, b);
    case "modulo":
      return modulo(a, b);
  }
});
