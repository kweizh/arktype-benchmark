import { type } from "arktype"

/**
 * Matches ISO-8601 date-time strings that carry **explicit** timezone info:
 *   - UTC suffix:          Z  (or lowercase z)
 *   - Numeric offset:      ±HH:MM  (e.g. +05:00, -08:00)
 *
 * The regex intentionally excludes "local" date-times (no tz suffix) so that
 * callers can never accidentally produce a Date whose UTC value depends on the
 * runtime's local timezone.
 *
 * Pattern breakdown:
 *   ^\d{4}            – four-digit year
 *   -(0[1-9]|1[0-2]) – month (01–12)
 *   -([12]\d|0[1-9]|3[01]) – day (01–31)
 *   T                 – date/time separator
 *   ([01]\d|2[0-3])   – hours (00–23)
 *   :[0-5]\d          – minutes (00–59)
 *   (:[0-5]\d         – seconds (optional)
 *     (\.\d+)?        –   fractional seconds (optional)
 *   )?
 *   (Z|[+-][01]\d:[0-5]\d) – REQUIRED timezone: Z or ±HH:MM
 *   $
 */
const ISO_8601_WITH_TZ =
	/^\d{4}-(0[1-9]|1[0-2])-([12]\d|0[1-9]|3[01])T([01]\d|2[0-3]):[0-5]\d(:[0-5]\d(\.\d+)?)?(Z|[+-]([01]\d|2[0-3]):[0-5]\d)$/i

/**
 * ArkType morph that:
 *  1. Asserts the input is a `string`
 *  2. Narrows it to strings matching ISO-8601 **with** an explicit timezone
 *  3. Morphs the validated string into a `Date`
 */
const isoDateWithTz = type("string").narrow(
	(s, ctx) =>
		ISO_8601_WITH_TZ.test(s) ||
		ctx.reject({
			expected: "an ISO-8601 date-time string with explicit timezone (Z or ±HH:MM)",
			actual: JSON.stringify(s),
		})
).pipe(s => new Date(s))

/**
 * Parse an ISO-8601 date-time string that includes explicit timezone info
 * (`Z` or `±HH:MM`) into a JavaScript `Date`.
 *
 * Throws an `ArkError` for any input that is not a string, does not match
 * ISO-8601, or omits the timezone offset.
 *
 * @example
 * parseIsoDate("2024-01-15T10:30:00Z")        // → Date (UTC)
 * parseIsoDate("2024-01-15T10:30:00+05:00")   // → Date (offset preserved)
 * parseIsoDate("2024-01-15T10:30:00")          // throws – no timezone
 * parseIsoDate("not-a-date")                   // throws
 */
export const parseIsoDate = (input: unknown): Date => isoDateWithTz.assert(input)
