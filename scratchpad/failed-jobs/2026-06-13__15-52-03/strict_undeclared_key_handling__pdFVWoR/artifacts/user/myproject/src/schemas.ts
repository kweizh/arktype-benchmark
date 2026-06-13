import { type } from "arktype"

// Loose (default): undeclared keys are passed through as-is
export const LooseUser = type({
	name: "string",
	"+": "ignore"
})

// Reject: undeclared keys cause a validation failure
export const RejectUser = type({
	name: "string",
	"+": "reject"
})

// Delete: undeclared keys are stripped from the output
export const DeleteUser = type({
	name: "string",
	"+": "delete"
})
