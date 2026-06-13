import { type } from "arktype";

// "ignore" is the default — undeclared keys pass through and are preserved
export const LooseUser = type({
  name: "string",
});

// "reject" — undeclared keys cause validation failure (returns type.errors)
export const RejectUser = type({
  name: "string",
}).onUndeclaredKey("reject");

// "delete" — undeclared keys are stripped from the output
export const DeleteUser = type({
  name: "string",
}).onUndeclaredKey("delete");
