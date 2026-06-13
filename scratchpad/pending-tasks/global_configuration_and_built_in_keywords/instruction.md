ArkType caches and compiles built-in keywords as soon as the library is imported. Applying global configuration changes too late in the execution cycle will fail to configure these built-in keywords.

You need to correctly set up a global ArkType configuration that modifies the default number validation behavior in a Node.js environment. Create two files: a `config.ts` file that globally disables `NaN` for numbers (setting `numberAllowsNaN: false`), and an `index.ts` file that imports this configuration and defines a simple user schema with an alphanumeric `username` and an `email`.

**Constraints:**
- You MUST separate the configuration into its own `config.ts` file.
- You MUST import `config.ts` into your entrypoint (`index.ts`) BEFORE any `"arktype"` imports to avoid the cached keyword friction point.
- Do NOT use standard TypeScript configuration files for this runtime logic; use `"arktype/config"`.