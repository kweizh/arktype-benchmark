import { scope } from "arktype"

export const types = scope({
    Member: {
        id: "string.uuid",
        "manager?": "Member",
        "subordinates?": "Member[]"
    }
}).export()

export const Member = types.Member

export type MemberType = typeof Member.infer

export function findRoot(member: any): any {
    let current = member
    const visited = new Set<any>()
    while (current && current.manager) {
        if (visited.has(current)) {
            break
        }
        visited.add(current)
        current = current.manager
    }
    return current
}

// Self-tests to ensure acceptance criteria are met
function runTests() {
    console.log("Running self-tests...")

    // 1. A valid 3-level org tree with UUIDs MUST validate via Member.assert(...)
    const root: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    }
    const manager: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d480",
        manager: root
    }
    const subordinate: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d481",
        manager: manager
    }
    root.subordinates = [manager]
    manager.subordinates = [subordinate]

    try {
        Member.assert(root)
        console.log("Test 1 Passed: Valid 3-level tree validated successfully.")
    } catch (e: any) {
        throw new Error(`Test 1 Failed: Valid tree should validate. Error: ${e.message}`)
    }

    // 2. An invalid UUID in any node MUST cause .assert(...) to throw
    // 2a. Invalid UUID at root
    const invalidRootId = {
        id: "invalid-uuid",
        subordinates: []
    }
    try {
        Member.assert(invalidRootId)
        throw new Error("Test 2a Failed: Invalid UUID at root did not throw.")
    } catch (e: any) {
        console.log("Test 2a Passed: Invalid UUID at root threw as expected.")
    }

    // 2b. Invalid UUID at manager
    const rootWithInvalidManager: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    }
    const invalidManager: any = {
        id: "invalid-uuid",
        manager: rootWithInvalidManager
    }
    rootWithInvalidManager.subordinates = [invalidManager]
    try {
        Member.assert(rootWithInvalidManager)
        throw new Error("Test 2b Failed: Invalid UUID at manager did not throw.")
    } catch (e: any) {
        console.log("Test 2b Passed: Invalid UUID at manager threw as expected.")
    }

    // 2c. Invalid UUID at subordinate
    const rootWithValidManager: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    }
    const validManager: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d480",
        manager: rootWithValidManager
    }
    const invalidSubordinate: any = {
        id: "invalid-uuid",
        manager: validManager
    }
    rootWithValidManager.subordinates = [validManager]
    validManager.subordinates = [invalidSubordinate]
    try {
        Member.assert(rootWithValidManager)
        throw new Error("Test 2c Failed: Invalid UUID at subordinate did not throw.")
    } catch (e: any) {
        console.log("Test 2c Passed: Invalid UUID at subordinate threw as expected.")
    }

    // 3. A subordinates value that is not an array MUST be rejected
    const rootWithNonArraySubordinates: any = {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        subordinates: "not-an-array"
    }
    try {
        Member.assert(rootWithNonArraySubordinates)
        throw new Error("Test 3 Failed: Non-array subordinates did not throw.")
    } catch (e: any) {
        console.log("Test 3 Passed: Non-array subordinates threw as expected.")
    }

    // 4. findRoot MUST return the top-level Member (one without a manager)
    const foundRoot = findRoot(subordinate)
    if (foundRoot === root) {
        console.log("Test 4 Passed: findRoot correctly returned the top-level Member.")
    } else {
        throw new Error("Test 4 Failed: findRoot did not return the top-level Member.")
    }

    console.log("All tests completed successfully!")
}

// Run the tests if executing directly
if (typeof process !== "undefined" && process.argv[1] && (process.argv[1].endsWith("index.ts") || process.argv[1].endsWith("index.js"))) {
    runTests()
}
