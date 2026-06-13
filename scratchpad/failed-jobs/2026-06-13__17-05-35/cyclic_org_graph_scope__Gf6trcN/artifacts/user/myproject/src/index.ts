import { scope } from "arktype";

// Create a cyclic Member schema using scope().
// Both manager and subordinates are optional (defined with "?" suffix).
// manager references Member itself (cyclic), and subordinates is an array of Members.
// Each Member must have an id (UUID string) and a name (string).
export const { Member } = scope({
  Member: {
    id: "string.uuid",
    name: "string",
    "manager?": "Member",
    "subordinates?": "Member[]",
  },
}).export();

// findRoot: traverse up the manager chain to find the top-level member (one without a manager).
export function findRoot(member: typeof Member.infer): typeof Member.infer {
  let current = member;
  while (current.manager) {
    current = current.manager;
  }
  return current;
}
