import { type } from "arktype";

export const LooseUser = type({ name: "string" });

export const RejectUser = type({ name: "string" }).onUndeclaredKey("reject");

export const DeleteUser = type({ name: "string" }).onUndeclaredKey("delete");