ArkType 2.2 provides the `type.fn` utility to validate function inputs and return values at runtime, preventing invalid data from propagating through core logic functions.

You need to create a validated function named `calculateTotal` using `type.fn`. The function must accept an array of numbers (`prices`) as its first parameter, and an optional numeric multiplier (`taxRate`) defaulting to `0.1` as its second parameter. It must return a validated numeric `total`.

**Constraints:**
- You MUST use the `type.fn` API introduced in ArkType 2.2.
- The default value for the second parameter MUST be defined syntactically within the ArkType string expression (e.g., `number = 0.1`).
- The function must throw a `TraversalError` if invoked with an array containing non-numeric strings.