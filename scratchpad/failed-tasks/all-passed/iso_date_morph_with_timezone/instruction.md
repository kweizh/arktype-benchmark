# ArkType: ISO-8601 Date Morph That Requires Explicit Timezone

## Goal
In the project at `/home/user/myproject`, build an ArkType (v2.2.0) morph that converts an ISO-8601 date string into a JavaScript `Date`, accepting **only** strings that already include explicit timezone information (`Z` or `±HH:MM`). Expose it as `parseIsoDate(input: unknown): Date` from `src/parseIsoDate.ts`.

## Acceptance Criteria
1. `parseIsoDate("2024-01-15T10:30:00Z")` MUST morph to a valid `Date` instance whose `toISOString()` returns `"2024-01-15T10:30:00.000Z"`.
2. `parseIsoDate("2024-01-15T10:30:00+05:00")` MUST morph to a `Date` instance.
3. `parseIsoDate("2024-01-15T10:30:00")` (no timezone) MUST be rejected.
4. `parseIsoDate("not-a-date")` MUST be rejected.
5. The exported function `parseIsoDate(input: unknown): Date` MUST throw on rejection (via `.assert(...)`).
