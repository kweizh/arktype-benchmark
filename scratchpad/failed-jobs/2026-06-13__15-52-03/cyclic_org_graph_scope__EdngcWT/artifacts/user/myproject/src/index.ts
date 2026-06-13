import { scope } from "arktype";

// ---------------------------------------------------------------------------
// Cyclic Member schema via scope
// ---------------------------------------------------------------------------
// ArkType resolves forward references inside a scope, making it possible to
// define a self-referential (cyclic) type where a Member can contain its
// manager (another Member) and an array of subordinates (Member[]).
// ---------------------------------------------------------------------------

const { Member } = scope({
  Member: {
    id: "string.uuid",
    name: "string",
    // Optional back-reference: the direct manager of this member
    "manager?": "Member",
    // Optional forward-reference: people who report to this member
    "subordinates?": "Member[]",
  },
}).export();

// ---------------------------------------------------------------------------
// findRoot – walks up / iterates the tree to find the top-level member
// (the one without a `manager` property).
// ---------------------------------------------------------------------------

type MemberType = typeof Member.infer;

export function findRoot(node: MemberType): MemberType {
  // If this node has a manager, walk up the hierarchy.
  if (node.manager !== undefined) {
    return findRoot(node.manager);
  }
  return node;
}

export { Member };

// ---------------------------------------------------------------------------
// Demo / smoke-test (runs when executed directly with `npx tsx src/index.ts`)
// ---------------------------------------------------------------------------

// Build a valid 3-level org tree (root → manager → subordinate)
const subordinate: MemberType = {
  id: "550e8400-e29b-41d4-a716-446655440002",
  name: "Alice (subordinate)",
};

const manager: MemberType = {
  id: "550e8400-e29b-41d4-a716-446655440001",
  name: "Bob (manager)",
  subordinates: [subordinate],
};

const root: MemberType = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  name: "Carol (root / CEO)",
  subordinates: [manager],
};

// Link back-references so the graph is fully cyclic
subordinate.manager = manager;
manager.manager = root;

// ── Criterion 1: valid 3-level tree MUST validate ──────────────────────────
console.log("=== Test 1: valid tree validates ===");
Member.assert(root);
console.log("✓ root validates");
Member.assert(manager);
console.log("✓ manager validates");
Member.assert(subordinate);
console.log("✓ subordinate validates");

// ── Criterion 2: invalid UUID must throw ───────────────────────────────────
console.log("\n=== Test 2: invalid UUID throws ===");
try {
  Member.assert({
    id: "not-a-uuid",
    name: "Bad Actor",
  });
  console.error("✗ Should have thrown for invalid UUID");
  process.exit(1);
} catch (e) {
  console.log("✓ Threw for invalid UUID:", (e as Error).message);
}

// ── Criterion 3: subordinates must be an array ─────────────────────────────
console.log("\n=== Test 3: non-array subordinates throws ===");
try {
  Member.assert({
    id: "550e8400-e29b-41d4-a716-446655440003",
    name: "Bad Node",
    subordinates: "not-an-array",
  });
  console.error("✗ Should have thrown for non-array subordinates");
  process.exit(1);
} catch (e) {
  console.log("✓ Threw for non-array subordinates:", (e as Error).message);
}

// ── Criterion 4: findRoot returns the top-level member ────────────────────
console.log("\n=== Test 4: findRoot returns the root ===");
const found = findRoot(subordinate);
if (found.id !== root.id) {
  console.error("✗ findRoot returned wrong node:", found.id);
  process.exit(1);
}
console.log("✓ findRoot returned root:", found.name);

console.log("\nAll tests passed ✓");
