import { parseIsoDate } from "./parseIsoDate.js"
import assert from "assert"

console.log("Starting validation tests...")

try {
  // 1. parseIsoDate("2024-01-15T10:30:00Z") MUST morph to a valid Date instance whose toISOString() returns "2024-01-15T10:30:00.000Z".
  const d1 = parseIsoDate("2024-01-15T10:30:00Z")
  assert(d1 instanceof Date, "d1 should be a Date instance")
  assert.strictEqual(d1.toISOString(), "2024-01-15T10:30:00.000Z", "d1.toISOString() mismatch")
  console.log("✓ Criterion 1 passed: 2024-01-15T10:30:00Z -> Date")

  // 2. parseIsoDate("2024-01-15T10:30:00+05:00") MUST morph to a Date instance.
  const d2 = parseIsoDate("2024-01-15T10:30:00+05:00")
  assert(d2 instanceof Date, "d2 should be a Date instance")
  assert.strictEqual(d2.toISOString(), "2024-01-15T05:30:00.000Z", "d2.toISOString() mismatch")
  console.log("✓ Criterion 2 passed: 2024-01-15T10:30:00+05:00 -> Date")

  // 3. parseIsoDate("2024-01-15T10:30:00") (no timezone) MUST be rejected.
  assert.throws(() => {
    parseIsoDate("2024-01-15T10:30:00")
  }, /an ISO-8601 date string with an explicit timezone/)
  console.log("✓ Criterion 3 passed: 2024-01-15T10:30:00 rejected")

  // 4. parseIsoDate("not-a-date") MUST be rejected.
  assert.throws(() => {
    parseIsoDate("not-a-date")
  }, /an ISO-8601 date string with an explicit timezone/)
  console.log("✓ Criterion 4 passed: 'not-a-date' rejected")

  // 5. The exported function parseIsoDate(input: unknown): Date MUST throw on rejection (via .assert(...)).
  assert.throws(() => {
    parseIsoDate(123)
  })
  assert.throws(() => {
    parseIsoDate(null)
  })
  assert.throws(() => {
    parseIsoDate(undefined)
  })
  assert.throws(() => {
    parseIsoDate({})
  })
  console.log("✓ Criterion 5 passed: non-string inputs rejected")

  console.log("All validation tests passed successfully!")
} catch (error) {
  console.error("Validation tests failed:", error)
  process.exit(1)
}
