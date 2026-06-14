import { type } from "arktype";

// ── Shared logical shape ─────────────────────────────────────────────────────

const userShape = {
  id: "string.uuid",
  name: "string",
  email: "string.email",
} as const;

// ── Three schemas — differing only in the `+` (undeclared-key) setting ───────

/** Default: extra keys are silently preserved in the output. */
const ignoreSchema = type({
  ...userShape,
  "+": "ignore",
});

/** Strict: extra keys cause a validation error. */
const rejectSchema = type({
  ...userShape,
  "+": "reject",
});

/** Sanitising: extra keys are stripped from the validated output. */
const deleteSchema = type({
  ...userShape,
  "+": "delete",
});

// ── Dispatch map ─────────────────────────────────────────────────────────────

const schemas = {
  ignore: ignoreSchema,
  reject: rejectSchema,
  delete: deleteSchema,
} as const;

type Mode = keyof typeof schemas;

// ── Stdin reader ─────────────────────────────────────────────────────────────

function readStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    let buf = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      buf += chunk;
    });
    process.stdin.on("end", () => resolve(buf));
    process.stdin.on("error", reject);
  });
}

// ── Entry point ───────────────────────────────────────────────────────────────

const raw = await readStdin();

let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch {
  console.log("INVALID: input is not valid JSON");
  process.exit(0);
}

const input = parsed as { mode?: unknown; payload?: unknown };
const mode = input.mode;

if (
  typeof mode !== "string" ||
  !Object.prototype.hasOwnProperty.call(schemas, mode)
) {
  const allowed = Object.keys(schemas).join(" | ");
  console.log(
    `INVALID: unknown mode ${JSON.stringify(mode)} — expected one of: ${allowed}`
  );
  process.exit(0);
}

const schema = schemas[mode as Mode];
const result = schema(input.payload);

if (result instanceof type.errors) {
  // For undeclared-key rejections ArkType reports the offending key inside the
  // error summary; we surface it verbatim so the key name is always visible.
  console.log(`INVALID: ${result.summary}`);
} else {
  console.log("VALID");
  console.log(JSON.stringify(result));
}

process.exit(0);
