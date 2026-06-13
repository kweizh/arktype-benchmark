ArkType utilizes morphs and pipes to execute data transformations (like parsing strings or coercing types) sequentially within validation checks. 

You need to implement a string-to-boolean morph pipeline named `StringToBoolSchema`. The schema must accept a string, evaluate it, and coerce the exact string literals `"true"`, `"1"`, and `"yes"` to the boolean `true`, and `"false"`, `"0"`, and `"no"` to the boolean `false`. 

**Constraints:**
- You MUST use ArkType's pipe operator (`|>` or `"to"`) for the transformation.
- The schema MUST throw or return a structured `TraversalError` if any unrecognized string is provided.
- Do NOT use external coercion libraries; rely strictly on ArkType's validation and morph functions.