import * as readline from "readline";
import { compute } from "./src/calculator.js";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

rl.on("line", (line) => {
  const trimmed = line.trim();
  if (!trimmed) {
    rl.close();
    return;
  }
  try {
    const data = JSON.parse(trimmed);
    try {
      const result = compute(data.op, data.a, data.b);
      console.log(`OK ${result}`);
    } catch (e: any) {
      console.log(`ERR ${e.message}`);
    }
  } catch (err: any) {
    console.log(`ERR ${err.message}`);
  }
  rl.close();
});
