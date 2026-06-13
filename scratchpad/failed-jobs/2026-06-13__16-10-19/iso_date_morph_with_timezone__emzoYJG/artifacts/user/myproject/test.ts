import { type } from "arktype";

const IsoDateWithTimezone = type("string")
    .narrow((s) => {
        const regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
        if (!regex.test(s)) return false;
        return !Number.isNaN(Date.parse(s));
    })
    .pipe((s) => new Date(s));

export function parseIsoDate(input: unknown): Date {
    return IsoDateWithTimezone.assert(input);
}

console.log(parseIsoDate("2024-01-15T10:30:00Z"));
console.log(parseIsoDate("2024-01-15T10:30:00+05:00"));

try {
    parseIsoDate("2024-01-15T10:30:00");
    console.error("Should have thrown");
} catch (e) {
    console.log("Threw correctly for no timezone");
}

try {
    parseIsoDate("not-a-date");
    console.error("Should have thrown");
} catch (e) {
    console.log("Threw correctly for not-a-date");
}
