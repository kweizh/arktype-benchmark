import { TraversalError } from "arktype"
import { compute } from "./src/engine.ts"

const raw = await new Promise<string>((resolve) => {
  let data = ""
  process.stdin.setEncoding("utf8")
  process.stdin.on("data", (chunk) => { data += chunk })
  process.stdin.on("end", () => { resolve(data) })
})

const input = JSON.parse(raw.trim()) as { op: unknown; a: unknown; b: unknown }

try {
  const result = compute(input.op as never, input.a as never, input.b as never)
  process.stdout.write(`OK ${result}\n`)
} catch (err) {
  if (err instanceof TraversalError) {
    process.stdout.write(`ERR ${err.message}\n`)
  } else {
    throw err
  }
}

process.exit(0)
