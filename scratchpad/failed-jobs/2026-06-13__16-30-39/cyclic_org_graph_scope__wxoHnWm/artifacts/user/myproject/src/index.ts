import { scope } from "arktype";

const { Member } = scope({
  Member: {
    "id": "string.uuid",
    "name": "string",
    "manager?": "Member",
    "subordinates?": "Member[]",
  },
}).export();

type Member = typeof Member.infer;

function findRoot(member: Member): Member {
  let current: Member = member;
  while (current.manager) {
    current = current.manager;
  }
  return current;
}

// --- Demo / validation tests ---

const ceoId = "550e8400-e29b-41d4-a716-446655440000";
const vpId = "550e8400-e29b-41d4-a716-446655440001";
const engId = "550e8400-e29b-41d4-a716-446655440002";

// 1) Valid 3-level org tree must validate
const engineer = Member.assert({
  id: engId,
  name: "Alice",
  manager: {
    id: vpId,
    name: "Bob",
    manager: {
      id: ceoId,
      name: "Carol",
    },
  },
});

console.log("✅ Valid 3-level org tree validated:", engineer.name);

// 2) Invalid UUID must throw
try {
  Member.assert({ id: "not-a-uuid", name: "Bad" });
  console.error("❌ Invalid UUID was NOT rejected");
} catch {
  console.log("✅ Invalid UUID correctly rejected");
}

// 3) Non-array subordinates must be rejected
try {
  Member.assert({
    id: ceoId,
    name: "Carol",
    subordinates: "not-an-array" as unknown as never,
  });
  console.error("❌ Non-array subordinates was NOT rejected");
} catch {
  console.log("✅ Non-array subordinates correctly rejected");
}

// 4) findRoot must return the top-level member (no manager)
const root = findRoot(engineer);
console.log("✅ findRoot returned:", root.name, "(id:", root.id + ")");

export { Member, findRoot };