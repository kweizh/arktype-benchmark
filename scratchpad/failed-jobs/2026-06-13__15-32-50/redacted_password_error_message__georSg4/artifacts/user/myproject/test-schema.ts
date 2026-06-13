import { PasswordSchema } from "./src/schema.js";
import { type } from "arktype";

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

console.log("Running comprehensive tests for PasswordSchema...\n");

// Test 1: PasswordSchema is a function/validator
assert(typeof PasswordSchema === "function", "PasswordSchema should be a function");

// Test 2: Valid password (length >= 8)
const validPw = "longenoughpw";
const validResult = PasswordSchema(validPw);
assert(!(validResult instanceof type.errors), "Valid password should not produce errors");
assert(validResult === validPw, "Valid password should return the parsed value");
console.log("✅ Passed: Valid password ('longenoughpw') parses successfully.");

// Test 3: Valid password of exactly 8 characters (other than "mySecret")
const valid8Pw = "another8";
const valid8Result = PasswordSchema(valid8Pw);
assert(!(valid8Result instanceof type.errors), "Valid 8-char password should not produce errors");
assert(valid8Result === valid8Pw, "Valid 8-char password should return the parsed value");
console.log("✅ Passed: Valid 8-char password ('another8') parses successfully.");

// Test 4: Short password (length < 8)
const shortPw = "secret";
const shortResult = PasswordSchema(shortPw);
assert(shortResult instanceof type.errors, "Short password should produce errors");
const shortMsg = String(shortResult);
assert(shortMsg.includes("<redacted>"), "Error message for short password must contain '<redacted>'");
assert(!shortMsg.includes(shortPw), "Error message for short password must NOT contain the password itself");
console.log("✅ Passed: Short password ('secret') fails, is redacted, and doesn't leak password.");

// Test 5: "mySecret" password
const mySecretPw = "mySecret";
const mySecretResult = PasswordSchema(mySecretPw);
assert(mySecretResult instanceof type.errors, "'mySecret' should produce errors");
const mySecretMsg = String(mySecretResult);
assert(mySecretMsg.includes("<redacted>"), "Error message for 'mySecret' must contain '<redacted>'");
assert(!mySecretMsg.includes(mySecretPw), "Error message for 'mySecret' must NOT contain the password itself");
console.log("✅ Passed: 'mySecret' password fails, is redacted, and doesn't leak password.");

// Test 6: Non-string input
const numberInput = 123;
const numberResult = PasswordSchema(numberInput as any);
assert(numberResult instanceof type.errors, "Number input should produce errors");
const numberMsg = String(numberResult);
assert(numberMsg.includes("<redacted>"), "Error message for non-string must contain '<redacted>'");
assert(!numberMsg.includes("123"), "Error message for non-string must NOT contain the input value");
console.log("✅ Passed: Non-string input fails, is redacted, and doesn't leak value.");

console.log("\nAll tests passed successfully! 🎉");
