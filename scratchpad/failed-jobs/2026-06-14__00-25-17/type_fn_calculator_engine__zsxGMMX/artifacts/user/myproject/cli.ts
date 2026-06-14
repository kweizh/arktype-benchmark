import { fn, TraversalError } from "arktype"
import { createInterface } from "node:readline"

const add = fn("number", "number", ":", "number")((a, b) => a + b)
const subtract = fn("number", "number", ":", "number")((a, b) => a - b)
const multiply = fn("number", "number", ":", "number")((a, b) => a * b)
const divide = fn("number", "(number>0 | number<0)", ":", "number")((a, b) => a / b)
const modulo = fn("number", "(number.integer>0 | number.integer<0)", ":", "number")((a, b) => a % b)

const compute = fn(
  "'add' | 'subtract' | 'multiply' | 'divide' | 'modulo'",
  "number",
  "number",
  ":",
  "number"
)((op, a, b) => {
  switch (op) {
    case "add": return add(a, b)
    case "subtract": return subtract(a, b)
    case "multiply": return multiply(a, b)
    case "divide": return divide(a, b)
    case "modulo": return modulo(a, b)
  }
})

const rl = createInterface({ input: process.stdin })
rl.on("line", (line) => {
  const { op, a, b } = JSON.parse(line)
  try {
    const result = compute(op, a, b)
    console.log(`OK ${result}`)
  } catch (e) {
    if (e instanceof TraversalError) {
      console.log(`ERR ${e.message}`)
    } else {
      throw e
    }
  }
  rl.close()
})