import { type } from "arktype";

/**
 * ArkType morph that validates an ISO-8601 date string requiring
 * explicit timezone information (Z or ±HH:MM) and converts it to a Date.
 *
 * - Accepts: "2024-01-15T10:30:00Z", "2024-01-15T10:30:00+05:00"
 * - Rejects: "2024-01-15T10:30:00" (no timezone), "not-a-date"
 */
const IsoDateWithTimezone = type("string.date.iso")
  .narrow((s) => /[Zz]|[+-]\d{2}:\d{2}$/.test(s))
  .pipe((s) => new Date(s));

/**
 * Parses an unknown value as an ISO-8601 date string with explicit timezone,
 * returning a Date instance.
 *
 * @throws Throws on rejection (invalid format, missing timezone, or non-string input)
 */
export function parseIsoDate(input: unknown): Date {
  return IsoDateWithTimezone.assert(input);
}