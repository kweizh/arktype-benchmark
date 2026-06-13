import { type } from "arktype";

// Shared schema used by both index.ts and broken.ts.
// Whether { x: NaN } is accepted depends entirely on whether
// configure({ numberAllowsNaN: true }) was called BEFORE this
// module was first imported (i.e. before this type was compiled).
export const Point = type({ x: "number" });
