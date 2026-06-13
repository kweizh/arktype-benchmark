import { type } from "arktype";

export const LooseUser = type({
    name: "string"
});

export const RejectUser = type({
    name: "string",
    "+": "reject"
});

export const DeleteUser = type({
    name: "string",
    "+": "delete"
});
