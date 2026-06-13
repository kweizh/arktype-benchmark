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
