import { fn } from "arktype";

export const add = fn("number", "number", ":", "number")(
  (a: number, b: number): number => a + b,
);

export const subtract = fn("number", "number", ":", "number")(
  (a: number, b: number): number => a - b,
);

export const multiply = fn("number", "number", ":", "number")(
  (a: number, b: number): number => a * b,
);

// divide must reject any divisor equal to 0
// "number < 0 | number > 0" means any number except 0
export const divide = fn("number", "number < 0 | number > 0", ":", "number")(
  (a: number, b: number): number => a / b,
);

// modulo must reject any divisor that is not a non-zero integer
// number % 1 ensures integer; (number < 0 | number > 0) ensures non-zero
export const modulo = fn("number", "number % 1 & (number < 0 | number > 0)", ":", "number")(
  (a: number, b: number): number => a % b,
);

export const operations = {
  add,
  subtract,
  multiply,
  divide,
  modulo,
} as const;

export type OpName = keyof typeof operations;
