import { type } from "arktype"

// This schema is defined at module-load time. Whether it allows NaN
// depends on whether the global config has already been applied
// when this module is first imported.
export const schema = type({ x: "number" })