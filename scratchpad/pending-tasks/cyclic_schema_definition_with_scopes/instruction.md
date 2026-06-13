Recursive and cyclic data structures require encapsulated resolution spaces, known as "scopes," to avoid endless loops and compile-time TypeScript reference errors.

You need to define a recursive file system schema using `scope`. The scope should contain a `File` alias (an object with a `name` string and `size` integer) and a `Directory` alias (an object with a `name` string and a `contents` array that can contain either `File` or `Directory` objects). You must then export the scope as a reusable module.

**Constraints:**
- You MUST use the `scope` function to define the cyclic relationships.
- You MUST export the scope using `.export()` to make the module reusable.
- The `contents` array must properly reference the internal aliases defined within the scope space.