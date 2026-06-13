import { LooseUser, RejectUser, DeleteUser } from "./src/schemas.js"
import { type } from "arktype"

console.log("Starting tests...")

// Test 1: LooseUser({ name: "a", extra: 1 }) MUST return an object where extra === 1.
const looseResult = LooseUser({ name: "a", extra: 1 })
if (looseResult instanceof type.errors) {
    console.error("FAIL: LooseUser failed validation on extra key", looseResult.summary)
    process.exit(1)
} else if ((looseResult as any).extra !== 1) {
    console.error("FAIL: LooseUser did not preserve 'extra' key", looseResult)
    process.exit(1)
} else {
    console.log("PASS: LooseUser preserves extra keys")
}

// Test 2: RejectUser({ name: "a", extra: 1 }) MUST return a type.errors instance (validation failure).
const rejectResult = RejectUser({ name: "a", extra: 1 })
if (!(rejectResult instanceof type.errors)) {
    console.error("FAIL: RejectUser did not return a type.errors instance", rejectResult)
    process.exit(1)
} else {
    console.log("PASS: RejectUser correctly returned validation failure (type.errors)")
}

// Test 3: DeleteUser({ name: "a", extra: 1 }) MUST return an object where "extra" in result === false.
const deleteResult = DeleteUser({ name: "a", extra: 1 })
if (deleteResult instanceof type.errors) {
    console.error("FAIL: DeleteUser failed validation on extra key", deleteResult.summary)
    process.exit(1)
} else if ("extra" in (deleteResult as any)) {
    console.error("FAIL: DeleteUser did not delete the 'extra' key", deleteResult)
    process.exit(1)
} else {
    console.log("PASS: DeleteUser correctly deleted the extra key")
}

// Test 4: All three schemas MUST accept { name: "a" } without errors (no type.errors returned).
const looseOk = LooseUser({ name: "a" })
const rejectOk = RejectUser({ name: "a" })
const deleteOk = DeleteUser({ name: "a" })

if (looseOk instanceof type.errors) {
    console.error("FAIL: LooseUser rejected valid name", looseOk.summary)
    process.exit(1)
}
if (rejectOk instanceof type.errors) {
    console.error("FAIL: RejectUser rejected valid name", rejectOk.summary)
    process.exit(1)
}
if (deleteOk instanceof type.errors) {
    console.error("FAIL: DeleteUser rejected valid name", deleteOk.summary)
    process.exit(1)
}

console.log("PASS: All schemas accepted valid name")
console.log("ALL TESTS PASSED SUCCESSFULLY!")
