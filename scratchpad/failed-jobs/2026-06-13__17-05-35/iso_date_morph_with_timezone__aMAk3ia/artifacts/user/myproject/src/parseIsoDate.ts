import { type } from "arktype";

/**
 * ISO-8601 date-time string that MUST include an explicit timezone offset.
 *
 * Accepts:
 *   - "Z" (UTC) suffix:  2024-01-15T10:30:00Z
 *   - Numeric offset:    2024-01-15T10:30:00+05:00 / 2024-01-15T10:30:00-05:00
 *
 * Rejects:
 *   - Strings without a timezone (e.g. "2024-01-15T10:30:00")
 *   - Non-date strings
 *
 * The regex breakdown:
 *   ^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?   → date + time + optional fractional seconds
 *   (Z|[+-]\d{2}:\d{2})$                              → mandatory explicit timezone
 */
const isoWithTimezonePattern =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;

const IsoDateMorph = type("string").pipe((s, ctx) => {
  if (!isoWithTimezonePattern.test(s)) {
    return ctx.error(
      "an ISO-8601 date-time string with explicit timezone (e.g. 2024-01-15T10:30:00Z or 2024-01-15T10:30:00+05:00)"
    );
  }

  const date = new Date(s);
  if (Number.isNaN(date.valueOf())) {
    return ctx.error("a valid date");
  }

  return date;
});

/**
 * Parses an ISO-8601 date-time string into a JavaScript `Date`.
 *
 * The input MUST include an explicit timezone (`Z` or `±HH:MM`).
 * Strings without a timezone (e.g. "2024-01-15T10:30:00") are rejected.
 *
 * @throws {ArkErrors} if the input is not a valid ISO-8601 date-time string
 *                     with an explicit timezone.
 */
export function parseIsoDate(input: unknown): Date {
  return IsoDateMorph.assert(input);
}
