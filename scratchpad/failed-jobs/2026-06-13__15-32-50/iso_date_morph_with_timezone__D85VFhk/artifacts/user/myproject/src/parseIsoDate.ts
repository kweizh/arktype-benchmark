import { type } from "arktype"

// Regular expression to match ISO-8601 strings with explicit timezone (Z or ±HH:MM)
const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/

// ArkType morph to parse ISO-8601 date string to a Date instance
const isoDateWithTimezone = type("string").pipe((s, ctx) => {
  if (!isoDateRegex.test(s)) {
    return ctx.error("an ISO-8601 date string with an explicit timezone (Z or ±HH:MM)")
  }
  const d = new Date(s)
  if (isNaN(d.getTime())) {
    return ctx.error("a valid ISO-8601 date string")
  }
  return d
})

/**
 * Parses an ISO-8601 date string with explicit timezone into a JavaScript Date.
 * Rejects strings without explicit timezone information (Z or ±HH:MM) or invalid dates.
 * 
 * @param input The value to parse.
 * @returns A valid Date instance.
 * @throws An ArkError if validation or parsing fails.
 */
export function parseIsoDate(input: unknown): Date {
  return isoDateWithTimezone.assert(input)
}
