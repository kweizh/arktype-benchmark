import { type } from "arktype"

// add: (a: number, b: number) => number
export const add = type.fn("number", "number", ":", "number")(
  (a, b) => a + b
)

// subtract: (a: number, b: number) => number
export const subtract = type.fn("number", "number", ":", "number")(
  (a, b) => a - b
)

// multiply: (a: number, b: number) => number
export const multiply = type.fn("number", "number", ":", "number")(
  (a, b) => a * b
)

// divide: divisor must be non-zero (either strictly positive or strictly negative)
export const divide = type.fn("number", "number > 0 | number < 0", ":", "number")(
  (a, b) => a / b
)

// modulo: divisor must be a non-zero integer
// "number % 1" constrains to integers; the union with positive/negative excludes zero
export const modulo = type.fn(
  "number",
  "(number % 1 > 0) | (number % 1 < 0)",
  ":",
  "number"
)(
  (a, b) => a % b
)

// compute dispatcher: op is constrained to the literal union of operation names
export const compute = type.fn(
  "'add' | 'subtract' | 'multiply' | 'divide' | 'modulo'",
  "number",
  "number",
  ":",
  "number"
)(
  (op, a, b) => {
    switch (op) {
      case "add":      return add(a, b)
      case "subtract": return subtract(a, b)
      case "multiply": return multiply(a, b)
      case "divide":   return divide(a, b)
      case "modulo":   return modulo(a, b)
    }
  }
)
